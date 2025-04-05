from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs


"""
    "18": {
        "174": [
            false,
            true
        ],
        "276": [
            false
        ],
        "1239": [
            false,
            true
        ],
        "6922": [
            false
        ]
"""

as_graph_info_002 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(8, 9),
            PeerLink(9, 10),
            PeerLink(9, 3),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=174, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=174, customer_asn=18),
            CPLink(provider_asn=1239, customer_asn=18),
            CPLink(provider_asn=5, customer_asn=1),
            # CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=174),
            CPLink(provider_asn=9, customer_asn=1239),
            CPLink(provider_asn=10, customer_asn=18),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=8),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, 18),
        (1, 174, 3, 1239),
        (5, 8, 9, 10),
        (ASNs.REFLECTOR.value, 12),
    ),
)