from .as_graph_info_004 import as_graph_info_004

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.utils.diagram import SAVDiagram
from sav_pkg.policies.bgp import BGPExport2SomeSuperSubPrefix, BGPExport2Some
from sav_pkg.policies.sav import StrictuRPF

desc = "Single reflector, e2s"

"""
e2s weights
"17": {
    "6461": 0.25,
    "19782": 1.0
},

path prepending 
"17": {
    "6461": [
        true
    ],
    "19782": [
        false
    ]
},
"""

strict_001 = EngineTestConfig(
    name="strict_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        BaseSAVPolicyCls=StrictuRPF,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({17}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                17: BGPExport2SomeSuperSubPrefix,
                ASNs.ATTACKER.value: BGPExport2Some,
            }
        )
    ),
    as_graph_info=as_graph_info_004,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)