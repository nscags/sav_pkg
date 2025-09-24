from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagram
from sav_pkg.policies.sav import BAR_SAV_Full

from .as_graph_info_000 import as_graph_info_000


desc = "testing bar-sav pi"

bar_sav_pi_006 = EngineTestConfig(
    name="bar_sav_pi_006",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_reflector_asns=frozenset({1}),
        override_attacker_asns=frozenset({666}),
        override_victim_asns=frozenset({777}),
        override_sav_asns=frozenset({1}),
        BaseSAVPolicyCls=BAR_SAV_Full,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)