from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull, ASPAFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_engine.policies import BAR_SAV_PI_PP_Alg_A
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.utils.diagram import SAVDiagram



as_graph_info = ASGraphInfo(
    peer_links=frozenset({
        PeerLink(3, 4),
    }),
    customer_provider_links=frozenset([
        CPLink(provider_asn=2, customer_asn=1),
        CPLink(provider_asn=6, customer_asn=1),
        CPLink(provider_asn=2, customer_asn=6),
        CPLink(provider_asn=5, customer_asn=6),
        CPLink(provider_asn=4, customer_asn=5),
        CPLink(provider_asn=2, customer_asn=3),
    ]),
)

desc = "False postiive test" 

bspi_pp_013 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bspi_pp_013",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=ASPAFull,
        BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_A,
        num_attackers=0,
        override_reflector_asns=frozenset({1}),
        override_victim_asns=frozenset({3}),
        override_sav_asns=frozenset({1}),
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)