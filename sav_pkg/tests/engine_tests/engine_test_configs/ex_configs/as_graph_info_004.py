from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

r"""
    4
   / \
  3   5
 / \
1   2
"""

as_graph_info_004 = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=4, customer_asn=3),
            CPLink(provider_asn=4, customer_asn=5),
        ]
    ),
)
