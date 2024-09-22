from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import Prefixes

class FeasiblePathuRPF(BaseSAVPolicy):
    name: str = "Feasible-Path uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, engine, as_path):  
        
        # Feasible-Path uRPF is applied to only customer and peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            for prefix, ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).items():
                if prefix == Prefixes.VICTIM.value:
                    return True
            return False