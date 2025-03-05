from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sav_pkg.utils.utils import get_applied_interfaces

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario

class BaseSAVPolicy(ABC):
    name: str = "NoSAV"

    @staticmethod
    def validate(
        as_obj: "AS", 
        source_prefix: str, 
        prev_hop: "AS", 
        engine: "SimulationEngine", 
        scenario: "SAVScenario",
    ):
        """
        Applies SAV policy to specificed interfaces.
        """
        sav_policy = scenario.sav_policy_asn_dict[as_obj.asn]
        applied_interfaces = get_applied_interfaces(as_obj, scenario, sav_policy)

        if any(prev_hop.asn in subset for subset in applied_interfaces):
            return sav_policy._validate(
                as_obj, 
                source_prefix,
                prev_hop,
                engine,
                scenario,
            )
        else:
            # Also considered applying Loose uRPF here since most policies/RFCs
            # recommended Loose uRPF for provider interfaces
            # However impact should be _extremely_ minimal
            return True
                

    @staticmethod
    @abstractmethod
    def _validate(self, *args, **kwargs) -> bool:
        """
        Performs validation policy on packet
        """
        pass