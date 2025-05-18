import math
import random
from typing import TYPE_CHECKING, Optional

from bgpy.enums import (
    SpecialPercentAdoptions,
    Timestamps,
)
from bgpy.simulation_engine import BaseSimulationEngine, Policy
from bgpy.simulation_framework.scenarios import Scenario
from bgpy.simulation_framework.scenarios.preprocess_anns_funcs import noop
from frozendict import frozendict
from roa_checker import ROA

from sav_pkg.enums import Prefixes
from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SAVScenario(Scenario):
    
    def __init__(
        self,
        *,
        scenario_config: SAVScenarioConfig,
        percent_adoption: float | SpecialPercentAdoptions = 0,
        engine: BaseSimulationEngine | None = None,
        prev_scenario: Optional["SAVScenario"] = None,
        preprocess_anns_func=noop,
    ):
        """inits attrs

        Any kwarg prefixed with default is only required for the test suite/YAML
        """
        print("Initializing SAVScenario", flush=True)
        # Config's ScenarioCls must be the same as instantiated Scenario
        assert scenario_config.ScenarioCls == self.__class__, (
            "The config's scenario class is "
            f"{scenario_config.ScenarioCls.__name__}, but the scenario used is "
            f"{self.__class__.__name__}"
        )

        self.scenario_config: SAVScenarioConfig = scenario_config
        self.percent_adoption: float | SpecialPercentAdoptions = percent_adoption

        self.attacker_asns: frozenset[int] = self._get_attacker_asns(
            scenario_config.override_attacker_asns, engine, prev_scenario
        )

        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, engine, prev_scenario
        )

        self.reflector_asns: frozenset[int] = self._get_reflector_asns(
            scenario_config.override_reflector_asns, engine, prev_scenario
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
        print("Initializing SAVScenario done", flush=True)

    ##################
    # Get Reflectors #
    ##################

    def _get_reflector_asns(
        self,
        override_reflector_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
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
        percent_adoption: float | SpecialPercentAdoptions,
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns possible reflectors ASNs, defaulted from config"""

        # NOTE: may change to combine stubs/mh, input_clique, etc AS groups
        #       this filters IXPs, which seems to be done for adoption as well

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

    #####################
    # Get Announcements #
    #####################

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        """
        All victims, attackers, and reflectors announce a unique prefix
        """

        # NOTE: this logic doesn't allow for multiple victims/attackers since
        #       all victim/attacker ASes will originate the same prefix
        #       In our simulations we use 1 victim/attacker pair so this
        #       functionality is unnecessary, will need to add in future
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

        # NOTE: with this logic, we are limited to 256 reflectors
        #       For our simulations we typically run 5-10 reflectors
        for i, reflector_asn in enumerate(self.reflector_asns):
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=f"1.2.{i}.0/24",
                    as_path=(reflector_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        return tuple(anns)

    #####################
    # Get Adopting ASNs #
    #####################

    def _get_sav_policies_asn_dict(self, engine):
        sav_policy_asn_dict = dict()

        # Override SAV asns
        if self.scenario_config.override_sav_asns is not None:
            for asn in self.scenario_config.override_sav_asns:
                sav_policy_asn_dict[asn] = self.scenario_config.BaseSAVPolicyCls
        else:
            sav_policy_asn_dict = self._get_randomized_sav_asn_dict(engine)

        return frozendict(sav_policy_asn_dict)

    def _get_randomized_sav_asn_dict(
        self,
        engine: BaseSimulationEngine,
    ):
        """Get adopting ASNs and non default ASNs

        By default, to get even adoption, adopt in each of the three
        subcategories
        """

        # Get the asn_cls_dict without randomized adoption
        asn_sav_cls_dict = dict(self.scenario_config.hardcoded_asn_sav_dict)
        for asn in self._default_sav_adopters:
            asn_sav_cls_dict[asn] = self.scenario_config.BaseSAVPolicyCls

        # Randomly adopt in all three subcategories
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = engine.as_graph.asn_groups[subcategory]
            # Remove ASes that are already pre-set
            # Ex: Attacker and victim
            # Ex: ROV Nodes (in certain situations)
            possible_adopters = asns.difference(self._preset_sav_asns)

            # Get how many ASes should be adopting

            # Round for the start and end of the graph
            # (if 0 ASes would be adopting, have 1 as adopt)
            # (If all ASes would be adopting, have all -1 adopt)
            # This was a feature request, but it's not supported
            if self.percent_adoption == SpecialPercentAdoptions.ONLY_ONE:
                k = 1
            elif self.percent_adoption == SpecialPercentAdoptions.ALL_BUT_ONE:
                k = len(possible_adopters) - 1
            # Really used just for testing
            elif self.percent_adoption == 0:
                k = 0
            else:
                err = f"{self.percent_adoption}"
                assert isinstance(self.percent_adoption, float), err
                k = math.ceil(len(possible_adopters) * self.percent_adoption)

            # https://stackoverflow.com/a/15837796/8903959
            possible_adopters_tup = tuple(possible_adopters)
            try:
                for asn in random.sample(possible_adopters_tup, k):
                    asn_sav_cls_dict[asn] = self.scenario_config.BaseSAVPolicyCls
            except ValueError:
                raise ValueError(f"{k} can't be sampled from {len(possible_adopters)}")
        return asn_sav_cls_dict

    @property
    def _default_sav_adopters(self) -> frozenset[int]:
        """Reflectors adopt by default if set in Scenario Config"""

        if self.scenario_config.reflector_default_adopters:
            return self.reflector_asns
        else:
            return frozenset()

    @property
    def _preset_sav_asns(self) -> frozenset[int]:
        """ASNs that have a preset adoption policy"""

        # Returns the union of default adopters and non adopters
        hardcoded_asns = set(self.scenario_config.hardcoded_asn_sav_dict)
        # reflectors (if set in config), victims, attackers, AS w/ hardcoded policies
        return (
            self._default_sav_adopters
            | self._default_adopters
            | self._default_non_adopters
            | hardcoded_asns
        )
