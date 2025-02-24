from .as_graph_info_005 import as_graph_info_005

from frozendict import frozendict

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
from sav_pkg.simulation_engine.policies.sav import EnhancedFeasiblePathuRPFAlgA
from sav_pkg.simulation_engine.policies.bgp import BGPFullExport2SomePrefixSpecific

desc = "Export 2 some passing for EFP Alg A"

config_038 = EngineTestConfig(
    name="config_038",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_non_default_asn_cls_dict=frozendict({5: BGPFullExport2SomePrefixSpecific}),
        num_attackers=0,
        override_victim_asns=frozenset({5}),
        override_reflector_asns=frozenset({4}),
        override_sav_asns=frozenset({4}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
    ),
    as_graph_info=as_graph_info_005,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
