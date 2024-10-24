from typing import Iterable

from bgpy.enums import Plane, ASGroups

from sav_pkg.simulation_framework.metric_tracker.metric_key import MetricKey
from sav_pkg.enums import Outcomes

# First attempt, didn't work with pickle (idk why?)
# def get_metric_keys() -> Iterable[MetricKey]:
#     for plane in [Plane.DATA]:
#         for as_group in [ASGroups.ALL_WOUT_IXPS]:
#             for outcome in [Outcomes.FALSE_NEGATIVE, Outcomes.TRUE_POSITIVE]:
#                 yield MetricKey(plane=plane, outcome=outcome, as_group=as_group)

# TODO: add additional metrics
def get_metric_keys() -> Iterable[MetricKey]:
    metric_keys = [
        MetricKey(plane=plane, outcome=outcome, as_group=as_group)
        for plane in [Plane.DATA]
        for as_group in [ASGroups.ALL_WOUT_IXPS]
        for outcome in [Outcomes.FALSE_NEGATIVE, Outcomes.FALSE_POSITIVE]
    ]
    return metric_keys

