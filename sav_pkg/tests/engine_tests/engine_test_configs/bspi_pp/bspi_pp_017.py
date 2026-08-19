from bgpy.simulation_engine.policies import ASRAFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_engine.policies import BAR_SAV_PI_PP
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.utils.diagram import SAVDiagram



as_graph_info = ASGraphInfo(
    peer_links=frozenset({
        PeerLink(2, 4),
        PeerLink(5, 6),
    }),
    customer_provider_links=frozenset([
        CPLink(provider_asn=2, customer_asn=1),
        CPLink(provider_asn=3, customer_asn=1),
        CPLink(provider_asn=6, customer_asn=3),
        CPLink(provider_asn=4, customer_asn=7),
        CPLink(provider_asn=5, customer_asn=7),
        CPLink(provider_asn=1, customer_asn=8),
        CPLink(provider_asn=9, customer_asn=8),
        CPLink(provider_asn=10, customer_asn=9),
        CPLink(provider_asn=11, customer_asn=10),
        CPLink(provider_asn=12, customer_asn=11),
        CPLink(provider_asn=4, customer_asn=12),
    ]),
    diagram_ranks=(
        (4, 5, 6, 2),
        (12, 7, 3),
        (11, 1),
        (10,),
        (9,),
        (8,),
    ),
)

desc = "False positive test: Case C keeps only the min-distance branch (no peer link at the source)"

bspi_pp_017 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bspi_pp_017",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=ASRAFull,
        BaseSAVPolicyCls=BAR_SAV_PI_PP,
        num_attackers=0,
        override_reflector_asns=frozenset({8}),
        override_victim_asns=frozenset({7}),
        override_sav_asns=frozenset({1}),
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)
