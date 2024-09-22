from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import ASNs

class EnhancedFeasiblePath(BaseSAVPolicy):
    name: str = "EFP uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, engine, as_path):
        # EFP uRPF is applied to only customer and peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            for prefix, ann_info in as_obj.policy._ribs_in.data.get(prev_hop.asn, {}).items():
                ann = ann_info.unprocessed_ann
                if ann.as_path[-1] == ASNs.VICTIM.value:
                    return True
            return False
        
            # this might be wrong, we should be looking in the dict where prev_hop = neighbor_asn
        
            # the above code may be more correct for EFP uRPF
            # any prefix from the same origin AS should be accepted on any of the recieved interfaces
            # i.e. prefix doesn't matter, all are accepted, can just look at origin AS
            # For basic feasible path, we should consider just a single prefix (won't change graphs)

            # Interface, Origin AS, prefix
            # For each Origin AS,
            # keep track of prefixes and interfaces you recieve said prefixes
            # Any prefix on any of the interface recieved should be accepted
            # i.e. if you get multiple prefixes from the same origin AS on multiple interfaces
            # then any of those prefixes should be accepted on any of those interfaces
            # origin_prefix_dict = dict()
            # for neighbor_asn, prefix_dict in as_obj.policy._ribs_in.data.items():
            #     if neighbor_asn in as_obj.customer_asns:
            #         for prefix, ann_info in prefix_dict.items():
            #             ann = ann_info.unprocessed_ann
            #             origin_asn = ann.as_path[-1]
            #             if origin_asn not in origin_prefix_dict:
            #                 origin_prefix_dict[origin_asn] = set()

            # for neighbor_asn, prefix_dict in as_obj.policy._ribs_in.data.items():
            #     for prefix, ann_info in prefix_dict.items():
            #         ann = ann_info.unprocessed_ann
            #         origin_asn = ann.as_path[-1]
            #         if origin_asn in origin_prefix_dict:
            #             origin_prefix_dict[origin_asn].add(prefix)
            