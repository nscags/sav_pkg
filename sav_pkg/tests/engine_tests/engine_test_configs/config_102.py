from frozendict import frozendict
from .as_graph_info_000 import as_graph_info_000

from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import StrictuRPF
from sav_pkg.simulation_framework import MetricTracker

desc = "Single reflector with stub or multihome providers running StrictuRPF"

config_102 = EngineTestConfig(
    name="config_102",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),
        override_sav_asns=frozenset({1, 2, 4, 10}),
        BaseSAVPolicyCls=StrictuRPF,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=MetricTracker
)