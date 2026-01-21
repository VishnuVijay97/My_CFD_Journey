# CHT Heat Exchanger Automation (OpenFOAM)

This project is a reproducible CFD workflow demonstrating **multi-region conjugate heat transfer (CHT)** with **automation**:
- Two regions: `air` + `porous`
- Rotor/zone preparation in `air` (topology + baffles + MRF zone)
- Parametric sweep over operating conditions
- Automated KPI extraction + cross-case comparison plots

---

## What this project demonstrates

### Physics / Modeling
- Multi-region CHT simulation using `chtMultiRegionSimpleFoam`
- Region coupling via multi-region framework (`constant/regionProperties`)
- Porous region modeled as a separate region (`porous`) with its own properties
- Rotor handling in `air`:
  - `topoSet` to create sets/zones (`system/air/topoSetDict.1`, `topoSetDict.2`)
  - `createBaffles` for internal surfaces (as configured by the case)
  - `MRFProperties` in `constant/air/`

### Automation / Engineering workflow
- Batch runs with a parameter sweep:
  - `U_air` (m/s)
  - `T_porous_inlet` (K)
- Controlled parallel execution:
  - `decomposePar -allRegions`
  - `mpirun ... chtMultiRegionSimpleFoam -parallel`
  - `reconstructPar -allRegions -latestTime`
- KPI post-processing scripts:
  - per-case KPI plots
  - global comparison summary (`CSV` + plots)

---

## Repository policy (important)
Large generated data is intentionally **NOT** version-controlled:
- Mesh: `constant/**/polyMesh/`
- Runtime outputs: `processor*/`, `postProcessing/`, `VTK/`
- Sweep run folders: `run_*`
This keeps the repo lightweight and reviewable. The workflow regenerates what it needs from the case setup and scripts.

---

## Folder structure

- `heatExchanger_base/`  
  Base multi-region case (inputs only). Contains:
  - `0/` and `0.orig/` (initial fields)
  - `constant/` (region properties, MRF, thermophysical props, etc.)
  - `system/` (numerics + region dictionaries)
    - `system/air/blockMeshDict`, `topoSetDict.*`, `createBafflesDict`, etc.
    - `system/porous/blockMeshDict`, etc.

- `setParams.sh`  
  Applies sweep parameters to the copied case folder.

- `sweep_parallel.sh`  
  Main automation script: clones base case, generates mesh + zones, runs solver in parallel, reconstructs, and triggers KPI scripts.

- `scripts/`
  - `plot_case_kpis.py`
  - `compare_cases.py`

- `results_global/`  
  Global KPI plots + `kpi_summary.csv` (small artifacts kept for portfolio review).

- `Heat_Exchanger_Automation_Report.pdf`  
  Project documentation/report.

---

## Requirements
- OpenFOAM installed and sourced (e.g., `source /opt/openfoam*/etc/bashrc`)
- MPI available (`mpirun`)
- Python 3 for plotting scripts

Check quickly:
```bash
which chtMultiRegionSimpleFoam
which mpirun
python3 --version
