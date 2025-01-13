from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework import SAVScenario


class StrictuRPF(BaseSAVPolicy):
    name: str = "Strict uRPF"

    @staticmethod
    def validate(
        as_obj: "AS", 
        source_prefix: str, 
        prev_hop: "AS", 
        engine: "SimulationEngine", 
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Strict uRPF.
        """
        # Strict uRPF is applied to only customer and peer interfaces
        if prev_hop.asn in as_obj.provider_asns:
            return True
        else:
            for prefix, ann in as_obj.policy._local_rib.data.items():
                if prefix == source_prefix and ann.next_hop_asn == prev_hop.asn:
                    return True

            return False
