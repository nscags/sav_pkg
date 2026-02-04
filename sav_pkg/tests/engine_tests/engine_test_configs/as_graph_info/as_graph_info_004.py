from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo
from sav_pkg.enums import ASNs

## Graph Example 4 - Larger Network with Multiple Paths and High Complexity ##
as_graph_info_004 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(14, 15),
            PeerLink(15, 16),
            PeerLink(16, 17),
            PeerLink(18, 19),
            PeerLink(19, 20),
            PeerLink(21, 22),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=6, customer_asn=3),
            CPLink(provider_asn=7, customer_asn=4),
            CPLink(provider_asn=8, customer_asn=5),
            CPLink(provider_asn=9, customer_asn=6),
            CPLink(provider_asn=10, customer_asn=7),
            CPLink(provider_asn=11, customer_asn=8),
            CPLink(provider_asn=12, customer_asn=9),
            CPLink(provider_asn=13, customer_asn=10),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=11),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=12),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=13),
            CPLink(provider_asn=14, customer_asn=11),
            CPLink(provider_asn=15, customer_asn=12),
            CPLink(provider_asn=16, customer_asn=13),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9, 10),
        (11, 12, 13),
        (14, 15, 16, 17, 18, 19, 20, 21, 22),
        (ASNs.REFLECTOR.value,),     #keep comma or errors
    ),
)