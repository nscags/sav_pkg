from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig
from frozendict import frozendict

from sav_pkg.enums import ASNs
from sav_pkg.policies.bgp import BGPExport2Some
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioDSR,
)
from sav_pkg.utils.diagram_dsr import SAVDiagramDSR

from .as_graph_info_006 import as_graph_info_006

desc = "Testing e2s w superprefix"

"""
Superprefix
"205": {
    "21976": 1.0,
    "46887": 0.0
},
"""

config_e2s_001 = EngineTestConfig(
    name="config_e2s_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioDSR,
        BasePolicyCls=BGP,
        override_anycast_server_asns=frozenset({666}),
        override_edge_server_asns=frozenset({205}),
        override_user_asns=frozenset({555}),
        override_sav_asns=frozenset({555}),
        hardcoded_asn_cls_dict=frozendict(
            {205: BGPExport2Some,
             666: BGPExport2Some}
        )
    ),
    as_graph_info=as_graph_info_006,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)