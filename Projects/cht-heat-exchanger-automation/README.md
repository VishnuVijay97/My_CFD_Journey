# CHT Heat Exchanger Automation (OpenFOAM)

## What this project is
Multi-region conjugate heat transfer (air + porous region) case automated with a parametric sweep.

## What it demonstrates
- Multi-region CHT setup (air + porous)
- Automated parametric sweep:
  - Air inlet velocity: `U_air` (m/s)
  - Porous inlet temperature: `T_porous_inlet` (K)
- Automated post-processing: KPI extraction + comparison plots

## How to run

### 1) Requirements
- OpenFOAM environment sourced
- MPI available (`mpirun`)
- Python3 for plotting scripts

### 2) Run the sweep
From this folder:
```bash
chmod +x sweep_parallel.sh setParams.sh
./sweep_parallel.sh
