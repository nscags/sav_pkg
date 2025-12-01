from .as_graph_info_000 import as_graph_info_000

from frozendict import frozendict
# from datetime import date

from bgpy.simulation_engine.policies import BGPFull, ASPAFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav.bar_sav import BAR_SAV
from sav_pkg.policies.aspa import ASPAFullNoExport2Some
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioBATAnn,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import MetricTracker
from sav_pkg.utils.diagram import SAVDiagram


desc = "SAVScenarioBATAnn test"

config_010 = EngineTestConfig(
    name="config_010",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioBATAnn,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV,
        reflector_default_adopters=True,
        victim_providers_ann=True,
        override_victim_asns=frozenset({777}),
        override_attacker_asns=frozenset({666}),
        override_reflector_asns=frozenset({555}),
        override_non_default_asn_cls_dict=frozendict({
            1: ASPAFullNoExport2Some,
            10: ASPAFullNoExport2Some,
        }),
        hardcoded_asn_cls_dict=frozendict({
            777: ASPAFullNoExport2Some,
        })
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)