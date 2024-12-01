from frozendict import frozendict
from bgpy.simulation_engine.policies import BGPFull
from .as_graph_info_007 import as_graph_info_007 
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework import SAVASGraphAnalyzer, MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import RFC8704

config_700 = EngineTestConfig(
    name="config_700",
    desc="Minimal functional test for RFC8704",
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),  
        override_sav_asns=frozenset({1, 2, 3, ASNs.REFLECTOR.value}),  
        BaseSAVPolicyCls=RFC8704,
    ),
    as_graph_info=as_graph_info_007,  # Use the minimal testing graph
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)