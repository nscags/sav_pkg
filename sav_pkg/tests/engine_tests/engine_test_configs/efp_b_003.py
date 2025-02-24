from .e2s_ps_000 import as_graph_info_011

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_engine.policies import EnhancedFeasiblePathuRPFAlgB
from sav_pkg.simulation_framework import SAVASGraphAnalyzer, MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.enums import Interfaces

desc = "EFP Alg B Provider Interfaces Only"

efp_b_003 = EngineTestConfig(
    name="efp_b_003",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=2,
        num_victims=0,
        override_attacker_asns=frozenset({1, 7}),
        override_victim_asns=frozenset(),
        override_reflector_asns=frozenset({3}),
        override_sav_asns=frozenset({3}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB, 
        override_default_interface_dict=frozendict(
            {EnhancedFeasiblePathuRPFAlgB.name: frozenset([
                Interfaces.PROVIDER.value
            ])}
        ),
    ),
    as_graph_info=as_graph_info_011,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)