from frozendict import frozendict
from .as_graph_info_000 import as_graph_info_000

from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)
from sav_pkg.simulation_engine import BGPFull, BAR_SAV


desc = "Single reflector w/ BAR SAV"

config_400 = EngineTestConfig(
    name="config_400",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),
        BaseSAVPolicyCls=BAR_SAV
    ),
    as_graph_info=as_graph_info_000,
)
