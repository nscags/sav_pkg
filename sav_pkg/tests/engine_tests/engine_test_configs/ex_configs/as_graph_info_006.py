from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs


as_graph_info_006 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(8, 9),
            PeerLink(9, 10),
            PeerLink(9, 3),
            PeerLink(4, 9),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=5, customer_asn=1),
            # CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=2),
            CPLink(provider_asn=10, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=8),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),
        (1, 2, 3, 4),
        (5, 8, 9, 10),
        (ASNs.REFLECTOR.value, 12),
    ),
)
