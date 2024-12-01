from .feasible_path_urpf import FeasiblePathuRPF


class FeasiblePathuRPFOnlyCustomers(FeasiblePathuRPF):
    name: str = "FP uRPF Only Customers"

    @staticmethod
    def validate(as_obj, source_prefix, prev_hop, engine, scenario):
        """
        Validates incoming packets based on Feasible-Path uRPF.
        Applied only to customer interfaces
        """
        if prev_hop.asn in as_obj.customer_asns:
            return FeasiblePathuRPF.validate(as_obj, source_prefix, prev_hop, engine, scenario)
        else:
            return True