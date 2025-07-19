from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioNoExport2Some,
)
from sav_pkg.policies.sav import BAR_SAV
from sav_pkg.policies.aspa import ASPAFullNoExport2Some
from sav_pkg.utils.diagram import SAVDiagram

from .as_graph_info_001 import as_graph_info_001

desc = "Testing e2s scenario "

config_no_e2s_002 = EngineTestConfig(
    name="config_no_e2s_002",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioNoExport2Some,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV,
        AdoptPolicyCls=ASPAFullNoExport2Some,
        num_attackers=0,
        override_victim_asns=frozenset({4}),
        override_reflector_asns=frozenset({3}),
        override_sav_asns=frozenset({3}),
    ),
    as_graph_info=as_graph_info_001,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)