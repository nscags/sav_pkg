from typing import TYPE_CHECKING

from sav_pkg.simulation_framework.scenarios import SAVScenario
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
                    prefix=Prefixes.VICTIM.value,
                    as_path=(victim_asn,),
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

        for i, reflector_asn in enumerate(self.reflector_asns):
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=f"1.{i+2}.0.0/24",
                    as_path=(reflector_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        return tuple(anns)