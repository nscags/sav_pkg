from typing import Optional, TYPE_CHECKING

from bgpy.simulation_framework.scenarios.roa_info import ROAInfo

from .scenario import SAVScenario
from sav_pkg.enums import Prefixes

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenarioROA(SAVScenario):

    def _get_roa_infos(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
        prev_scenario: Optional["SAVScenario"] = None,
    ) -> tuple[ROAInfo, ...]:
        """Returns a tuple of ROAInfo's"""

        err: str = "Fix the roa_origins of the " "announcements for multiple victims"
        assert len(self.victim_asns) == 1, err

        roa_origin: int = next(iter(self.victim_asns))

        return (ROAInfo(Prefixes.VICTIM.value, roa_origin),)