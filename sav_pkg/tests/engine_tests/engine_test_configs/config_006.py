from .as_graph_info_000 import as_graph_info_000

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
from sav_pkg.policies.bgp.bgp_export2some import BGPExport2Some
from sav_pkg.policies.sav import StrictuRPF


desc = "Single reflector, e2s"

config_006 = EngineTestConfig(
    name="config_006",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({12}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                12: BGPExport2Some,
            }
        ),
        BaseSAVPolicyCls=StrictuRPF,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)