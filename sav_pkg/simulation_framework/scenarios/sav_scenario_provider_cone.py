from .sav_scenario import SAVScenario

from typing import TYPE_CHECKING, Optional, Union
from frozendict import frozendict

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_engine import BaseSimulationEngine, Policy
from bgpy.simulation_framework.scenarios.preprocess_anns_funcs import noop

from roa_checker import ROA

from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class SAVScenarioProviderCone(SAVScenario):

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
        # Config's ScenarioCls must be the same as instantiated Scenario
        assert scenario_config.ScenarioCls == self.__class__, (
            "The config's scenario class is "
            f"{scenario_config.ScenarioCls.__name__}, but the scenario used is "
            f"{self.__class__.__name__}"
        )

        self.scenario_config: SAVScenarioConfig = scenario_config
        self.percent_adoption: float | SpecialPercentAdoptions = percent_adoption

        # Set attacker_asns to empty to avoid errors when getting reflector asns (see SAVScenario)
        self.attacker_asns = frozenset()

        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, engine, prev_scenario
        )

        self.reflector_asns: frozenset[int] = self._get_reflector_asns(
            scenario_config.override_reflector_asns, engine, prev_scenario
        )

        # since attackers must be in the provider cone of the validator, 
        # we must get attacker ASNs after getting reflector ASNs 
        self.attacker_asns: frozenset[int] = self._get_attacker_asns(
            scenario_config.override_attacker_asns, engine, prev_scenario
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
    
    def _get_possible_attacker_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["SAVScenario"],
    ) -> frozenset[int]:
        """Returns possible attacker ASNs, defaulted from config"""

        provider_cone = set()
        for reflector_asn in self.reflector_asns:
            as_obj = engine.as_graph.as_dict[reflector_asn]
            visited = set()
            stack = [as_obj]
            while stack:
                current = stack.pop()
                for provider in current.providers:
                    if provider.asn not in visited:
                        visited.add(provider.asn)
                        stack.append(provider)
            provider_cone.update(visited)

        possible_asns = frozenset(provider_cone)
        if not possible_asns:
            possible_asns = super()._get_possible_attacker_asns(engine, percent_adoption, prev_scenario)

        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        # Remove victims and reflectors from possible attackers
        possible_asns = possible_asns.difference(self.victim_asns)
        possible_asns = possible_asns.difference(self.reflector_asns)
        return possible_asns
