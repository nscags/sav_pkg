from bgpy.simulation_engine import BGP
from bgpy.enums import Relationships 


class BGPExport2Some(BGP):
    name: str = "BGP E2S"
        
    def _propagate(
        self: "BGP",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None:
        """Propogates announcements from local rib to other ASes

        send_rels is the relationships that are acceptable to send
        """

        if propagate_to.value == Relationships.PROVIDERS.value:
            neighbors = self.as_.providers

            for prefix, unprocessed_ann in self._local_rib.items():
                if neighbors and unprocessed_ann.recv_relationship in send_rels:
                    ann = unprocessed_ann.copy({"next_hop_asn": self.as_.asn})
            
            for i, neighbor in enumerate(neighbors):
                ann = ann.copy({"prefix": f"7.7.{7+i}.0/24"})
                # print(f"\nBGPE2S: \nAnn: \n{ann} \n{neighbor}")
                if not self._prev_sent(neighbor, ann):
                    self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)