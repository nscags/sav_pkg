from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

r"""
    4
   / \
  3   2
  |   |
  1   |
   \ /
    5
"""

as_graph_info_005 = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=5),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=3),
        ]
    ),
)
