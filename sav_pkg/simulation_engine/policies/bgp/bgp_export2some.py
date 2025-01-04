from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.shared.enums import Relationships

class BGPExport2Some(BGP):
    name: str = "BGP Export2Some"
        
    def _propagate(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None:
        """Propogates announcements from local rib to other ASes

        send_rels is the relationships that are acceptable to send
        """

        # percent of providers to export to 
        percent = 0.5 

        if propagate_to.value == Relationships.PROVIDERS.value:
            neighbors = self.as_.providers

            num = max(1, int(len(neighbors) * percent))
            some_neighbors = sorted(neighbors, key=lambda n: n.asn)[:num]

            for _prefix, unprocessed_ann in self.local_rib.items():
                if neighbors and unprocessed_ann.recv_relationship in send_rels:
                    ann = unprocessed_ann.copy({"next_hop_asn": self.as_.asn})
                else:
                    continue

                for neighbor in some_neighbors:
                    if ann.recv_relationship in send_rels and not self._prev_sent(
                        neighbor, ann
                    ):
                        self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
        else:
            super()._propagate(propagate_to, send_rels)