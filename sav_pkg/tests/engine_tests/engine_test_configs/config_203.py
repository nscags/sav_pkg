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

desc = "Limited SAV enforcement running Feasible-Path uRPF: AS 8,10"

config_203 = EngineTestConfig(
    name="config_203",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),
        override_sav_asns=frozenset({8, 10}),  # Only AS 8 and 10 enforce SAV
        BaseSAVPolicyCls=FeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_000,  
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer
)