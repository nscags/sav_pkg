import random
from typing import TYPE_CHECKING, Optional, Union

from bgpy.enums import (
    SpecialPercentAdoptions,
    Timestamps,
)
from bgpy.simulation_engine import BaseSimulationEngine, Policy
from bgpy.simulation_framework.scenarios.preprocess_anns_funcs import noop
from frozendict import frozendict
from roa_checker import ROA

from .sav_scenario import SAVScenario
from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig
from sav_pkg.enums import Prefixes

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenarioDSR(SAVScenario):

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

        # for the DSR scenario we have three entities
        # anycast server: announces the prefix (implied that user routes request here)
        # edge server: in a separate AS, the anycast server routes a response using this server
        #              this edge server does not announce the same prefix, but it routes data packets
        #              using an IP address in the prefix announced by the anycast server
        # user: destination for edge server, receives the response 

        # we will model the response traffic with SAV deployed
        # since the AS is routing packets for a prefix it didn't announce, it causes issues for SAV filters
        # anycast_server: simply announces prefix, but does nothing else
        # edge_server: will use victim AS implementation, will automatically route packets and track metrics
        # user: reflector, will announce its own separate prefix, destination, doesn't route packets

        self.attacker_asns = frozenset()

        self.edge_server_asns: frozenset[int] = self._get_edge_server_asns(
            scenario_config.override_edge_server_asns, engine, prev_scenario
        )
        self.victim_asns = self.edge_server_asns

        self.user_asns: frozenset[int] = self._get_reflector_asns(
            scenario_config.override_user_asns, engine, prev_scenario
        )
        self.reflector_asns = self.user_asns

        self.anycast_server_asns: frozenset[int] = self._get_anycast_server_asns(
            scenario_config.override_anycast_server_asns, engine, prev_scenario
        )

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
        """Returns anycast server ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_anycast_server_asns is not None:
            anycast_server_asns = override_anycast_server_asns
        # Reuse the anycast servers from the last scenario for comparability
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

        err = "Number of anycast servers is different from anycast_servers length"
        assert len(anycast_server_asns) == self.scenario_config.num_anycast_servers, err

        return anycast_server_asns

    def _get_possible_anycast_server_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns possible reflectors ASNs, defaulted from config"""

        possible_asns = engine.as_graph.asn_groups[
            self.scenario_config.anycast_server_subcategory_attr
        ]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        # Remove edge servers and users from possible anycast servers
        possible_asns = possible_asns.difference(self.edge_server_asns)
        possible_asns = possible_asns.difference(self.user_asns)
        return possible_asns

    ####################
    # Get Edge Servers #
    ####################

    def _get_edge_server_asns(
        self,
        override_edge_server_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
        prev_scenario: Optional["SAVScenarioDSR"],
    ) -> frozenset[int]:
        """Returns edge server ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_edge_server_asns is not None:
            edge_server_asns = override_edge_server_asns
        # Reuse the edge server from the last scenario for comparability
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

        err = "Number of edge servers is different from edge_server length"
        assert len(edge_server_asns) == self.scenario_config.num_edge_servers, err

        return edge_server_asns

    def _get_possible_edge_server_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["SAVScenario"],
    ) -> frozenset[int]:
        """Returns possible edge server ASNs, defaulted from config"""

        possible_asns = engine.as_graph.asn_groups[
            self.scenario_config.edge_server_subcategory_attr
        ]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        return possible_asns

    #####################
    # Get Announcements #
    #####################

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        """
        All victims, attackers, and reflectors announce a unique prefix
        """

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

        for user_asn in self.user_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.USER.value,
                    as_path=(user_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        return tuple(anns)
