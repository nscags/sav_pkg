from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.enums import Relationships

from sav_pkg.enums import Prefixes


class BGPExport2SomePrefixSpecific(BGP):
    name: str = "BGP E2S PS"
    
    def _propagate(
        self: "BGPExport2SomePrefixSpecific",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None:
        """Propogates announcements from local rib to other ASes

        send_rels is the relationships that are acceptable to send
        """

        # percent of providers to export to 
        # Measurement of routes from RIPE route collectors showed that
        # on average an AS which does not export to all will export to
        # 56.22% of their providers 
        # NOTE: this measurement is not entirely accurate
        percent = 0.5622

        if propagate_to.value == Relationships.PROVIDERS.value:
            neighbors = self.as_.providers

            num = max(1, int(len(neighbors) * percent))
            some_neighbors = sorted(neighbors, key=lambda n: n.asn)[:num]

            for _prefix, unprocessed_ann in self._local_rib.items():
                if neighbors and unprocessed_ann.recv_relationship in send_rels:
                    ann = unprocessed_ann.copy({"next_hop_asn": self.as_.asn})
                else:
                    continue

                for neighbor in some_neighbors:
                    if ann.recv_relationship in send_rels and not self._prev_sent(
                        neighbor, ann
                    ):
                        self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
                
                # NOTE: Prefix Specific Export-to-Some requires Victim/Legit Sender to originate default prefix
                if ann.recv_relationship == Relationships.ORIGIN and ann.prefix == Prefixes.VICTIM.value:
                    other_ann = ann.copy({"prefix": "9.9.0.0/16"})
                else:
                    other_ann = ann
                
                for neighbor in neighbors:
                    if neighbor not in some_neighbors:
                        # Victim/Legit Sender AS propagates a new announcement with separate prefix to all providers which
                        # did not recieve the original announcement
                        # some policies use route info from any prefix (but same origin AS) to create rpf list
                        if ann.recv_relationship in send_rels and not self._prev_sent(
                            neighbor, other_ann
                        ):
                            self._process_outgoing_ann(neighbor, other_ann, propagate_to, send_rels)
        else:
            super()._propagate(propagate_to, send_rels)