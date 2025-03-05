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
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Feasible-Path uRPF.
        """
        for ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).values():
            if (
                as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                )
                and ann_info.unprocessed_ann.prefix == source_prefix
            ):
                return True
        return False