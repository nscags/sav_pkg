from bgpy.simulation_engine import ROVFull
from bgpy.simulation_engine.ann_containers import RIBsIn, RIBsOut, SendQueue

class ROVFullwSAV(ROVFull):
    name: str = "ROVFull"

    def __init__(self, 
                 *args, 
                 _ribs_in: RIBsIn | None = None, 
                 _ribs_out: RIBsOut | None = None, 
                 _send_q: SendQueue | None = None, 
                 source_address_validation_policy = None, 
                 **kwargs):
        self.source_address_validation_policy = source_address_validation_policy
        super().__init__(*args, _ribs_in=_ribs_in, _ribs_out=_ribs_out, _send_q=_send_q, **kwargs)