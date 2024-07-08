from typing import TYPE_CHECKING

from sav_pkg.simluation_framework.scenarios import SAVScenario
from sav_pkg.enums import Prefixes, Timestamps

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann

class SAVScenarioMultipleReflectors(SAVScenario):
    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        """
        """

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX1.value,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX2.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )

        prefixes = [Prefixes.PREFIX3.value, Prefixes.PREFIX4.value]

        for i, reflector_asn in enumerate(self.reflector_asns):
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=prefixes[i],
                    as_path=(reflector_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )


        return tuple(anns)