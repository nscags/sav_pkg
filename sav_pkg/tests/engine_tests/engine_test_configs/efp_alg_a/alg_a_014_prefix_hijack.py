from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav.efp_urpf_alg_a import EnhancedFeasiblePathuRPFAlgA
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenario
from sav_pkg.simulation_framework.scenarios.sav_scenario_config2 import (
    SAVScenarioConfig2,
)
from sav_pkg.utils.diagram import SAVDiagram

from ..as_graph_info.as_graph_info_000 import as_graph_info_000

desc = "alg a with 1 reflector, prefix hijack, new attacker/victim"

alg_a_013_prefix_hijack = EngineTestConfig(
    name="alg_a_014_prefix_hijack",
    desc=desc,
    scenario_config=SAVScenarioConfig2(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        num_reflectors=1,
        source_prefix="7.7.7.0/24",
        attacker_prefix="7.7.7.0/24",
        override_attacker_asns=frozenset({12}),
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({1}),
        override_sav_asns=frozenset({9, 4, 5, 12}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)

# nodes:
# (1, 2, 3, 4)
# (5, 8, 9, 10)
# (12)