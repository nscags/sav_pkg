from .base_sav_policy import BaseSAVPolicy


class LooseuRPF(BaseSAVPolicy):
    name: str = "Loose uRPF"

    @staticmethod
    def validate(as_obj, source_prefix, prev_hop, engine, scenario):
        for ann in as_obj.policy._local_rib.data.values():
            if ann.prefix == source_prefix:
                return True
        return False
