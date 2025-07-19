from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink


as_graph_info_001 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=3),
        ]
    ),
)