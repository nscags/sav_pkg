from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink


as_graph_info_009 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(4, 5),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=5, customer_asn=3),
        ]
    ),
    diagram_ranks=(
        (1, 2, 3),
        (4, 5),
    ),
)
