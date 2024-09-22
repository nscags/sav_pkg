from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""

This graph can highlight every example of Gao Rexford Valley Free Routing

(see config 001 for description)
Graph is too complex for an ascii drawing, just view the PDF
"""

as_graph_info_002 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=3),
            CPLink(provider_asn=4, customer_asn=3),
            CPLink(provider_asn=4, customer_asn=5),
        ]
    ),
    diagram_ranks=(
        (1,),
        (3, 5),
        (4,),
    ),
)
