# from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink
# from bgpy.as_graphs import ASGraphInfo
# from sav_pkg.enums import ASNs

# as_graph_info_007 = ASGraphInfo(
#     peer_links=frozenset(
#         {
#             PeerLink(10, 11),
#             PeerLink(12, 13),
#             PeerLink(11, 14),
#             PeerLink(13, 15),
#             PeerLink(15, 16),
#         }
#     ),
#     customer_provider_links=frozenset(
#         [
#             # Core Attack and Victim Links
#             CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
#             CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),

#             # Hierarchical connections with interdependencies
#             CPLink(provider_asn=3, customer_asn=1),
#             CPLink(provider_asn=4, customer_asn=2),
#             CPLink(provider_asn=3, customer_asn=4),  # Creating interdependence
#             CPLink(provider_asn=5, customer_asn=3),
#             CPLink(provider_asn=6, customer_asn=5),

 

#             # Reflectors connected across various levels
#             CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=9),
#             CPLink(provider_asn=ASNs.REFLECTOR.value, customer_asn=10),
#             CPLink(provider_asn=9, customer_asn=7),
#             CPLink(provider_asn=10, customer_asn=8),

#             # Connections linking different parts of the network
#             CPLink(provider_asn=11, customer_asn=5),
#             CPLink(provider_asn=12, customer_asn=11),
#             CPLink(provider_asn=13, customer_asn=9),
#             CPLink(provider_asn=14, customer_asn=12),
#         ]
#     ),
#     diagram_ranks=(
#         (ASNs.ATTACKER.value, ASNs.VICTIM.value),
#         (1, 2),
#         (3, 4, 5),
#         (9, 10, 11),
#         (12, 13, 14, 15, 16),
#         (ASNs.REFLECTOR.value,),
#     ),
# )