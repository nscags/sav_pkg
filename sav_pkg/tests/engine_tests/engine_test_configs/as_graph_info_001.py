from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""

This graph can highlight every example of Gao Rexford Valley Free Routing

(see config 001 for description)
Graph is too complex for an ascii drawing, just view the PDF
"""


as_graph_info_001 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(1, 2),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
        ]
    ),
    diagram_ranks=(
        (ASNs.VICTIM.value,),
        (1, 2),
    ),
)

"""




"""
