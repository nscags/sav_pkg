from typing import TYPE_CHECKING

from bgpy.simulation_engine import Policy
from bgpy.simulation_engine.simulation_engines import SimulationEngine
from yamlable import yaml_info

if TYPE_CHECKING:
    from bgpy.simulation_framework import Scenario
    from sav_pkg.simulation_engine.policies.sav.base_sav_policy import BaseSAVPolicy


@yaml_info(yaml_tag="SAVSimulationEngine")
class SAVSimulationEngine(SimulationEngine):
    """Extends SimulationEngine to also assign SAV policies to ASes"""

    def setup(self, scenario: "Scenario") -> None:
        """Sets AS classes, seeds announcements, and assigns SAV policies"""

        super().setup(scenario)
        self._set_sav_classes(scenario.sav_policy_asn_dict)

    def _set_sav_classes(
        self,
        sav_policy_asn_dict,
    ) -> None:
        """Assigns SAV policy instances to ASes, None for non-adopters"""

        for as_obj in self.as_graph:
            sav_cls = sav_policy_asn_dict.get(as_obj.asn)
            as_obj.sav_policy = sav_cls() if sav_cls is not None else None
