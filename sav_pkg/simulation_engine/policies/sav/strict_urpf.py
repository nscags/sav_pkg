from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import ASNs

class StrictuRPF(BaseSAVPolicy):
    name: str = "Strict uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):
        # Strict uRPF is applied to only customer and peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            # Get announcement to source address
            for ann in as_obj.policy._local_rib.data.values():
                # TODO: this should really be checked by prefix not ASN
                if ann.as_path[-1] == ASNs.VICTIM.value and ann.next_hop_asn == prev_hop.asn:
                    return True
                
            return False