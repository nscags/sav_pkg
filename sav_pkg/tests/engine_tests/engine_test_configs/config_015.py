from frozendict import frozendict

from .as_graph_info_002 import as_graph_info_002

from bgpy.simulation_engine.policies import BGPFull
from bgpy.simulation_engine import Announcement as Ann
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs, Prefixes
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine.policies.bgp.bgpfull_export2some import BGPFullExport2Some  
from sav_pkg.simulation_engine import EnhancedFeasiblePathuRPF


desc = ""

config_015 = EngineTestConfig(
    name="config_015",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_non_default_asn_cls_dict=frozendict({1: BGPFullExport2Some}),
        num_attackers=0,
        num_reflectors=2,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({2, 3}),
        override_sav_asns=frozenset({2, 3}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_002,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
