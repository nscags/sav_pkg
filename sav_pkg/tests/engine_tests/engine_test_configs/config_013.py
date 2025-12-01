from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink


as_graph_info_000 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(5, 6),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=6, customer_asn=2),
            CPLink(provider_asn=4, customer_asn=3),
            CPLink(provider_asn=8, customer_asn=6),
            # CPLink(provider_asn=8, customer_asn=7),
            CPLink(provider_asn=8, customer_asn=9),
            CPLink(provider_asn=5, customer_asn=4),
            CPLink(provider_asn=9, customer_asn=4),
        ]
    ),
)

from frozendict import frozendict
# from datetime import date

from bgpy.simulation_engine.policies import BGPFull, ASPAFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.policies.sav.bar_sav import BAR_SAV
from sav_pkg.policies.aspa import ASPAFullNoExport2Some
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import MetricTracker
from sav_pkg.utils.diagram import SAVDiagram


desc = "BAR-SAV false positive test"

config_013 = EngineTestConfig(
    name="config_013",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV,
        num_attackers=0,
        reflector_default_adopters=True,
        override_victim_asns=frozenset({1}),
        override_reflector_asns=frozenset({9}),
        hardcoded_asn_cls_dict=frozendict({
            4: ASPAFullNoExport2Some,
        })
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)