from bgpy.simulation_engine.policies import BGP
from bgpy.tests.engine_tests import EngineTestConfig

from sav_pkg.enums import ASNs
from sav_pkg.policies.sav.loose_urpf import LooseuRPF
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import (
    SAVScenario,
    SAVScenarioConfig,
)
from sav_pkg.utils.diagram import SAVDiagram

from ..as_graph_info.as_graph_info_000 import as_graph_info_000

desc = "Loose uRPF with 2 reflectors, different SAV ASNs, new attacker/victim"

loose_019 = EngineTestConfig( #change name
    name="loose_019", #change name
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        num_reflectors=2,
        override_attacker_asns=frozenset({9}),
        override_victim_asns=frozenset({8}),
        override_reflector_asns=frozenset({12,10}),
        override_sav_asns=frozenset({9, 4, 5, 12}),
        BaseSAVPolicyCls=LooseuRPF,
    ),
    as_graph_info=as_graph_info_000,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    MetricTrackerCls=SAVMetricTracker,
)

# nodes:
# (1, 2, 3, 4)
# (5, 8, 9, 10)
# (12)