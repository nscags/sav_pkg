from frozendict import frozendict
from .as_graph_info_003 import as_graph_info_003

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import StrictuRPF

desc = "Double reflector running StrictuRPF"

config_3103 = EngineTestConfig(
    name="config_3103",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=2,
        num_victims=2,
        num_reflectors=2,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value, 3}),
        override_victim_asns=frozenset({ASNs.VICTIM.value,4}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value,12}),
        override_non_default_asn_cls_dict=frozendict(),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        BaseSAVPolicyCls=StrictuRPF,
    ),
    as_graph_info=as_graph_info_003,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer
)
