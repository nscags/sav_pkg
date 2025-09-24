from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav import BAR_SAV_PI
from sav_pkg.policies.bgp import BGPExport2Some
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioExport2Some,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram

from .as_graph_info_011 import as_graph_info_011

desc = "BAR SAV PI with e2s (path prepending)"

bar_sav_pi_003 = EngineTestConfig(
    name="bar_sav_pi_003",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioExport2Some,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        override_victim_asns=frozenset({17}),
        override_reflector_asns=frozenset({3}),
        override_sav_asns=frozenset({3}),
        BaseSAVPolicyCls=BAR_SAV_PI,
        hardcoded_asn_cls_dict=frozendict(
            {17: BGPExport2Some}
        )
    ),
    as_graph_info=as_graph_info_011,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)