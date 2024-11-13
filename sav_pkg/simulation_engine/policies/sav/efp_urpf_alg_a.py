from .base_sav_policy import BaseSAVPolicy
from .loose_urpf import LooseuRPF

class EnhancedFeasiblePathuRPFAlgA(BaseSAVPolicy):
    name: str = "EFP uRPF Alg A"

    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):
        if prev_hop.asn in as_obj.provider_asns:
            return LooseuRPF(
                as_obj=as_obj,
                prev_hop=prev_hop,
                origin=origin,
                engine=engine
            )
        else:
            # Create the set of unique origin ASes considering only the routes in the Adj-RIBs-In 
            # of customer interfaces. Call it Set A = {AS1, AS2, ..., ASn}.
            A = set()
            for customer_asn in as_obj.customer_asns:
                for ann_info in as_obj.policy._ribs_in.data.get(customer_asn, {}).values():
                    origin_asn = ann_info.unprocessed_ann.as_path[-1]
                    A.add(origin_asn)
            # Considering all routes in Adj-RIBs-In for all interfaces (customer, lateral peer, and transit provider),
            # form the set of unique prefixes that have a common origin AS1. Call it Set X1.
            for origin_asn in A: 
                for prefix, ann_info in as_obj.policy._ribs_in.data.items():
                    origin_asn_ = ann_info.unprocessed_ann.as_path[-1]
                    if origin_asn_ == origin_asn:
                        pass
            # Include Set X1 in the RPF list on all customer interfaces on which one or more of the prefixes 
            # in Set X1 were received.

            # Repeat Steps 2 and 3 for each of the remaining ASes in Set A (i.e., for ASi, where i = 2, ..., n).
            raise NotImplementedError