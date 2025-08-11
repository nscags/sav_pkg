from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig
from frozendict import frozendict

from sav_pkg.enums import ASNs
from sav_pkg.policies.bgp import BGPExport2Some
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioExport2Some,
)
from sav_pkg.utils.diagram import SAVDiagram

from .as_graph_info_006 import as_graph_info_006

desc = "Testing DSR e2s w superprefix"

"""
Superprefix
"205": {
    "21976": 1.0,
    "46887": 0.0
},
"""

config_e2s_000 = EngineTestConfig(
    name="config_e2s_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioExport2Some,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_victim_asns=frozenset({205}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        hardcoded_asn_cls_dict=frozendict(
            {205: BGPExport2Some}
        )
    ),
    as_graph_info=as_graph_info_006,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)