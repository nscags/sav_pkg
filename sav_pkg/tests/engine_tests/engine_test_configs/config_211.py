from frozendict import frozendict
from .as_graph_info_000 import as_graph_info_000

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import FeasiblePathuRPF

desc = "Dual reflector running Feasible-Path uRPF: reflectors: 555, 12 | Attacker: 666, 1"

config_211 = EngineTestConfig(
    name="config_211",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_reflectors=2,
        num_attackers=2,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value, 1}),
        override_victim_asns=frozenset({4}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value, 12}),  # Added second reflector
        override_non_default_asn_cls_dict=frozendict(),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value, 12}),  # Reflectors
        BaseSAVPolicyCls=FeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_000,  # Use original graph info with two reflectors
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer
)