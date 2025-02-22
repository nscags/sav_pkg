from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

r"""
  1    2
   \ /
4   3   5
 \ / \ /
  6   7
"""

as_graph_info_011 = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=6),
            CPLink(provider_asn=4, customer_asn=6),
            CPLink(provider_asn=3, customer_asn=7),
            CPLink(provider_asn=5, customer_asn=7),
        ]
    ),
)


from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer, MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine.policies.bgp import BGPFullExport2SomePrefixSpecific


desc = "Prefix Specific Export-to-Some"

e2s_ps_000 = EngineTestConfig(
    name="e2s_ps_000",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_non_default_asn_cls_dict=frozendict(
            {
                6: BGPFullExport2SomePrefixSpecific,
                7: BGPFullExport2SomePrefixSpecific,
                3: BGPFullExport2SomePrefixSpecific,
            }
        ),
        override_attacker_asns=frozenset({7}),
        override_victim_asns=frozenset({6}),
        override_reflector_asns=frozenset({3}),
    ),
    as_graph_info=as_graph_info_011,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
