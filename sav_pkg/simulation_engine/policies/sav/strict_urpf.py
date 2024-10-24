from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import Prefixes

class StrictuRPF(BaseSAVPolicy):
    name: str = "Strict uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):
        """
        Validates incoming packets based on Strict uRPF.

        Parameters:
        - as_obj: The AS object representing the current AS.
        - prev_hop: The AS object representing the previous hop (neighbor from which the packet arrived).
        - origin: The origin ASN of the packet.
        - engine: The simulation engine.

        Returns:
        - True if the packet is accepted according to Strict uRPF.
        - False if the packet is dropped.
        """
        # Strict uRPF is applied to only customer and peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            # Get announcement to source address
            for ann in as_obj.policy._local_rib.data.values():
                if ann.prefix == Prefixes.VICTIM.value and ann.next_hop_asn == prev_hop.asn:
                    return True
                
            return False