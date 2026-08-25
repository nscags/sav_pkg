import hashlib
import math
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
from bgpy.simulation_framework.scenarios import Scenario

from sav_pkg.enums import Prefixes
from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class SAVScenario(Scenario):

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

        self.attacker_asns: frozenset[int] = self._get_attacker_asns(
            scenario_config.override_attacker_asns, attacker_asns, engine
        )
        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, victim_asns, engine
        )
        self.reflector_asns: frozenset[int] = self._get_reflector_asns(
            scenario_config.override_reflector_asns, reflector_asns, engine
        )

        # adopting_asns = SAV adopters
        self.adopting_asns: frozenset[int] = self._get_sav_adopting_asns(
            adopting_asns, engine
        )
        self.sav_policy_asn_dict = self._build_sav_policy_asn_dict()

        # Control-plane adopters (e.g. ASPA) - separate from SAV adoption
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

    #####################
    # Policy assignment #
    #####################

    def get_policy_cls(self, as_obj) -> type[Policy]:
        """Returns control-plane policy class for a given AS"""

        asn = as_obj.asn
        if self.scenario_config.AttackerBasePolicyCls and asn in self.attacker_asns:
            return self.scenario_config.AttackerBasePolicyCls
        elif Cls := self.scenario_config.hardcoded_asn_cls_dict.get(asn):
            return Cls
        elif asn in self._ctrl_plane_adopters or asn in self._default_adopters:
            return self.scenario_config.AdoptPolicyCls
        else:
            return self.scenario_config.BasePolicyCls

    ###############
    # Get Victims #
    ###############

    def _get_possible_victim_asns(
        self,
        engine,
        percent_adoption,
    ) -> frozenset[int]:
        group_asns = engine.as_graph.asn_groups[self.scenario_config.victim_subcategory_attr]
        hardcoded_asns = self.scenario_config.hardcoded_asn_cls_dict.keys()
        possible_asns = frozenset(set(hardcoded_asns) & set(group_asns))
        if not possible_asns:
            possible_asns = super()._get_possible_victim_asns(engine, percent_adoption)
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        return possible_asns

    ##################
    # Get Reflectors #
    ##################

    def _get_reflector_asns(
        self,
        override_reflector_asns: frozenset[int] | None,
        reflector_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        """Returns reflector ASNs"""

        if override_reflector_asns is not None:
            result = override_reflector_asns
        elif (
            reflector_asns is not None
            and len(reflector_asns) == self.scenario_config.num_reflectors
        ):
            result = reflector_asns
        else:
            assert engine
            possible = self._get_possible_reflector_asns(engine, self.percent_adoption)
            result = frozenset(
                self._sample_asns(
                    possible, self.scenario_config.num_reflectors, "reflector"
                )
            )

        err = "Number of reflectors is different from reflectors length"
        assert len(result) == self.scenario_config.num_reflectors, err
        return result

    def _get_possible_reflector_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
    ) -> frozenset[int]:
        """Returns possible reflector ASNs"""

        possible_asns = engine.as_graph.asn_groups[
            self.scenario_config.reflector_subcategory_attr
        ]
        possible_asns = possible_asns.difference(self.attacker_asns)
        possible_asns = possible_asns.difference(self.victim_asns)
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        return possible_asns

    #####################
    # Get Announcements #
    #####################

    def _get_announcements(
        self,
        engine: Optional[BaseSimulationEngine] = None,
    ) -> tuple["Ann", ...]:
        """All victims, attackers, and reflectors announce a unique prefix"""

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.VICTIM.value,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )
            if self.scenario_config.victim_providers_ann:
                victim_as_obj = engine.as_graph.as_dict[victim_asn]
                for i, provider_asn in enumerate(victim_as_obj.provider_asns):
                    anns.append(
                        self.scenario_config.AnnCls(
                            prefix=f"5.6.{i}.0/24",
                            as_path=(provider_asn,),
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
                    prefix=f"1.2.{i}.0/24",
                    as_path=(reflector_asn,),
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
        """Returns a tuple of ROAs"""

        if self.scenario_config.source_prefix_roa:
            err = "Fix the roa_origins of the announcements for multiple victims"
            assert len(self.victim_asns) == 1, err
            roa_origin: int = next(iter(self.victim_asns))
            return (ROA(prefix=ip_network(self.scenario_config.source_prefix), origin=roa_origin),)
        else:
            return ()

    #####################
    # Get SAV Adopting ASNs #
    #####################

    def _get_sav_adopting_asns(
        self,
        adopting_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        """Returns the set of randomly-sampled SAV adopters (excludes hardcoded/default)"""

        if self.scenario_config.override_sav_asns is not None:
            return frozenset(self.scenario_config.override_sav_asns)
        elif adopting_asns is not None:
            return adopting_asns
        elif engine is None:
            return frozenset()
        else:
            return self._get_randomized_sav_adopters(engine)

    def _get_randomized_sav_adopters(
        self,
        engine: BaseSimulationEngine,
    ) -> frozenset[int]:
        """Randomly samples SAV adopters across adoption subcategories"""

        adopters: set[int] = set()
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = engine.as_graph.asn_groups[subcategory]
            possible = asns.difference(self._preset_sav_asns)

            if self.scenario_config.attacker_providers_non_adopters:
                attacker_provider_asns: set[int] = set()
                for attacker_asn in self.attacker_asns:
                    attacker_as_obj = engine.as_graph.as_dict[attacker_asn]
                    attacker_provider_asns.update(attacker_as_obj.provider_asns)
                possible = frozenset(possible - attacker_provider_asns)

            if self.percent_adoption == SpecialPercentAdoptions.ONLY_ONE:
                k = 1
            elif self.percent_adoption == SpecialPercentAdoptions.ALL_BUT_ONE:
                k = len(possible) - 1
            elif self.percent_adoption == 0:
                k = 0
            else:
                assert isinstance(self.percent_adoption, float), f"{self.percent_adoption}"
                k = math.ceil(len(possible) * self.percent_adoption)

            try:
                adopters.update(self._sample_asns(possible, k, "sav_adopters"))
            except ValueError:
                raise ValueError(f"{k} can't be sampled from {len(possible)}")
        return frozenset(adopters)

    def _build_sav_policy_asn_dict(self) -> frozendict:
        """Builds sav_policy_asn_dict from hardcoded, default, and randomized adopters"""

        sav_dict: dict = dict(self.scenario_config.hardcoded_asn_sav_dict)
        for asn in self._default_sav_adopters:
            sav_dict[asn] = self.scenario_config.BaseSAVPolicyCls
        for asn in self.adopting_asns:
            if asn not in sav_dict:
                sav_dict[asn] = self.scenario_config.BaseSAVPolicyCls
        return frozendict(sav_dict)

    ###########################
    # Get ctrl-plane adopters #
    ###########################

    def _get_ctrl_plane_adopters(
        self,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        """Randomly samples control-plane (e.g. ASPA) adopters"""

        pa = self.scenario_config.ctrl_plane_percent_adoption
        if engine is None or pa == 0:
            return frozenset()

        adopters: set[int] = set()
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = engine.as_graph.asn_groups[subcategory]
            possible = asns.difference(self._preset_asns)

            if pa == SpecialPercentAdoptions.ONLY_ONE:
                k = 1
            elif pa == SpecialPercentAdoptions.ALL_BUT_ONE:
                k = len(possible) - 1
            else:
                assert isinstance(pa, float), f"{pa}"
                k = math.ceil(len(possible) * pa)

            try:
                adopters.update(self._sample_asns(possible, k, "ctrl_plane"))
            except ValueError:
                raise ValueError(f"{k} can't be sampled from {len(possible)}")
        return frozenset(adopters)

    ############
    # Sampling #
    ############

    def _sample_asns(
        self,
        possible: frozenset[int],
        k: int,
        salt: str,
    ) -> list[int]:
        """
        Returns the first k ASNs of this trial's fixed ordering

        Every random selection funnels through here, and every selection is a
        prefix of one ordering that is shuffled once per trial. That makes the
        selections incremental: the 20% set is a superset of the 10% set by
        construction, and the reflectors come out identical in every scenario
        of the trial.

        Doing it this way rather than threading state through the simulation
        loop is deliberate. Simulation._run_chunk resets adopting_asns at the
        top of every percent adoption, never carries ctrl plane adopters or
        reflectors at all, and splits trials across parse_cpus worker
        processes, so carried state would not survive anyway.

        salt names the selection ("reflector", "sav_adopters", "ctrl_plane")
        so the three orderings are independent of each other.

        NOTE: nesting holds as long as the candidate pool is the same in every
        scenario of the trial. The pools are `subcategory - _preset_asns` and
        `subcategory - _preset_sav_asns`, so scenario configs being compared
        must agree on hardcoded_asn_cls_dict / hardcoded_asn_sav_dict,
        victim_default_adopters and reflector_default_adopters. Varying only
        ctrl_plane_percent_adoption / percent_adoption is fine.
        """
        if k <= 0:
            return []
        if k > len(possible):
            # same failure the callers already expect from random.sample
            raise ValueError(f"{k} can't be sampled from {len(possible)}")

        # sorted() first so the ordering depends only on the seed, never on
        # set iteration order
        ordering = sorted(possible)
        random.Random(self._sample_seed(salt)).shuffle(ordering)

        return ordering[:k]

    def _sample_seed(self, salt: str) -> int:
        """
        A seed fixed within a trial that differs between trials

        bgpy holds attacker_asns and victim_asns constant across every percent
        adoption and every scenario config of a trial, then redraws them for
        the next trial (Simulation._run_chunk), so they are the one thing
        already on hand that identifies "this trial". Both are set before any
        of the three selections happen.

        md5 rather than hash(): str hashing is salted per process, and trials
        are split across parse_cpus worker processes.
        """
        key = "|".join(
            (
                salt,
                ",".join(str(x) for x in sorted(self.victim_asns)),
                ",".join(str(x) for x in sorted(self.attacker_asns)),
            )
        )
        return int.from_bytes(hashlib.md5(key.encode()).digest()[:8], "big")

    ####################
    # Preset ASN props #
    ####################

    @property
    def _default_adopters(self) -> frozenset[int]:
        """Victims adopt control-plane policy by default if configured"""

        if self.scenario_config.victim_default_adopters:
            return self.victim_asns
        else:
            return frozenset()

    @property
    def _default_non_adopters(self) -> frozenset[int]:
        return self.attacker_asns

    @property
    def _default_sav_adopters(self) -> frozenset[int]:
        """Reflectors adopt SAV policy by default if configured"""

        if self.scenario_config.reflector_default_adopters:
            return self.reflector_asns
        else:
            return frozenset()

    @property
    def _preset_asns(self) -> frozenset[int]:
        """ASNs excluded from randomized ctrl-plane adoption"""

        hardcoded_asns = set(self.scenario_config.hardcoded_asn_cls_dict)
        return (
            self._default_adopters
            | self._default_non_adopters
            | hardcoded_asns
        )

    @property
    def _preset_sav_asns(self) -> frozenset[int]:
        """ASNs excluded from randomized SAV adoption"""

        hardcoded_asns = set(self.scenario_config.hardcoded_asn_sav_dict)
        return (
            self._default_sav_adopters
            | self._default_adopters
            | self._default_non_adopters
            | hardcoded_asns
        )
