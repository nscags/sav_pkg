from frozendict import frozendict
from .as_graph_info_003 import as_graph_info_003

from bgpy.simulation_engine import (
    BGP,
    StrictuRPF,
)

from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simluation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)


desc = "Single reflector w/ Strict uRPF, Expected to filter spoofed packet"

config_003 = EngineTestConfig(
    name="config_003",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),
        BaseSAVPolicyCls=StrictuRPF
    ),
    as_graph_info=as_graph_info_003,
)
