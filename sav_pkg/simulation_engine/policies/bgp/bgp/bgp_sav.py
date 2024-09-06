from typing import Any, Optional, TYPE_CHECKING

from bgpy.simulation_engine.ann_containers import LocalRIB
from bgpy.simulation_engine.ann_containers import RecvQueue
from bgpy.simulation_engine.policies import BGP

if TYPE_CHECKING:
    from bgpy.as_graphs import AS


class BGPwSAV(BGP):
    name: str = "BGP"

    def __init__(
        self,
        _local_rib: Optional[LocalRIB] = None,
        _recv_q: Optional[RecvQueue] = None,
        as_: Optional["AS"] = None,
        source_address_validation_policy = None
    ) -> None:
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph

        This is also useful for regenerating an AS from YAML
        """

        super().__init__(_local_rib=_local_rib, _recv_q=_recv_q, as_=as_)
        self.source_address_validation_policy = source_address_validation_policy