from .base_sav_policy import BaseSAVPolicy

class StrictuRPF(BaseSAVPolicy):
    name: str = "Strict-uRPF"

    def validate(self, as_obj, prev_hop, source):
        # Strict uRPF is applied to only customer and peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            # Get announcement to source address
            for ann in as_obj.policy._local_rib.data.values():
                if ann.as_path[-1] == source:
                    source_ann = ann

            if source_ann is None:
                raise TypeError

            # check if interfaces match (symmetric route)
            if source_ann.next_hop_asn == prev_hop.asn:
                return True
            else:
                # raise ValueError(f"{source_ann.next_hop_asn}, {prev_hop.asn}")
                return False