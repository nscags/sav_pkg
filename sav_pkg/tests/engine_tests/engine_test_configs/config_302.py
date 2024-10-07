from frozendict import frozendict
from .as_graph_info_001 import as_graph_info_001

from bgpy.simulation_engine.policies import BGPFull
from bgpy.tests.engine_tests import EngineTestConfig
from bgpy.simulation_engine import Announcement as Ann

from sav_pkg.enums import ASNs, Prefixes
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_framework import SAVASGraphAnalyzer
from sav_pkg.utils import SAVDiagram
from sav_pkg.simulation_engine import EnhancedFeasiblePathuRPF

desc = "Single reflector running EFP uRPF"

config_302 = EngineTestConfig(
    name="config_302",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        num_attackers=0,
        num_reflectors=2,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({1, 2}),
        override_non_default_asn_cls_dict=frozendict(),
        override_announcements=(Ann(
            prefix=Prefixes.VICTIM.value,
            as_path=(1, ASNs.VICTIM.value),
            next_hop_asn=1,
            seed_asn=ASNs.VICTIM.value,
        ), Ann(
            prefix=Prefixes.VICTIM.value,
            as_path=(ASNs.VICTIM.value,),
            next_hop_asn=1,
            seed_asn=ASNs.VICTIM.value,
        ),
        
        
        
        # Ann(
        #     prefix='1.1.0.0/23',
        #     as_path=(2, ASNs.VICTIM.value),
        #     next_hop_asn=1,
        #     seed_asn=ASNs.VICTIM.value,
        # ), Ann(
        #     prefix='1.2.0.0/24',
        #     as_path=(1,),
        #     next_hop_asn=ASNs.VICTIM.value,
        #     seed_asn=1,
        # ), Ann(
        #     prefix='1.3.0.0/24',
        #     as_path=(2,),
        #     next_hop_asn=ASNs.VICTIM.value,
        #     seed_asn=2,
        # )
        # Ann(
        #     prefix=Prefixes.VICTIM.value,
        #     as_path=(ASNs.VICTIM.value,),
        #     next_hop_asn=2,
        #     seed_asn=ASNs.VICTIM.value,
        # )
        ),
        override_sav_asns=frozenset({1, 2}),
        BaseSAVPolicyCls=EnhancedFeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_001,
    DiagramCls=SAVDiagram,
    ASGraphAnalyzerCls=SAVASGraphAnalyzer
)
