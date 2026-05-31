from dataclasses import dataclass, field

from bgpy.shared.enums import ASGroups
from bgpy.simulation_framework.scenarios import ScenarioConfig
from frozendict import frozendict

from sav_pkg.enums import Prefixes
from sav_pkg.simulation_engine.policies.sav.base_sav_policy import BaseSAVPolicy


@dataclass(frozen=True)
class SAVScenarioConfig(ScenarioConfig):
    # reflectors
    num_reflectors: int = 1
    reflector_subcategory_attr: str | None = ASGroups.ALL_WOUT_IXPS.value
    override_reflector_asns: frozenset[int] | None = None
    # source prefix used for data packets
    source_prefix: str = Prefixes.VICTIM.value
    # issue ROA for specificed source prefix
    source_prefix_roa: bool = False
    # attacker's providers can be set to not adopt any SAV policy
    attacker_providers_non_adopters: bool = False
    # toggle for victim's providers announing 
    victim_providers_ann: bool = False
    # toggle for attacker's strategy, either broadcasting or best path routing
    attacker_broadcast: bool = True
    # ignore disconnected ASes
    ignore_disconnections: bool = True
    BaseSAVPolicyCls: type[BaseSAVPolicy] | None = None
    # reflectors adopt SAV policy by default
    reflector_default_adopters: bool = False
    # victims adopt CRTL-PLANE policy by default (AdoptPolicyCls)
    victim_default_adopters: bool = False
    # set of asns adopting SAV, will adopt BaseSAVPolicyCls by defualt
    override_sav_asns: frozenset[int] | None = None
    # Optional hardcode asn with SAV in case of testing with multiple ASes running
    # different SAV policies
    hardcoded_asn_sav_dict: frozendict[int, type[BaseSAVPolicy]] = field(
        # Mypy doesn't understand frozendict typing, just ignore it
        default_factory=frozendict  # type: ignore
    )
    # Special percent adoption for control plane policies
    # I hijacked the default percent_adopt for SAV policies
    ctrl_plane_percent_adoption: float = 0.0