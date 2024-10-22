from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import ASNs, Prefixes

class EnhancedFeasiblePathuRPF(BaseSAVPolicy):
    name: str = "EFP uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):
        # EFP uRPF is applied to only customer
        if (prev_hop.asn in as_obj.provider_asns or
            prev_hop.asn in as_obj.peer_asns):
            return True
        else:
            # Create the set of all directly connected customer interfaces. 
            # Call it Set I = {I1, I2, ..., Ik}.
            i = set(as_obj.customer_asns)

            # Create the set of all unique prefixes for which routes exist in Adj-RIBs-In 
            # for the interfaces in Set I. Call it Set P = {P1, P2, ..., Pm}.
            p = set()
            # Create the set of all unique origin ASes seen in the routes that exist in Adj-RIBs-In 
            # for the interfaces in Set I. Call it Set A = {AS1, AS2, ..., ASn}.
            a = set()
            for customer_asn in i:
                for prefix, ann_info in as_obj.policy._ribs_in.data.get(customer_asn, {}).items():
                    p.add(prefix)
                    
                    ann = ann_info.unprocessed_ann
                    origin_ = ann.as_path[-1]
                    a.add(origin_)

            # Create the set of all unique prefixes for which routes exist in Adj-RIBs-In 
            # of all lateral peer and transit provider interfaces such that each of the routes 
            # has its origin AS belonging in Set A. Call it Set Q = {Q1, Q2, ..., Qj}.
            q = set()
            for peer_asn in as_obj.peer_asns:
                for prefix, ann_info in as_obj.policy._ribs_in.data.get(peer_asn, {}).items():
                    ann = ann_info.unprocessed_ann
                    origin_ = ann.as_path[-1]

                    if origin_ in a:
                        q.add(prefix)
            
            for provider_asn in as_obj.provider_asns:
                for prefix, ann_info in as_obj.policy._ribs_in.data.get(provider_asn, {}).items():
                    ann = ann_info.unprocessed_ann
                    origin_ = ann.as_path[-1]

                    if origin_ in a:
                        q.add(prefix)

            # Then, Set Z = Union(P,Q) is the RPF list that is applied for every customer interface in Set I.
            z = p.union(q)

            # previous hop not in customer interfaces
            if prev_hop.asn not in i:
                return False
            
            # TODO: This should be any address within the victim's prefix
            # prefix not in allowed set (will always be victim prefix)
            if Prefixes.VICTIM.value not in z:
                return False
            # origin not in allowed set
            if origin not in a:
                return False
            
            return True
            

            






