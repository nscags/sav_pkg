from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.enums import ASNs

r"""

This graph can highlight every example of Gao Rexford Valley Free Routing

(see config 001 for description)
Graph is too complex for an ascii drawing, just view the PDF
"""


as_graph_info_006 = ASGraphInfo(
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
            CPLink(provider_asn=21976, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=21976, customer_asn=205),
            CPLink(provider_asn=46887, customer_asn=205),
            CPLink(provider_asn=5, customer_asn=1),
            # CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=21976),
            CPLink(provider_asn=9, customer_asn=46887),
            CPLink(provider_asn=10, customer_asn=205),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=8),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, 205),
        (1, 21976, 3, 46887),
        (5, 8, 9, 10),
        (ASNs.REFLECTOR.value, 12),
    ),
)