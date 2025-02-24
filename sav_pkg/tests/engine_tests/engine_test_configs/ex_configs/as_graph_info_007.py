from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

r"""
Asymmetric Route Graph
"""


as_graph_info_007 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(1, 2),
            PeerLink(3, 2),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=ASNs.REFLECTOR.value),
            CPLink(provider_asn=3, customer_asn=5),
            CPLink(provider_asn=4, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=8),
            CPLink(provider_asn=8, customer_asn=ASNs.ATTACKER.value)
        ]
    ),
    diagram_ranks=(
        (ASNs.VICTIM.value, ASNs.ATTACKER.value),
        (5, 8),
        (3, 4, ASNs.REFLECTOR.value),
        (1, 2),
    ),
)