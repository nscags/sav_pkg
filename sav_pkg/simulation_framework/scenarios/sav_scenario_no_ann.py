from typing import TYPE_CHECKING

from bgpy.enums import Prefixes
from bgpy.enums import Timestamps

from sav_pkg.enums import Prefixes
from .sav_scenario_roa import SAVScenarioROA

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class SAVScenarioNoAnnouncements(SAVScenarioROA):
    """
    Victim ASes do not originate any prefixes and therefore are not seeded with any announcements.
    However, there exists a ROA for the victim's prefix
    """

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        anns = list()

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
                    prefix=f"1.2.{i}.0/24",
                    as_path=(reflector_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        return tuple(anns)