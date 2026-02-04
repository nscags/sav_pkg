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

from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_009


desc = "Basic DSR Scenario test, example from BAR-SAV I-D. Expected false positive with BAR-SAV (origin w/o ROA)."

dsr_002 = EngineTestConfig(
    name="dsr_002",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioDSR,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        source_prefix=Prefixes.ANYCAST_SERVER.value,
        override_user_asns=frozenset({1}),
        override_edge_server_asns=frozenset({2}),
        override_anycast_server_asns=frozenset({3}),
        override_sav_asns=frozenset({4}),
        BaseSAVPolicyCls=BAR_SAV,
        ignore_disconnections=False,
    ),
    as_graph_info=as_graph_info_009,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)