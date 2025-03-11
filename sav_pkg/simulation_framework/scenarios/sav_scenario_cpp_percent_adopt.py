from typing import TYPE_CHECKING
import random
import math

from bgpy.enums import SpecialPercentAdoptions

from .sav_scenario import SAVScenario

if TYPE_CHECKING:
    from bgpy.simulation_engine import BaseSimulationEngine, Policy
    

class SAVScenarioCPPPercentAdopt(SAVScenario):

    def _get_randomized_non_default_asn_cls_dict(
        self,
        engine: "BaseSimulationEngine",
    ) -> dict[int, type["Policy"]]:
        """Get adopting ASNs and non default ASNs

        By default, to get even adoption, adopt in each of the three
        subcategories

        """

        # Get the asn_cls_dict without randomized adoption
        asn_cls_dict = dict(self.scenario_config.hardcoded_asn_cls_dict)
        for asn in self._default_adopters:
            asn_cls_dict[asn] = self.scenario_config.AdoptPolicyCls

        # Randomly adopt in all three subcategories
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = engine.as_graph.asn_groups[subcategory]
            # Remove ASes that are already pre-set
            # Ex: Attacker and victim
            # Ex: ROV Nodes (in certain situations)
            possible_adopters = asns.difference(self._preset_asns)

            # Get how many ASes should be adopting

            # Round for the start and end of the graph
            # (if 0 ASes would be adopting, have 1 as adopt)
            # (If all ASes would be adopting, have all -1 adopt)
            # This was a feature request, but it's not supported
            if self.scenario_config.special_percent_adoption == SpecialPercentAdoptions.ONLY_ONE:
                k = 1
            elif self.scenario_config.special_percent_adoption == SpecialPercentAdoptions.ALL_BUT_ONE:
                k = len(possible_adopters) - 1
            # Really used just for testing
            elif self.scenario_config.special_percent_adoption == 0:
                k = 0
            else:
                err = f"{self.scenario_config.special_percent_adoption}"
                assert isinstance(self.scenario_config.special_percent_adoption, float), err
                k = math.ceil(len(possible_adopters) * self.scenario_config.special_percent_adoption)

            # https://stackoverflow.com/a/15837796/8903959
            possible_adopters_tup = tuple(possible_adopters)
            try:
                for asn in random.sample(possible_adopters_tup, k):
                    asn_cls_dict[asn] = self.scenario_config.AdoptPolicyCls
            except ValueError:
                raise ValueError(f"{k} can't be sampled from {len(possible_adopters)}")
        return asn_cls_dict