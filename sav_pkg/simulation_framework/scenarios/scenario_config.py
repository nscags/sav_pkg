from dataclasses import dataclass, field
from typing import Optional
from frozendict import frozendict

from bgpy.simulation_framework.scenarios import ScenarioConfig

from sav_pkg.enums import ASGroups, Prefixes
from sav_pkg.simulation_engine import BaseSAVPolicy


@dataclass(frozen=True)
class SAVScenarioConfig(ScenarioConfig):
    num_reflectors: int = 1
    reflector_subcategory_attr: Optional[str] = ASGroups.ALL_WOUT_IXPS.value
    override_reflector_asns: Optional[frozenset[int]] = None

    victim_source_prefix = Prefixes.VICTIM.value

    BaseSAVPolicyCls: Optional[BaseSAVPolicy] = BaseSAVPolicy
    reflector_default_adopters: Optional[bool] = False
    # set of asns adopting SAV, will adopt BaseSAVPolicyCls by defualt
    override_sav_asns: Optional[frozenset[int]] = None
    # Optional hardcode asn with SAV in case of testing with multiple ASes running
    # different SAV policies
    hardcoded_asn_sav_dict: frozendict[int, type[BaseSAVPolicy]] = field(
        # Mypy doesn't understand frozendict typing, just ignore it
        default_factory=frozendict  # type: ignore
    )
