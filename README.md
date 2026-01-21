# My_CFD_JOURNEY

A curated portfolio of CFD/CAE projects focused on **reproducible workflows**, **automation**, and **engineering-grade documentation**.  
Each project folder contains its own `README.md` with setup + run instructions.

> Note: Large simulation artifacts (e.g., `polyMesh/`, `processor*/`, large Fluent files, time directories) are intentionally excluded from Git to keep the repository reviewable. Where required, large inputs are provided via a `data/` folder + external download link + checksum.

---

## Projects

### 1) CHT Heat Exchanger Automation (OpenFOAM)
**Folder:** `Projects/cht-heat-exchanger-automation/`

**What it is:** Conjugate Heat Transfer (CHT) multi-region case automated with a parameter sweep and KPI extraction.

**What it demonstrates:**
- OpenFOAM multi-region CHT workflow (`chtMultiRegionSimpleFoam`)
- Automation: parametric sweep (velocity + temperature), parallel execution, logging discipline
- Post-processing: automated KPI plots + CSV summary (ΔP, ΔT, outlet temperature, mass flow trends)

**Outputs:** `results_global/` (plots + summary CSV), `logs/` (run logs), `scripts/` (Python plotting/comparison)

---

### 2) Cavitation Study (ANSYS Fluent)
**Folder:** `Projects/cavitation-ansys/`

**What it is:** Cavitation simulation workflow in ANSYS Fluent, structured so the setup is reproducible from a minimal set of inputs.

**What it demonstrates:**
- Fluent workflow organization (case/mesh/journal approach)
- Keeping only “reproducibility-critical” files tracked (journal + one mesh + one base case as needed)
- Clear separation between inputs (`data/`) and generated artifacts (ignored)

**How to reproduce:** Use the project README and run the journal/setup procedure using the files in `data/`.

---

### 3) DrivAer Aerodynamic Benchmark (ANSYS + OpenFOAM)
**Folder:** `Projects/drivaer-aero-benchmark/`

**What it is:** External aerodynamics benchmarking on DrivAer Estateback configuration, with both ANSYS (workflow capture) and OpenFOAM (mesh conversion + solver pipeline).

**What it demonstrates:**
- Practical portfolio approach: store only the minimal reproducible inputs + clear instructions
- Fluent → OpenFOAM mesh conversion workflow (with external mesh download + checksum)
- Automated “one-command” run philosophy using `Allrun` (OpenFOAM)

**Sub-structure (typical):**
- `Estateback_Ansys/` → curated ANSYS inputs and a minimal workflow pack
- `Estateback_OpenFOAM/` → `case_base/`, `data/` (external mesh), and `Allrun`-style run pipeline

---

## Repo conventions (important)

### `data/` folders
Some projects include a `data/` folder containing the **minimum** large inputs needed to reproduce the case (mesh/case/journal).  
Large files are often **not** committed to GitHub; instead the project README provides:
- a download link (e.g., Google Drive)
- a checksum (SHA-256) to verify integrity
- commands to regenerate OpenFOAM meshes / run scripts

### What is intentionally NOT tracked
To keep the repo lean and reviewable:
- OpenFOAM generated mesh: `constant/polyMesh/`
- solver outputs: time folders like `1000/`, `2000/`, etc.
- `processor*/`, `postProcessing/`, logs
- Fluent heavy artifacts (`*.trn`, huge `*.dat.h5`, etc.) unless explicitly required

---

## Quick navigation

- Certificates: `Certificates/`
- All projects: `Projects/`
  - `Projects/cht-heat-exchanger-automation/`
  - `Projects/cavitation-ansys/`
  - `Projects/drivaer-aero-benchmark/`

---

## Contact / context
This repository is maintained as a professional CFD portfolio: emphasis is on **repeatable workflows**, **clean structure**, and **engineering reasoning** in the documentation.
