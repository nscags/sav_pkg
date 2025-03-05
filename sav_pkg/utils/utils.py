import json
import os
import random
from pathlib import Path
from typing import TYPE_CHECKING, Iterable
from frozendict import frozendict

from bgpy.simulation_engine import ROVFull
from bgpy.enums import Plane, ASGroups
# from rov_collector import rov_collector_classes

from sav_pkg.simulation_framework.metric_tracker.metric_key import MetricKey
from sav_pkg.enums import Interfaces
from sav_pkg.enums import Outcomes

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario
    from sav_pkg.policies.sav.base_sav_policy import BaseSAVPolicy


# First attempt, didn't work with pickle (idk why?)
# def get_metric_keys() -> Iterable[MetricKey]:
#     for plane in [Plane.DATA]:
#         for as_group in [ASGroups.ALL_WOUT_IXPS]:
#             for outcome in [Outcomes.FALSE_NEGATIVE, Outcomes.TRUE_POSITIVE]:
#                 yield MetricKey(plane=plane, outcome=outcome, as_group=as_group)

def get_metric_keys() -> Iterable[MetricKey]:
    metric_keys = [
        MetricKey(plane=plane, outcome=outcome, as_group=as_group)
        for plane in [Plane.DATA]
        for as_group in [ASGroups.ALL_WOUT_IXPS]
        for outcome in [
            Outcomes.FALSE_NEGATIVE,
            Outcomes.FALSE_POSITIVE,
            Outcomes.TRUE_NEGATIVE,
            Outcomes.TRUE_POSITIVE,
            Outcomes.FILTERED_ON_PATH,
            Outcomes.DISCONNECTED,
            Outcomes.FORWARD,
        ]
    ]
    return metric_keys


# NOTE: for BAR SAV ROV adoption doesn't actually matter
#       Only ROA adoption (for Victim/Legit Sender) has an impact 
#       Leaving here for now, may be useful for SAV attacks paper
def get_real_world_rov_asn_cls_dict(
    json_path: Path = Path.home() / "rov_info.json",
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
    "NoSAV": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Loose uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Strict uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "Feasible-Path uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "EFP uRPF Alg A": frozenset([Interfaces.CUSTOMER.value]),
    "EFP uRPF Alg A w Peers": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "EFP uRPF Alg B": frozenset([Interfaces.CUSTOMER.value]),
    "RFC8704": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "BAR SAV": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "Procedure X": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
})

def get_applied_interfaces(
        as_obj: AS, 
        scenario: SAVScenario, 
        sav_policy: "BaseSAVPolicy"
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