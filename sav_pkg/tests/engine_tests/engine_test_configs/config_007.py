from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink


as_graph_info_000 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=2, customer_asn=3),
        ]
    ),
)


from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagram
from sav_pkg.policies.sav import BAR_SAV
from sav_pkg.policies.bgp import BGPFullNoExport2Some
from sav_pkg.policies.aspa import ASPAFullNoExport2Some 


desc = "False Positive scenario for BAR-SAV w/ ASPA & providers announce, origin and transit AS export-to-some"

config_006 = EngineTestConfig(
    name="config_006",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        victim_providers_ann=True,
        override_reflector_asns=frozenset({3}),
        override_victim_asns=frozenset({1}),
        override_sav_asns=frozenset({3}),
        BaseSAVPolicyCls=BAR_SAV,
        hardcoded_asn_cls_dict=frozendict({
            1: BGPFullNoExport2Some,
        })
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)