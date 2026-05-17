from frozendict import frozendict
# from datetime import date

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from sav_pkg.simulation_engine.policies.sav.bar_sav import BAR_SAV
from sav_pkg.simulation_engine.policies.aspa import ASPAFullNoExport2Some
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.utils.diagram import SAVDiagram


as_graph_info_000 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=777),
            CPLink(provider_asn=2, customer_asn=777),
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=3),
            CPLink(provider_asn=8, customer_asn=5),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=5, customer_asn=4),
            CPLink(provider_asn=6, customer_asn=4),
            CPLink(provider_asn=7, customer_asn=6),
            CPLink(provider_asn=8, customer_asn=7),
        ]
    ),
)

desc = "BAR-SAV false positive test"

bar_sav_003 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bar_sav_003",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        BaseSAVPolicyCls=BAR_SAV,
        num_attackers=0,
        reflector_default_adopters=True,
        override_victim_asns=frozenset({777}),
        override_reflector_asns=frozenset({7}),
        hardcoded_asn_cls_dict=frozendict({
            777: ASPAFullNoExport2Some,
            2: ASPAFullNoExport2Some,
        })
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)