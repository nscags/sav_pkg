from frozendict import frozendict
from .as_graph_info_000 import as_graph_info_000

from bgpy.simulation_engine import BGPFull

from sav_pkg.simulation_engine import EnhancedFeasiblePath
from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenario,
)


desc = "Single reflector w/ Enhanced Feasible-Path uRPF"

config_300 = EngineTestConfig(
    name="config_300",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value}),
        override_non_default_asn_cls_dict=frozendict(),
        BaseSAVPolicyCls=EnhancedFeasiblePath
    ),
    as_graph_info=as_graph_info_000,
)
