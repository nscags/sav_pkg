"""Single source of truth for the bspi_pp/bspp simulation sweep.

Each axis below is a dimension of the experiment matrix. Adding a new value
to an axis (e.g. a new export-behavior variant) automatically doubles/extends
MATRIX without touching run_matrix.py or run_matrix.sh.
"""
import itertools
from pathlib import Path

from bgpy.simulation_engine import BGPFull, ASPAFull, ASRAFull
from bgpy.shared.enums import ASGroups

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
    SAVScenarioMinFP,
)
from sav_pkg.simulation_engine.policies.sav import (
    BAR_SAV_PI_PP_Alg_A,
    BAR_SAV_PI_PP_Alg_B,
    BAR_SAV_PP_wBSPI_PP_Alg_A,
    BAR_SAV_PP_wBSPI_PP_Alg_B,
)


POLICY = ("bspi_pp", "bspp")
SCENARIO = ("base", "min_fp")
ADOPTS = ("aspa", "asra")
ALGS = ("a", "b")
SPOOFING_AS = (True, False)
PERCENTS = (0.0, 0.1, 0.2, 0.5, 0.8, 0.99)

NUM_REFLECTORS = 5
NUM_TRIALS = 100

_POLICY_CLS = {
    ("bspi_pp", "a"): BAR_SAV_PI_PP_Alg_A,
    ("bspi_pp", "b"): BAR_SAV_PI_PP_Alg_B,
    ("bspp", "a"): BAR_SAV_PP_wBSPI_PP_Alg_A,
    ("bspp", "b"): BAR_SAV_PP_wBSPI_PP_Alg_B,
}

_ADOPT_CLS = {
    "aspa": ASPAFull,
    "asra": ASRAFull,
}

_SCENARIO_CLS = {
    "base": SAVScenario,
    "min_fp": SAVScenarioMinFP,
}

EXPORT_POLICY = "e2a"


def build_scenario_configs(
    policy: str,
    scenario: str,
    adopt: str,
    alg: str,
    attacker_broadcast: bool,
) -> tuple[SAVScenarioConfig, ...]:
    ScenarioCls = _SCENARIO_CLS[scenario]
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
                num_reflectors=NUM_REFLECTORS,
                reflector_default_adopters=True,
                attacker_broadcast=attacker_broadcast,
                scenario_label=f"{adopt}_{round(percent * 100)}",
            )
        )
    return tuple(configs)


def output_dir(
    policy: str,
    scenario: str,
    adopt: str,
    alg: str,
    attacker_broadcast: bool,
) -> Path:
    # policy / algorithm / export_policy / scenario / attacker_model / adopt
    spoofing_dir = "spoofing_as" if attacker_broadcast else "spoofing_host"
    return Path(
        f"~/sav/results/{policy}/alg_{alg}/{EXPORT_POLICY}/"
        f"{scenario}/{spoofing_dir}/{adopt}"
    ).expanduser()


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
