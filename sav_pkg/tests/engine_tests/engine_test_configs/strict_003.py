from frozendict import frozendict

from .ex_configs.as_graph_info_006 import as_graph_info_006

from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs, Interfaces
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import StrictuRPF

desc = "Strict uRPF deployed on all interfaces"

strict_003 = EngineTestConfig(
    name="strict_003",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        num_reflectors=3,
        override_reflector_asns=frozenset({1, 9, 10}),
        override_sav_asns=frozenset({1, 9, 10}),
        BaseSAVPolicyCls=StrictuRPF,
        override_default_interface_dict=frozendict(
            {StrictuRPF.name: frozenset([
                Interfaces.CUSTOMER.value, 
                Interfaces.PEER.value, 
                Interfaces.PROVIDER.value
            ])}
        )
    ),
    as_graph_info=as_graph_info_006,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
