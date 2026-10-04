"""Batch-generate Detection Rate / False Positive Rate graphs.

This is the on-disk, non-interactive version of the plotting cell you run
by hand in Colab: same policy_config / excluded_labels / merge_policies /
legend_order knobs below, edited the same way you already edit them --
just looped over every data.csv found under --root instead of one file
at a time, and saved to PNG instead of plt.show().

Usage:
    python3 make_graphs.py                       # ~/sav/results -> ~/sav/results/graphs
    python3 make_graphs.py --root ~/sav/results/bspi_pp --out ~/sav/graphs_bspi_pp

Each data.csv at <root>/.../some/combo/data.csv produces two files at
<out>/.../some/combo/detection_rate.png and .../false_positive_rate.png,
mirroring the results tree so nothing collides and it's obvious which
combo a graph belongs to.
"""
import argparse
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless -- no display on the HPC
import matplotlib.pyplot as plt

# ============================================================
# Settings -- copied straight from the Colab plotting script.
# Edit these the same way you'd edit them there; they're applied
# to every data.csv found under --root. Add per-scenario_label
# exceptions here (new excluded_labels / merge_policies entries,
# or a new policy_config key) rather than special-casing files.
# ============================================================
excluded_labels = {
    # "strict",
    # "feasible",
    # "feasible_otc",
    # "feasible_all",
    # "efp_a",
    # "efp_a_w_peers",
    # "efp_b",
    # "bar_sav",
    # "bar_sav_roa",
    # "bar_sav_aspa",
    # "bar_sav_full",
    # "bar_sav_full_roa",
    # "bar_sav_full_aspa",

    # "loose",
    # "rfc8704",
    # "bar_sav_pi",
    # "bar_sav_aspa0",
    # "bar_sav_aspa10",
    # "bar_sav_aspa20",
    # "bar_sav_aspa50",
    # "bar_sav_aspa80",
    # "bar_sav_aspa99",
}

specific_percent_adopt = [0, 0.1, 0.2, 0.5, 0.8, 0.99]

# Define visual + label config for policies
policy_config = {

    # Baselines
    # "loose": {"label": "Loose uRPF", "color": "tab:brown", "linestyle": "-", "marker": "^"},

    # "strict": {"label": "Strict (Applied to customers and peers)", "color": "tab:blue", "linestyle": "-", "marker": "X"},
    "strict": {"label": "Strict uRPF", "color": "tab:blue", "linestyle": "-", "marker": "X"},
    # "strict_otc": {"label": "Strict (Applied to only to customers)", "color": "tab:orange", "linestyle": "-.", "marker": "x"},

    "feasible_all": {"label": "FP-uRPF (all interfaces)", "color": "tab:blue", "linestyle": "-", "marker": "s"},
    "feasible": {"label": "FP-uRPF", "color": "tab:red", "linestyle": "--", "marker": "^"},
    # "feasible": {"label": "FP-uRPF (customers and bilateral peers)", "color": "tab:red", "linestyle": "--", "marker": "^"},
    # "feasible_wo_providers": {"label": "FP-uRPF (customers and bilateral peers)", "color": "tab:red", "linestyle": "-.", "marker": "^"},
    # "feasible_wo_providers": {"label": "FP-uRPF", "color": "tab:red", "linestyle": "--", "marker": "^"},
    "feasible_otc": {"label": "FP-uRPF (only customers)", "color": "tab:green", "linestyle": "-.", "marker": "o"},

    # EFP Algorithms
    "efp_a_w_peers": {"label": "EFP-A w/ Bilateral Peers", "color": "tab:green", "linestyle": "-.", "marker": "D"},
    "efp_a": {"label": "EFP-A", "color": "tab:orange", "linestyle": "-", "marker": "d"},
    "efp_b": {"label": "EFP-B", "color": "tab:purple", "linestyle": "--", "marker": "s"},

    # BAR-SAV Variants
    "bar_sav": {"label": "BAR-SAV w/ Loose", "color": "navy", "linestyle": "--", "marker": "D"},
    # "bar_sav": {"label": "BAR-SAV w/ Loose \n(w/o ROA for edge server)", "color": "navy", "linestyle": "--", "marker": "D"},
    # "bar_sav": {"label": "BAR-SAV w/ Loose \n(origin w/o ASPA)", "color": "navy", "linestyle": "--", "marker": "D"},
    "bar_sav_roa": {"label": "BAR-SAV w/ Loose \n(w/ ROA for edge server)", "color": "darkred", "linestyle": "-", "marker": "*"},
    "bar_sav_aspa": {"label": "BAR-SAV w/ Loose \n(origin w/ ASPA)", "color": "darkred", "linestyle": "-", "marker": "s"},
    # "bar_sav_full_aspa_te": {"label": "BAR-SAV w/ Loose (origin w/ ASPA)", "color": "darkred", "linestyle": "-", "marker": "s"},


    # BAR-SAV w/PI Variants
    "bar_sav_full": {"label": "BAR-SAV w/ BSPI", "color": "goldenrod", "linestyle": "-", "marker": "o"},
    # "bar_sav_full": {"label": "BAR-SAV w/ BSPI \n(w/o ROA for edge server)", "color": "goldenrod", "linestyle": "-", "marker": "o"},
    # "bar_sav_full": {"label": "BAR-SAV w/ BSPI \n(origin w/o ASPA)", "color": "goldenrod", "linestyle": "-", "marker": "o"},
    # "bar_sav_full_roa": {"label": "BAR-SAV w/ BSPI \n(w/ ROA for edge server)", "color": "tab:cyan", "linestyle": ":", "marker": "d"},
    # "bar_sav_full_aspa": {"label": "BAR-SAV w/ BSPI \n(origin w/ ASPA)", "color": "tab:pink", "linestyle": ":", "marker": "p"},
    # "bar_sav_full_aspa_te": {"label": "BAR-SAV w/ BSPI (origin w/ ASPA)", "color": "tab:pink", "linestyle": ":", "marker": "p"},
    # "bar_sav_full_aspa_e2s": {"label": "BAR-SAV w/ BSPI (origin w/ ASPA)", "color": "tab:pink", "linestyle": ":", "marker": "p"},

    "asra_0": {"label": "BAR-SAV++ (0% ASRA)", "color": "tab:red", "linestyle": "-", "marker": "D"},
    "asra_10": {"label": "BAR-SAV++ (10% ASRA)", "color": "tab:blue", "linestyle": "--", "marker": "o"},
    "asra_20": {"label": "BAR-SAV++ (20% ASRA)", "color": "tab:green", "linestyle": "-.", "marker": "p"},
    "asra_50": {"label": "BAR-SAV++ (50% ASRA)", "color": "tab:pink", "linestyle": ":", "marker": "s"},
    "asra_80": {"label": "BAR-SAV++ (80% ASRA)", "color": "tab:purple", "linestyle": "-.", "marker": "*"},
    "asra_99": {"label": "BAR-SAV++ (99% ASRA)", "color": "tab:orange", "linestyle": "--", "marker": "d"},

    "aspa_0": {"label": "BAR-SAV++ (0% ASPA)", "color": "tab:red", "linestyle": "-", "marker": "D"},
    "aspa_10": {"label": "BAR-SAV++ (10% ASPA)", "color": "tab:blue", "linestyle": "--", "marker": "o"},
    "aspa_20": {"label": "BAR-SAV++ (20% ASPA)", "color": "tab:green", "linestyle": "-.", "marker": "p"},
    "aspa_50": {"label": "BAR-SAV++ (50% ASPA)", "color": "tab:pink", "linestyle": ":", "marker": "s"},
    "aspa_80": {"label": "BAR-SAV++ (80% ASPA)", "color": "tab:purple", "linestyle": "-.", "marker": "*"},
    "aspa_99": {"label": "BAR-SAV++ (99% ASPA)", "color": "tab:orange", "linestyle": "--", "marker": "d"},

    # "asra": {"label": "BAR-SAV-PI++ ASRA", "color": "tab:red", "linestyle": "-", "marker": "D"},
    # "aspa": {"label": "BAR-SAV-PI++ ASPA", "color": "tab:blue", "linestyle": "-", "marker": "o"},
    # "bgp": {"label": "BAR-SAV-PI++ BGP", "color": "tab:green", "linestyle": "-", "marker": "p"},

    "other": {"label": "Other Policies", "color": "black", "linestyle": "-", "marker": "x"},
}
merge_policies = [
    # "feasible",
    # "efp_a",
    # "efp_a_w_peers",
    # "efp_b",
    # "bar_sav",
    # "bar_sav_full",
    # "bar_sav_full_aspa"
]

# Explicit legend order (by labels given in policy_config above)
legend_order = [
    "Strict uRPF",
    "FP-uRPF",
    "FP-uRPF (all interfaces)",
    "FP-uRPF (customers and bilateral peers)",
    "FP-uRPF (only customers)",

    "EFP-A w/ Bilateral Peers",
    "EFP-A",
    "EFP-B",

    "BAR-SAV w/ Loose",
    "BAR-SAV w/ BSPI",

    "BAR-SAV w/ BSPI (origin w/o ASPA)",
    "BAR-SAV w/ Loose (origin w/o ASPA)",
    "BAR-SAV w/ BSPI (origin w/ ASPA)",
    "BAR-SAV w/ Loose (origin w/ ASPA)",

    "BAR-SAV w/ BSPI (w/o ROA for edge server)",
    "BAR-SAV w/ Loose (w/o ROA for edge server)",
    "BAR-SAV w/ BSPI (w/ ROA for edge server)",
    "BAR-SAV w/ Loose (w/ ROA for edge server)",

    "Loose",
    "Other Policies",
]


def compute_metric(df, include_outcomes):
    subset = df[df["outcome"].isin(include_outcomes)]
    values = subset.pivot_table(
        index="percent_adopt", columns="scenario_label", values="value", aggfunc="sum"
    )
    errors = (
        subset.pivot_table(
            index="percent_adopt", columns="scenario_label", values="yerr", aggfunc="sum"
        )
        if "yerr" in subset.columns
        else None
    )
    available = values.index.intersection(specific_percent_adopt)
    return values.loc[available], errors.loc[available] if errors is not None else None


def plot_metric(values, ylabel, out_path: Path, errors=None, dpi=150) -> bool:
    if values.empty:
        return False

    plt.figure(figsize=(10, 6), dpi=dpi)
    plotted = {}
    plotted_other = False

    for policy in values.columns:
        if policy in excluded_labels:
            continue

        # Redirect visually identical policies to 'other'
        is_other = policy in merge_policies
        if is_other:
            if plotted_other:
                continue  # skip plotting duplicates
            policy_key = "other"
            plotted_other = True
        else:
            policy_key = policy

        conf = policy_config.get(policy_key, {})
        label = conf.get("label", policy.replace("_", " ").title())
        color = conf.get("color", "black")
        linestyle = conf.get("linestyle", "-")
        marker = conf.get("marker", "o")
        y = values[policy]
        yerr_raw = errors[policy] if errors is not None and policy in errors.columns else None

        # Bound lower error bars to not go below 0
        if yerr_raw is not None:
            lower = [min(val, err) if val - err < 0 else err for val, err in zip(y, yerr_raw)]
            upper = yerr_raw
            yerr = [lower, upper]
        else:
            yerr = None

        z = 3 if policy in ("bar_sav_full_aspa", "bar_sav_full_roa") else 2
        line = plt.errorbar(
            values.index, y, yerr=yerr, label=label,
            linestyle=linestyle, color=color, marker=marker,
            capsize=4, markersize=12, linewidth=3.8, zorder=z
        )
        plotted[label] = line[0]

    # Axis formatting
    fontsize = 24
    plt.xlabel("Percent SAV Adoption (%)", fontdict={"fontsize": fontsize})
    plt.ylabel(f"{ylabel} (%)", fontdict={"fontsize": fontsize})
    plt.xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], ["0", "20", "40", "60", "80", "100"])
    plt.tick_params(axis="both", labelsize=18)
    plt.xlim(0, 1.0)
    plt.grid(axis="y")
    plt.tight_layout()

    # Keep only the ones that were actually plotted
    ordered_handles = [plotted[label] for label in legend_order if label in plotted]
    ordered_labels = [label for label in legend_order if label in plotted]

    # Add any extra labels that were plotted but not in legend_order
    for label, handle in plotted.items():
        if label not in ordered_labels:
            ordered_handles.append(handle)
            ordered_labels.append(label)

    legend = plt.legend(
        ordered_handles, ordered_labels,
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


def make_graphs_for_csv(csv_path: Path, graphs_root: Path, results_root: Path) -> None:
    rel_dir = csv_path.parent.relative_to(results_root)

    try:
        data = pd.read_csv(csv_path)
    except Exception as e:
        print(f"  SKIP ({e}): {rel_dir}")
        return

    out_dir = graphs_root / rel_dir

    detection_vals, detection_errs = compute_metric(data, ["DETECTION_RATE"])
    false_pos_vals, false_pos_errs = compute_metric(data, ["FALSE_POSITIVE_RATE"])

    wrote_detection = plot_metric(
        detection_vals, "Detection Rate", out_dir / "detection_rate.png", detection_errs
    )
    wrote_fp = plot_metric(
        false_pos_vals, "False Positive Rate", out_dir / "false_positive_rate.png", false_pos_errs
    )

    if wrote_detection or wrote_fp:
        print(f"  wrote: {rel_dir}")
    else:
        print(f"  nothing to plot (no DETECTION_RATE/FALSE_POSITIVE_RATE rows): {rel_dir}")


# Subdirectories of --root that are searched for data.csv
SEARCH_DIRS = (
    "bspi_pp/alg_a",
    "bspi_pp/alg_b",
    "bspp/alg_a",
    "bspp/alg_b",
)


def main():
    parser = argparse.ArgumentParser(
        description="Batch-generate Detection Rate / False Positive Rate graphs "
        "for every data.csv found under --root."
    )
    parser.add_argument(
        "--root", type=Path,
        # sav/sav_pkg/scripts/make_graphs.py -> sav/results, wherever sav/ lives
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

    # Only the current matrix results; everything else under bspp/ and
    # bspi_pp/ is legacy
    csv_files = sorted(
        p
        for search_dir in SEARCH_DIRS
        if (root / search_dir).is_dir()
        for p in (root / search_dir).rglob("data.csv")
    )
    print(f"Found {len(csv_files)} data.csv file(s) under {root} in {', '.join(SEARCH_DIRS)}")
    print(f"Writing graphs to {graphs_root}\n")

    for csv_path in csv_files:
        make_graphs_for_csv(csv_path, graphs_root, root)


if __name__ == "__main__":
    main()
