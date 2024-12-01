from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

r"""
  2 - 3
   \ /
    1
"""

as_graph_info_002 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(2, 3)  
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=1),
        ]
    ),
)
