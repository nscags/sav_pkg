from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

r"""
    6
    |
    3---5
    |   |
    2   1
     \ /
      4
"""

as_graph_info_010 = ASGraphInfo(
    peer_links=frozenset(
        [
            PeerLink(3, 5),
        ]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=6, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=5, customer_asn=1),
        ]
    ),
    diagram_ranks=(
        (4,),
        (2, 1),
        (3, 5),
        (6,),
    ),
)
