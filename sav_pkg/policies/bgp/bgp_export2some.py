import random
import math

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

        # TODO: rewite, should select providers randomly
        #       percentage of providers should be based on measurement data
        #       sorta need a variety of options
        #       you have to export to a minimum of 1, but the percent of providers exported to is unknown currently

        percent = 0.50

        if propagate_to.value == Relationships.PROVIDERS.value:
            neighbors = self.as_.providers

            num = math.ceil(len(neighbors) * percent)
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
                self._other_propagate(propagate_to, send_rels, other_neighbors, ann)
        else:
            super()._propagate(propagate_to, send_rels)

    def _other_propagate(
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