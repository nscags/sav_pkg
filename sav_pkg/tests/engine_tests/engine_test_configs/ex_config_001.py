from frozendict import frozendict
from .as_graph_info_001 import as_graph_info_001

from bgpy.simulation_engine import (
    BGPSimplePolicy,
)

from sav_pkg.tests import EngineTestConfig
from sav_pkg.enums import ASNs
from sav_pkg.simluation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioMultipleReflectors,
)


desc = "SAV test with multiple reflectors and default metrics"

ex_config_001 = EngineTestConfig(
    name="ex_001_sav",
    desc=desc,
    scenario_config=SAVScenarioConfig(
        ScenarioCls=SAVScenarioMultipleReflectors,
        BasePolicyCls=BGPSimplePolicy,
        num_reflectors=2,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_reflector_asns=frozenset({ASNs.REFLECTOR.value, 5}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_001,
)
