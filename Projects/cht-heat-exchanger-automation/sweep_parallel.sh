#!/usr/bin/env bash
set -euo pipefail

BASE="heatExchanger_base"

# Sweep Settings 2*2=4cases
U_LIST=(5 8)
T_LIST=(400 440)

# Parallel Settings (my machine safe max proc = 12)
NPROCS_PER_CASE=4
MAX_CONCURRENT_CASES=2

#  clean processors after reconstructions
CLEAN_PROCESSORS=true

#  Safety Checks before running

# check base exists
if [ ! -d "$BASE" ]; then
    echo "ERROR: Base case folder '$BASE' not found."
    exit 1
fi

# check setter script exists and executable
if [ ! -x "./setParams.sh" ]; then
    echo "ERROR: setParams.sh not found or not executable."
    echo " Run : chmod +x setParams.sh"
    exit 1
fi

# check decomposePar dict
if [ ! -f "$BASE/system/decomposeParDict" ]; then
    echo "ERROR: $BASE/system/decomposeParDict not found."
    exit 1
fi


#  Main run_function()
run_case() {
    local caseDir="$1"
    local U="$2"
    local T="$3"

    # print status header
    echo "=========================================="
    echo "Running case : $caseDir"
    echo "U_air= $U (m/s) | T-porous_inlet= $T (k)"
    echo "MPI ranks per case = $NPROCS_PER_CASE"
    echo "=========================================="

    #create fresh case folder
    rm -rf "$caseDir"
    cp -r "$BASE" "$caseDir"

    #  Apply parameters using setter script
    ./setParams.sh "$caseDir" "$U" "$T" > "$caseDir/log.setParams" 2>&1


    # Run OpenFOAM solver pipeline
    (
    cd "$caseDir"

    # ------------------------------------------
    # 0) Clean any old generated mesh/results
    # ------------------------------------------
    rm -rf constant/polyMesh constant/*/polyMesh
    rm -rf processor* postProcessing VTK
    rm -f log.blockMesh.* log.topoSet.* log.createBaffles.* log.checkMesh.*

    # ------------------------------------------
    # 1) Mesh generation (multi-region)
    # ------------------------------------------
    blockMesh -region air    > log.blockMesh.air    2>&1
    blockMesh -region porous > log.blockMesh.porous 2>&1

    # Optional but recommended sanity check:
    checkMesh -region air    > log.checkMesh.air    2>&1
    checkMesh -region porous > log.checkMesh.porous 2>&1

    # ------------------------------------------
    # 2) Rotor blades / baffles in air region
    # ------------------------------------------
    topoSet -region air -dict system/topoSetDict.1 > log.topoSet.air.1 2>&1

    # If createBaffles ever prompts interactively, uncomment the 'yes |' variant.
    createBaffles -region air -overwrite > log.createBaffles.air 2>&1
    # yes | createBaffles -region air -overwrite > log.createBaffles.air 2>&1

    # ------------------------------------------
    # 3) Rotor zone for MRF (cellZone creation)
    # ------------------------------------------
    topoSet -region air -dict system/topoSetDict.2 > log.topoSet.air.2 2>&1

    # remove topoSet intermediate artifacts (safe after topoSet)
    rm -rf constant/air/polyMesh/sets

    # ------------------------------------------
    # 4) Parallel pipeline
    # ------------------------------------------
    decomposePar -allRegions -force > log.decompose 2>&1

    mpirun -np "$NPROCS_PER_CASE" chtMultiRegionSimpleFoam -parallel > log.solve 2>&1

    foamLog log.solve > log.foamLog 2>&1 || true

    reconstructPar -allRegions -latestTime > log.reconstruct 2>&1

    if [ "$CLEAN_PROCESSORS" = true ]; then
        rm -rf processor*
    fi
)

     echo " Finished case : $caseDir"

}

#  Active job counter
active_jobs() {
    jobs -rp | wc -l
}

#  tracking background process
pids=()

#  Nested sweep loop to launch the cases
 for U in "${U_LIST[@]}"; do
    for T in "${T_LIST[@]}"; do
        caseDir="run_U${U}_Tp${T}"

        #wait until we have a freeslot
        while [ "$(active_jobs)" -ge "$MAX_CONCURRENT_CASES" ]; do
            sleep 2
        done

        #Launching the case in background
        run_case "$caseDir" "$U" "$T" &
        pids+=($!)
    done
done

# waiting for all cases to finish
 fail=0
 for pid in "${pids[@]}"; do
    if ! wait "$pid"; then
        fail=1
    fi
done

if [ "$fail" -ne 0 ]; then
    echo " one or more cases failed. check log.solve inside each case folder."
    exit 1
fi

echo " All cases completed successfully"


echo "=========================================="
echo "Post-processing: plotting KPI histories"
echo "=========================================="

mkdir -p logs

python3 scripts/plot_case_kpis.py > logs/log.plotKpis 2>&1 || true

echo " KPI plots generated (check logs/log.plotKpis)"


python3 scripts/compare_cases.py > logs/log.compareCases 2>&1 || true
echo " Global KPI summary generated (results_global/)"
