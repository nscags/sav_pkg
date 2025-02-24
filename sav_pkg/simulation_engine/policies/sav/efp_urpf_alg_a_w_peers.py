from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework import SAVScenario


class EnhancedFeasiblePathuRPFAlgAwPeers(BaseSAVPolicy):
    name: str = "EFP uRPF Alg A w Peers"
    
    @staticmethod
    def validate(
        as_obj: "AS", 
        source_prefix: str, 
        prev_hop: "AS", 
        engine: "SimulationEngine", 
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Enhanced Feasible-Path uRPF Algorithm A
        with extension to include peer interfaces.

        In RFC 8704, the authors reference that EFP Alg A can be extended to apply to 
        peer interfaces. This extension seems fairly straightforward, we simply will consider
        peers in the first step (creating set A), and apply rpf list to customer and peer interfaces
        """
        # Create the set of unique origin ASes considering only the routes in the Adj-RIBs-In of 
        # customer and peer interfaces. Call it Set A = {AS1, AS2, ..., ASn}.
        A = set()
        for asn in (as_obj.customer_asns | as_obj.peer_asns):
            for prefix, ann_info in as_obj.policy._ribs_in.data.get(
                asn, {}
            ).items():
                if as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    A.add(ann_info.unprocessed_ann.origin)
        
        # Considering all routes in Adj-RIBs-In for all interfaces (customer, lateral peer, and transit provider), 
        # form the set of unique prefixes that have a common origin AS1. Call it Set X1.

        # Include Set X1 in the RPF list on all customer and peer interfaces on which one or 
        # more of the prefixes in Set X1 were received.

        # Repeat Steps 2 and 3 for each of the remaining ASes in Set A (i.e., for ASi, where i = 2, ..., n).
        X = dict()
        for origin_asn in A:
            X[origin_asn] = set()
            for _asn, prefix_dict in as_obj.policy._ribs_in.data.items():
                for prefix, ann_info in prefix_dict.items():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ) and ann_info.unprocessed_ann.origin == origin_asn:
                        X[origin_asn].add(ann_info.unprocessed_ann.prefix)

        rpf_list = set()
        for prefix, ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).items():
            if as_obj.policy._valid_ann(
                ann_info.unprocessed_ann, ann_info.recv_relationship
            ):
                for xi in X.values():
                    if prefix in xi:
                        rpf_list.update(xi)

        return source_prefix in rpf_list
                