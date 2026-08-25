from frozendict import frozendict

from bgpy.simulation_engine.policies import ASRAFull, BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_engine.policies import BAR_SAV_PI_PP_Alg_A
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioDSRConfig, SAVScenarioDSR
from sav_pkg.utils.diagram_dsr import SAVDiagramDSR
from sav_pkg.enums import Prefixes



as_graph_info = ASGraphInfo(
    peer_links=frozenset({
        PeerLink(11, 12),
    }),
    customer_provider_links=frozenset([
        CPLink(provider_asn=5,  customer_asn=2),
        CPLink(provider_asn=7,  customer_asn=5),
        CPLink(provider_asn=11, customer_asn=7),
        CPLink(provider_asn=12, customer_asn=8),
        CPLink(provider_asn=8,  customer_asn=6),
        CPLink(provider_asn=6,  customer_asn=2),
        CPLink(provider_asn=12,  customer_asn=13),
        CPLink(provider_asn=13,  customer_asn=1),
        CPLink(provider_asn=11,  customer_asn=14),
        CPLink(provider_asn=14,  customer_asn=3),
    ]),
)

desc = "Path inference: only AS11 (bilateral peer of AS12) adopts ASRA." 

bspi_pp_006 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bspi_pp_006",
    desc=desc,
    scenario_config=SAVScenarioDSRConfig(
        ScenarioCls=SAVScenarioDSR,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_A,
        override_edge_server_asns=frozenset({3}),
        override_user_asns=frozenset({2}),
        override_anycast_server_asns=frozenset({1}),
        override_sav_asns=frozenset({2}),
        hardcoded_asn_cls_dict=frozendict({
            12: ASRAFull,
        }),
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagramDSR,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)