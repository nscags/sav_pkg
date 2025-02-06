from .ex_configs.as_graph_info_001 import as_graph_info_001

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.enums import Interfaces
from sav_pkg.simulation_engine import FeasiblePathuRPF

desc = "False positive test for Feasible Path uRPF with Export-to-All"

fp_004 = EngineTestConfig(
    name="fp_004",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        num_reflectors=1,
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({3}),
        override_sav_asns=frozenset({3}),
        BaseSAVPolicyCls=FeasiblePathuRPF,
        override_default_interface_dict=frozendict(
            {FeasiblePathuRPF.name: frozenset([
                Interfaces.CUSTOMER.value, 
                Interfaces.PEER.value, 
                Interfaces.PROVIDER.value
            ])}
        )
    ),
    as_graph_info=as_graph_info_001,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
