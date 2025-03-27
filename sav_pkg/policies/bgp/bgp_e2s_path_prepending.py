from .bgp_export2some import BGPExport2Some

from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement as Ann

# from sav_pkg.enums import Prefixes


class BGPExport2SomePathPrepending(BGPExport2Some):
    name: str = "BGP E2S Path Prepending"

    def _propagate_to_others(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
        other_neighbors: set,
        ann: Ann,
    ):
        # path prepending can be done by transit ASes
        as_path = (self.as_.asn, self.as_.asn,) + ann.as_path
        other_ann = ann.copy({"as_path": as_path})
        
        for neighbor in other_neighbors:
            # Victim/Legit Sender AS propagates a new announcement with path prepending to all providers which
            # did not recieve the original announcement
            if ann.recv_relationship in send_rels and not self._prev_sent(
                neighbor, other_ann
            ):
                self._process_outgoing_ann(neighbor, other_ann, propagate_to, send_rels)