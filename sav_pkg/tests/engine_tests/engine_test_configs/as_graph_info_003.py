from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""

This graph can highlight every example of Gao Rexford Valley Free Routing

(see config 001 for description)
Graph is too complex for an ascii drawing, just view the PDF
"""

####      No Peer Links Graph      ###


as_graph_info_003 = ASGraphInfo(
    
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),

            CPLink(provider_asn=2, customer_asn= ASNs.VICTIM.value),

            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=3),
            CPLink(provider_asn=9, customer_asn=5),
            # CPLink(provider_asn=5, customer_asn=2),

            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=8),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
            CPLink(provider_asn=12, customer_asn=9),
            # CPLink(provider_asn=16, customer_asn=8),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),
        (1, 2),
        (3, 4, 5),
        (8, 9),
        (ASNs.REFLECTOR.value, 12),
    ),
)
