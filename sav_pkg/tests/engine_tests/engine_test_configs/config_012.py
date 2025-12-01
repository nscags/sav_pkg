from .as_graph_info_000 import as_graph_info_000

from frozendict import frozendict
# from datetime import date

from bgpy.simulation_engine.policies import BGPFull, ASPAFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav.bar_sav import BAR_SAV
from sav_pkg.policies.aspa import ASPAFullNoExport2Some
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioBATASPA,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import MetricTracker
from sav_pkg.utils.diagram import SAVDiagram


desc = "SAVScenarioBATASPA test"

config_012 = EngineTestConfig(
    name="config_012",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioBATASPA,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV,
        num_reflectors=5,
        reflector_default_adopters=True,
        victim_providers_ann=True,
        override_victim_asns=frozenset({777}),
        override_attacker_asns=frozenset({666}),
        override_sav_asns=frozendict({
            1: BAR_SAV, 
            2: BAR_SAV, 
            3: BAR_SAV, 
            8: BAR_SAV, 
            9: BAR_SAV, 
            12: BAR_SAV, 
            555: BAR_SAV,
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