from typing import Optional, TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp.bgp_full.propagate_funcs import _propagate, _process_outgoing_ann, _prev_sent, _send_anns
from bgpy.simulation_engine.policies.bgp.bgp_full.process_incoming_funcs import process_incoming_anns, _new_ann_better, _process_incoming_withdrawal, _select_best_ribs_in, _withdraw_ann_from_neighbors

from bgpy.simulation_engine.ann_containers import RIBsIn
from bgpy.simulation_engine.ann_containers import RIBsOut
from bgpy.simulation_engine.ann_containers import SendQueue
from bgpy.simulation_engine import BGPFull

if TYPE_CHECKING:
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPFullwSAV(BGPFull):
    name = "BGP Full"

    def __init__(
        self,
        *args,
        _ribs_in: Optional[RIBsIn] = None,
        _ribs_out: Optional[RIBsOut] = None,
        _send_q: Optional[SendQueue] = None,
        source_address_validation_policy = None,
        **kwargs,
    ):
        super().__init__(
            *args, 
            _ribs_in=_ribs_in, 
            _ribs_out=_ribs_out, 
            _send_q=_send_q, 
            **kwargs
        )
        self.source_address_validation_policy = source_address_validation_policy