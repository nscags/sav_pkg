from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs import ASGraphInfo

from sav_pkg.enums import ASNs

"""  
"17": {
    "6461": 0.25,
    "19782": 1.0
  },
"""


as_graph_info_004 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=6461, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=6461, customer_asn=17),
            CPLink(provider_asn=19782, customer_asn=17),
            CPLink(provider_asn=1, customer_asn=6461),
            CPLink(provider_asn=2, customer_asn=19782),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=1),
            CPLink(provider_asn=12, customer_asn=2),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, 17),
        (3, 6461, 19782),
        (1, 2),
        (ASNs.REFLECTOR.value, 12),
    ),
)