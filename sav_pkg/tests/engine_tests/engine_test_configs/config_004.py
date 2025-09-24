from .as_graph_info_002 import as_graph_info_002

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav import FeasiblePathuRPF
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import MetricTracker
from sav_pkg.utils.diagram import SAVDiagram
from sav_pkg.enums import Interfaces

desc = "False positive test for Feasible Path uRPF with Export-to-All"

config_004 = EngineTestConfig(
    name="config_004",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        num_reflectors=1,
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({5}),
        override_sav_asns=frozenset({5}),
        BaseSAVPolicyCls=FeasiblePathuRPF,
        override_default_interface_dict=frozendict({
            FeasiblePathuRPF.name: frozenset([
                    Interfaces.CUSTOMER.value,
                    Interfaces.PEER.value,
            ])
        })
    ),
    as_graph_info=as_graph_info_002,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)