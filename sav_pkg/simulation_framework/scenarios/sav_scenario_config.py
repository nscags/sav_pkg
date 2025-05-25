from dataclasses import dataclass, field

from bgpy.enums import ASGroups
from bgpy.simulation_framework.scenarios import ScenarioConfig
from frozendict import frozendict

from sav_pkg.enums import Prefixes
from sav_pkg.policies.sav.base_sav_policy import BaseSAVPolicy


@dataclass(frozen=True)
class SAVScenarioConfig(ScenarioConfig):
    num_reflectors: int = 1
    reflector_subcategory_attr: str | None = ASGroups.ALL_WOUT_IXPS.value
    override_reflector_asns: frozenset[int] | None = None

    victim_source_prefix: str = Prefixes.VICTIM.value

    BaseSAVPolicyCls: BaseSAVPolicy | None = BaseSAVPolicy
    reflector_default_adopters: bool | None = False
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
    special_percent_adoption: float = 0.0
    override_default_interface_dict: frozendict[str, frozenset] = None

    # DSR configs 
    # user 
    num_users: int = 1
    user_subcategory_attr: str | None = ASGroups.STUBS_OR_MH.value
    override_user_asns: frozenset[int] | None = None
    # anycast server
    num_anycast_servers: int = 1
    anycast_server_subcategory_attr: str | None = ASGroups.STUBS_OR_MH.value
    override_anycast_server_asns: frozenset[int] | None = None
    # edge server 
    num_edge_servers: int = 1
    edge_server_subcategory_attr: str | None = ASGroups.STUBS_OR_MH.value
    override_edge_server_asns: frozenset[int] | None = None
