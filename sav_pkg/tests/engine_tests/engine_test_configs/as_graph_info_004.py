from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""

This graph can highlight every example of Gao Rexford Valley Free Routing

(see config 001 for description)
Graph is too complex for an ascii drawing, just view the PDF
"""

as_graph_info_004 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(9, 8),
            PeerLink(8, 10),
            PeerLink(8, 3),
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
            CPLink(provider_asn=9, customer_asn=1),
            CPLink(provider_asn=9, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=4),
            CPLink(provider_asn=8, customer_asn=2),
            CPLink(provider_asn=10, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=11, customer_asn=9),
            CPLink(provider_asn=11, customer_asn=8),
            CPLink(provider_asn=11, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),
        (1, 2, 3, 4),
        (5, 9, 8, 10),
        (11, 12),
    ),
)
