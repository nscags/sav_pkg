from .as_graph_info_000 import as_graph_info_000

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioNoAnnouncements,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.utils.diagram import SAVDiagram
from sav_pkg.policies import RefinedAlgA, ASPAFullExport2Some


desc = "Single reflector running Refined Alg A, ASPAExport2some no ann, testing ASPA functionality"

refined_alg_a_001 = EngineTestConfig(
    name="refined_alg_a_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioNoAnnouncements,
        BasePolicyCls=BGPFull,
        override_non_default_asn_cls_dict=frozendict(
            {ASNs.VICTIM.value: ASPAFullExport2Some, 10: ASPAFullExport2Some}
        ),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value}),
        BaseSAVPolicyCls=RefinedAlgA,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)