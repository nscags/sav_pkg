from .bar_sav_010 import as_graph_info_011

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine.policies import EnhancedFeasiblePathuRPFAlgA


desc = "BAR SAV compared to EFP Alg A"

efp_a_004 = EngineTestConfig(
    name="efp_a_004",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_victims=0,
        override_attacker_asns=frozenset({4}),
        override_reflector_asns=frozenset({2}),
        override_sav_asns=frozenset({2}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA, 
    ),
    as_graph_info=as_graph_info_011,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
