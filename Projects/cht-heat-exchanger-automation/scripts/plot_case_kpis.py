#!/usr/bin/env python3
from pathlib import Path
import re
import numpy as np
import matplotlib.pyplot as plt

# ---- FunctionObject names (must match controlDict) ----
KPI_LIST = [
    "Tin_air",
    "Tout_air",
    "Pin_air",
    "Pout_air",
    "mdot_air_out",
    "Tout_porous",
]

# ---- Region mapping for multi-region postProcessing structure ----
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
    Extract U and Tp from folder name like: run_U5_Tp400
    """
    m = re.search(r"run_U(\d+)_Tp(\d+)", case_name)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def find_latest_dat_file(func_dir: Path) -> Path | None:
    """
    Finds the latest *.dat file inside:
      postProcessing/<kpi>/<time>/surfaceFieldValue.dat
    or (multi-region):
      postProcessing/<region>/<kpi>/<time>/surfaceFieldValue.dat
    """
    if not func_dir.exists():
        return None

    dat_files = sorted(func_dir.rglob("*.dat"))
    if not dat_files:
        return None

    return dat_files[-1]


def read_foam_dat(file_path: Path):
    """
    Reads an OpenFOAM functionObject .dat file:
    - skips comment lines starting with '#'
    - assumes col0 = iteration/time
    - assumes last column = KPI value
    """
    xs, ys = [], []

    with file_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            try:
                x = float(parts[0])
                y = float(parts[-1])
            except ValueError:
                continue

            xs.append(x)
            ys.append(y)

    return np.array(xs), np.array(ys)


def save_single_plot(x, y, out_png: Path, title: str, ylabel: str):
    """
    Saves one KPI plot as a standalone PNG.
    """
    plt.figure()
    plt.plot(x, y)
    plt.grid(True)
    plt.xlabel("Iteration / pseudo-time")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()


def make_dashboard(case_name: str, out_png: Path, series: dict):
    """
    Create a 2×3 dashboard image with core KPIs.

    Layout:
    [Tin_air]   [Tout_air]   [DeltaT_air]
    [DeltaP]    [mdot_out]   [Tout_porous]
    """
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    fig.suptitle(f"KPI Dashboard — {case_name}", fontsize=14)

    def plot_if_exists(ax, key, title, ylabel):
        if key not in series:
            ax.set_title(f"{title}\n(MISSING)")
            ax.grid(True)
            return
        x, y = series[key]
        ax.plot(x, y)
        ax.set_title(title)
        ax.set_xlabel("Iteration / pseudo-time")
        ax.set_ylabel(ylabel)
        ax.grid(True)

    plot_if_exists(axes[0, 0], "Tin_air", "Tin_air", "T (K)")
    plot_if_exists(axes[0, 1], "Tout_air", "Tout_air", "T (K)")
    plot_if_exists(axes[0, 2], "DeltaT_air", "DeltaT_air = Tout - Tin", "ΔT (K)")

    plot_if_exists(axes[1, 0], "DeltaP_air", "DeltaP_air = Pin - Pout", "Δp (Pa)")
    plot_if_exists(axes[1, 1], "mdot_air_out", "mdot_air_out (sum(phi))", "phi-sum (solver units)")
    plot_if_exists(axes[1, 2], "Tout_porous", "Tout_porous", "T (K)")

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def main():
    root = Path(".")
    cases = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("run_U")])

    if not cases:
        print("❌ No case folders found like run_U*_Tp* in current directory.")
        print("Run this script from the main folder containing run_U*_Tp* folders.")
        return

    for case in cases:
        post = case / "postProcessing"
        if not post.exists():
            print(f"[SKIP] {case.name}: no postProcessing/ folder found.")
            continue

        out_dir = case / "results"
        out_dir.mkdir(exist_ok=True)

        U, Tp = parse_case_inputs(case.name)
        print(f"\n=== Processing {case.name} (U={U}, Tp={Tp}) ===")

        series = {}

        # --- Load base KPIs ---
        for kpi in KPI_LIST:
            region = KPI_REGION.get(kpi)

            # Try both layouts:
            # 1) postProcessing/<kpi>
            # 2) postProcessing/<region>/<kpi>
            candidates = [post / kpi]
            if region:
                candidates.append(post / region / kpi)

            dat_file = None
            for func_dir in candidates:
                dat_file = find_latest_dat_file(func_dir)
                if dat_file is not None:
                    break

            if dat_file is None:
                print(f"  [MISS] {kpi}: no .dat file found")
                continue

            x, y = read_foam_dat(dat_file)
            if len(x) < 2:
                print(f"  [MISS] {kpi}: not enough datapoints")
                continue

            series[kpi] = (x, y)

            save_single_plot(
                x, y,
                out_dir / f"{kpi}.png",
                title=f"{kpi} vs Iteration ({case.name})",
                ylabel=kpi
            )
            print(f"  [OK] {kpi}.png")

        # --- Derived KPI: DeltaT_air = Tout_air - Tin_air ---
        if "Tin_air" in series and "Tout_air" in series:
            x_out, y_out = series["Tout_air"]
            x_in, y_in = series["Tin_air"]

            y_in_interp = np.interp(x_out, x_in, y_in)
            dT = y_out - y_in_interp
            series["DeltaT_air"] = (x_out, dT)

            save_single_plot(
                x_out, dT,
                out_dir / "DeltaT_air.png",
                title=f"DeltaT_air vs Iteration ({case.name})",
                ylabel="DeltaT_air (K)"
            )
            print("  [OK] DeltaT_air.png")
        else:
            print("  [MISS] DeltaT_air: Tin_air or Tout_air missing")

        # --- Derived KPI: DeltaP_air = Pin_air - Pout_air ---
        if "Pin_air" in series and "Pout_air" in series:
            x_pin, y_pin = series["Pin_air"]
            x_pout, y_pout = series["Pout_air"]

            y_pout_interp = np.interp(x_pin, x_pout, y_pout)
            dP = y_pin - y_pout_interp
            series["DeltaP_air"] = (x_pin, dP)

            save_single_plot(
                x_pin, dP,
                out_dir / "DeltaP_air.png",
                title=f"DeltaP_air vs Iteration ({case.name})",
                ylabel="DeltaP_air (Pa)"
            )
            print("  [OK] DeltaP_air.png")
        else:
            print("  [MISS] DeltaP_air: Pin_air or Pout_air missing")

        # --- Dashboard plot ---
        dashboard_path = out_dir / "KPI_dashboard.png"
        make_dashboard(case.name, dashboard_path, series)
        print("  [OK] KPI_dashboard.png")

    print("\n✅ Done. Each case now has a results/ folder with KPI plots + dashboard.")


if __name__ == "__main__":
    main()
