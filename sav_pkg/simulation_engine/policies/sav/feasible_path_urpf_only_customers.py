from .feasible_path_urpf import FeasiblePathuRPF

class FeasiblePathuRPFOnlyCustomers(FeasiblePathuRPF):
    name: str = "FP uRPF Only Customers"
    
    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):
        # For this version of FP we aren't validating packets received on peer interfaces
        # i.e. only customer interfaces
        # this is so we can compared results with EFP uRPF
        if prev_hop.asn in as_obj.peer_asns:
            return True
        else:
            return FeasiblePathuRPF.validate(as_obj, prev_hop, origin, engine)
