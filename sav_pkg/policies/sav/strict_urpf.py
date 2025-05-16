import ipaddress
from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class StrictuRPF(BaseSAVPolicy):
    name: str = "Strict uRPF"

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Strict uRPF.
        """
        src_prefix = ipaddress.ip_network(source_prefix)

        best_ann = None
        best_prefix_len = -1
        for prefix, ann in as_obj.policy._local_rib.data.items():
            ann_prefix = ipaddress.ip_network(prefix)
            if src_prefix.subnet_of(ann_prefix):
                if ann_prefix.prefixlen > best_prefix_len:
                    best_ann = ann
                    best_prefix_len = ann_prefix.prefixlen

        if best_ann and best_ann.next_hop_asn == prev_hop.asn:
            return True
        return False
