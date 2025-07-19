from typing import TYPE_CHECKING, Optional

from bgpy.enums import Timestamps
from bgpy.simulation_engine import BaseSimulationEngine

from .sav_scenario import SAVScenario

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann 


class SAVScenarioNoExport2Some(SAVScenario):

    def _get_announcements(
        self,
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["SAVScenario"] = None,
    ) -> tuple["Ann", ...]:
        """
        Providers of the victim announce their own prefix. This is because 
        policies such as BAR-SAV use all announcement received to build 
        a customer cone. In the case of no-export to some, the providers of
        the victim announcing routes allows the verifier deploying BAR-SAV to
        reconstuct the customer cone up to the provider of the vicitm AS. This
        allow a victim AS to be included in the verifiers customer cone if they
        adopt ASPA. This better simulates the impact when only the origin adopting
        ASPA. 
        """

        anns = list(super()._get_announcements(engine, prev_scenario))

        for victim_asn in self.victim_asns:
            victim_as_obj = engine.as_graph.as_dict[victim_asn]
            for i, provider_asn in enumerate(victim_as_obj.provider_asns):
                anns.append(
                    self.scenario_config.AnnCls(
                        prefix=f"5.6.{i}.0/24",
                        as_path=(provider_asn,),
                        timestamp=Timestamps.VICTIM.value,
                    )
                )

        return tuple(anns)
        