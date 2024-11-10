from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo
from sav_pkg.enums import ASNs

as_graph_info_001 = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=4),
            CPLink(provider_asn=8, customer_asn=ASNs.VICTIM.value),
        ]
    ),
    diagram_ranks=(
        (1, 2, 4),
        (5, 8, ASNs.VICTIM.value),
    ),
)
