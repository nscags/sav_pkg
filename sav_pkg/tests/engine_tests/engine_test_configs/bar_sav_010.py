from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

r"""
  2---1
  |   |
  3   |
   \ /
    4
"""

as_graph_info_011 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(2, 1)  
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=4),
            CPLink(provider_asn=1, customer_asn=4),
        ]
    ),
    diagram_ranks=(
        (4,),
        (3,),
        (2, 1),
    )
)


from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram  
from sav_pkg.simulation_engine.policies import RefinedAlgA


desc = "BAR SAV compared to EFP Alg A"

bar_sav_010 = EngineTestConfig(
    name="bar_sav_010",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_victims=0,
        override_attacker_asns=frozenset({4}),
        override_reflector_asns=frozenset({2}),
        override_sav_asns=frozenset({2}),
        BaseSAVPolicyCls=RefinedAlgA, 
    ),
    as_graph_info=as_graph_info_011,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
