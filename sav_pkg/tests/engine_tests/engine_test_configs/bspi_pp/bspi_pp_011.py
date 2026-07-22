from frozendict import frozendict

from bgpy.simulation_engine.policies import BGPFull, ASPAFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_engine.policies import BAR_SAV_PI_PP
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.utils.diagram import SAVDiagram


# Rebuilt verbatim from the real ASPAFull trace: F=46887, source=39745,
# prev_hop=1299, ground_truth P(S)={1299, 6461}, algorithm computed {3356,
# 6461} (missing 1299). Every provider edge below is copied directly from
# the "o_providers_of (policy-labeled)" dump in that trace, so this is the
# exact real subgraph that produced the false positive - not a synthetic
# reconstruction. ASN 46887 -> AS2 (F), 39745 -> AS3 (victim/source), plus
# a dedicated attacker AS1 hanging directly off AS1299's renamed stand-in
# AS20 (F's provider that legitimate traffic was wrongly dropped from).
#
# ASN remapping (real -> test):
#   46887 -> 2   (F / reflector / sav enforcer)
#   39745 -> 3   (victim / source)
#   1299  -> 20  (F's real provider - the one wrongly excluded)
#   3356  -> 21  (F's real provider - kept)
#   6461  -> 22  (F's real provider - kept)
#   8708  -> 30
#   6663  -> 31
#   1121  -> 40
#   2914  -> 41
#   39686 -> 42
#   215638-> 43
#   3223  -> 44
#   6939  -> 45
#   5405  -> 46
#   6910  -> 47
#   3491  -> 50
#   5511  -> 51
#   35625 -> 52
#   9002  -> 53
#   6762  -> 54
#   201709-> 55
#   174   -> 56
#   7922  -> 57
#   3320  -> 58
#   3257  -> 59
#   12956 -> 60
#   701   -> 61
#   8881  -> 62
#   199938-> 63
#   6453  -> 64
#   15943 -> 65
#   attacker (new, dedicated) -> 99, hangs directly off AS20 (=1299)

as_graph_info = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset([
        # F=AS2's real direct providers
        CPLink(provider_asn=20, customer_asn=2),
        CPLink(provider_asn=21, customer_asn=2),
        CPLink(provider_asn=22, customer_asn=2),

        # AS3 (victim/source, real ASN 39745) -> providers {30, 31}
        CPLink(provider_asn=30, customer_asn=3),
        CPLink(provider_asn=31, customer_asn=3),

        # AS30 (8708) -> providers {43, 21, 47}
        CPLink(provider_asn=43, customer_asn=30),
        CPLink(provider_asn=21, customer_asn=30),
        CPLink(provider_asn=47, customer_asn=30),

        # AS31 (6663) -> providers {40, 41, 42, 20, 43, 44, 45, 21, 46}
        CPLink(provider_asn=40, customer_asn=31),
        CPLink(provider_asn=41, customer_asn=31),
        CPLink(provider_asn=42, customer_asn=31),
        CPLink(provider_asn=20, customer_asn=31),
        CPLink(provider_asn=43, customer_asn=31),
        CPLink(provider_asn=44, customer_asn=31),
        CPLink(provider_asn=45, customer_asn=31),
        CPLink(provider_asn=21, customer_asn=31),
        CPLink(provider_asn=46, customer_asn=31),

        # AS42 (39686) -> providers {59, 21, 52}
        CPLink(provider_asn=59, customer_asn=42),
        CPLink(provider_asn=21, customer_asn=42),
        CPLink(provider_asn=52, customer_asn=42),

        # AS43 (215638) -> providers {53, 20, 56}
        CPLink(provider_asn=53, customer_asn=43),
        CPLink(provider_asn=20, customer_asn=43),
        CPLink(provider_asn=56, customer_asn=43),

        # AS44 (3223) -> providers {60, 41, 50, 51, 54, 57, 20, 43, 21}
        CPLink(provider_asn=60, customer_asn=44),
        CPLink(provider_asn=41, customer_asn=44),
        CPLink(provider_asn=50, customer_asn=44),
        CPLink(provider_asn=51, customer_asn=44),
        CPLink(provider_asn=54, customer_asn=44),
        CPLink(provider_asn=57, customer_asn=44),
        CPLink(provider_asn=20, customer_asn=44),
        CPLink(provider_asn=43, customer_asn=44),
        CPLink(provider_asn=21, customer_asn=44),

        # AS45 (6939) -> providers {55, 20, 21, 61}
        CPLink(provider_asn=55, customer_asn=45),
        CPLink(provider_asn=20, customer_asn=45),
        CPLink(provider_asn=21, customer_asn=45),
        CPLink(provider_asn=61, customer_asn=45),

        # AS46 (5405) -> providers {41, 20, 58, 59, 54}
        CPLink(provider_asn=41, customer_asn=46),
        CPLink(provider_asn=20, customer_asn=46),
        CPLink(provider_asn=58, customer_asn=46),
        CPLink(provider_asn=59, customer_asn=46),
        CPLink(provider_asn=54, customer_asn=46),

        # AS47 (6910) -> providers {20, 56, 42}
        CPLink(provider_asn=20, customer_asn=47),
        CPLink(provider_asn=56, customer_asn=47),
        CPLink(provider_asn=42, customer_asn=47),

        # AS52 (35625) -> providers {59, 21, 51}
        CPLink(provider_asn=59, customer_asn=52),
        CPLink(provider_asn=21, customer_asn=52),
        CPLink(provider_asn=51, customer_asn=52),

        # AS53 (9002) -> providers {59, 21, 64}
        CPLink(provider_asn=59, customer_asn=53),
        CPLink(provider_asn=21, customer_asn=53),
        CPLink(provider_asn=64, customer_asn=53),

        # AS55 (201709) -> providers {62, 63, 46}
        CPLink(provider_asn=62, customer_asn=55),
        CPLink(provider_asn=63, customer_asn=55),
        CPLink(provider_asn=46, customer_asn=55),

        # AS57 (7922) -> providers {21, 64}
        CPLink(provider_asn=21, customer_asn=57),
        CPLink(provider_asn=64, customer_asn=57),

        # AS62 (8881) -> providers {20, 64, 42, 58, 21, 56}
        CPLink(provider_asn=20, customer_asn=62),
        CPLink(provider_asn=64, customer_asn=62),
        CPLink(provider_asn=42, customer_asn=62),
        CPLink(provider_asn=58, customer_asn=62),
        CPLink(provider_asn=21, customer_asn=62),
        CPLink(provider_asn=56, customer_asn=62),

        # AS63 (199938) -> providers {20, 65}
        CPLink(provider_asn=20, customer_asn=63),
        CPLink(provider_asn=65, customer_asn=63),

        # AS65 (15943) -> providers {41, 20, 64, 59, 54, 21, 56}
        CPLink(provider_asn=41, customer_asn=65),
        CPLink(provider_asn=20, customer_asn=65),
        CPLink(provider_asn=64, customer_asn=65),
        CPLink(provider_asn=59, customer_asn=65),
        CPLink(provider_asn=54, customer_asn=65),
        CPLink(provider_asn=21, customer_asn=65),
        CPLink(provider_asn=56, customer_asn=65),

        # Dedicated attacker, directly below AS20 (real ASN 1299) - so its
        # spoofed packet claiming source=AS3 (39745) arrives at F via
        # prev_hop=20, exactly matching the original bug report.
        CPLink(provider_asn=20, customer_asn=99),
    ]),
)

desc = (
    # "Verbatim reconstruction of a REAL false positive observed in "
    # "production simulation (F=46887, source=39745, prev_hop=1299, ASPA "
    # "full adoption). Real ASN 46887->AS2 (F), 39745->AS3 (victim), "
    # "1299->AS20 (F's real provider that legitimate AS3 traffic gets "
    # "wrongly dropped from). All edges are copied directly from the "
    # "o_providers_of dump of that run. AS30 (real 8708) has a short real "
    # "chain straight to AS21 (real 3356, F's provider) but ALSO a longer "
    # "real chain to AS20 (real 1299) via AS43->AS56 (215638->174, "
    # "confirmed real peers of 1299/20). BAR_SAV_PI_PP's Case C keeps only "
    # "the shortest chain per node, so the longer-but-equally-real path to "
    # "AS20 gets silently dropped at multiple levels, and the final P(AS3) "
    # "computed by the algorithm excludes AS20 even though AS3 genuinely "
    # "has real ASPA-published paths reaching it."
)

bspi_pp_011 = EngineTestConfig(
    SimulationEngineCls=SAVSimulationEngine,
    name="bspi_pp_011",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=ASPAFull,
        BaseSAVPolicyCls=BAR_SAV_PI_PP,
        override_attacker_asns=frozenset({99}),
        override_reflector_asns=frozenset({2}),
        override_victim_asns=frozenset({3}),
        override_sav_asns=frozenset({2}),
        # hardcoded_asn_cls_dict=frozendict({
        #     asn: ASPAFull
        #     for asn in (
        #         3, 30, 31, 40, 41, 42, 43, 44, 45, 46, 47,
        #         50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
        #         61, 62, 63, 64, 65,
        #     )
        # }),
    ),
    as_graph_info=as_graph_info,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer,
    GraphDataAggregatorCls=SAVMetricTracker,
)
