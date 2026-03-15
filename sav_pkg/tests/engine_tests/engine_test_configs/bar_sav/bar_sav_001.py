from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram_dsr import SAVDiagram
from sav_pkg.simulation_engine.policies.sav import BAR_SAV
from sav_pkg.simulation_engine.policies.bgp import BGPFullNoExport2Some
from sav_pkg.simulation_engine.policies.aspa import ASPAFullNoExport2Some 


as_graph_info_000 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=6, customer_asn=3),
            CPLink(provider_asn=5, customer_asn=6),
            CPLink(provider_asn=7, customer_asn=2),
            CPLink(provider_asn=4, customer_asn=7),
            CPLink(provider_asn=4, customer_asn=5),
        ]
    ),
)

desc = "False Positive scenario for BAR-SAV w/ ASPA & providers announce, origin and transit AS export-to-some"

bar_sav_001 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bar_sav_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        victim_providers_ann=True,
        override_reflector_asns=frozenset({5}),
        override_victim_asns=frozenset({1}),
        override_sav_asns=frozenset({5}),
        BaseSAVPolicyCls=BAR_SAV,
        hardcoded_asn_cls_dict=frozendict({
            1: ASPAFullNoExport2Some,
            3: BGPFullNoExport2Some,
        })
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)