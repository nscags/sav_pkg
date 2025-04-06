import random
from frozendict import frozendict

from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement as Ann

from sav_pkg.utils.utils import get_e2s_asn_provider_weight_dict, get_e2s_asn_provider_prepending_dict
from sav_pkg.enums import Prefixes


class BGPExport2Some(BGP):
    name: str = "BGP E2S"

    def _provider_export_control(
        self
    ) -> set:  
        DEFAULT_EXPORT_WEIGHT = 0.5739

        e2s_asn_provider_weight_dict: frozendict = get_e2s_asn_provider_weight_dict(self.as_.asn)

        providers = self.as_.provider_asns

        export_set = set()
        for provider in providers:
            # if provider doesn't have a weight
            # due to differences between measurement data and CAIDA topology
            # default to the avg percent of of providers exported to per AS
            weight = (e2s_asn_provider_weight_dict or {}).get(provider, DEFAULT_EXPORT_WEIGHT)
            if random.random() < weight:
                export_set.add(provider)

        if export_set:
            return export_set

        # Ensure that at least one provider is selected
        if e2s_asn_provider_weight_dict:
            valid_weights = {p: e2s_asn_provider_weight_dict.get(p, DEFAULT_EXPORT_WEIGHT) for p in providers}
            if valid_weights:
                providers_list = list(valid_weights.keys())
                weights_list = list(valid_weights.values())
                if sum(weights_list) > 0:
                    export_set.add(random.choices(providers_list, weights=weights_list, k=1)[0])
                else:
                    # All weights are 0, just pick one provider at random
                    # I don't know if this is an error somewhere in my code or if its the data (probably not)
                    # but this is needed to prevent errors
                    # if all weights are 0, then an AS would export to none of its providers
                    # for a mh AS, this doesn't really make sense 
                    # (technically mh includes peer interfaces, so it could work)
                    export_set.add(random.choice(providers_list))
        else:
            export_set.add(random.choice(providers))

        return export_set

    def _path_prepending(
        self,
        provider,
    ) -> bool:
        
        e2s_asn_provider_path_prepending_dict: frozendict = get_e2s_asn_provider_prepending_dict(self.as_.asn)

        if not e2s_asn_provider_path_prepending_dict:
            return False
        
        prepending_list = e2s_asn_provider_path_prepending_dict.get(provider.asn)
        if not prepending_list:
            return False
        
        if len(prepending_list) > 1:
            return random.choice(prepending_list)
        else:
            return prepending_list[0]

    def _propagate(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None:
        """
        Modified propagtion logic to export to subset of providers
        """

        if propagate_to.value == Relationships.PROVIDERS.value:
            neighbors = self.as_.providers
            if not neighbors:
                return
            some_neighbors_asns = self._provider_export_control()
            some_neighbors = [neighbor for neighbor in neighbors if neighbor.asn in some_neighbors_asns]

            for _prefix, unprocessed_ann in self._local_rib.items():
                if neighbors and unprocessed_ann.recv_relationship in send_rels:
                    ann = unprocessed_ann.copy({"next_hop_asn": self.as_.asn})
                else:
                    continue

                for neighbor in some_neighbors:
                    if ann.recv_relationship in send_rels and not self._prev_sent(
                        neighbor, ann
                    ):
                        ann2 = ann
                        if self._path_prepending(neighbor):
                            as_path = (self.as_.asn, self.as_.asn,) + ann.as_path
                            ann2 = ann.copy({"as_path": as_path})
                        self._process_outgoing_ann(neighbor, ann2, propagate_to, send_rels)

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
        # NOTE: using this method means victim MUST use dedicated prefix
        if ann.recv_relationship == Relationships.ORIGIN and ann.prefix == Prefixes.VICTIM.value:
            other_ann = ann.copy({"prefix": "9.9.0.0/16"})
        else:
            other_ann = ann
        
        e2s_asn_provider_weight_dict: frozendict = get_e2s_asn_provider_weight_dict(self.as_.asn)
        for neighbor in other_neighbors:
            # If the neighbor is weighted with 0, do not export anything to them
            if e2s_asn_provider_weight_dict.get(neighbor.asn) == 0:
                continue
            # Victim/Legit Sender AS propagates a new announcement with separate prefix to all providers which
            # did not recieve the original announcement
            # some policies use route info from any prefix (but same origin AS) to create rpf list
            if ann.recv_relationship in send_rels and not self._prev_sent(
                neighbor, other_ann
            ):
                # though transit ASes can perform path prepending, we only have measurement data for origin ASes
                other_ann2 = other_ann
                if (self._path_prepending(neighbor) 
                    and ann.recv_relationship == Relationships.ORIGIN 
                    and ann.prefix == Prefixes.VICTIM.value
                ):
                    as_path = (self.as_.asn, self.as_.asn,) + ann.as_path
                    other_ann2 = other_ann.copy({"as_path": as_path})

                self._process_outgoing_ann(neighbor, other_ann2, propagate_to, send_rels)