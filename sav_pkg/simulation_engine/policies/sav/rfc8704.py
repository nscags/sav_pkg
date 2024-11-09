from .base_sav_policy import BaseSAVPolicy
from .efp_urpf import EnhancedFeasiblePathuRPF
from .strict_urpf import StrictuRPF

class RFC8704(BaseSAVPolicy):
    name: str = "RFC8704"

    def validate(self, as_obj, prev_hop, origin, engine):
        """
        Validates packets based on security recommendations listed in RFC 8704
        

        "For a directly connected single-homed stub AS (customer), 
        the AS under consideration SHOULD perform SAV based on the strict uRPF method.
        
        For all other scenarios:    
        - The EFP-uRPF method with Algorithm B (see Section 3.4) SHOULD be applied on customer interfaces.
        - The loose uRPF method SHOULD be applied on lateral peer and transit provider interfaces."
        """
        raise NotImplementedError