from .ex_configs.as_graph_info_010 import as_graph_info_010

from frozendict import frozendict

from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import LooseuRPF
from sav_pkg.simulation_engine.policies import BGPExport2Some

desc = "False Positive for Loose uRPF with Export-to-Some"

loose_001 = EngineTestConfig(
    name="loose_001",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        num_attackers=0,
        override_victim_asns=frozenset({4}),
        override_reflector_asns=frozenset({6}),
        override_sav_asns=frozenset({6}),
        override_non_default_asn_cls_dict=frozendict({4: BGPExport2Some}),
        BaseSAVPolicyCls=LooseuRPF,
    ),
    as_graph_info=as_graph_info_010,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
