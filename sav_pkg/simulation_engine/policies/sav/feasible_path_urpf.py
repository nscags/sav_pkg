from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import Prefixes

class FeasiblePathuRPF(BaseSAVPolicy):
    name: str = "Feasible-Path uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):  
        """
        Validates incoming packets based on Feasible-Path uRPF.

        Parameters:
        - as_obj: The AS object representing the current AS.
        - prev_hop: The AS object representing the previous hop (neighbor from which the packet arrived).
        - origin: The origin ASN of the packet.
        - engine: The simulation engine.

        Returns:
        - True if the packet is accepted according to Feasible-Path uRPF.
        - False if the packet is dropped.
        """
        # Feasible-Path uRPF is applied to only customer and peer interfaces
        # Allow all traffic from provider ASNs
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            # Convert the source IP to an IPv4Address object
            source_ip = Prefixes.VICTIM.value
            # Get all prefixes announced by the previous hop
            prefixes = as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).keys()
            # Check if the source IP belongs to any of these prefixes
            for prefix in prefixes:
                if source_ip == prefix:
                    return True
            return False