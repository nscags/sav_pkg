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
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=4193, customer_asn=100),
            CPLink(provider_asn=46301, customer_asn=100),
            CPLink(provider_asn=1, customer_asn=46301),
            CPLink(provider_asn=555, customer_asn=1),
            CPLink(provider_asn=555, customer_asn=4193),
        ]
    ),
)