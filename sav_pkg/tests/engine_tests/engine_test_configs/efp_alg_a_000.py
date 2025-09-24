from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav import EnhancedFeasiblePathuRPFAlgA
from sav_pkg.policies.bgp import BGPFullExport2Some
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram

from .as_graph_info_003 import as_graph_info_003

desc = "EFP uRPF Alg A"

efp_alg_a_000 = EngineTestConfig(
    name="efp_alg_a_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        override_victim_asns=frozenset({100}),
        override_reflector_asns=frozenset({555}),
        override_sav_asns=frozenset({555}),
        override_non_default_asn_cls_dict=frozendict(
            {
                100: BGPFullExport2Some,
            }
        ),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
    ),
    as_graph_info=as_graph_info_003,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)