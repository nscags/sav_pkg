import json
import os
import random
from pathlib import Path
from typing import TYPE_CHECKING

from bgpy.enums import ASGroups, Plane
from bgpy.simulation_engine import ROVFull
from frozendict import frozendict

from sav_pkg.enums import Interfaces, Outcomes
from sav_pkg.simulation_framework.metric_tracker.metric_key import MetricKey

# from rov_collector import rov_collector_classes

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS

# First attempt, didn't work with pickle (idk why?)
# def get_metric_keys() -> Iterable[MetricKey]:
#     for plane in [Plane.DATA]:
#         for as_group in [ASGroups.ALL_WOUT_IXPS]:
#             for outcome in [Outcomes.FALSE_NEGATIVE, Outcomes.TRUE_POSITIVE]:
#                 yield MetricKey(plane=plane, outcome=outcome, as_group=as_group)

def get_metric_keys(
    planes: list[Plane] | None = None,
    as_groups: list[ASGroups] | None = None
) -> list['MetricKey']:
    planes = planes or [Plane.DATA]
    as_groups = as_groups or [ASGroups.ALL_WOUT_IXPS]

    metric_keys = [
        MetricKey(plane=plane, outcome=outcome, as_group=as_group)
        for plane in planes
        for as_group in as_groups
        for outcome in [
            Outcomes.FALSE_POSITIVE_RATE,
            Outcomes.DETECTION_RATE,
            # Outcomes.DISCONNECTED,
            # Outcomes.TRUE_NEGATIVE,
            # Outcomes.FALSE_NEGATIVE,
            # Outcomes.TRUE_POSITIVE,
            # Outcomes.FALSE_POSITIVE,
            # Outcomes.A_FILTERED_ON_PATH,
            # Outcomes.V_FILTERED_ON_PATH,
        ]
    ]
    return metric_keys


# NOTE: for BAR SAV, ROV adoption doesn't actually matter
#       Only ROA adoption (for Victim/Legit Sender) has an impact
#       Leaving here for now, may be useful for SAV attacks paper
#
#       Addtionally, both attacker/victim/reflectors all announce
#       their own legitimate prefixes, so ROV wouldn't be useful in
#       this context, again will probably be useful in SAV attacks paper
def get_real_world_rov_asn_cls_dict(
    json_path: Path = Path.home() / "data/rov_info.json",
    requests_cache_db_path: Path | None = None,
) -> frozendict[int, type[ROVFull]]:
    if not json_path.exists():
        print("oh no")
        # for CollectorCls in rov_collector_classes:
        #     CollectorCls(
        #         json_path=json_path,
        #         requests_cache_db_path=requests_cache_db_path,
        #     ).run()

    python_hash_seed = os.environ.get("PYTHONHASHSEED")
    if python_hash_seed:
        random.seed(int(python_hash_seed))

    with json_path.open() as f:
        data = json.load(f)
        hardcoded_dict = dict()
        for asn, info_list in data.items():
            max_percent: float = 0
            # Calculate max_percent for each ASN
            for info in info_list:
                max_percent = max(max_percent, float(info["percent"]))

            # Use max_percent as the probability for inclusion
            if random.random() * 100 < max_percent:
                hardcoded_dict[int(asn)] = ROVFull
    return frozendict(hardcoded_dict)


DEFAULT_SAV_POLICY_INTERFACE_DICT: frozendict[str, frozenset] = frozendict({
    "No SAV": frozenset(),
    "Loose uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Strict uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "Feasible-Path uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "EFP-A": frozenset([Interfaces.CUSTOMER.value]),
    "EFP-A w/ Peers": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "EFP-B": frozenset([Interfaces.CUSTOMER.value]),
    "RFC8704": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "BAR-SAV": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "BAR-SAV-PI": frozenset([Interfaces.PROVIDER.value]),
    "BAR-SAV w/ BSPI": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Procedure X": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
})

def get_applied_interfaces(
    as_obj: "AS",
    scenario,
    sav_policy
):
    """Gets the applied interfaces based on the given SAV policy."""

    interfaces = (
        scenario.scenario_config.override_default_interface_dict.get(sav_policy.name)
        if scenario.scenario_config.override_default_interface_dict
        else DEFAULT_SAV_POLICY_INTERFACE_DICT[sav_policy.name]
    )

    interface_map = {
        Interfaces.CUSTOMER.value: as_obj.customer_asns,
        Interfaces.PEER.value: as_obj.peer_asns,
        Interfaces.PROVIDER.value: as_obj.provider_asns,
    }

    applied_interfaces = {interface_map[i] for i in interfaces if i in interface_map}

    return applied_interfaces


def get_traffic_engineering_behavior_asn_cls_dict(
    export_policy,
    traffic_engineering_subcategory = None,  # default None = return all ASNs
    path_prepending: bool = True,
    json_path: Path = Path.home() / "data/traffic_engineering_behaviors.json",
):
    """
    Return ASNs filtered by traffic engineering behavior and optional path prepending.
    """
    if not json_path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(json_path) as f:
        data = json.load(f)

    filtered_asns = {}

    for asn, providers in data.items():
        # If returning all ASNs
        if traffic_engineering_subcategory in (None, "all"):
            filtered_asns[int(asn)] = export_policy
            continue

        # Only consider ASNs that have at least one provider in the requested category
        providers_in_category = [
            p_data for p_data in providers.values()
            if p_data["category"] == traffic_engineering_subcategory
        ]
        if not providers_in_category:
            continue

        if path_prepending:
            # Include all ASNs in this category
            filtered_asns[int(asn)] = export_policy
        else:
            # Include only if none of the providers prepend
            if all(not any(p_data.get("prepending", [])) for p_data in providers_in_category):
                filtered_asns[int(asn)] = export_policy

    return frozendict(filtered_asns)


def get_traffic_engineering_behaviors_dict(
    json_path: Path = Path.home() / "data/traffic_engineering_behaviors.json",
) -> frozendict:
    """"""

    if not json_path.exists():
        print("oh no")
        raise FileNotFoundError(f"File: 'traffic_engineering_behaviors.json' not found in {json_path}.")

    with open(json_path) as f:
        data = json.load(f)

    formatted_data = {int(asn): providers for asn, providers in data.items()}

    return frozendict(formatted_data)