# from bgpy.simulation_engine.policies import BGP
# from bgpy.tests.engine_tests import EngineTestConfig
#
# from sav_pkg.enums import ASNs
# from sav_pkg.policies.sav import LooseuRPF
# from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
# from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
# from sav_pkg.simulation_framework.scenarios import (
#     SAVScenario,
#     SAVScenarioConfig,
# )
# from sav_pkg.utils.diagram import SAVDiagram
# from .as_graph_info_006 import as_graph_info_006 ##choose as my wish
#
# desc = "Loose uRPF with three reflectors, different SAV ASNs, new attacker/victim"
#
#  ## use in graph_006 = (1, 21976, 3, 46887), 205,12  (5, 8, 9, 10)
# test_028 = EngineTestConfig( #change name
#     name="test_028", #change name
#     desc=desc,
#     scenario_config=SAVScenarioConfig(
#         ScenarioCls=SAVScenario,
#         BasePolicyCls=BGP,
#         num_reflectors=4,
#         override_attacker_asns=frozenset({10}),
#         override_victim_asns=frozenset({1}),
#         override_reflector_asns=frozenset({9, 46887, 5,12}),
#         override_sav_asns=frozenset({9, 8, 5, 12}),
#         BaseSAVPolicyCls=LooseuRPF,
#     ),
#     as_graph_info=as_graph_info_006,
#     DiagramCls=SAVDiagram,
#     ASGraphAnalyzerCls=SAVASGraphAnalyzer,
#     MetricTrackerCls=SAVMetricTracker,
# )
