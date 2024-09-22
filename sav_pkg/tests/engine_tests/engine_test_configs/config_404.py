from frozendict import frozendict
from .as_graph_info_002 import as_graph_info_002

from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario
)

from sav_pkg.simulation_engine import BGPFull
from sav_pkg.simulation_engine import BAR_SAV


desc = "BAR SAV test"

config_404 = EngineTestConfig(
    name="config_404",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        num_attackers=0,
        override_victim_asns=frozenset({3}),
        override_reflector_asns=frozenset({4}),
        override_non_default_asn_cls_dict=frozendict(),
        BaseSAVPolicyCls=BAR_SAV
    ),
    as_graph_info=as_graph_info_002,
)
