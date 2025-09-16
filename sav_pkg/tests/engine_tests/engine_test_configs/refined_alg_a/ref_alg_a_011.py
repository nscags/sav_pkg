from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.policies.sav.refined_alg_a import  RefinedAlgA
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram

from ..as_graph_info.as_graph_info_000 import as_graph_info_000

desc = "ref alg a with 0 reflectors, different SAV ASNs, new attacker/victim"

ref_alg_a_011 = EngineTestConfig( #change name
    name="ref_alg_a_011", #change name
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        num_reflectors=0,
        override_attacker_asns=frozenset({2}),
        override_victim_asns=frozenset({12}),
        override_reflector_asns=frozenset({}),
        override_sav_asns=frozenset({9, 4, 5, 12}),
        BaseSAVPolicyCls=RefinedAlgA,
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