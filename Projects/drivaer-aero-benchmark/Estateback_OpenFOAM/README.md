# DrivAer Estateback (OpenFOAM) — Run Guide (Allrun workflow)

This OpenFOAM case is designed to be run using a single script (`Allrun`) that:
1) cleans old results,
2) converts a Fluent mesh (`.msh`) to OpenFOAM (`polyMesh`),
3) checks mesh quality,
4) runs the solver (parallel),
5) reconstructs results,
6) runs basic post-processing,
7) prepares ParaView.

The Fluent mesh is **not stored in GitHub** because it is large. You download it from Google Drive and place it in `data/`.

---

## Folder structure (important)

Inside `Projects/drivaer-aero-benchmark/Estateback_OpenFOAM/`:

- `case_base/`  
  OpenFOAM inputs (`0/`, `constant/`, `system/`) **without** `polyMesh`

- `data/`  
  You place the Fluent mesh here: `estateback.msh` (downloaded)

- `run_case/`  
  Created locally by you. This is the working directory that will contain:
  - `constant/polyMesh` (generated)
  - time folders (results)
  - logs, postProcessing output

---

## Requirements

- OpenFOAM installed and available in your shell (`source .../etc/bashrc`)
- MPI available (for parallel run): `mpirun`
- Optional but recommended: `dos2unix`, `gzip`

---

## Step 1 — Download mesh (required)

Download `estateback.msh`:
- https://drive.google.com/file/d/1gZUXGs3iyH5QFQRo5zy6YsoTs_BTFb43/view?usp=sharing

Place it here:
- `Projects/drivaer-aero-benchmark/Estateback_OpenFOAM/data/estateback.msh`

### Verify download (recommended)
From repo root:
```bash
sha256sum Projects/drivaer-aero-benchmark/Estateback_OpenFOAM/data/estateback.msh
