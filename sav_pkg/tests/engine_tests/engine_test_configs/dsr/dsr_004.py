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

from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_000


desc = "Basic DSR scenario. Testing how disconnections are handled with ignore_disconnections=False"

dsr_004 = EngineTestConfig(
    name="dsr_004",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioDSR,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        num_users=3,
        source_prefix=Prefixes.ANYCAST_SERVER.value,
        source_prefix_roa=True,
        override_user_asns=frozenset({555, 12, 5}),
        override_edge_server_asns=frozenset({777}),
        override_anycast_server_asns=frozenset({666}),
        override_sav_asns=frozenset({555, 12, 5}),
        BaseSAVPolicyCls=BAR_SAV,
        ignore_disconnections=False,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)