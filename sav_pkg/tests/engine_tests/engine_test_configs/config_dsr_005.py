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

from .as_graph_info_000 import as_graph_info_000


desc = "Test DSR Scenario, multiple users, no ROA"

config_dsr_005 = EngineTestConfig(
    name="config_dsr_005",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioDSR,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        num_users=3,
        source_prefix=Prefixes.ANYCAST_SERVER.value,
        override_user_asns=frozenset({555, 8, 9}),
        override_edge_server_asns=frozenset({777}),
        override_anycast_server_asns=frozenset({666}),
        override_sav_asns=frozenset({555, 8, 9}),
        BaseSAVPolicyCls=BAR_SAV,
        ignore_disconnections=False,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)