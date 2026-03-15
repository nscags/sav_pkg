from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_001

from frozendict import frozendict
# from datetime import date

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine

from sav_pkg.simulation_engine.policies.sav.bar_sav import BAR_SAV
from sav_pkg.simulation_engine.policies.aspa import ASPAFullNoExport2Some
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import MetricTracker
from sav_pkg.utils.diagram import SAVDiagram


desc = "ASPAFullNoExport2Some test"

aspa_000 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="aspa_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV,
        num_attackers=0,
        override_victim_asns=frozenset({4}),
        override_reflector_asns=frozenset({3}),
        override_sav_asns=frozenset({3}),
        override_non_default_asn_cls_dict=frozendict({
            4: ASPAFullNoExport2Some,
        }),
    ),
    as_graph_info=as_graph_info_001,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)