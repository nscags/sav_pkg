from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.policies.sav.feasible_path_urpf import FeasiblePathuRPF
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram

from ..as_graph_info.as_graph_info_000 import as_graph_info_000

desc = "feasible  with 3 reflectors, different SAV ASNs, new attacker/victim"

feasible_014 = EngineTestConfig( #change name
    name="feasible_014", #change name
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        num_reflectors=3,
        override_attacker_asns=frozenset({8}),
        override_victim_asns=frozenset({9}),
        override_reflector_asns=frozenset({1,3,8}),
        override_sav_asns=frozenset({4, 5, 12}),
        BaseSAVPolicyCls=FeasiblePathuRPF, #change
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