from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioDSR,
    SAVScenarioDSRConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagramDSR
from sav_pkg.enums import Prefixes
from sav_pkg.simulation_engine.policies.sav import BAR_SAV
from sav_pkg.simulation_engine.policies.bgp import BGPFullNoExport2Some
from sav_pkg.tests.engine_tests.engine_test_configs.as_graph_info import as_graph_info_012


desc = "Testing how disconnections are handled with ignore_disconnections=False. " \
       "User will not receive announcement from edge server, should apply disconnected"

dsr_005 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="dsr_005",
    desc=desc,
    scenario_config=SAVScenarioDSRConfig(
        ScenarioCls=SAVScenarioDSR,
        BasePolicyCls=BGPFull,
        override_user_asns=frozenset({4}),
        override_edge_server_asns=frozenset({1}),
        override_anycast_server_asns=frozenset({5}),
        override_sav_asns=frozenset({4}),
        BaseSAVPolicyCls=BAR_SAV,
        hardcoded_asn_cls_dict=frozendict({
            1: BGPFullNoExport2Some,
        })
    ),
    as_graph_info=as_graph_info_012,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)