from frozendict import frozendict
from .as_graph_info_002 import as_graph_info_002  # A graph with customers and Reflector
from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework import SAVASGraphAnalyzer, MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import RFC8704

desc = "RFC8704 - Enhanced Feasible Path Validation for Customers"

config_701 = EngineTestConfig(
    name="config_701",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),  # Reflector enforces SAV
        BaseSAVPolicyCls=RFC8704,
    ),
    as_graph_info=as_graph_info_002,  # Graph with attackers and customers
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)