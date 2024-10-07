from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import Prefixes

class FeasiblePathuRPF(BaseSAVPolicy):
    name: str = "Feasible-Path uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):  
        
        # Feasible-Path uRPF is applied to only customer and peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            # check local rib to see if it contains a path to the IP address through
            # the interface you recieved the packet
            # this will always be the victim's IP address because either the packet was
            # sent by a legitimate sender (victim) or the packet was sent by the attacker
            # using a spoofed IP address (IP address of the victim/legit sender)
            for prefix, ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).items():
                if prefix == Prefixes.VICTIM.value:
                    return True
            return False