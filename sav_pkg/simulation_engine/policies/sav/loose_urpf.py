from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework import SAVScenario

class LooseuRPF(BaseSAVPolicy):
    name: str = "Loose uRPF"

    @staticmethod
    def validate(
        as_obj: "AS", 
        source_prefix: str, 
        prev_hop: "AS", 
        engine: "SimulationEngine", 
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Loose uRPF.
        """
        for ann in as_obj.policy._local_rib.data.values():
            if ann.prefix == source_prefix:
                return True
        return False
