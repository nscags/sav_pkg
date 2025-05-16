from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs import ASGraphInfo


as_graph_info_008 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=4193, customer_asn=100),
            CPLink(provider_asn=10580, customer_asn=100),
            CPLink(provider_asn=16158, customer_asn=100),
        ]
    ),
    diagram_ranks=(
        (100,),
        (4193, 10580, 16158),
    ),
)