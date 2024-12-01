from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo
from sav_pkg.enums import ASNs

## Graph for Testing RFC8704 ##
as_graph_info_007 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(1, 2),
            PeerLink(2, 3),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=4, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=1),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=2),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),  # Stub ASNs
        (4, 5),  # Providers
        (1, 2, 3),  # Peers
        (ASNs.REFLECTOR.value,),  # Reflector ASN
    ),
)