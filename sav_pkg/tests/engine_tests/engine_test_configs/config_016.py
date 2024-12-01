from frozendict import frozendict

from .as_graph_info_003 import as_graph_info_003

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
from sav_pkg.simulation_engine import FeasiblePathuRPF


desc = ""

config_016 = EngineTestConfig(
    name="config_016",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_non_default_asn_cls_dict=frozendict({1: BGPFullExport2Some}),
        num_attackers=0,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({4}),
        override_sav_asns=frozenset({4}),
        BaseSAVPolicyCls=FeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_003,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
