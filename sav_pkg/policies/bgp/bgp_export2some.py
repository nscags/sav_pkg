import random
# import math

from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement as Ann


class BGPExport2Some(BGP):
    name: str = "BGP E2S"
        
    def _propagate(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None:
        """
        Modified propagtion logic to export to subset of providers
        Providers are selected randomly
        No export to remaining providers
        """

        # Based on measurement data, e2s ASes export prefixes to 57.39% of providers
        percent = 0.5739

        if propagate_to.value == Relationships.PROVIDERS.value:
            neighbors = self.as_.providers

            # No providers, return else raise error
            if not neighbors:
                return
            
            # AS must export to at least one provider
            num = max(1, int(len(neighbors) * percent))
            # num = math.ceil(len(neighbors) * percent)
            
            # https://stackoverflow.com/a/15837796/8903959
            some_neighbors = random.sample(tuple(neighbors), num)

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

                other_neighbors = [n for n in neighbors if n not in some_neighbors]
                self._propagate_to_others(propagate_to, send_rels, other_neighbors, ann)
        else:
            super()._propagate(propagate_to, send_rels)

    def _propagate_to_others(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
        other_neighbors: set,
        ann: Ann,
    ):
        """
        propagation logic for remaining providers which did not recieve the announcement
        """
        pass