import json
import os
import random
from pathlib import Path

from bgpy.simulation_engine import ROVFull
from frozendict import frozendict
# from rov_collector import rov_collector_classes

from sav_pkg.enums import Interfaces


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


from sav_pkg.enums import Interfaces

default_sav_policy_interface_dict: frozendict[str, frozenset] = {
    "NoSAV": frozenset([
        Interfaces.CUSTOMER.value, 
        Interfaces.PEER.value, 
        Interfaces.PROVIDER.value,
    ]),
    "Loose uRPF": frozenset([
        Interfaces.CUSTOMER.value, 
        Interfaces.PEER.value, 
        Interfaces.PROVIDER.value,
    ]),
    "Strict uRPF": frozenset([
        Interfaces.CUSTOMER.value, 
        Interfaces.PEER.value, 
    ]),
    "Feasible-Path uRPF": frozenset([
        Interfaces.CUSTOMER.value, 
        Interfaces.PEER.value, 
    ]),
    "EFP uRPF Alg A": frozenset([
        Interfaces.CUSTOMER.value,
    ]),
    "EFP uRPF Alg A w Peers": frozenset([
        Interfaces.CUSTOMER.value,
        Interfaces.PEER.value,
    ]),
    "EFP uRPF Alg B": frozenset([
        Interfaces.CUSTOMER.value, 
    ]),
    "RFC8704": frozenset([
        Interfaces.CUSTOMER.value, 
        Interfaces.PEER.value, 
        Interfaces.PROVIDER.value,
    ]),
    "BAR SAV": frozenset([
        Interfaces.CUSTOMER.value, 
        Interfaces.PEER.value, 
    ]),
    "Procedure X": frozenset([
        Interfaces.CUSTOMER.value, 
        Interfaces.PEER.value, 
    ]),
}

def get_applied_interfaces(as_obj, scenario, sav_policy):
    
    if scenario.scenario_config.override_default_interface_dict is not None:
        interfaces = scenario.scenario_config.override_default_interface_dict[sav_policy.name]
    else:
        interfaces = default_sav_policy_interface_dict[sav_policy.name]
    
    applied_interfaces = set()
    if Interfaces.CUSTOMER.value in interfaces:
        applied_interfaces.add(as_obj.customer_asns)
    if Interfaces.PEER.value in interfaces:
        applied_interfaces.add(as_obj.peer_asns)
    if Interfaces.PROVIDER.value in interfaces:
        applied_interfaces.add(as_obj.provider_asns)

    return applied_interfaces
