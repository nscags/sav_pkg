from .as_graph_info_003 import as_graph_info_003

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioExport2Some,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.utils.diagram import SAVDiagram
from sav_pkg.policies.bgp.bgp_export2some import BGPExport2Some

desc = "Testing that e2s scenario randomly samples from hardcoded_asn_cls_dict"

"""
  "100": {
    "4193": 0.0,
    "10580": 0.16666666666666666,
    "16158": 0.16666666666666666,
    "46197": 0.16666666666666666,
    "46301": 0.16666666666666666,
    "329381": 0.16666666666666666,
    "395727": 0.16666666666666666
  },

    "100": {
        "4193": [],
        "10580": [
            true
        ],
        "16158": [
            false
        ],
        "46197": [
            false
        ],
        "46301": [
            false
        ],
        "329381": [
            false
        ],
        "395727": [
            false
        ]
    },
"""

config_010 = EngineTestConfig(
    name="config_010",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioExport2Some,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        hardcoded_asn_cls_dict=frozendict(
            {100: BGPExport2Some}
        )
    ),
    as_graph_info=as_graph_info_003,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)