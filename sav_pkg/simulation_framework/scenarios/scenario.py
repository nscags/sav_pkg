from typing import Optional, TYPE_CHECKING, Union, Type
import random
from frozendict import frozendict

from bgpy.simulation_framework.scenarios import Scenario
from bgpy.simulation_framework.scenarios.preprocess_anns_funcs import noop, PREPROCESS_ANNS_FUNC_TYPE
from bgpy.simulation_framework.scenarios.roa_info import ROAInfo
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_engine import Policy
from bgpy.enums import Timestamps
from bgpy.enums import (
    SpecialPercentAdoptions,
)

from sav_pkg.enums import Prefixes
from .scenario_config import SAVScenarioConfig


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenario(Scenario):

    def __init__(
        self,
        *,
        scenario_config: SAVScenarioConfig,
        percent_adoption: Union[float, SpecialPercentAdoptions] = 0,
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["Scenario"] = None,
        preprocess_anns_func: PREPROCESS_ANNS_FUNC_TYPE = noop,
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
        self.percent_adoption: Union[float, SpecialPercentAdoptions] = percent_adoption

        self.attacker_asns: frozenset[int] = self._get_attacker_asns(
            scenario_config.override_attacker_asns, engine, prev_scenario
        )

        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, engine, prev_scenario
        )

        self.reflector_asns: frozenset[int] = self._get_reflector_asns(
            scenario_config.override_reflector_asns, engine, prev_scenario
        )

        # TODO: create function which assigns ASN to SAV policy
        #       go through hardcoded first, otherwise default to BaseSAVPolicyCls
        self.sav_policy_asn_dict = self._get_sav_policies_asn_dict()
 
        self.non_default_asn_cls_dict: frozendict[int, type[Policy]] = (
            self._get_non_default_asn_cls_dict(
                scenario_config.override_non_default_asn_cls_dict, engine, prev_scenario
            )
        )

        if self.scenario_config.override_announcements:
            self.announcements: tuple["Ann", ...] = (
                self.scenario_config.override_announcements
            )
            self.roa_infos: tuple[ROAInfo, ...] = (
                self.scenario_config.override_roa_infos
            )
        else:
            anns = self._get_announcements(engine=engine, prev_scenario=prev_scenario)
            self.roa_infos = self._get_roa_infos(
                announcements=anns, engine=engine, prev_scenario=prev_scenario
            )
            anns = self._add_roa_info_to_anns(
                announcements=anns, engine=engine, prev_scenario=prev_scenario
            )
            self.announcements = preprocess_anns_func(self, anns, engine, prev_scenario)

        self.ordered_prefix_subprefix_dict: dict[str, list[str]] = (
            self._get_ordered_prefix_subprefix_dict()
        )

        self.policy_classes_used: frozenset[Type[Policy]] = frozenset()


    ##################
    # Get Reflectors #
    ##################

    def _get_reflector_asns(
        self,
        override_reflector_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns reflector ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_reflector_asns is not None:
            reflector_asns = override_reflector_asns
        # Reuse the reflectors from the last scenario for comparability
        elif prev_scenario:
            reflector_asns = prev_scenario.reflector_asns
        # This is being initialized for the first time
        else:
            assert engine
            possible_reflector_asns = self._get_possible_reflector_asns(
                engine, self.percent_adoption, prev_scenario
            )
            # https://stackoverflow.com/a/15837796/8903959
            reflector_asns = frozenset(
                random.sample(
                    tuple(possible_reflector_asns), self.scenario_config.num_reflectors
                )
            )

        err = "Number of reflectors is different from reflectors length"
        assert len(reflector_asns) == self.scenario_config.num_reflectors, err

        return reflector_asns

    def _get_possible_reflector_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns possible reflectors ASNs, defaulted from config"""

        possible_asns = engine.as_graph.asn_groups[
            self.scenario_config.reflector_subcategory_attr
        ]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        # Remove attackers and victims from possible reflectors
        possible_asns = possible_asns.difference(self.attacker_asns)
        possible_asns = possible_asns.difference(self.victim_asns)
        return possible_asns

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
    
    #############################
    #     Get SAV Policies      #
    #############################

    def _get_sav_policies_asn_dict(self):
        # assign hardcoded SAV policies
        sav_policy_asn_dict = dict()
        if self.scenario_config.hardcoded_asn_sav_dict is not None:
            for asn, sav_policy in self.scenario_config.hardcoded_asn_sav_dict.items():
                sav_policy[asn] = sav_policy
        # remaining adopting ASes default to BaseSAVPolicy
        for asn in self.scenario_config.override_sav_asns:
            if asn not in sav_policy_asn_dict:
                sav_policy_asn_dict[asn] = self.scenario_config.BaseSAVPolicyCls

        return frozendict(sav_policy_asn_dict)