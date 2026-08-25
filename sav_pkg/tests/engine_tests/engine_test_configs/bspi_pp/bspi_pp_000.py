# from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_engine.policies import BAR_SAV_PI_PP_Alg_A
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.utils.diagram import SAVDiagram


as_graph_info = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(8, 9),
            PeerLink(5, 6),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=6, customer_asn=2),
            CPLink(provider_asn=6, customer_asn=3),
            CPLink(provider_asn=7, customer_asn=4),
            CPLink(provider_asn=8, customer_asn=5),
            CPLink(provider_asn=8, customer_asn=6),
            CPLink(provider_asn=9, customer_asn=7),
        ]
    ),
)

desc = "BAR-SAV-PI++ test"

bspi_pp_000 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bspi_pp_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_A,
        override_attacker_asns=frozenset({3,}),
        override_reflector_asns=frozenset({2,}),
        override_victim_asns=frozenset({1,}),
        override_sav_asns=frozenset({2,}),
        # hardcoded_asn_cls_dict=frozendict(
            # {}
        # )
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)