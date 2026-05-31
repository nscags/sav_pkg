from dataclasses import dataclass

from bgpy.shared.enums import ASGroups

from .sav_scenario_config import SAVScenarioConfig
from sav_pkg.enums import Prefixes



@dataclass(frozen=True)
class SAVScenarioDSRConfig(SAVScenarioConfig):
    # users 
    num_users: int = 1
    user_subcategory_attr: str | None = ASGroups.STUBS_OR_MH.value
    override_user_asns: frozenset[int] | None = None
    # anycast servers
    num_anycast_servers: int = 1
    anycast_server_subcategory_attr: str | None = ASGroups.STUBS_OR_MH.value
    override_anycast_server_asns: frozenset[int] | None = None
    # edge servers
    num_edge_servers: int = 1
    edge_server_subcategory_attr: str | None = ASGroups.STUBS_OR_MH.value
    override_edge_server_asns: frozenset[int] | None = None

    source_prefix: str = Prefixes.ANYCAST_SERVER.value
    source_prefix_roa: bool = True
    ignore_disconnections: bool = False