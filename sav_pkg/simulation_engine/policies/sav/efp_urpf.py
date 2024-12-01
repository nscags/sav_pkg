from .base_sav_policy import BaseSAVPolicy


class EnhancedFeasiblePathuRPF(BaseSAVPolicy):
    name: str = "EFP uRPF"

    @staticmethod
    def validate(as_obj, source_prefix, prev_hop, engine, scenario):
        # The EFP-uRPF method with Algorithm B SHOULD be applied on customer interfaces.
        if prev_hop.asn in (as_obj.peer_asns | as_obj.provider_asns):
            return True
        else:
            # Create the set of all directly connected customer interfaces.
            # Call it Set I = {I1, I2, ..., Ik}.
            I = as_obj.customer_asns

            # Create the set of all unique prefixes for which routes exist in Adj-RIBs-In
            # for the interfaces in Set I. Call it Set P = {P1, P2, ..., Pm}.

            # Create the set of all unique origin ASes seen in the routes that exist in Adj-RIBs-In
            # for the interfaces in Set I. Call it Set A = {AS1, AS2, ..., ASn}.
            P = set()
            A = set()
            for customer_asn in I:
                for prefix, ann_info in as_obj.policy._ribs_in.data.get(
                    customer_asn, {}
                ).items():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ):
                        P.add(prefix)
                        A.add(ann_info.unprocessed_ann.origin)

            # Create the set of all unique prefixes for which routes exist in Adj-RIBs-In
            # of all lateral peer and transit provider interfaces such that each of the routes
            # has its origin AS belonging in Set A. Call it Set Q = {Q1, Q2, ..., Qj}.
            Q = set()
            for peer_asn in as_obj.peer_asns:
                for prefix, ann_info in as_obj.policy._ribs_in.data.get(
                    peer_asn, {}
                ).items():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ):
                        if ann_info.unprocessed_ann.origin in A:
                            Q.add(prefix)

            for provider_asn in as_obj.provider_asns:
                for prefix, ann_info in as_obj.policy._ribs_in.data.get(
                    provider_asn, {}
                ).items():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ):
                        if ann_info.unprocessed_ann.origin in A:
                            Q.add(prefix)

            # Then, Set Z = Union(P,Q) is the RPF list that is applied for every customer interface in Set I.
            Z = P.union(Q)

            return source_prefix in Z
