import ipaddress
from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class EFP_A(BaseSAVPolicy):
    name: str = "EFP-A"

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Enhanced Feasible-Path uRPF Algorithm A.
        """
        # Create the set of unique origin ASes considering only the routes in the Adj-RIBs-In of customer interfaces.
        # Call it Set A = {AS1, AS2, ..., ASn}.
        A = set()
        for customer_asn in as_obj.customer_asns:
            for prefix, ann_info in as_obj.policy._ribs_in.data.get(
                customer_asn, {}
            ).items():
                if as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    A.add(ann_info.unprocessed_ann.origin)

        # Considering all routes in Adj-RIBs-In for all interfaces (customer, lateral peer, and transit provider),
        # form the set of unique prefixes that have a common origin AS1. Call it Set X1.

        # Repeat Steps 2 and 3 for each of the remaining ASes in Set A (i.e., for ASi, where i = 2, ..., n).
        X = dict()
        for origin_asn in A:
            X[origin_asn] = set()
            for customer_asn, prefix_dict in as_obj.policy._ribs_in.data.items():
                for prefix, ann_info in prefix_dict.items():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ) and ann_info.unprocessed_ann.origin == origin_asn:
                        X[origin_asn].add(ann_info.unprocessed_ann.prefix)

        # Include Set X1 in the RPF list on all customer interfaces on which one or
        # more of the prefixes in Set X1 were received.

        rpf_list = set()
        for prefix, ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).items():
            if as_obj.policy._valid_ann(
                ann_info.unprocessed_ann, ann_info.recv_relationship
            ):
                for xi in X.values():
                    if prefix in xi:
                        rpf_list.update(xi)

        src_prefix = ipaddress.ip_network(source_prefix)
        return any(src_prefix.subnet_of(ipaddress.ip_network(prefix)) for prefix in rpf_list)
