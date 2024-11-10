from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo
from sav_pkg.enums import ASNs

as_graph_info_005 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(3, 4),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=8, customer_asn=4),
            CPLink(provider_asn=8, customer_asn=ASNs.VICTIM.value),
        ]
    ),
    diagram_ranks=(
        (2, 3, 4),
        (8, ASNs.VICTIM.value),
    ),
    sav_adopting_ases=frozenset(
        {
            1, 5, ASNs.VICTIM.value
        }
    )
)
