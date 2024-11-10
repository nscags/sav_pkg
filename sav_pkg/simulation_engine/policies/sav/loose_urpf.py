from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import Prefixes

class LooseuRPF(BaseSAVPolicy):
    name: str = "Loose uRPF"

    @staticmethod
    def validate(as_obj, prev_hop, origin, engine):
        for ann in as_obj.policy._local_rib.data.values():
            if ann.prefix == Prefixes.VICTIM.value:
                return True
