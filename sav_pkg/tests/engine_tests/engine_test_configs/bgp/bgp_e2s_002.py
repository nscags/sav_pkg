from frozendict import frozendict

from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.enums import ASNs
from sav_pkg.simulation_engine.policies import BGPExport2Some
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.utils.diagram import SAVDiagram


"""
Export ratio
"1050": {
    "34927": 1.0,
    "47272": 1.0,
    "53667": 0.5,
    "399646": 0.5
},

Superprefix
"1050": {
    "34927": 0.0,
    "47272": 0.0,
    "53667": 0.0,
    "399646": 0.0
},
"""

as_graph_info = ASGraphInfo(
    customer_provider_links=frozenset(
        [

            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=53667, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=53667, customer_asn=1050),
            CPLink(provider_asn=399646, customer_asn=1050),
            CPLink(provider_asn=34927, customer_asn=1050),
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=53667),
            CPLink(provider_asn=9, customer_asn=399646),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=8),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
        ]
    ),
)

desc = "Testing BGPExport2Some with real data. " \
       "Export-to-some"

bgp_e2s_002 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bgp_e2s_002",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_victim_asns=frozenset({1050}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        hardcoded_asn_cls_dict=frozendict(
            {1050: BGPExport2Some}
        )
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)