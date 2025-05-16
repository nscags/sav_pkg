from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink

from sav_pkg.enums import ASNs

"""
  "100": {
    "4193": 0.0,
    "10580": 0.16666666666666666,
    "16158": 0.16666666666666666,
    "46197": 0.16666666666666666,
    "46301": 0.16666666666666666,
    "329381": 0.16666666666666666,
    "395727": 0.16666666666666666
  },
"""

as_graph_info_003 = ASGraphInfo(
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
            CPLink(provider_asn=4193, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=4193, customer_asn=100),
            CPLink(provider_asn=46301, customer_asn=100),
            CPLink(provider_asn=5, customer_asn=1),
            # CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=4193),
            CPLink(provider_asn=9, customer_asn=46301),
            CPLink(provider_asn=10, customer_asn=100),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=8),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, 100),
        (1, 4193, 3, 46301),
        (5, 8, 9, 10),
        (ASNs.REFLECTOR.value, 12),
    ),
)
