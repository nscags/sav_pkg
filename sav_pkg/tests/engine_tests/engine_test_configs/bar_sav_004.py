from .ex_configs.as_graph_info_004 import as_graph_info_004

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.simulation_framework import MetricTracker
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import RefinedAlgA


desc = "bar sav default not on provider interfaces"

bar_sav_004 = EngineTestConfig(
    name="bar_sav_004",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({1}),
        override_victim_asns=frozenset({2}),
        override_reflector_asns=frozenset({5}),
        override_sav_asns=frozenset({5}),
        BaseSAVPolicyCls=RefinedAlgA,
    ),
    as_graph_info=as_graph_info_004,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker,
)
