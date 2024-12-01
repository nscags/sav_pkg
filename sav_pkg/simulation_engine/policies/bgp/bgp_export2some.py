from bgpy.simulation_engine import BGP, Policy, Announcement as Ann
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
        elif propagate_to.value == Relationships.PEERS.value:
            neighbors = self.as_.peers
        elif propagate_to.value == Relationships.CUSTOMERS.value:
            neighbors = self.as_.customers
        else:
            raise NotImplementedError

        for prefix, unprocessed_ann in self._local_rib.items():
            # Starting in v4 we must set the next_hop when sending
            # Copying announcements is a bottleneck for sims,
            # so we try to do this as little as possible
            if neighbors and unprocessed_ann.recv_relationship in send_rels:
                ann = unprocessed_ann.copy({"next_hop_asn": self.as_.asn})
            else:
                continue

            for neighbor in neighbors:
                if ann.recv_relationship in send_rels and not self._prev_sent(
                    neighbor, ann
                ):
                    # Policy took care of it's own propagation for this ann
                    if self._policy_propagate(neighbor, ann, propagate_to, send_rels):
                        continue
                    else:
                        self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)