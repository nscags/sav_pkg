from .sav_scenario import SAVScenario

from typing import TYPE_CHECKING, Optional, Union

from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import BaseSimulationEngine

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

        # Temporarily set attacker_asns to empty so _get_reflector_asns and
        # _get_victim_asns don't error (they exclude attacker ASNs).
        # The real attacker_asns are determined after reflectors are set.
        self._pre_attacker_asns: frozenset[int] = frozenset()

        super().__init__(
            scenario_config=scenario_config,
            percent_adoption=percent_adoption,
            engine=engine,
            attacker_asns=frozenset(),  # placeholder so super() completes
            victim_asns=victim_asns,
            adopting_asns=adopting_asns,
            reflector_asns=reflector_asns,
        )

        # Now that reflectors are set, compute the real attacker_asns from
        # the provider cone of the reflectors.
        self.attacker_asns = self._get_attacker_asns(
            scenario_config.override_attacker_asns, attacker_asns, engine
        )

    def _get_possible_attacker_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
    ) -> frozenset[int]:
        """Returns attacker ASNs from the provider cone of each reflector"""

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
            possible_asns = super()._get_possible_attacker_asns(engine, percent_adoption)

        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        possible_asns = possible_asns.difference(self.victim_asns)
        possible_asns = possible_asns.difference(self.reflector_asns)
        return possible_asns
