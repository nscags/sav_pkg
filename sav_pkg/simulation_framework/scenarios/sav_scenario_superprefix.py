from .sav_scenario import SAVScenario

from typing import TYPE_CHECKING, Optional

from bgpy.enums import (
    Timestamps,
)
from bgpy.simulation_engine import BaseSimulationEngine

from sav_pkg.enums import Prefixes

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann

class SAVScenarioSuperprefix(SAVScenario):

    def _get_announcements(
        self,
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["SAVScenario"] = None,
    ) -> tuple["Ann", ...]:
        """
        All victims, attackers, and reflectors announce a unique prefix
        """

        # NOTE: this logic doesn't allow for multiple victims/attackers since
        #       all victim/attacker ASes will originate the same prefix
        #       In our simulations we use 1 victim/attacker pair so this
        #       functionality is unnecessary, may need to add in future
        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.VICTIM.value,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )
            if self.scenario_config.victim_providers_ann:
                # Providers of the victim announce their own prefix. This is because 
                # policies such as BAR-SAV use all announcement received to build 
                # a customer cone. In the case of no-export to some, the providers of
                # the victim announcing routes allows the verifier deploying BAR-SAV to
                # reconstuct the customer cone up to the provider of the vicitm AS. This
                # allow a victim AS to be included in the verifiers customer cone if they
                # adopt ASPA. This better simulates the impact when only the origin adopting ASPA. 
                victim_as_obj = engine.as_graph.as_dict[victim_asn]
                for i, provider_asn in enumerate(victim_as_obj.provider_asns):
                    anns.append(
                        self.scenario_config.AnnCls(
                            prefix=f"5.6.{i}.0/24",
                            as_path=(provider_asn,),
                            timestamp=Timestamps.VICTIM.value,
                        )
                    )

        # attack announces a superprefix covering the legitimate subprefix
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix="7.7.0.0/16",
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )

        # NOTE: with this logic, we are limited to 256 reflectors
        #       For our simulations we typically run 5-10 reflectors for efficiency
        for i, reflector_asn in enumerate(self.reflector_asns):
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=f"1.2.{i}.0/24",
                    as_path=(reflector_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        return tuple(anns)
    