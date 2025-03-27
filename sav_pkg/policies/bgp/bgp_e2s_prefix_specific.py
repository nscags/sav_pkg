from .bgp_export2some import BGPExport2Some

from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement as Ann

from sav_pkg.enums import Prefixes


class BGPExport2SomePrefixSpecific(BGPExport2Some):
    name: str = "BGP E2S Prefix Specific"

    def _propagate_to_others(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
        other_neighbors: set,
        ann: Ann,
    ):
        # NOTE: using this method means victim MUST use dedicated prefix
        if ann.recv_relationship == Relationships.ORIGIN and ann.prefix == Prefixes.VICTIM.value:
            other_ann = ann.copy({"prefix": "9.9.0.0/16"})
        else:
            other_ann = ann
        
        for neighbor in other_neighbors:
            # Victim/Legit Sender AS propagates a new announcement with separate prefix to all providers which
            # did not recieve the original announcement
            # some policies use route info from any prefix (but same origin AS) to create rpf list
            if ann.recv_relationship in send_rels and not self._prev_sent(
                neighbor, other_ann
            ):
                self._process_outgoing_ann(neighbor, other_ann, propagate_to, send_rels)