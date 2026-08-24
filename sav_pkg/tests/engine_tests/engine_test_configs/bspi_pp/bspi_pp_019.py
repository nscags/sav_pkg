from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull, ASRAFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_engine.policies import BAR_SAV_PI_PP
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.utils.diagram import SAVDiagram



as_graph_info = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset([
        CPLink(provider_asn=2, customer_asn=1),
        CPLink(provider_asn=3, customer_asn=1),
        CPLink(provider_asn=6, customer_asn=2),
        CPLink(provider_asn=4, customer_asn=6),
        CPLink(provider_asn=3, customer_asn=4),
        CPLink(provider_asn=3, customer_asn=5),
        CPLink(provider_asn=4, customer_asn=7),
        CPLink(provider_asn=5, customer_asn=7),
    ]),
    diagram_ranks=(
        (3,),
        (4, 5),
        (6, 7),
        (2,),
        (1,),
    ),
)

desc = "Same as config 18 but the providers of the source announce their own prefixes. \
        This is not enough as the validator still does not see the connection from the \
        source its provider."

bspi_pp_019 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bspi_pp_019",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV_PI_PP,
        num_attackers=0,
        victim_providers_ann=True,
        override_reflector_asns=frozenset({1}),
        override_victim_asns=frozenset({7}),
        override_sav_asns=frozenset({1}),
        hardcoded_asn_cls_dict=frozendict({
            4: ASRAFull,
            6: ASRAFull,
        }),
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)
