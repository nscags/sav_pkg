from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioDSR,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagramDSR
from sav_pkg.enums import Prefixes
from sav_pkg.policies.sav import BAR_SAV
from sav_pkg.policies.bgp import BGPFullNoExport2Some
from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_012


desc = "Testing how disconnections are handled with ignore_disconnections=False. " \
       "User will not receive announcement from edge server, should apply disconnected"

dsr_005 = EngineTestConfig(
    name="dsr_005",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioDSR,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        source_prefix=Prefixes.ANYCAST_SERVER.value,
        override_user_asns=frozenset({4}),
        override_edge_server_asns=frozenset({1}),
        override_anycast_server_asns=frozenset({5}),
        override_sav_asns=frozenset({4}),
        BaseSAVPolicyCls=BAR_SAV,
        ignore_disconnections=False,
        hardcoded_asn_cls_dict=frozendict({
            1: BGPFullNoExport2Some,
        })
    ),
    as_graph_info=as_graph_info_012,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)