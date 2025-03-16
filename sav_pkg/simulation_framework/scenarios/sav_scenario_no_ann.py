from typing import Optional, TYPE_CHECKING

from bgpy.simulation_framework.scenarios.scenario import Scenario
from bgpy.simulation_framework.scenarios.roa_info import ROAInfo
from bgpy.enums import Prefixes
from bgpy.enums import Timestamps

from sav_pkg.enums import Prefixes
from .sav_scenario import SAVScenario

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenarioNoAnnouncements(SAVScenario):
    """
    Victim does not announce anything but has a ROA for it's prefix
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

    def _get_roa_infos(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
        prev_scenario: Optional["Scenario"] = None,
    ) -> tuple[ROAInfo, ...]:
        """Returns a tuple of ROAInfo's"""

        err: str = "Fix the roa_origins of the " "announcements for multiple victims"
        assert len(self.victim_asns) == 1, err

        roa_origin: int = next(iter(self.victim_asns))

        return (ROAInfo(Prefixes.VICTIM.value, roa_origin),)