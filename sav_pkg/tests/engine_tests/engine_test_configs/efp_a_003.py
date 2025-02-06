from frozendict import frozendict

from .ex_configs.as_graph_info_002 import as_graph_info_002

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine.policies.bgp import BGPFullExport2Some  
from sav_pkg.simulation_engine.policies import EnhancedFeasiblePathuRPFAlgA


desc = "Basic Export to Some"

efp_a_003 = EngineTestConfig(
    name="efp_a_003",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_non_default_asn_cls_dict=frozendict({1: BGPFullExport2Some}),
        num_attackers=0,
        num_reflectors=2,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({2, 3}),
        override_sav_asns=frozenset({2, 3}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA, 
    ),
    as_graph_info=as_graph_info_002,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
