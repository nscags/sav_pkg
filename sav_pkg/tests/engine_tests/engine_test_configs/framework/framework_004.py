from bgpy.simulation_engine.policies import BGPFull, ROVFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagram
from sav_pkg.policies.sav import StrictuRPF

from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_000


desc = "Config test - victim_default_adopters=True: " \
       "Victim AS should adopt ROV"

framework_004 = EngineTestConfig(
    name="framework_004",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        AdoptPolicyCls=ROVFull,
        victim_default_adopters=True,
        override_reflector_asns=frozenset({555}),
        override_attacker_asns=frozenset({666}),
        override_victim_asns=frozenset({777}),
        BaseSAVPolicyCls=StrictuRPF,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)