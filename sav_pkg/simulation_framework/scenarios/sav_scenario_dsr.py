import random
from ipaddress import ip_network
from typing import TYPE_CHECKING, Optional

from frozendict import frozendict
from roa_checker import ROA

from bgpy.shared.enums import (
    SpecialPercentAdoptions,
    Timestamps,
)
from bgpy.simulation_engine import BaseSimulationEngine, Policy

from .sav_scenario import SAVScenario
from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig
from sav_pkg.enums import Prefixes

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class SAVScenarioDSR(SAVScenario):

    def __init__(
        self,
        *,
        scenario_config: SAVScenarioConfig,
        percent_adoption: float | SpecialPercentAdoptions = 0,
        engine: BaseSimulationEngine | None = None,
        attacker_asns: frozenset[int] | None = None,
        victim_asns: frozenset[int] | None = None,
        adopting_asns: frozenset[int] | None = None,
        reflector_asns: frozenset[int] | None = None,
    ):
        assert scenario_config.ScenarioCls == self.__class__, (
            "The config's scenario class is "
            f"{scenario_config.ScenarioCls.__name__}, but the scenario used is "
            f"{self.__class__.__name__}"
        )

        self.scenario_config: SAVScenarioConfig = scenario_config
        self.percent_adoption: float | SpecialPercentAdoptions = percent_adoption

        # DSR has no external attacker
        self.attacker_asns: frozenset[int] = frozenset()

        self.anycast_server_asns: frozenset[int] = self._get_anycast_server_asns(
            scenario_config.override_anycast_server_asns, None, engine
        )
        self.edge_server_asns: frozenset[int] = self._get_edge_server_asns(
            scenario_config.override_edge_server_asns, None, engine
        )
        self.victim_asns = self.edge_server_asns

        self.user_asns: frozenset[int] = self._get_user_asns(
            scenario_config.override_user_asns, None, engine
        )
        self.reflector_asns = self.user_asns

        # adopting_asns = SAV adopters
        self.adopting_asns: frozenset[int] = self._get_sav_adopting_asns(
            adopting_asns, engine
        )
        self.sav_policy_asn_dict = self._build_sav_policy_asn_dict()

        self._ctrl_plane_adopters: frozenset[int] = self._get_ctrl_plane_adopters(engine)

        if scenario_config.override_announcements is not None:
            self.announcements: tuple["Ann", ...] = scenario_config.override_announcements
            self.roas: tuple[ROA, ...] = scenario_config.override_roas or ()
        else:
            self.announcements = self._get_announcements(engine=engine)
            self.roas = self._get_roas(announcements=self.announcements, engine=engine)

        self._reset_and_add_roas_to_roa_checker()

        self.ordered_prefix_subprefix_dict: dict[str, list[str]] = (
            self._get_ordered_prefix_subprefix_dict()
        )

    #######################
    # Get Anycast Servers #
    #######################

    def _get_anycast_server_asns(
        self,
        override_anycast_server_asns: frozenset[int] | None,
        prev_anycast_server_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        if override_anycast_server_asns is not None:
            anycast_server_asns = override_anycast_server_asns
        elif (
            prev_anycast_server_asns is not None
            and len(prev_anycast_server_asns) == self.scenario_config.num_anycast_servers
        ):
            anycast_server_asns = prev_anycast_server_asns
        else:
            assert engine
            possible = self._get_possible_anycast_server_asns(engine)
            anycast_server_asns = frozenset(
                random.sample(tuple(possible), self.scenario_config.num_anycast_servers)
            )

        err = "Number of anycast_servers is different from anycast_servers length"
        assert len(anycast_server_asns) == self.scenario_config.num_anycast_servers, err
        return anycast_server_asns

    def _get_possible_anycast_server_asns(
        self,
        engine: BaseSimulationEngine,
    ) -> frozenset[int]:
        group_asns = engine.as_graph.asn_groups[self.scenario_config.anycast_server_subcategory_attr]
        hardcoded_asns = self.scenario_config.hardcoded_asn_cls_dict.keys()
        possible_asns = frozenset(set(hardcoded_asns) & set(group_asns))
        assert possible_asns, (
            "No possible anycast server ASNs found. "
            "Ensure hardcoded_asn_cls_dict contains ASNs in the anycast_server_subcategory."
        )
        return possible_asns

    ####################
    # Get Edge Servers #
    ####################

    def _get_edge_server_asns(
        self,
        override_edge_server_asns: frozenset[int] | None,
        prev_edge_server_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        if override_edge_server_asns is not None:
            edge_server_asns = override_edge_server_asns
        elif (
            prev_edge_server_asns is not None
            and len(prev_edge_server_asns) == self.scenario_config.num_edge_servers
        ):
            edge_server_asns = prev_edge_server_asns
        else:
            assert engine
            possible = self._get_possible_edge_server_asns(engine)
            edge_server_asns = frozenset(
                random.sample(tuple(possible), self.scenario_config.num_edge_servers)
            )

        err = "Number of edge_servers is different from edge_servers length"
        assert len(edge_server_asns) == self.scenario_config.num_edge_servers, err
        return edge_server_asns

    def _get_possible_edge_server_asns(
        self,
        engine: BaseSimulationEngine,
    ) -> frozenset[int]:
        group_asns = engine.as_graph.asn_groups[self.scenario_config.edge_server_subcategory_attr]
        hardcoded_asns = self.scenario_config.hardcoded_asn_cls_dict.keys()
        possible_asns = frozenset(set(hardcoded_asns) & set(group_asns))
        assert possible_asns, (
            "No possible edge server ASNs found. "
            "Ensure hardcoded_asn_cls_dict contains ASNs in the edge_server_subcategory."
        )
        possible_asns = possible_asns.difference(self.anycast_server_asns)
        return possible_asns

    #############
    # Get Users #
    #############

    def _get_user_asns(
        self,
        override_user_asns: frozenset[int] | None,
        prev_user_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        if override_user_asns is not None:
            user_asns = override_user_asns
        elif (
            prev_user_asns is not None
            and len(prev_user_asns) == self.scenario_config.num_users
        ):
            user_asns = prev_user_asns
        else:
            assert engine
            possible = self._get_possible_user_asns(engine)
            user_asns = frozenset(
                random.sample(tuple(possible), self.scenario_config.num_users)
            )

        err = "Number of users is different from users length"
        assert len(user_asns) == self.scenario_config.num_users, err
        return user_asns

    def _get_possible_user_asns(
        self,
        engine: BaseSimulationEngine,
    ) -> frozenset[int]:
        possible_asns = engine.as_graph.asn_groups[self.scenario_config.user_subcategory_attr]
        possible_asns = possible_asns.difference(self.anycast_server_asns)
        possible_asns = possible_asns.difference(self.edge_server_asns)
        return possible_asns

    #####################
    # Get Announcements #
    #####################

    def _get_announcements(self, engine=None, **kwargs) -> tuple["Ann", ...]:
        """All anycast servers, edge servers, and users announce a unique prefix"""

        anns = list()
        for anycast_server_asn in self.anycast_server_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.ANYCAST_SERVER.value,
                    as_path=(anycast_server_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        for edge_server_asn in self.edge_server_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.EDGE_SERVER.value,
                    as_path=(edge_server_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        for i, user_asn in enumerate(self.user_asns):
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=f"3.3.{i}.0/24",
                    as_path=(user_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        return tuple(anns)

    ################
    # Get ROA Info #
    ################

    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional[BaseSimulationEngine] = None,
    ) -> tuple[ROA, ...]:
        if self.scenario_config.source_prefix_roa:
            err = "Fix the roa_origins of the announcements for multiple edge servers"
            assert len(self.edge_server_asns) == 1, err
            roa_origin: int = next(iter(self.edge_server_asns))
            return (ROA(prefix=ip_network(self.scenario_config.source_prefix), origin=roa_origin),)
        else:
            return ()
