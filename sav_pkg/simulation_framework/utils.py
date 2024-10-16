
from sav_pkg.simulation_framework.metric_tracker.metric_key import MetricKey
from sav_pkg.enums import Outcomes, ASGroups

# TODO: add additional metrics
def get_metric_key():
    outcome = Outcomes.FALSE_NEGATIVE.value
    as_group = ASGroups.REFLECTORS.value

    yield MetricKey(outcome=outcome, as_group=as_group)
