from frozendict import frozendict
from .as_graph_info_001 import as_graph_info_001

from sav_pkg.simulation_engine import FeasiblePathuRPF
from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioMultipleReflectors,
)
from sav_pkg.simulation_engine import BGPFull


desc = "Every AS is a reflector running Feasible-Path uRPF"

config_201 = EngineTestConfig(
    name="config_201",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioMultipleReflectors,
        BasePolicyCls=BGPFull,
        num_reflectors=10,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({1,2,3,4,5,8,9,10,11,12}),
        override_non_default_asn_cls_dict=frozendict(),
        BaseSAVPolicyCls=FeasiblePathuRPF,
    ),
    as_graph_info=as_graph_info_001,
)
