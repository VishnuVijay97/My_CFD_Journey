#!/usr/bin/env python3
from pathlib import Path
import re
import csv
import numpy as np
import matplotlib.pyplot as plt

# --- KPIs produced by your functionObjects ---
KPI_LIST = [
    "Tin_air",
    "Tout_air",
    "Pin_air",
    "Pout_air",
    "mdot_air_out",
    "Tout_porous",
]

# --- Region mapping for your multi-region postProcessing layout ---
KPI_REGION = {
    "Tin_air": "air",
    "Tout_air": "air",
    "Pin_air": "air",
    "Pout_air": "air",
    "mdot_air_out": "air",
    "Tout_porous": "porous",
}

def parse_case_inputs(case_name: str):
    """
    Extract U and Tp from folder name: run_U5_Tp400
    """
    m = re.search(r"run_U(\d+)_Tp(\d+)", case_name)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))

def find_latest_dat_file(func_dir: Path) -> Path | None:
    """
    Find newest .dat file under a functionObject directory.
    """
    if not func_dir.exists():
        return None
    dats = sorted(func_dir.rglob("*.dat"))
    if not dats:
        return None
    return dats[-1]

def read_last_value(file_path: Path) -> float | None:
    """
    Read last numeric value from an OpenFOAM .dat file:
    - ignore '#'
    - last column is KPI value
    """
    last_val = None
    with file_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            try:
                last_val = float(parts[-1])
            except ValueError:
                continue
    return last_val

def get_kpi_final(case_dir: Path, kpi: str) -> float | None:
    """
    Return final value of a KPI from:
      postProcessing/<region>/<kpi>/.../*.dat   (multi-region style)
    or postProcessing/<kpi>/.../*.dat          (fallback)
    """
    post = case_dir / "postProcessing"
    region = KPI_REGION.get(kpi)

    candidates = [post / kpi]
    if region:
        candidates.append(post / region / kpi)

    dat_file = None
    for func_dir in candidates:
        dat_file = find_latest_dat_file(func_dir)
        if dat_file is not None:
            break

    if dat_file is None:
        return None

    return read_last_value(dat_file)

def save_bar_plot(labels, values, title, ylabel, out_png):
    plt.figure(figsize=(10, 4))
    plt.bar(labels, values)
    plt.grid(True, axis="y")
    plt.xticks(rotation=30, ha="right")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(out_png, dpi=180)
    plt.close()

def save_scatter_plot(x, y, labels, title, xlabel, ylabel, out_png):
    plt.figure(figsize=(6, 5))
    plt.scatter(x, y)
    for xi, yi, lab in zip(x, y, labels):
        plt.annotate(lab, (xi, yi), fontsize=8, xytext=(5, 5), textcoords="offset points")
    plt.grid(True)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(out_png, dpi=180)
    plt.close()

def main():
    root = Path(".")
    cases = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("run_U")])

    if not cases:
        print("❌ No cases found like run_U*_Tp* in current directory.")
        return

    results_dir = root / "results_global"
    results_dir.mkdir(exist_ok=True)

    rows = []

    for case in cases:
        U, Tp = parse_case_inputs(case.name)
        if U is None:
            continue

        # read finals
        vals = {}
        for kpi in KPI_LIST:
            vals[kpi] = get_kpi_final(case, kpi)

        Tin = vals["Tin_air"]
        Tout = vals["Tout_air"]
        Pin = vals["Pin_air"]
        Pout = vals["Pout_air"]
        mdot = vals["mdot_air_out"]
        Tpor_out = vals["Tout_porous"]

        # derived
        dT = (Tout - Tin) if (Tin is not None and Tout is not None) else None
        dP = (Pin - Pout) if (Pin is not None and Pout is not None) else None

        # store
        rows.append({
            "case": case.name,
            "U_air": U,
            "Tpor_in": Tp,
            "Tin_air": Tin,
            "Tout_air": Tout,
            "DeltaT_air": dT,
            "Pin_air": Pin,
            "Pout_air": Pout,
            "DeltaP_air": dP,
            "mdot_air_out": mdot,
            "Tout_porous": Tpor_out
        })

    # ---- write CSV summary ----
    csv_path = results_dir / "kpi_summary.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Wrote: {csv_path}")

    # ---- global plots (final values) ----
    labels = [r["case"] for r in rows]

    def safe_vals(key):
        out = []
        for r in rows:
            v = r[key]
            out.append(np.nan if v is None else v)
        return np.array(out, dtype=float)

    Tout_all = safe_vals("Tout_air")
    dT_all   = safe_vals("DeltaT_air")
    dP_all   = safe_vals("DeltaP_air")
    mdot_all = safe_vals("mdot_air_out")

    save_bar_plot(labels, Tout_all, "Tout_air (final) by case", "Tout_air (K)", results_dir / "Tout_air_final.png")
    save_bar_plot(labels, dT_all,   "DeltaT_air (final) by case", "DeltaT_air (K)", results_dir / "DeltaT_air_final.png")
    save_bar_plot(labels, dP_all,   "DeltaP_air (final) by case", "DeltaP_air (Pa)", results_dir / "DeltaP_air_final.png")
    save_bar_plot(labels, mdot_all, "mdot_air_out (final) by case", "sum(phi) (solver units)", results_dir / "mdot_air_out_final.png")

    # ---- tradeoff plot: DeltaT vs DeltaP ----
    if not np.all(np.isnan(dT_all)) and not np.all(np.isnan(dP_all)):
        save_scatter_plot(
            dP_all, dT_all, labels,
            "Tradeoff: DeltaT_air vs DeltaP_air (final)",
            "DeltaP_air (Pa)",
            "DeltaT_air (K)",
            results_dir / "DeltaT_vs_DeltaP.png"
        )

    print("✅ Global comparison plots written to results_global/")

if __name__ == "__main__":
    main()
