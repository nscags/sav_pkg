from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

as_graph_info_000 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=5, customer_asn=3),
            CPLink(provider_asn=5, customer_asn=4),
        ]
    ),
)

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


desc = "BAR-SAV 000 - Basic functionality test"

bar_sav_000 = EngineTestConfig(
    name="bar_sav_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_reflector_asns=frozenset({5}),
        override_attacker_asns=frozenset({1}),
        override_victim_asns=frozenset({2}),
        override_sav_asns=frozenset({5}),
        BaseSAVPolicyCls=BAR_SAV,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)