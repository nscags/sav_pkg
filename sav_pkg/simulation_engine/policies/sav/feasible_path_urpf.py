from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import Prefixes

class FeasiblePathuRPF(BaseSAVPolicy):
    name: str = "Feasible-Path uRPF"

    @staticmethod
    def validate(as_obj, source_prefix, prev_hop, engine, scenario):  
        """
        Validates incoming packets based on Feasible-Path uRPF.
        """
        # Feasible-Path uRPF is applied to only customer and peer interfaces
        if prev_hop.asn in as_obj.provider_asns:
            return True
        else:
            # Get all prefixes announced by the previous hop 
            # Check if the source IP belongs to any of these prefixes
            # print(as_obj.policy._ribs_in, flush=True)
            # print(as_obj.asn)
            for ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).values(): 
                if (as_obj.policy._valid_ann(ann_info.unprocessed_ann, ann_info.recv_relationship) 
                    and ann_info.unprocessed_ann.prefix == source_prefix):
                    return True
            return False