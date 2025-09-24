import random

from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement as Ann
from bgpy.simulation_engine.policies.bgp import BGP

from sav_pkg.enums import Prefixes
from sav_pkg.utils.utils import get_traffic_engineering_behaviors_dict



class BGPExport2Some(BGP):
    name: str = "BGP E2S"

    DEFAULT_EXPORT_RATIO = 0.5
    traffic_engineering_behaviors_dict = get_traffic_engineering_behaviors_dict()

    def _propagate(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> None:
        """
        Modified propagtion logic to export to subset of providers
        """
        # export to some (providers), i.e. export-to-some is only applied to provider interfaces
        # remaining customer+peer interfaces are export-to-all
        if propagate_to.value == Relationships.PROVIDERS.value:
            neighbors = self.as_.providers
            if not neighbors: # no neighbors, bye bye
                return
            # Decide the "some" neighbors to export to,
            # this is based off weights assigned from measurement data
            some_neighbors_asns = self._provider_export_control()
            some_neighbors = [neighbor for neighbor in neighbors if neighbor.asn in some_neighbors_asns]

            for _prefix, unprocessed_ann in self._local_rib.items():
                if some_neighbors and unprocessed_ann.recv_relationship in send_rels:
                    ann = unprocessed_ann.copy({"next_hop_asn": self.as_.asn})
                else:
                    continue

                for neighbor in some_neighbors:
                    if ann.recv_relationship in send_rels and not self._prev_sent(
                        neighbor, ann
                    ):
                        ann2 = ann
                        # add path prepending based on measurement data
                        if (self._path_prepending(neighbor)
                            and ann.recv_relationship == Relationships.ORIGIN
                            and ann.prefix in [Prefixes.VICTIM.value, Prefixes.ANYCAST_SERVER.value, Prefixes.EDGE_SERVER.value]
                        ):
                            # avg = 3
                            # as_path = (self.as_.asn, self.as_.asn, self.as_.asn) + ann.as_path
                            # upper 99th percentile = 8
                            as_path = (self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn) + ann.as_path
                            ann2 = ann.copy({"as_path": as_path})
                        self._process_outgoing_ann(neighbor, ann2, propagate_to, send_rels)
                # decide what to send to other nieghbors who did not receive the original announcement
                # either: superprefix, separate prefix, or nothing
                # additionally these annoucnements can also be sent with path prepending
                other_neighbors = [n for n in neighbors if n not in some_neighbors]
                self._propagate_to_others(propagate_to, send_rels, other_neighbors, ann)
        else:
            super()._propagate(propagate_to, send_rels)

    def _provider_export_control(self) -> set:
        """
        Determine subset of providers the AS will export to using the export ratios
        from the traffic engineering behaviors data.
        """
        provider_weight_dict = self.traffic_engineering_behaviors_dict.get(self.as_.asn, {})
        export_set = set()
        for provider in self.as_.provider_asns:
            provider_data = provider_weight_dict.get(str(provider), {})
            export_ratio = provider_data.get("export_ratio", self.DEFAULT_EXPORT_RATIO)
            if export_ratio > 0 and random.random() < export_ratio:
                export_set.add(provider)

        # Ensure at least one provider with weight > 0 is selected
        valid_weights = {
            p: provider_weight_dict.get(str(p), {}).get("export_ratio", self.DEFAULT_EXPORT_RATIO)
            for p in self.as_.provider_asns
            if provider_weight_dict.get(str(p), {}).get("export_ratio", self.DEFAULT_EXPORT_RATIO) > 0
        }
        if not export_set and valid_weights:
            providers_list = list(valid_weights.keys())
            weights_list = list(valid_weights.values())
            export_set.add(random.choices(providers_list, weights=weights_list, k=1)[0])

        return export_set

    def _path_prepending(self, provider) -> bool:
        """
        Determine if AS performs path prepending to the given provider.
        """
        prepending_list = (
            self.traffic_engineering_behaviors_dict.get(self.as_.asn, {}).get(str(provider.asn), {}).get("prepending", [])
        )

        if not prepending_list:
            return False

        unique_vals = set(prepending_list)
        if unique_vals == {False}:
            return False
        elif unique_vals == {True}:
            return True
        else:
            return random.choice(prepending_list)

    def _propagate_to_others(
        self: "BGPExport2Some",
        propagate_to: Relationships,
        send_rels: set[Relationships],
        other_neighbors: set,
        ann: Ann,
    ) -> None:
        """
        Propagation logic for providers which did not receive the original announcement
        """
        asn_data = self.traffic_engineering_behaviors_dict.get(self.as_.asn, {})

        for neighbor in other_neighbors:
            provider_data = asn_data.get(str(neighbor.asn), {})

            # Skip if export ratio is 0
            export_ratio = provider_data.get("export_ratio", self.DEFAULT_EXPORT_RATIO)
            if export_ratio == 0:
                continue

            # NOTE: using this method means victim MUST use dedicated prefix
            #       this also means we must modify this to do DSR with e2s
            if (
                ann.recv_relationship == Relationships.ORIGIN
                and ann.prefix in [Prefixes.VICTIM.value, Prefixes.ANYCAST_SERVER.value, Prefixes.EDGE_SERVER.value]
            ):
                # Use superprefix ratio to determine separate announcement
                superprefix_ratio = provider_data.get("superprefix_ratio", 0)
                other_ann = self._get_super_sep_prefix_ann(ann, superprefix_ratio)
            else:
                other_ann = ann

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
                    and ann.prefix in [
                        Prefixes.VICTIM.value, 
                        Prefixes.ANYCAST_SERVER.value, 
                        Prefixes.EDGE_SERVER.value, 
                        "7.7.0.0/16", # superprefixes
                        "2.1.0.0/16",
                        "2.2.0.0/16",
                        "8.7.7.0/24", # separate prefixes                                                                                                            
                        "3.1.0.0/24",
                        "3.2.0.0/24",
                    ]
                ):
                    # avg = 3
                    # as_path = (self.as_.asn, self.as_.asn, self.as_.asn) + ann.as_path
                    # upper 99th percentile = 8
                    as_path = (self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn, self.as_.asn) + ann.as_path        
                    other_ann2 = other_ann.copy({"as_path": as_path})

                self._process_outgoing_ann(neighbor, other_ann2, propagate_to, send_rels)

    def _get_super_sep_prefix_ann(self, ann: Ann, weight):
        # VICTIM: str = "7.7.7.0/24"
        # ANYCAST_SERVER: str = "2.1.0.0/24"
        # EDGE_SERVER: str = "2.2.0.0/24"
        ip, mask = ann.prefix.split('/')
        octets = ip.split('.')

        if random.random() < weight:
            # Super prefix case: set 3rd octet to 0, mask to /16
            # VICTIM: str = "7.7.0.0/16"
            # ANYCAST_SERVER: str = "2.1.0.0/16"
            # EDGE_SERVER: str = "2.2.0.0/16"
            octets[2] = '0'
            mask = '16'
        else:
            # Other prefix case: increment 1st octet by 1
            # VICTIM: str = "8.7.7.0/24"
            # ANYCAST_SERVER: str = "3.1.0.0/24"
            # EDGE_SERVER: str = "3.2.0.0/24"
            octets[0] = str(int(octets[0]) + 1)

        new_prefix = '.'.join(octets) + '/' + mask
        return ann.copy({"prefix": new_prefix})