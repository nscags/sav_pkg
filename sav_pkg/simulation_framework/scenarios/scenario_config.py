from dataclasses import dataclass
from typing import Optional
from frozendict import frozendict

from bgpy.simulation_framework.scenarios import ScenarioConfig
from bgpy.enums import ASGroups

from sav_pkg.simulation_engine import BaseSAVPolicy 

@dataclass(frozen=True)
class SAVScenarioConfig(ScenarioConfig):
    num_reflectors: int = 1
    reflector_subcategory_attr: Optional[str] = ASGroups.STUBS_OR_MH.value
    override_reflector_asns: Optional[frozenset[int]] = None

    # base SAV class
    BaseSAVPolicyCls: Optional[BaseSAVPolicy] = None
    # set of asns adopting SAV, will adopt BaseSAVPolicyCls by defualt
    override_sav_asns: Optional[frozenset[int]] = None
    # Optional hardcode asn with SAV in case of testing with multiple ASes running
    # different SAV policies
    hardcoded_asn_sav_dict: Optional[frozendict] = None
