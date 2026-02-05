import ipaddress
from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class FeasiblePathuRPF(BaseSAVPolicy):
    name: str = "Feasible-Path uRPF"

    @staticmethod
    def validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario,
    ) -> bool:
        # FP-uRPF is applied to only customer and bilateral peer interfaces
        if prev_hop.asn not in (as_obj.customer_asns | as_obj.peer_asns):
            return True 
        else:
            return FeasiblePathuRPF._validate(as_obj, source_prefix, prev_hop, engine, scenario)

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Feasible-Path uRPF.
        """
        src_prefix = ipaddress.ip_network(source_prefix)

        for ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).values():
            ann_prefix = ipaddress.ip_network(ann_info.unprocessed_ann.prefix)
            if src_prefix.subnet_of(ann_prefix):
                if as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    # print(ann_info, flush=True)
                    return True
        return False
