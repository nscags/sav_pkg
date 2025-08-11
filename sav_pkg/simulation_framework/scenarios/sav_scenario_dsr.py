import random
from typing import TYPE_CHECKING, Optional
from frozendict import frozendict

from bgpy.enums import (
    SpecialPercentAdoptions,
    Timestamps,
)
from bgpy.simulation_engine import BaseSimulationEngine, Policy
from bgpy.simulation_framework.scenarios.preprocess_anns_funcs import noop
from bgpy.simulation_framework.scenarios.roa_info import ROAInfo
from roa_checker import ROA

from .sav_scenario_e2s import SAVScenarioExport2Some
from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig
from sav_pkg.enums import Prefixes

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenarioDSR(SAVScenarioExport2Some):
    
    def __init__(
        self,
        *,
        scenario_config: SAVScenarioConfig,
        percent_adoption: float | SpecialPercentAdoptions = 0,
        engine: BaseSimulationEngine | None = None,
        prev_scenario: Optional["SAVScenarioDSR"] = None,
        preprocess_anns_func=noop,
    ):
        """inits attrs

        Any kwarg prefixed with default is only required for the test suite/YAML
        """
        # Config's ScenarioCls must be the same as instantiated Scenario
        assert scenario_config.ScenarioCls == self.__class__, (
            "The config's scenario class is "
            f"{scenario_config.ScenarioCls.__name__}, but the scenario used is "
            f"{self.__class__.__name__}"
        )

        self.scenario_config: SAVScenarioConfig = scenario_config
        self.percent_adoption: float | SpecialPercentAdoptions = percent_adoption

        self.attacker_asns: frozenset[int] = frozenset()

        self.anycast_server_asns: frozenset[int] = self._get_anycast_server_asns(
            scenario_config.override_anycast_server_asns, engine, prev_scenario
        )

        self.edge_server_asns: frozenset[int] = self._get_edge_server_asns(
            scenario_config.override_edge_server_asns, engine, prev_scenario
        )
        self.victim_asns = self.edge_server_asns

        self.user_asns: frozenset[int] = self._get_user_asns(
            scenario_config.override_user_asns, engine, prev_scenario
        )
        self.reflector_asns = self.user_asns

        self.sav_policy_asn_dict = self._get_sav_policies_asn_dict(engine)

        self.non_default_asn_cls_dict: frozendict[
            int, type[Policy]
        ] = self._get_non_default_asn_cls_dict(
            scenario_config.override_non_default_asn_cls_dict, engine, prev_scenario
        )

        if self.scenario_config.override_announcements:
            self.announcements: tuple[
                "Ann", ...
            ] = self.scenario_config.override_announcements
            self.roa_infos: tuple[ROA, ...] = self.scenario_config.override_roa_infos
        else:
            anns = self._get_announcements(engine=engine, prev_scenario=prev_scenario)
            self.roa_infos = self._get_roa_infos(
                announcements=anns, engine=engine, prev_scenario=prev_scenario
            )
            anns = self._add_roa_info_to_anns(
                announcements=anns, engine=engine, prev_scenario=prev_scenario
            )
            self.announcements = preprocess_anns_func(self, anns, engine, prev_scenario)

        self.ordered_prefix_subprefix_dict: dict[
            str, list[str]
        ] = self._get_ordered_prefix_subprefix_dict()

        self.policy_classes_used: frozenset[type[Policy]] = frozenset()

    #######################
    # Get Anycast Servers #
    #######################

    def _get_anycast_server_asns(
        self,
        override_anycast_server_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns anycast_server ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_anycast_server_asns is not None:
            anycast_server_asns = override_anycast_server_asns
        # Reuse the anycast_servers from the last scenario for comparability
        elif prev_scenario:
            anycast_server_asns = prev_scenario.anycast_server_asns
        # This is being initialized for the first time
        else:
            assert engine
            possible_anycast_server_asns = self._get_possible_anycast_server_asns(
                engine, self.percent_adoption, prev_scenario
            )
            # https://stackoverflow.com/a/15837796/8903959
            anycast_server_asns = frozenset(
                random.sample(
                    tuple(possible_anycast_server_asns), self.scenario_config.num_anycast_servers
                )
            )

        err = "Number of anycast_servers is different from anycast_servers length"
        assert len(anycast_server_asns) == self.scenario_config.num_anycast_servers, err

        return anycast_server_asns

    def _get_possible_anycast_server_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns possible anycast_servers ASNs, defaulted from config"""
        group_asns = engine.as_graph.asn_groups[self.scenario_config.anycast_server_subcategory_attr]
        hardcoded_asns = self.scenario_config.hardcoded_asn_cls_dict.keys()
        possible_asns = frozenset(set(hardcoded_asns) & set(group_asns))
        assert possible_asns
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        return possible_asns
    
    ####################
    # Get Edge Servers #
    ####################

    def _get_edge_server_asns(
        self,
        override_edge_server_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns edge_server ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_edge_server_asns is not None:
            edge_server_asns = override_edge_server_asns
        # Reuse the edge_servers from the last scenario for comparability
        elif prev_scenario:
            edge_server_asns = prev_scenario.edge_server_asns
        # This is being initialized for the first time
        else:
            assert engine
            possible_edge_server_asns = self._get_possible_edge_server_asns(
                engine, self.percent_adoption, prev_scenario
            )
            # https://stackoverflow.com/a/15837796/8903959
            edge_server_asns = frozenset(
                random.sample(
                    tuple(possible_edge_server_asns), self.scenario_config.num_edge_servers
                )
            )

        err = "Number of edge_servers is different from edge_servers length"
        assert len(edge_server_asns) == self.scenario_config.num_edge_servers, err

        return edge_server_asns

    def _get_possible_edge_server_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns possible edge_servers ASNs, defaulted from config"""

        group_asns = engine.as_graph.asn_groups[self.scenario_config.edge_server_subcategory_attr]
        hardcoded_asns = self.scenario_config.hardcoded_asn_cls_dict.keys()
        possible_asns = frozenset(set(hardcoded_asns) & set(group_asns))
        assert possible_asns
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        possible_asns = possible_asns.difference(self.anycast_server_asns)
        return possible_asns

    #############
    # Get Users #
    #############

    def _get_user_asns(
        self,
        override_user_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns user ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_user_asns is not None:
            user_asns = override_user_asns
        # Reuse the users from the last scenario for comparability
        elif prev_scenario:
            user_asns = prev_scenario.user_asns
        # This is being initialized for the first time
        else:
            assert engine
            possible_user_asns = self._get_possible_user_asns(
                engine, self.percent_adoption, prev_scenario
            )
            # https://stackoverflow.com/a/15837796/8903959
            user_asns = frozenset(
                random.sample(
                    tuple(possible_user_asns), self.scenario_config.num_users
                )
            )

        err = "Number of users is different from users length"
        assert len(user_asns) == self.scenario_config.num_users, err

        return user_asns

    def _get_possible_user_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns possible users ASNs, defaulted from config"""

        possible_asns = engine.as_graph.asn_groups[
            self.scenario_config.user_subcategory_attr
        ]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        # Remove anycast and edge servers from possible users
        possible_asns = possible_asns.difference(self.anycast_server_asns)
        possible_asns = possible_asns.difference(self.edge_server_asns)
        return possible_asns

    #####################
    # Get Announcements #
    #####################

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        """
        All anycast servers, edge servers, and users announce a unique prefix
        """

        # NOTE: this logic doesn't allow for multiple anycast/edge servers since
        #       all anycast/edge ASes will originate the same prefix
        #       In our simulations we use 1 anycast/edge server pair so this
        #       functionality is unnecessary, may need to add in future
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

        # NOTE: with this logic, we are limited to 256 users
        #       For our simulations we typically run 5-10 users
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

    def _get_roa_infos(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
        prev_scenario: Optional["SAVScenarioDSR"] = None,
    ) -> tuple[ROAInfo, ...]:
        """Returns a tuple of ROAInfo's"""

        if self.scenario_config.source_prefix_roa:
            err: str = "Fix the roa_origins of the " "announcements for multiple edge servers"
            assert len(self.edge_server_asns) == 1, err

            roa_origin: int = next(iter(self.edge_server_asns))
            return (ROAInfo(self.scenario_config.source_prefix, roa_origin),)
        else:
            return ()