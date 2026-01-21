# DrivAer Estateback (ANSYS Fluent) – Curated Inputs

This folder contains the **minimal reproducible input pack** for my DrivAer Estateback Fluent run.
The full run history (transcripts, videos, backups) is intentionally excluded from Git to keep the repo clean.

## Use these files (in `data/`)
- `trial2_ver4.msh.h5`  
  Mesh file (Fluent Meshing output)

- `trial2_ver4_noslip_final.cas.h5`  
  Fluent case setup (models, materials, BCs, solver settings, cavitation setup, etc.)

- `trial2_ver4.cst` (optional)  
  Fluent session/state file (GUI state). Not required for batch runs.

- `DrivAerCar_Estateback_Rear_End_1.3.scdocx` (optional)  
  CAD reference used during setup (kept for traceability).

## How to run (high level)
### GUI
1) Open Fluent
2) Read Case:
   - File → Read → Case… → `data/trial2_ver4_noslip_final.cas.h5`
3) If needed, read mesh:
   - File → Read → Mesh… → `data/trial2_ver4.msh.h5`
4) Initialize → Run iterations
5) Export the solution data to run it in CFD-Post using the state file from the data folder.

