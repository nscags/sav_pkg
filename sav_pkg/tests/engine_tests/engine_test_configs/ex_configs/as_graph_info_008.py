from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""

"""


as_graph_info_008 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(5, 4),
            PeerLink(7, 6),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),  
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),  
            CPLink(provider_asn=5, customer_asn=1),  
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=6, customer_asn=3),
            CPLink(provider_asn=7, customer_asn=5),
            CPLink(provider_asn=6, customer_asn=4),  
        ]
    ),
    diagram_ranks=(
        (ASNs.VICTIM.value, ASNs.ATTACKER.value),
        (1, 2, 3),
        (5, 4),
        (7, 6),
    ),
)