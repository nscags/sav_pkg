from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_engine.policies import BeAR_SAV_PI_B
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.utils.diagram import SAVDiagram



as_graph_info = ASGraphInfo(
    # the input clique is assumed known by every AS, even at 0% adoption
    input_clique_asns=frozenset({2, 5}),
    peer_links=frozenset({
        PeerLink(2, 5),
    }),
    customer_provider_links=frozenset([
        # F's two provider interfaces
        CPLink(provider_asn=2, customer_asn=1),
        CPLink(provider_asn=3, customer_asn=1),
        # 3's providers: 2 (inferred, keeps D_f short) and 4 (never inferred)
        CPLink(provider_asn=2, customer_asn=3),
        CPLink(provider_asn=4, customer_asn=3),
        # the descent from the tier 1 down into F that BSPI++ cannot see
        CPLink(provider_asn=5, customer_asn=4),
        # source
        CPLink(provider_asn=5, customer_asn=6),
    ]),
    diagram_ranks=(
        (2, 5),
        (4, 6),
        (3,),
        (1,),
    ),
)

desc = "Same graph as bear_sav_pi_022, under Algorithm B. Still a false positive: \
        \nCase B at the tier 1 AS5 returns a non-empty confirmed set so Case C never \
        \nruns there, and at AS6 Case C has only one branch, so the union in \
        \nAlgorithm B changes nothing."

bear_sav_pi_023 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bear_sav_pi_023",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BeAR_SAV_PI_B,
        num_attackers=0,
        override_reflector_asns=frozenset({1}),
        override_victim_asns=frozenset({6}),
        override_sav_asns=frozenset({1}),
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)
