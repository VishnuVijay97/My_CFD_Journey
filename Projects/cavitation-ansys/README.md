# ANSYS Fluent Cavitation (Journal-Driven Workflow)

This project is structured so that the **case can be reproduced by running a Fluent journal**.
The repository keeps only the **minimum required inputs + documentation**, and ignores large solver outputs and backups.

---

## What you get in this repo

### 1) Documentation
- `Cavitation.pdf` : report / explanation
- `Cavitation.pptx` : presentation slides
- `meshpu12.png`, `meshpuc.png`, `pr_bar.png`, `vel_bar.png` : small preview images

### 2) Minimal reproducible inputs (important)
All required run inputs are inside:

- `data/`

Expected files in `data/`:
- `orifice.msh.h5`  → mesh (required)
- `orifice.cas.h5`  → Fluent case setup (required)
- `fix.jou` (or main journal) → journal that sets up/updates and runs the simulation (required)

> **Why both mesh + case?**  
> - The mesh is the geometry discretization.  
> - The case contains physics models, materials, BCs, solver settings, cavitation setup, etc.  
> Depending on how the journal is written, it may read the mesh or it may read the case directly.
> Keeping both makes the workflow robust across machines.

---

## What is intentionally NOT tracked (ignored)
These folders/files are kept locally but not pushed to GitHub because they are large and/or generated:
- Solver dumps / backups: `*.trn`
- Large run outputs: `*.dat.h5`, report `.out` files
- Old parametric variants: `orifice0.5p*`, `orifice1p*`, etc.
- Workflow artifacts: `*_workflow_files/`
- Result folders like `sol/`
- Any extra mesh duplicates under `mesh/` or `case and data/`

This keeps the repo reviewable and avoids accidental multi-GB uploads.

---

## How to run (batch mode)

### Option A — Run from Fluent GUI (simple)
1. Open Fluent
2. Set working directory to this project folder:
   `Projects/cavitation-ansys/`
3. Run the journal:
   - File → Read → Journal…
   - Select: `data/fix.jou`

### Option B — Run from command line (recommended for reproducibility)
From **Windows CMD/PowerShell**, inside this folder, run:

```bat
fluent 3ddp -g -t4 -i data\fix.jou
