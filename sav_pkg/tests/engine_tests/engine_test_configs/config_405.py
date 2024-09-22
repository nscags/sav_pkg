from frozendict import frozendict
from .as_graph_info_001 import as_graph_info_001

from sav_pkg.simulation_engine import BAR_SAV
from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioMultipleReflectors,
)
from sav_pkg.simulation_engine import ASPAFull

desc = "Almost every AS is a reflector running BAR SAV"

config_405 = EngineTestConfig(
    name="config_405",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioMultipleReflectors,
        BasePolicyCls=ASPAFull,
        num_reflectors=9,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({2,3,4,5,8,9,10,11,12}),
        override_non_default_asn_cls_dict=frozendict(),
        BaseSAVPolicyCls=BAR_SAV,
    ),
    as_graph_info=as_graph_info_001,
)
