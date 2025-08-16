from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav import BAR_SAV_PI
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram

from .as_graph_info_000 import as_graph_info_000

desc = "BAR SAV PI"

bar_sav_pi_004 = EngineTestConfig(
    name="bar_sav_pi_004",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_reflectors=11,
        num_attackers=0,
        override_victim_asns=frozenset({777}),
        override_reflector_asns=frozenset({1, 2, 3, 4, 5, 8, 9, 10, 555, 12, 666}),
        override_sav_asns=frozenset({1, 2, 3, 4, 5, 8, 9, 10, 555, 12, 666}),
        BaseSAVPolicyCls=BAR_SAV_PI,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)