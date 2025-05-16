from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.enums import ASNs

"""  
"17": {
    "6461": 0.25,
    "19782": 1.0
  },
"""


as_graph_info_001 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(8, 9),
            PeerLink(9, 10),
            PeerLink(9, 3),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=6461, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=6461, customer_asn=17),
            CPLink(provider_asn=19782, customer_asn=17),
            CPLink(provider_asn=5, customer_asn=1),
            # CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=6461),
            CPLink(provider_asn=9, customer_asn=19782),
            CPLink(provider_asn=10, customer_asn=17),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=8),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, 17),
        (1, 6461, 3, 19782),
        (5, 8, 9, 10),
        (ASNs.REFLECTOR.value, 12),
    ),
)
