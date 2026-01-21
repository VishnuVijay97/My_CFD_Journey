#!/usr/bin/env bash
set -e

#  Argument counter check
if [ $# -ne 3 ]; then
    echo " Usage : $0 <caseDir> <U_air_mps> <T_porous_K>"
    exit 1
fi

#  Read inpt arguments into variable
caseDir="$1"
Uair="$2"
Tpor="$3"

# Folder existence check
if [ ! -d "$caseDir" ]; then
    echo " ERROR: caseDir '$caseDir' doesnot exist"
    exit 1
fi

#  Base line constants
U0=5.0
k0=0.375
eps0=0.54

# Compute k_new and eps_new based on new air inlet velocity
read kNew epsNew < <(python3 - <<PY
U=float("$Uair")
U0=float("$U0")
k0=float("$k0")
e0=float("$eps0")
k = k0*(U/U0)**2
e = e0*(U/U0)**3
print(k, e)
PY
)

#  Print values been applied
echo "Case: $caseDir"
echo "U_air = $Uair m/s"
echo "T_porous_inlet = $Tpor K"
echo "k_air = $kNew"
echo "epsilon_air = $epsNew"

#  Modify OpenFOAM dictionaries using foamDictioanry

foamDictionary \
    -entry "boundaryField.inlet.value" \
    -set "uniform (0 0 $Uair)" \
"$caseDir/0/air/U"

foamDictionary \
    -entry "internalField" \
    -set "uniform $kNew" \
"$caseDir/0/air/k"

foamDictionary \
    -entry "internalField" \
    -set "uniform $epsNew" \
"$caseDir/0/air/epsilon"

foamDictionary \
    -entry "boundaryField.inlet.value" \
    -set "uniform $Tpor" \
"$caseDir/0/porous/T"

# Final confirmation.
echo "parameters updated."