from .base_sav_policy import BaseSAVPolicy

class StrictuRPF(BaseSAVPolicy):
    name: str = "Strict uRPF"

    @staticmethod
    def validate(as_obj, source_prefix, prev_hop, engine, scenario):
        """
        Validates incoming packets based on Strict uRPF.
        """
        # Strict uRPF is applied to only customer and peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            for prefix, ann in as_obj.policy._local_rib.data.items():
                if prefix == source_prefix and ann.next_hop_asn == prev_hop.asn:
                    return True
                
            return False