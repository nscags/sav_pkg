from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""
Attempt to replicate false positive graph for feasible path urpf
"""


as_graph_info_004 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(3, 4),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=5, customer_asn=4),
            CPLink(provider_asn=5, customer_asn=6),
        ]
    ),
    diagram_ranks=(
        (1, 2),
        (3, 4, 6),
        (5,)
    ),
)
