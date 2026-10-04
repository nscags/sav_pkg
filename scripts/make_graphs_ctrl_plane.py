"""Batch-generate False Positive Rate graphs against control-plane adoption.

Companion to make_graphs.py, built from the same data.csv files with the two
adoption axes swapped: the x-axis is the ASPA/ASRA adoption parsed from each
scenario_label (aspa_50 -> 50%), and each line is one SAV adoption level
(percent_adopt). Each graph is written next to the make_graphs.py output for
the same combo, as false_positive_rate_by_aspa.png or ..._by_asra.png.

Result dirs whose scenario_labels aren't all aspa_<n> or all asra_<n> (older
one-off runs) are skipped.

Usage:
    python3 make_graphs_ctrl_plane.py --root <results dir> --out <graphs dir>
"""
import argparse
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless -- no display on the HPC
import matplotlib.pyplot as plt

# SAV adoption levels to draw a line for
specific_percent_adopt = [0, 0.1, 0.2, 0.5, 0.8, 0.99]

# Visual + label config for each SAV adoption line, same palette the
# aspa_<n>/asra_<n> lines use in make_graphs.py
sav_line_config = {
    0.0: {"label": "0% SAV adoption", "color": "tab:red", "linestyle": "-", "marker": "D"},
    0.1: {"label": "10% SAV adoption", "color": "tab:blue", "linestyle": "--", "marker": "o"},
    0.2: {"label": "20% SAV adoption", "color": "tab:green", "linestyle": "-.", "marker": "p"},
    0.5: {"label": "50% SAV adoption", "color": "tab:pink", "linestyle": ":", "marker": "s"},
    0.8: {"label": "80% SAV adoption", "color": "tab:purple", "linestyle": "-.", "marker": "*"},
    0.99: {"label": "99% SAV adoption", "color": "tab:orange", "linestyle": "--", "marker": "d"},
}

# scenario_label -> (control-plane policy, adoption %), e.g. asra_50 -> (asra, 50)
LABEL_PATTERN = r"^(aspa|asra)_(\d+)$"


def compute_fpr_by_ctrl_plane(df):
    """Returns (aspa|asra, values, errors) pivoted to ctrl-plane x SAV, or
    None if this data.csv isn't a single aspa/asra sweep"""
    subset = df[df["outcome"] == "FALSE_POSITIVE_RATE"].copy()
    if subset.empty:
        return None

    parsed = subset["scenario_label"].str.extract(LABEL_PATTERN)
    if parsed.isna().any().any() or parsed[0].nunique() != 1:
        return None
    kind = parsed[0].iloc[0]
    subset["ctrl_plane_adopt"] = parsed[1].astype(int) / 100

    values = subset.pivot_table(
        index="ctrl_plane_adopt", columns="percent_adopt", values="value", aggfunc="sum"
    )
    errors = subset.pivot_table(
        index="ctrl_plane_adopt", columns="percent_adopt", values="yerr", aggfunc="sum"
    )
    keep = [c for c in values.columns if c in specific_percent_adopt]
    return kind, values[keep], errors[keep]


def plot_fpr_by_ctrl_plane(kind, values, errors, out_path: Path, dpi=150) -> bool:
    if values.empty:
        return False

    plt.figure(figsize=(10, 6), dpi=dpi)

    for sav_adopt in values.columns:
        conf = sav_line_config.get(sav_adopt, {})
        label = conf.get("label", f"{round(sav_adopt * 100)}% SAV adoption")
        y = values[sav_adopt]
        yerr_raw = errors[sav_adopt] if sav_adopt in errors.columns else None

        # Bound lower error bars to not go below 0
        if yerr_raw is not None:
            lower = [min(val, err) if val - err < 0 else err for val, err in zip(y, yerr_raw)]
            yerr = [lower, yerr_raw]
        else:
            yerr = None

        plt.errorbar(
            values.index, y, yerr=yerr, label=label,
            linestyle=conf.get("linestyle", "-"),
            color=conf.get("color", "black"),
            marker=conf.get("marker", "o"),
            capsize=4, markersize=12, linewidth=3.8, zorder=2,
        )

    # Axis formatting, same as make_graphs.py
    fontsize = 24
    plt.xlabel(f"Percent {kind.upper()} Adoption (%)", fontdict={"fontsize": fontsize})
    plt.ylabel("False Positive Rate (%)", fontdict={"fontsize": fontsize})
    plt.xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], ["0", "20", "40", "60", "80", "100"])
    plt.tick_params(axis="both", labelsize=18)
    plt.xlim(0, 1.0)
    plt.grid(axis="y")
    plt.tight_layout()

    legend = plt.legend(
        loc="upper left",
        frameon=True,
        handlelength=4,
        handletextpad=1.2,
        labelspacing=0.4,
        borderpad=0.4,
        markerscale=1.2,
        fontsize=16,
    )
    legend.set_zorder(3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    return True


def make_graph_for_csv(csv_path: Path, graphs_root: Path, results_root: Path) -> None:
    rel_dir = csv_path.parent.relative_to(results_root)

    try:
        data = pd.read_csv(csv_path)
    except Exception as e:
        print(f"  SKIP ({e}): {rel_dir}")
        return

    result = compute_fpr_by_ctrl_plane(data)
    if result is None:
        print(f"  skip (not a single aspa_<n>/asra_<n> sweep): {rel_dir}")
        return

    kind, values, errors = result
    out_path = graphs_root / rel_dir / f"false_positive_rate_by_{kind}.png"
    if plot_fpr_by_ctrl_plane(kind, values, errors, out_path):
        print(f"  wrote: {rel_dir}/{out_path.name}")
    else:
        print(f"  nothing to plot: {rel_dir}")


# Subdirectories of --root that are searched for data.csv
SEARCH_DIRS = (
    "bear_sav_pi/alg_a",
    "bear_sav_pi/alg_b",
    "bear_sav/alg_a",
    "bear_sav/alg_b",
)


def main():
    parser = argparse.ArgumentParser(
        description="False Positive Rate vs ASPA/ASRA adoption, one line per SAV "
        "adoption level, for every data.csv found under --root."
    )
    parser.add_argument(
        "--root", type=Path,
        # sav/sav_pkg/scripts/make_graphs_ctrl_plane.py -> sav/results, wherever sav/ lives
        default=Path(__file__).resolve().parents[2] / "results",
        help="Directory to search for data.csv (default: sav/results)",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Where to write graphs, mirroring --root's structure "
        "(default: a 'graphs' dir alongside --root, i.e. sav/graphs)",
    )
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    graphs_root = (args.out.expanduser() if args.out else root.parent / "graphs").resolve()

    # Only the current matrix results; everything else under bear_sav/ and
    # bear_sav_pi/ is legacy
    csv_files = sorted(
        p
        for search_dir in SEARCH_DIRS
        if (root / search_dir).is_dir()
        for p in (root / search_dir).rglob("data.csv")
    )
    print(f"Found {len(csv_files)} data.csv file(s) under {root} in {', '.join(SEARCH_DIRS)}")
    print(f"Writing graphs to {graphs_root}\n")

    for csv_path in csv_files:
        make_graph_for_csv(csv_path, graphs_root, root)


if __name__ == "__main__":
    main()
