from typing import TYPE_CHECKING, Optional

from bgpy.simulation_framework.scenarios.roa_info import ROAInfo

from sav_pkg.enums import Prefixes

from .sav_scenario_dsr import SAVScenarioDSR

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenarioDSRROA(SAVScenarioDSR):

    def _get_roa_infos(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
        prev_scenario: Optional["SAVScenarioDSRROA"] = None,
    ) -> tuple[ROAInfo, ...]:
        """Returns a tuple of ROAInfo's"""

        err: str = "Fix the roa_origins of the " "announcements for multiple victims"
        assert len(self.edge_server_asns) == 1, err

        roa_origin: int = next(iter(self.edge_server_asns))

        return (ROAInfo(Prefixes.ANYCAST_SERVER.value, roa_origin),)