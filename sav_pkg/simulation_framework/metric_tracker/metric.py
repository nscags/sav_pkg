from collections import defaultdict
from dataclasses import replace
from typing import Optional

from bgpy.as_graphs import AS
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework.scenarios import Scenario

from .metric_key import MetricKey


class Metric:
    """Tracks a single metric"""

    def __init__(
        self,
        metric_key: MetricKey,
        percents: Optional[defaultdict[MetricKey, list[float]]] = None,
    ) -> None:
        # At this point the PolicyCls is None for the metric_key,
        # it's later added in the save_percents
        self.metric_key: MetricKey = metric_key
        self._numerator: float = 0
        self._denominator: float = 0
        if percents:
            self.percents: defaultdict[MetricKey, list[float]] = percents
        else:
            self.percents = defaultdict(list)

    def __add__(self, other):
        """Adds two Metric instances together."""

        if not isinstance(other, Metric):
            return NotImplemented

        if self.metric_key != other.metric_key:
            raise ValueError("Cannot add Metric objects with different metric_keys")

        result = Metric(self.metric_key)
        result._numerator = self._numerator + other._numerator
        result._denominator = self._denominator + other._denominator

        for obj in (self, other):
            for metric_key, percent_list in obj.percents.items():
                result.percents[metric_key].extend(percent_list)

        return result

    def save_percents(self):
        """Calculate and save percentage values"""
        if self._denominator != 0:
            percentage = (self._numerator / self._denominator) * 100
            self.percents[self.metric_key].append(percentage)
        else:
            self.percents[self.metric_key].append(0)

    # instead of calling add data with an outcome it will be called with the full dict
    # extract outcome from there
    def add_data(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        data_plane_outcomes,
    ):
        within_denom = self._add_denominator(
            as_obj=as_obj,
            engine=engine,
            scenario=scenario,
            data_plane_outcomes=data_plane_outcomes,
        )

        if within_denom:
            self._add_numerator(
                as_obj=as_obj,
                engine=engine,
                scenario=scenario,
                data_plane_outcomes=data_plane_outcomes,
            )

    def _add_numerator(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        data_plane_outcomes,
    ) -> None:
        """Adds to numerator if it is within the as group and the outcome is correct"""
        
        as_obj_outcomes = data_plane_outcomes.get(as_obj.asn)

        for origin, outcome_dict in as_obj_outcomes.items():
            for prev_hop, outcome in outcome_dict.items():
                if outcome == self.metric_key.outcome.value:
                    self._numerator += 1
                    return


    def _add_denominator(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        data_plane_outcomes,
    ) -> bool:
        """Adds to the denominator if it is within the as group"""

        if as_obj.asn in scenario.reflector_asns:
            self._denominator += 1
            return True
        else:
            return False