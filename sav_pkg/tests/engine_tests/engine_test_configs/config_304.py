from frozendict import frozendict
from .as_graph_info_004 import as_graph_info_004

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import EnhancedFeasiblePathuRPF

desc = "EFP uRPF"

config_304 = EngineTestConfig(
    name="config_304",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({2}),
        override_non_default_asn_cls_dict=frozendict(),
        override_sav_asns=frozenset({2}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_004,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)