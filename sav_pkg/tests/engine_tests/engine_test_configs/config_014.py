from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig
from frozendict import frozendict

from sav_pkg.policies.bgp.bgp_export2some import BGPExport2Some
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram

from .as_graph_info_008 import as_graph_info_008

"""
  "100": {
    "4193": 0.0,
    "10580": 0.16666666666666666,
    "16158": 0.16666666666666666,

    "100": {
        "4193": [],
        "10580": [
            true
        ],
        "16158": [
            false
        ],
"""

desc = "Single reflector"

config_014 = EngineTestConfig(
    name="config_014",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        num_attackers=0,
        num_reflectors=0,
        override_victim_asns=frozenset({100}),
        override_non_default_asn_cls_dict=frozendict(
            {100: BGPExport2Some}
        )
    ),
    as_graph_info=as_graph_info_008,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)
