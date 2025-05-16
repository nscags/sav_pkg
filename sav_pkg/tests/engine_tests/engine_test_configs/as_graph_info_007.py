from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from sav_pkg.enums import ASNs

as_graph_info_007 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=1),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=2),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=3),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),
        (1, 2, 3),
        (ASNs.REFLECTOR.value,),
    ),
)
