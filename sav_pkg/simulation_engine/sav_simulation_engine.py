from typing import Optional, TYPE_CHECKING

from frozendict import frozendict
from bgpy.simulation_engine import Policy
from bgpy.simulation_engine.simulation_engines import SimulationEngine

if TYPE_CHECKING:
    from bgpy.simulation_framework import Scenario
    from bgpy.simulation_engine import Announcement as Ann
    from sav_pkg.simulation_engine.policies.sav.base_sav_policy import BaseSAVPolicy


class SAVSimulationEngine(SimulationEngine):
    """Extends SimulationEngine to also assign SAV policies to ASes"""

    def setup(
        self,
        announcements: tuple["Ann", ...] = (),
        BasePolicyCls: type[Policy] = Policy,
        non_default_asn_cls_dict: frozendict[int, type[Policy]] = (
            frozendict()  # type: ignore
        ),
        prev_scenario: Optional["Scenario"] = None,
        attacker_asns: frozenset[int] = frozenset(),
        AttackerBasePolicyCls: Optional[type[Policy]] = None,
        sav_policy_asn_dict: frozendict[int, type["BaseSAVPolicy"]] = (
            frozendict()  # type: ignore
        ),
    ) -> frozenset[type[Policy]]:
        """Sets AS classes, seeds announcements, and assigns SAV policies"""

        policies_used = super().setup(
            announcements,
            BasePolicyCls,
            non_default_asn_cls_dict,
            prev_scenario,
            attacker_asns,
            AttackerBasePolicyCls,
        )
        self._set_sav_classes(sav_policy_asn_dict)
        return policies_used

    def _set_sav_classes(
        self,
        sav_policy_asn_dict: frozendict[int, type["BaseSAVPolicy"]],
    ) -> None:
        """Assigns SAV policy instances to ASes, None for non-adopters"""

        for as_obj in self.as_graph:
            sav_cls = sav_policy_asn_dict.get(as_obj.asn)
            as_obj.sav_policy = sav_cls() if sav_cls is not None else None
