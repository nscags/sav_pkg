from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo


as_graph_info_012 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(5, 2),
            PeerLink(5, 4),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=3),
        ]
    ),
    diagram_ranks=(
        (1,),
        (2, 3),
        (5, 4),
    ),
)