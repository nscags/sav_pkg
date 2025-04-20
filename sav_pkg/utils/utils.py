import json
import os
import random
from pathlib import Path
from typing import TYPE_CHECKING, Optional, List
from frozendict import frozendict

from bgpy.simulation_engine import ROVFull
from bgpy.enums import Plane, ASGroups
# from rov_collector import rov_collector_classes

from sav_pkg.simulation_framework.metric_tracker.metric_key import MetricKey
from sav_pkg.enums import Interfaces
from sav_pkg.enums import Outcomes

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS


# First attempt, didn't work with pickle (idk why?)
# def get_metric_keys() -> Iterable[MetricKey]:
#     for plane in [Plane.DATA]:
#         for as_group in [ASGroups.ALL_WOUT_IXPS]:
#             for outcome in [Outcomes.FALSE_NEGATIVE, Outcomes.TRUE_POSITIVE]:
#                 yield MetricKey(plane=plane, outcome=outcome, as_group=as_group)

def get_metric_keys(
    planes: Optional[List[Plane]] = None,
    as_groups: Optional[List[ASGroups]] = None
) -> List[MetricKey]:
    planes = planes or [Plane.DATA]
    as_groups = as_groups or [ASGroups.ALL_WOUT_IXPS]

    metric_keys = [
        MetricKey(plane=plane, outcome=outcome, as_group=as_group)
        for plane in planes
        for as_group in as_groups
        for outcome in [
            Outcomes.FALSE_NEGATIVE,
            Outcomes.FALSE_POSITIVE,
            Outcomes.TRUE_NEGATIVE,
            Outcomes.TRUE_POSITIVE,
            Outcomes.FILTERED_ON_PATH,
            Outcomes.DISCONNECTED,
            Outcomes.FORWARD,
            Outcomes.ATTACKER_SUCCESS,
            Outcomes.VICTIM_SUCCESS,
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
    "No SAV": frozenset(),
    "Loose uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Strict uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "Feasible-Path uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "EFP uRPF Alg A": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "EFP uRPF Alg A wo Peers": frozenset([Interfaces.CUSTOMER.value]),
    "EFP uRPF Alg B": frozenset([Interfaces.CUSTOMER.value]),
    "RFC8704": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Refined Alg A": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
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


def get_export_to_some_dict(
    e2s_policy,
    json_path: Path = Path.home() / "e2s_asn_provider_weights.json",
):
    if not json_path.exists():
        print("oh no")
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(json_path, "r") as f:
        export2some_raw = json.load(f)

    export2some_asn_cls_dict = frozendict({
        int(asn): e2s_policy for asn in export2some_raw.keys()
    })

    return export2some_asn_cls_dict


def get_e2s_asn_provider_weight_dict(
    json_path: Path = Path.home() / "e2s_asn_provider_weights.json",
) -> frozendict:
    """
    Retrieves dictionary of ASN, provider ASNs, and their corresponding weights

    Weights are percentage of unique IPv4 prefixes received on that interface divided 
    by the total number of unique prefixes exported by the AS.
    """
    
    if not json_path.exists():
        print("oh no")
        raise FileNotFoundError(f"File: 'e2s_asn_provider_weights.json' not found in {json_path}.")

    with open(json_path, "r") as f:
        raw_data = json.load(f)

    formatted_data = dict()
    for asn, inner_dict in raw_data.items():
        formatted_data[int(asn)] = {int(k): float(v) for k, v in inner_dict.items()}
    return frozendict(formatted_data)


def get_e2s_asn_provider_prepending_dict(
    json_path: Path = Path.home() / "mh_2p_export_to_some_prepending.json",
) -> frozendict:
    """
    Retrieves dictionary of ASN, provider ASNs, and if there is path preprending on that interface
    """
    
    if not json_path.exists():
        print("oh no")
        raise FileNotFoundError(f"File: 'asn_e2s_provider_weights.json' not found in {json_path}.")

    with open(json_path, "r") as f:
        raw_data = json.load(f)

    formatted_data = dict()
    for asn, inner_dict in raw_data.items():
        formatted_data[int(asn)] = {int(k): [bool(x) for x in v] for k, v in inner_dict.items()}
    return frozendict(formatted_data)


def get_e2s_superprefix_weight_dict(
    json_path: Path = Path.home() / "mh_2p_superprefix_weights.json",
) -> frozendict:
    """
    Retrieves dictionary of ASN, provider ASNs, and their corresponding weights

    Weights are percentage of unique IPv4 prefixes received on that interface which
    are a superprefix of another IPv4 prefix announced by that AS
    """
    
    if not json_path.exists():
        print("oh no")
        raise FileNotFoundError(f"File: 'mh_2p_superprefix_weights.json' not found in {json_path}.")

    with open(json_path, "r") as f:
        raw_data = json.load(f)

    formatted_data = dict()
    for asn, inner_dict in raw_data.items():
        formatted_data[int(asn)] = {int(k): float(v) for k, v in inner_dict.items()}
    return frozendict(formatted_data)