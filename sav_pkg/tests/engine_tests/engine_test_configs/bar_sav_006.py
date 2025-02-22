from .ex_configs.as_graph_info_009 import as_graph_info_009

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioROA,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import BAR_SAV, BGPFullExport2SomePrefixSpecific


desc = "BAR SAV False Positive Test with ROA (Expecting True Negative)"

bar_sav_006 = EngineTestConfig(
    name="bar_sav_006",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioROA,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({4}),
        override_reflector_asns=frozenset({6}),
        override_sav_asns=frozenset({6}),
        override_non_default_asn_cls_dict=frozendict({4:BGPFullExport2SomePrefixSpecific}),
        BaseSAVPolicyCls=BAR_SAV,
    ),
    as_graph_info=as_graph_info_009,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
