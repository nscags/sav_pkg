from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
from bgpy.as_graphs import ASGraphInfo
from sav_pkg.enums import ASNs

as_graph_info_006 = ASGraphInfo(

    customer_provider_links=frozenset(
        [
            # Main Attack and Victim Links
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),

            # Expansion of hierarchy with multiple layers
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=6, customer_asn=2),
            CPLink(provider_asn=7, customer_asn=3),
            CPLink(provider_asn=8, customer_asn=4),
            CPLink(provider_asn=9, customer_asn=5),
            CPLink(provider_asn=10, customer_asn=6),
            CPLink(provider_asn=11, customer_asn=7),
            CPLink(provider_asn=12, customer_asn=8),
            CPLink(provider_asn=13, customer_asn=9),
            CPLink(provider_asn=14, customer_asn=10),
            CPLink(provider_asn=15, customer_asn=11),
            CPLink(provider_asn=16, customer_asn=12),
            CPLink(provider_asn=17, customer_asn=13),
            CPLink(provider_asn=18, customer_asn=14),
            CPLink(provider_asn=19, customer_asn=15),
            CPLink(provider_asn=20, customer_asn=16),

            # Additional hierarchical ASes and redundancy paths
            CPLink(provider_asn=21, customer_asn=17),
            CPLink(provider_asn=22, customer_asn=18),
            CPLink(provider_asn=23, customer_asn=19),
            CPLink(provider_asn=24, customer_asn=20),
            CPLink(provider_asn=25, customer_asn=21),
            CPLink(provider_asn=26, customer_asn=22),
            CPLink(provider_asn=27, customer_asn=23),
            CPLink(provider_asn=28, customer_asn=24),

            # Subnetworks and interconnected reflectors
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=25),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=26),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=27),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=28),

            # Expanding subnetworks with deeper layers
            CPLink(provider_asn=29, customer_asn=26),
            CPLink(provider_asn=30, customer_asn=29),
            CPLink(provider_asn=31, customer_asn=30),
            CPLink(provider_asn=32, customer_asn=31),
            CPLink(provider_asn=33, customer_asn=32),
            CPLink(provider_asn=34, customer_asn=33),
            CPLink(provider_asn=35, customer_asn=34),
            CPLink(provider_asn=36, customer_asn=35),

            # Inter-layer connections with complex paths
            CPLink(provider_asn=37, customer_asn=36),
            CPLink(provider_asn=38, customer_asn=37),
            CPLink(provider_asn=39, customer_asn=38),
            CPLink(provider_asn=40, customer_asn=39),
            CPLink(provider_asn=41, customer_asn=40),
            CPLink(provider_asn=42, customer_asn=41),

            # Diverse reflector nodes across subnetworks
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=42),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=43),
            CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=44),
            CPLink(provider_asn=45, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=46, customer_asn=45),
            CPLink(provider_asn=47, customer_asn=46),
            CPLink(provider_asn=48, customer_asn=47),
            CPLink(provider_asn=49, customer_asn=48),
            CPLink(provider_asn=50, customer_asn=49),

            # Adding deep hierarchical levels
            CPLink(provider_asn=51, customer_asn=50),
            CPLink(provider_asn=52, customer_asn=51),
            CPLink(provider_asn=53, customer_asn=52),
            CPLink(provider_asn=54, customer_asn=53),
            CPLink(provider_asn=55, customer_asn=54),
            CPLink(provider_asn=56, customer_asn=55),
            CPLink(provider_asn=57, customer_asn=56),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),
        (1, 2, 3, 4),
        (5, 6, 7, 8, 9, 10, 11),
        (12, 13, 14, 15, 16, 17, 18, 19, 20),
        (21, 22, 23, 24, 25, 26, 27, 28),
        (29, 30, 31, 32, 33, 34, 35, 36),
        (37, 38, 39, 40, 41, 42),
        (43, 44, 45, 46, 47, 48, 49, 50, 51, 52),
        (53, 54, 55, 56, 57),
        (ASNs.REFLECTOR.value,),
    ),
)