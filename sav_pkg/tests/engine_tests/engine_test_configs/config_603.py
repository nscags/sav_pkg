from frozendict import frozendict
from .as_graph_info_002 import as_graph_info_002
from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import FeasiblePathuRPFOnlyCustomers

desc = "Reflector with only peer connections for FeasiblePathuRPFOnlyCustomers"

config_603 = EngineTestConfig(
    name="config_603",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        BaseSAVPolicyCls=FeasiblePathuRPFOnlyCustomers,
    ),
    as_graph_info=as_graph_info_002,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
)