from .ex_configs.as_graph_info_000 import as_graph_info_000

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import EnhancedFeasiblePathuRPFAlgAwPeers

desc = "Three reflectors running EFP uRPF Alg A with Peers, one disconnected from both victim and attacker"

efp_a_w_peers_000 = EngineTestConfig(
    name="efp_a_w_peers_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        num_reflectors=3,
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value, 5, 12}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value, 5, 12}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwPeers,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
