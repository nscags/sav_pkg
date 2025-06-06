from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioDSRROA,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagramDSR
from sav_pkg.enums import Prefixes
from sav_pkg.policies.sav import RefinedAlgA

from .as_graph_info_000 import as_graph_info_000


desc = "Test DSR Scenario, multiple users"

config_dsr_006 = EngineTestConfig(
    name="config_dsr_006",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioDSRROA,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        num_users=3,
        victim_source_prefix=Prefixes.ANYCAST_SERVER.value,
        override_user_asns=frozenset({555, 8, 9}),
        override_edge_server_asns=frozenset({777}),
        override_anycast_server_asns=frozenset({666}),
        override_sav_asns=frozenset({555, 8, 9}),
        BaseSAVPolicyCls=RefinedAlgA,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)
