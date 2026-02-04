from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagram
from sav_pkg.policies.sav import EFP_A

from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_000


desc = "Basic functionality test. EFP-A deployed on multiple reflectors, " \
       "includes disconnected reflectors for both attacker and legitimate origin."

efp_a_000 = EngineTestConfig(
    name="efp_a_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_reflectors=3,
        override_reflector_asns=frozenset({555, 5, 12}),
        override_attacker_asns=frozenset({666}),
        override_victim_asns=frozenset({777}),
        override_sav_asns=frozenset({555, 1, 12}),
        BaseSAVPolicyCls=EFP_A,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)