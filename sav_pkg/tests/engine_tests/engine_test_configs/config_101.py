from frozendict import frozendict
from .as_graph_info_001 import as_graph_info_001

from bgpy.simulation_engine import BGP

from sav_pkg.simulation_engine import StrictuRPF
from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioMultipleReflectors,
)


desc = "Every AS is a reflector running Strict uRPF"

config_101 = EngineTestConfig(
    name="config_101",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioMultipleReflectors,
        BasePolicyCls=BGP,
        num_reflectors=10,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({1,2,3,4,5,8,9,10,11,12}),
        override_non_default_asn_cls_dict=frozendict(),
        BaseSAVPolicyCls=StrictuRPF,
    ),
    as_graph_info=as_graph_info_001,
)
