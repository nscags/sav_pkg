from dataclasses import dataclass

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_framework.scenarios import ScenarioConfig

from .metric_key import MetricKey


@dataclass(frozen=True, slots=True)
class DataKey:
    """Key for storing data within the MetricTracker"""

    propagation_round: int
    percent_adopt: float | SpecialPercentAdoptions
    scenario_config: ScenarioConfig
    metric_key: MetricKey
