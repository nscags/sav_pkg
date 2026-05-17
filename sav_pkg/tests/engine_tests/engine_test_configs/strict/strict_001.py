from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagram
from sav_pkg.simulation_engine.policies.sav import StrictuRPF

from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_000


desc = "Basic functionality test. Strict uRPF is applied to both customer and peer interfaces, " \
       "and does not filter provider interfaces"

strict_001 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="strict_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_reflectors=3,
        override_reflector_asns=frozenset({555, 9, 2}),
        override_attacker_asns=frozenset({8}),
        override_victim_asns=frozenset({777}),
        override_sav_asns=frozenset({555, 9, 2}),
        BaseSAVPolicyCls=StrictuRPF,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)