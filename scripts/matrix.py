"""Single source of truth for the bear_sav_pi/bear_sav simulation sweep.

Each axis below is a dimension of the experiment matrix. Adding a new value
to an axis (e.g. a new export-behavior variant) automatically doubles/extends
MATRIX without touching run_matrix.py or run_matrix.sh.
"""
import itertools
from datetime import datetime
from pathlib import Path

# NOTE: bgpy/sav_pkg are deliberately NOT imported at module scope.
# Listing the matrix and printing an --array index string is pure metadata
# and must keep working even when the simulation stack can't import (a
# broken numpy on a login node, a half-built venv, etc). Otherwise
#   sbatch --array=$(python3 matrix.py ... --array) run_matrix.sh
# silently expands to `--array=` and submits the wrong thing.
# The heavy imports live inside build_scenario_configs(), which only
# run_matrix.py (on a compute node) ever calls.

POLICY = ("bear_sav_pi", "bear_sav")
# *_wp = "with paths": the SAV policies also use the precomputed background
# routes in ROUTES_DIR (every non-IXP AS announcing)
SCENARIO = ("base", "min_fp", "asl", "base_wp", "asl_wp")
ADOPTS = ("aspa", "asra")
ALGS = ("a", "b")
SPOOFING_AS = (True, False)
PERCENTS = (0.0, 0.1, 0.2, 0.5, 0.8, 0.99)

NUM_REFLECTORS = 5
NUM_TRIALS = 100

EXPORT_POLICY = "e2a"

# Every simulation runs on this one CAIDA snapshot (serial-2 20260901, cached
# by bgpy as CAIDAASGraphCollector_2026.09.24.txt in CAIDA_DIR), the graph the
# background routes were precomputed on. A fixed cache dir also avoids bgpy's
# per-day cache, which array tasks race on.
CAIDA_DL_TIME = datetime(2026, 9, 24)
CAIDA_DIR = "~/sav/caida"
ROUTES_DIR = "~/sav/routes/caida_20260901"


def num_reflectors(scenario: str) -> int:
    # ASL places the attackers relative to a single reflector
    return 1 if scenario.startswith("asl") else NUM_REFLECTORS


def build_scenario_configs(
    policy: str,
    scenario: str,
    adopt: str,
    alg: str,
    attacker_broadcast: bool,
) -> tuple:
    # Imported here, not at module scope, so that listing the matrix never
    # depends on the simulation stack being importable (see note at top).
    from bgpy.simulation_engine import BGPFull, ASPAFull, ASRAFull
    from bgpy.shared.enums import ASGroups

    from sav_pkg.simulation_framework.scenarios import (
        SAVScenarioConfig,
        SAVScenario,
        SAVScenarioMinFP,
        SAVScenarioASL,
    )
    from sav_pkg.simulation_engine.policies.sav import (
        BeAR_SAV_PI_A,
        BeAR_SAV_PI_B,
        BeAR_SAV_A,
        BeAR_SAV_B,
    )

    _POLICY_CLS = {
        ("bear_sav_pi", "a"): BeAR_SAV_PI_A,
        ("bear_sav_pi", "b"): BeAR_SAV_PI_B,
        ("bear_sav", "a"): BeAR_SAV_A,
        ("bear_sav", "b"): BeAR_SAV_B,
    }
    _ADOPT_CLS = {"aspa": ASPAFull, "asra": ASRAFull}
    _SCENARIO_CLS = {
        "base": SAVScenario,
        "min_fp": SAVScenarioMinFP,
        "asl": SAVScenarioASL,
        "base_wp": SAVScenario,
        "asl_wp": SAVScenarioASL,
    }

    ScenarioCls = _SCENARIO_CLS[scenario]
    routes_dir = ROUTES_DIR if scenario.endswith("_wp") else None
    BaseSAVPolicyCls = _POLICY_CLS[(policy, alg)]
    AdoptPolicyCls = _ADOPT_CLS[adopt]

    configs = []
    for percent in PERCENTS:
        configs.append(
            SAVScenarioConfig(
                ScenarioCls=ScenarioCls,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BaseSAVPolicyCls,
                AdoptPolicyCls=AdoptPolicyCls,
                ctrl_plane_percent_adoption=percent,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=num_reflectors(scenario),
                reflector_default_adopters=True,
                attacker_broadcast=attacker_broadcast,
                scenario_label=f"{adopt}_{round(percent * 100)}",
                routes_dir=routes_dir,
            )
        )
    return tuple(configs)


def as_graph_constructor_kwargs():
    """bgpy's default Simulation kwargs, but pinned to CAIDA_DL_TIME in CAIDA_DIR"""

    from frozendict import frozendict

    return frozendict(
        {
            "as_graph_collector_kwargs": frozendict(
                {
                    "dl_time": CAIDA_DL_TIME,
                    "cache_dir": Path(CAIDA_DIR).expanduser(),
                }
            ),
            "as_graph_kwargs": frozendict(
                {
                    "store_customer_cone_size": True,
                    "store_customer_cone_asns": False,
                    "store_provider_cone_size": False,
                    "store_provider_cone_asns": False,
                }
            ),
            "tsv_path": None,
        }
    )


def output_dir(
    policy: str,
    scenario: str,
    adopt: str,
    alg: str,
    attacker_broadcast: bool,
    num_trials: int = NUM_TRIALS,
) -> Path:
    # policy / algorithm / export_policy / scenario / attacker_model / adopt /
    # reflectors_trials
    spoofing_dir = "spoofing_as" if attacker_broadcast else "spoofing_host"
    return Path(
        f"~/sav/results/{policy}/alg_{alg}/{EXPORT_POLICY}/"
        f"{scenario}/{spoofing_dir}/{adopt}/"
        f"{num_reflectors(scenario)}r_{num_trials}t"
    ).expanduser()


def claim_output_dir(base: Path) -> Path:
    """
    Creates and returns base, or base_1, base_2, ... if it already exists

    mkdir with exist_ok=False is atomic, so two runs of the same combo
    started at the same time still get different directories.
    """
    candidate, n = base, 0
    while True:
        try:
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        except FileExistsError:
            n += 1
            candidate = base.with_name(f"{base.name}_{n}")


def _build_matrix() -> list[dict]:
    matrix = []
    for policy, scenario, adopt, alg, attacker_broadcast in itertools.product(
        POLICY, SCENARIO, ADOPTS, ALGS, SPOOFING_AS
    ):
        matrix.append(
            {
                "policy": policy,
                "scenario": scenario,
                "adopt": adopt,
                "alg": alg,
                "attacker_broadcast": attacker_broadcast,
            }
        )
    return matrix


MATRIX: list[dict] = _build_matrix()


def matching_indices(
    policy: set[str] | None = None,
    scenario: set[str] | None = None,
    adopt: set[str] | None = None,
    alg: set[str] | None = None,
    attacker_broadcast: set[bool] | None = None,
) -> list[int]:
    """Indices into MATRIX whose combo matches every given filter.

    A filter of None means "no restriction on this axis". Non-None filters
    are sets of allowed values for that axis.
    """
    indices = []
    for i, combo in enumerate(MATRIX):
        if policy is not None and combo["policy"] not in policy:
            continue
        if scenario is not None and combo["scenario"] not in scenario:
            continue
        if adopt is not None and combo["adopt"] not in adopt:
            continue
        if alg is not None and combo["alg"] not in alg:
            continue
        if (
            attacker_broadcast is not None
            and combo["attacker_broadcast"] not in attacker_broadcast
        ):
            continue
        indices.append(i)
    return indices


if __name__ == "__main__":
    import argparse

    def _split(val: str | None) -> set[str] | None:
        return set(val.split(",")) if val else None

    def _split_bool(val: str | None) -> set[bool] | None:
        if not val:
            return None
        return {v.strip().lower() in ("true", "1") for v in val.split(",")}

    parser = argparse.ArgumentParser(
        description=(
            "List matrix combos, optionally filtered by axis. "
            "Pass --array to print only a comma-separated index string "
            "suitable for `sbatch --array=`."
        )
    )
    parser.add_argument("--policy", help=f"comma-separated subset of {POLICY}")
    parser.add_argument("--scenario", help=f"comma-separated subset of {SCENARIO}")
    parser.add_argument("--adopt", help=f"comma-separated subset of {ADOPTS}")
    parser.add_argument("--alg", help=f"comma-separated subset of {ALGS}")
    parser.add_argument(
        "--attacker-broadcast", help="comma-separated subset of true,false"
    )
    parser.add_argument(
        "--array",
        action="store_true",
        help="print just the comma-separated indices, for sbatch --array=",
    )
    args = parser.parse_args()

    matched = matching_indices(
        policy=_split(args.policy),
        scenario=_split(args.scenario),
        adopt=_split(args.adopt),
        alg=_split(args.alg),
        attacker_broadcast=_split_bool(args.attacker_broadcast),
    )

    if args.array:
        print(",".join(str(i) for i in matched))
    else:
        for i in matched:
            print(i, MATRIX[i], output_dir(**MATRIX[i]))
