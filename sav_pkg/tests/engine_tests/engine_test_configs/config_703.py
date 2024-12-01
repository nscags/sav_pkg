from frozendict import frozendict
from .as_graph_info_007 import as_graph_info_007  # A complex graph with mixed interfaces
from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework import SAVASGraphAnalyzer, MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import RFC8704

# Description of the test scenario
desc = "RFC8704 - Mixed Validation Across Interfaces"

# Test configuration
config_703 = EngineTestConfig(
    name="config_703",  # Unique identifier for this test configuration
    desc=desc,  # Test description for debugging/logging
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,  # Scenario class for SAV testing
        BasePolicyCls=BGPFull,  # Base routing policy for ASes
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),  # Attackers in the scenario
        override_victim_asns=frozenset({ASNs.VICTIM.value}),  # Victim ASes
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),  # Reflectors
        override_non_default_asn_cls_dict=frozendict(),  # No non-default AS configurations
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),  # Reflectors enforce SAV
        BaseSAVPolicyCls=RFC8704,  # Use RFC8704-compliant SAV policy
    ),
    as_graph_info=as_graph_info_007,  # Graph file defining mixed interfaces (stub, customer, peers)
    DiagramCls=SAVDiagram,  # Class to generate diagrams for the SAV simulation
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,  # Analyzer for the AS graph
    MetricTrackerCls=MetricTracker,  # Tracks performance metrics during the simulation
)