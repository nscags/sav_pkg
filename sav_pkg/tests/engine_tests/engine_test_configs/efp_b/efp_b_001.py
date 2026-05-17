from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine

from sav_pkg.simulation_engine.policies.sav import EFP_B
from sav_pkg.simulation_engine.policies.bgp import BGPFullExport2Some
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram
from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_003


desc = "EFP uRPF Alg B"

efp_b_001 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="efp_b_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        override_victim_asns=frozenset({100}),
        override_reflector_asns=frozenset({555}),
        override_sav_asns=frozenset({555}),
        hardcoded_asn_cls_dict=frozendict(
            {
                100: BGPFullExport2Some,
            }
        ),
        BaseSAVPolicyCls=EFP_B,
    ),
    as_graph_info=as_graph_info_003,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)