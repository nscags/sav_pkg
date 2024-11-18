from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

r"""

"""

as_graph_info_001 = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=2, customer_asn=3),
        ]
    ),
    diagram_ranks=(
        (1,),
        (3, 4),
        (5,),
        (2,),
    ),
)