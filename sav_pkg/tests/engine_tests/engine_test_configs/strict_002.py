from frozendict import frozendict

from .ex_configs.as_graph_info_002 import as_graph_info_002

from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine.policies.bgp.bgp_export2some import BGPExport2Some  
from sav_pkg.simulation_engine.policies import StrictuRPF

desc = "Simple scenario with Export-to-Some and reflectors deploying Strict uRPF"

strict_002 = EngineTestConfig(
    name="strict_002",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        override_non_default_asn_cls_dict=frozendict({1: BGPExport2Some}),
        num_attackers=0,
        num_reflectors=2,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({2, 3}),
        override_sav_asns=frozenset({2, 3}),
        BaseSAVPolicyCls=StrictuRPF, 
    ),
    as_graph_info=as_graph_info_002,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
