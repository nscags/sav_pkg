import ipaddress
from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class LooseuRPF(BaseSAVPolicy):
    name: str = "Loose uRPF"

    @staticmethod
    def validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario,
    ) -> bool:
        # Loose uRPF can be applied to any interface
        return LooseuRPF._validate(as_obj, source_prefix, prev_hop, engine, scenario)

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Loose uRPF.
        """
        src_prefix = ipaddress.ip_network(source_prefix)
        for ann in as_obj.policy._local_rib.data.values():
            ann_prefix = ipaddress.ip_network(ann.prefix)
            if src_prefix.subnet_of(ann_prefix):
                return True
        return False
