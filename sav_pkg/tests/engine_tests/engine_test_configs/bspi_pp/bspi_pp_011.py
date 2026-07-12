from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull, ASPAFull
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
        PeerLink(4, 5),
    }),
    customer_provider_links=frozenset([
        # F=AS2, providers AS5 and AS6
        CPLink(provider_asn=5, customer_asn=2),
        CPLink(provider_asn=6, customer_asn=2),
        # AS4 peers with AS5, AS4 is provider of AS3
        CPLink(provider_asn=4, customer_asn=3),
        # AS6 is provider of AS3 (second path to origin)
        CPLink(provider_asn=6, customer_asn=3),
        # AS3 is provider of AS1 (origin)
        CPLink(provider_asn=3, customer_asn=1),
        # Attacker
        CPLink(provider_asn=6, customer_asn=7),
    ]),
)

bspi_pp_011 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bspi_pp_011",
    desc=(
        "Path ordering matters. AS4 adopts ASPA listing AS5 as provider "
        "(partial peak at AS4 in path via AS5). AS6 adopts ASPA listing "
        "AS2 as provider. Path via AS6: (AS6, AS3, AS1) — case 1 fires, "
        "confirms AS3 provider is AS6, inferred_providers[AS1]={AS3}, "
        "inferred_providers[AS3]={AS6}. Path via AS5: (AS5, AS4, AS3, AS1) "
        "— partial peak at AS4. Left neighbor AS5 is F's direct provider "
        "(known). Right neighbor AS3 — if path 1 processed first, AS3 "
        "already in inferred_providers so right link is resolved as DOWN. "
        "If path 2 processed first, AS3 is ambiguous."
    ),
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV_PI_PP,
        override_attacker_asns=frozenset({7}),
        override_reflector_asns=frozenset({2}),
        override_victim_asns=frozenset({1}),
        override_sav_asns=frozenset({2}),
        hardcoded_asn_cls_dict=frozendict({
            4: ASPAFull,  # lists AS5 as provider — partial peak
            6: ASPAFull,  # lists AS2 as provider — confirms path via AS6
            3: ASPAFull,  # lists AS6 as provider — confirms AS3→AS6 link
        }),
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)