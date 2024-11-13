from frozendict import frozendict
from .as_graph_info_001 import as_graph_info_001

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import FeasiblePathuRPF

desc = "Feasible Path uRPF on Asymmetric Route"

config_202 = EngineTestConfig(
    name="config_202",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),
        override_sav_asns=frozenset({ASNs.REFLECTOR.value, 2}),
        BaseSAVPolicyCls=FeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_001,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)