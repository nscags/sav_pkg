from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""

"""


as_graph_info_006 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(2, 3),
            PeerLink(2, 1)
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
        ]
    ),
    diagram_ranks=(
        (ASNs.VICTIM.value, ASNs.ATTACKER.value),
        (1, 3),
        (2,),
    ),
)