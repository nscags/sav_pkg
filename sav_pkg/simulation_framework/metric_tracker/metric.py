from collections import defaultdict

from bgpy.as_graphs import AS
from bgpy.simulation_engine import BaseSimulationEngine

from sav_pkg.simulation_framework.scenarios import SAVScenario
from sav_pkg.enums import Outcomes

from .metric_key import MetricKey


class Metric:
    """Tracks a single metric"""

    def __init__(
        self,
        metric_key: MetricKey,
        percents: defaultdict[MetricKey, list[float]] | None = None,
    ) -> None:
        # At this point the PolicyCls is None for the metric_key
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

    def add_data(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: SAVScenario,
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
        scenario: SAVScenario,
        data_plane_outcomes,
    ) -> None:
        """Adds to numerator if it is within the as group and the outcome is correct"""

        # as_obj = reflector, user
        # origin = attacker, victim, edge
        outcome_by_origin = dict()
        for (asn, _, _, origin), outcome in data_plane_outcomes.items():
            if asn != as_obj.asn:
                continue

            current = outcome_by_origin.get(origin)
            if current is None:
                outcome_by_origin[origin] = outcome
            else:
                if outcome < current:
                    outcome_by_origin[origin] = outcome

        if self.metric_key.outcome == Outcomes.DETECTION_RATE:
            for outcome in outcome_by_origin.values():
                if outcome in [Outcomes.TRUE_POSITIVE.value, Outcomes.A_FILTERED_ON_PATH.value]:
                    self._numerator += 1
        elif self.metric_key.outcome == Outcomes.FALSE_POSITIVE_RATE:
            for outcome in outcome_by_origin.values():
                if outcome in [Outcomes.FALSE_POSITIVE.value, Outcomes.V_FILTERED_ON_PATH.value]:
                    self._numerator += 1  
        else:
            for outcome in outcome_by_origin.values():
                if outcome == self.metric_key.outcome.value:
                    self._numerator += 1

    def _add_denominator(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: SAVScenario,
        data_plane_outcomes,
    ) -> bool:
        """Adds to the denominator if it is within the as group"""

        # Only track metrics at reflectors
        if as_obj.asn in scenario.reflector_asns:
            # ignore disconnections except for disconnected metric
            if self.metric_key.outcome != Outcomes.DISCONNECTED:
                relevant_entries = [
                    (origin, outcome)
                    for (asn, _, _, origin), outcome in data_plane_outcomes.items()
                    if asn == as_obj.asn
                ]
                # For Attacker and Victim success we ignore disconnected reflectors
                attacker_outcomes = [outcome for origin, outcome in relevant_entries if origin in scenario.attacker_asns]
                if self.metric_key.outcome == Outcomes.DETECTION_RATE:
                    if any(outcome == Outcomes.DISCONNECTED.value for outcome in attacker_outcomes):
                        return False
                victim_outcomes = [outcome for origin, outcome in relevant_entries if origin in scenario.victim_asns]
                if self.metric_key.outcome == Outcomes.FALSE_POSITIVE_RATE:
                    if any(outcome == Outcomes.DISCONNECTED.value for outcome in victim_outcomes):
                        return False
            self._denominator += 1
            return True
        else:
            return False