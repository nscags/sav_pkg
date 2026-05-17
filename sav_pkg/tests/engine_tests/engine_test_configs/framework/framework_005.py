from bgpy.simulation_engine.policies import BGPFull, ROVFull
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
from sav_pkg.enums import Prefixes
from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_000


desc = "Config test - source_prefix=Prefixes.ATTACKER.value: " \
       "Victim AS should route data packets with a source IP address in 6.6.6.0/24"

framework_005 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="framework_005",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        source_prefix=Prefixes.ATTACKER.value,
        source_prefix_roa=True,
        reflector_default_adopters=True,
        ignore_disconnections=False,
        override_reflector_asns=frozenset({555}),
        override_attacker_asns=frozenset({666}),
        override_victim_asns=frozenset({777}),
        BaseSAVPolicyCls=StrictuRPF,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)