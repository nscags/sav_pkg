from .sav_scenario_bat import SAVScenarioBAT

from typing import TYPE_CHECKING, Optional

from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.enums import Timestamps

from sav_pkg.enums import Prefixes
from sav_pkg.policies.bgp.bgpfull_noexport2some import BGPFullNoExport2Some
from sav_pkg.policies.aspa.aspafull_no_e2s import ASPAFullNoExport2Some

if TYPE_CHECKING:
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenarioBATAnn(SAVScenarioBAT):

    def _get_announcements(
        self,
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["SAVScenarioBATAnn"] = None,
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

        # rather than just the providers of the victim/traffic originating AS announcing a prefix,
        # all providers of a no-export-to-some AS will annouce their own prefix
        if self.scenario_config.victim_providers_ann:
            # get set of providers of no-e2s ASes
            no_e2s_providers = set()
            for asn, as_obj in engine.as_graph.as_dict.items():
                if self.non_default_asn_cls_dict.get(asn) == ASPAFullNoExport2Some:
                    no_e2s_providers.update(as_obj.provider_asns)

            # each provider of a no-e2s AS announces their own prefix
            for i, provider_asn in enumerate(no_e2s_providers):
                anns.append(
                    self.scenario_config.AnnCls(
                        prefix=f"5.{i // 256}.{i % 256}.0/24",
                        as_path=(provider_asn,),
                        timestamp=Timestamps.VICTIM.value,
                    )
                )

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.ATTACKER.value,
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
    