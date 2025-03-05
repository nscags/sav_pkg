from .ex_configs.as_graph_info_000 import as_graph_info_000

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull, ASPAFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioNoAnnouncements,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import RefinedAlgA

desc = "Single reflector running BAR SAV, victim does not announce prefix"

bar_sav_001 = EngineTestConfig(
    name="bar_sav_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioNoAnnouncements,
        BasePolicyCls=BGPFull,
        override_non_default_asn_cls_dict=frozendict(
            {ASNs.VICTIM.value: ASPAFull, 10: ASPAFull}
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
    MetricTrackerCls=MetricTracker,
)
