import ipaddress
from collections import defaultdict
from typing import TYPE_CHECKING

from bgpy.simulation_engine import ASPA, ASRA
from bgpy.shared.enums import ASGroups
from bgpy.simulation_engine.policies.policy import Policy

from sav_pkg.simulation_engine.policies.sav.base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario



class BAR_SAV_PI_PP(BaseSAVPolicy):
    name: str = "BAR-SAV-PI++"

    @staticmethod
    def validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ) -> bool:
        """
        """
        # BAR-SAV-PI++ is only applied to provider interfaces
        if prev_hop.asn not in as_obj.provider_asns:
            return True
        return BAR_SAV_PI_PP._validate(
            as_obj, source_prefix, prev_hop, engine, scenario
        )

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ) -> bool:
        """
        """
        # Get source ASNs from announcements and ROAs
        source_asns = BAR_SAV_PI_PP._get_source_asns(as_obj, source_prefix)
        if not source_asns:
            # did not receive any announcement for prefix + no ROA, this is essentially Loose uRPF
            return False 
        
        # Assume all ASes know the set of tier 1 ASes
        tier1_asns = frozenset(engine.as_graph.asn_groups[ASGroups.INPUT_CLIQUE.value])

        # infer relationships from BGP announcements, ASPA, and ASRA
        inferred_provider_relationships, inferred_peer_relationships, ambiguous_relationships = BAR_SAV_PI_PP._infer_relationships_from_paths(
            as_obj, engine, tier1_asns
        )

        # Build D_f and P_f for F's provider cone                   
        D_f, P_f = BAR_SAV_PI_PP._get_f_provider_cone(
            as_obj, engine, inferred_provider_relationships,
        )

        # determine P(S)
        for source_asn in source_asns:
            p_of_s = BAR_SAV_PI_PP._compute_p_of_source(
                as_obj,
                source_asn,
                engine,
                D_f,
                P_f,
                inferred_provider_relationships,
                inferred_peer_relationships,
                ambiguous_relationships,
            )
            if p_of_s is None:
                return True
            if prev_hop.asn in p_of_s:
                return True

        return False

    @staticmethod
    def _get_source_asns(
        as_obj: "AS",
        source_prefix: str,
    ) -> frozenset[int]:
        """
        """
        source_asns: set[int] = set()

        # TODO: Add Aggregator Prefix Authorization (APA) here
        # check and allow sources in which the validaing AS has 
        # received an announcement for source prefix. 
        # Add any ASes which have a ROA for the source prefix.
        # If there exists an APA for the source prefix: 
        #   add any ASes which are authorized
        #   remove ASes which have BGP announcement for source prefix, but not authorized with ROA or APA

        net = ipaddress.ip_network(source_prefix, strict=False)
        for roa in Policy.roa_checker.get_relevant_roas(net):
            source_asns.add(roa.origin)

        for ann_info in as_obj.policy.ribs_in.get_ann_infos(source_prefix):
            source_asns.add(ann_info.unprocessed_ann.origin)
        
        return frozenset(source_asns)
    
    def _infer_relationships_from_paths(
        as_obj: "AS",
        engine: "SimulationEngine",
        tier1_asns: frozenset[int],
    ) -> dict[int, frozenset[int]]:
        """
        """
        as_dict = engine.as_graph.as_dict

        inferred_providers: dict[int, set[int]] = defaultdict(set) # asn: provider_asn
        inferred_peers: dict[int, set[int]] = defaultdict(set)     # asn: peer_asn
        ambiguous: dict[int, set[int]] = defaultdict(set)          # asn: ambigous_relationship_asn

        # AS know their direct providers
        for provider_asn in as_obj.provider_asns:
            inferred_providers[as_obj.asn].add(provider_asn)

        # AS knows the input clique
        for t1 in tier1_asns:
            inferred_peers[t1].update(tier1_asns - {t1})

        # get all AS paths from announcements received on a provider interface
        for provider_asn in as_obj.provider_asns:
            for ann_info in as_obj.policy.ribs_in.data.get(provider_asn, {}).values():
                if as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    as_path = ann_info.unprocessed_ann.as_path
                    if len(as_path) < 2:
                        continue

                    # determine peak & infer relationships
                    peak_asns = BAR_SAV_PI_PP._determine_peak(as_obj, engine, tier1_asns, as_path)
                    BAR_SAV_PI_PP._infer_relationships_from_peak(
                        as_obj, 
                        as_dict, 
                        as_path, 
                        peak_asns,
                        inferred_providers, 
                        inferred_peers, 
                        ambiguous
                    )
                    for asn, inferred_provider_asn_set in inferred_providers.items():
                        tmp_as_obj = engine.as_graph.as_dict[asn]
                        for inferred_provider in inferred_provider_asn_set:
                            if inferred_provider not in tmp_as_obj.provider_asns:
                                raise ValueError(f"Inccorrectly inferred customer-provider relationship ({asn}-{inferred_provider}) from as path {as_path}")
        
                    for asn, inferred_peer_asn_set in inferred_peers.items():
                        tmp_as_obj = engine.as_graph.as_dict[asn]
                        for inferred_peer in inferred_peer_asn_set:
                            if inferred_peer not in tmp_as_obj.peer_asns:
                                raise ValueError(f"Inccorrectly inferred peer relationship ({asn}-{inferred_peer}) from as path {as_path}")

        return (
            {asn: frozenset(providers) for asn, providers in inferred_providers.items()},
            {asn: frozenset(peers) for asn, peers in inferred_peers.items()},
            {asn: frozenset(neighbors) for asn, neighbors in ambiguous.items()}
        )

    @staticmethod
    def _determine_peak(
        as_obj: "AS",
        engine: "SimulationEngine",
        tier1_asns: frozenset[int],
        as_path: tuple[int, ...],
    ):
        """
        """
        as_path_and_F = (as_obj.asn,) + as_path 
        as_dict = engine.as_graph.as_dict

        # 1. Shared Provider
        for i in range(len(as_path_and_F) - 2):
            left_asn = as_path_and_F[i]
            left_as = as_dict.get(left_asn)
            mid_asn = as_path_and_F[i + 1]
            mid_as = as_dict.get(mid_asn)
            right_asn = as_path_and_F[i + 2]
            right_as = as_dict.get(right_asn)

            left_up = (
                (left_as is not None
                and isinstance(left_as.policy, ASPA)
                and mid_asn in left_as.provider_asns)
                or
                (left_as is not None
                and left_asn == as_obj.asn
                and mid_asn in left_as.provider_asns)
                or
                (mid_as is not None
                and isinstance(mid_as.policy, ASRA)
                and left_asn in mid_as.customer_asns)
            )

            right_down = (
                (right_as is not None
                and isinstance(right_as.policy, ASPA)
                and mid_asn in right_as.provider_asns)
                or
                (mid_as is not None
                and isinstance(mid_as.policy, ASRA)
                and right_asn in mid_as.customer_asns)
            )

            if left_up and right_down:
                return (mid_asn,)
            
        # 2.1. Bilateral Peer w/ ASRA
        for i in range(len(as_path) - 1):
            left_asn = as_path[i]
            right_asn = as_path[i + 1]
            left_as = as_dict.get(left_asn)
            right_as = as_dict.get(right_asn)
            
            is_peer = (
                (left_as is not None
                and isinstance(left_as.policy, ASRA)
                and right_asn in left_as.peer_asns)
                or
                (right_as is not None
                and isinstance(right_as.policy, ASRA)
                and left_asn in right_as.peer_asns)
            )

            if is_peer:
                return (left_asn, right_asn)
        
        # 2.2. Bilateral Peer w/ 2 Top ASes
        top_indices = []
        for i, asn in enumerate(as_path):
            as_obj_i = as_dict.get(asn)
            if asn in tier1_asns:
                top_indices.append(i)
            elif (as_obj_i is not None and isinstance(as_obj_i.policy, ASPA)):
                left_neighbor = as_path[i - 1] if i > 0 else None
                right_neighbor = as_path[i + 1] if i < len(as_path) - 1 else None
                neighbors_in_path = {n for n in [left_neighbor, right_neighbor] if n is not None}
                if len(as_obj_i.provider_asns & neighbors_in_path) == 0:
                    # ASPA does not list any neighboring AS on path as a provider = top AS
                    top_indices.append(i)

        if len(top_indices) > 2:
            raise ValueError(f"More than 2 top ASes in the path? {top_indices}")
        
        if len(top_indices) == 2:
            return (as_path[top_indices[0]], as_path[top_indices[1]])

        # 3. Partial Peak
        if len(top_indices) == 1:
            peak_idx = top_indices[0]
            left_neighbor = as_path[peak_idx - 1] if peak_idx > 0 else None
            right_neighbor = as_path[peak_idx + 1] if peak_idx < len(as_path) - 1 else None
            return (left_neighbor, as_path[peak_idx], right_neighbor)
        
        # 4. No Peak
        return ()
    
    @staticmethod
    def _infer_relationships_from_peak(
        as_obj: "AS",
        as_dict: dict,
        as_path: tuple[int, ...],
        peak_asns: tuple,
        inferred_providers: dict[int, set[int]],
        inferred_peers: dict[int, set[int]],
        ambiguous: dict[int, set[int]],
    ):
        """
        """
        # 0. No Peak
        if len(peak_asns) == 0:
            # Direction
            link_types: list[str] = []
            for i in range(len(as_path) - 1):
                left_asn = as_path[i]
                right_asn = as_path[i + 1]
                left_as = as_dict.get(left_asn)
                right_as = as_dict.get(right_asn)

                is_up = (
                    (left_as is not None
                    and isinstance(left_as.policy, ASPA)
                    and right_asn in left_as.provider_asns)
                    or
                    (right_as is not None
                    and isinstance(right_as.policy, ASRA)
                    and left_asn in right_as.customer_asns)
                )

                is_down = (
                    (right_as is not None
                    and isinstance(right_as.policy, ASPA)
                    and left_asn in right_as.provider_asns)
                    or
                    (left_as is not None
                    and isinstance(left_as.policy, ASRA)
                    and right_asn in left_as.customer_asns)
                )

                if is_up and not is_down:
                    link_types.append("up")
                elif is_down and not is_up:
                    link_types.append("down")
                else:
                    link_types.append("ambiguous")

            # Find leftmost DOWN and rightmost UP
            leftmost_down: int | None = None
            for i, lt in enumerate(link_types):
                if lt == "down":
                    leftmost_down = i
                    break
            rightmost_up: int | None = None
            for i in range(len(link_types) - 1, -1, -1):
                if link_types[i] == "up":
                    rightmost_up = i
                    break

            if leftmost_down is not None:
                for i in range(leftmost_down, len(link_types)):
                    link_types[i] = "down"
            if rightmost_up is not None:
                for i in range(rightmost_up + 1):
                    link_types[i] = "up"

            for i, lt in enumerate(link_types):
                if lt == "up":
                    inferred_providers[as_path[i]].add(as_path[i + 1])
                elif lt == "down":
                    inferred_providers[as_path[i + 1]].add(as_path[i])
                else:
                    # Only add to ambiguous if not already confirmed via another path
                    if (as_path[i] != as_obj.asn
                        and as_path[i + 1] != as_obj.asn
                        and as_path[i + 1] not in inferred_providers.get(as_path[i], set())
                        and as_path[i] not in inferred_providers.get(as_path[i + 1], set())
                        and as_path[i + 1] not in inferred_peers.get(as_path[i], set())):
                        ambiguous[as_path[i]].add(as_path[i + 1])
                        ambiguous[as_path[i + 1]].add(as_path[i])

        # 1. Shared Provider
        elif len(peak_asns) == 1:
            peak_idx = as_path.index(peak_asns[0])
            for i in range(peak_idx):
                inferred_providers[as_path[i]].add(as_path[i + 1])
            for i in range(peak_idx, len(as_path) - 1):
                inferred_providers[as_path[i + 1]].add(as_path[i])
            return
        
        # 2. Bilateral Peer
        elif len(peak_asns) == 2:
            left_idx = as_path.index(peak_asns[0])
            right_idx = as_path.index(peak_asns[1])
            if left_idx > right_idx:
                left_idx, right_idx = right_idx, left_idx

            if right_idx - left_idx != 1:
                raise ValueError(
                    f"Two top ASes found at indices {left_idx} and {right_idx} but they are not adjacent in the path: {as_path}"
                )

            for i in range(left_idx):
                inferred_providers[as_path[i]].add(as_path[i + 1])
            for i in range(right_idx, len(as_path) - 1):
                inferred_providers[as_path[i + 1]].add(as_path[i])

            inferred_peers[as_path[left_idx]].add(as_path[right_idx])
            inferred_peers[as_path[right_idx]].add(as_path[left_idx])
            return
        
        # 3. Partial Peak
        if len(peak_asns) == 3:
            left_neighbor, peak, right_neighbor = peak_asns
            peak_idx = as_path.index(peak)

            for i in range(peak_idx - 1):
                inferred_providers[as_path[i]].add(as_path[i + 1])
            for i in range(peak_idx + 1, len(as_path) - 1):
                inferred_providers[as_path[i + 1]].add(as_path[i])

            for neighbor in (left_neighbor, right_neighbor):
                if neighbor is None:
                    continue
                neighbor_as = as_dict.get(neighbor)
                already_resolved = (
                    peak in inferred_providers.get(neighbor, set())
                    or neighbor in inferred_providers.get(peak, set())
                    or peak in inferred_peers.get(neighbor, set())
                    or neighbor in inferred_peers.get(peak, set())
                )
                if already_resolved:
                    continue
                if (neighbor_as is not None
                    and isinstance(neighbor_as.policy, ASPA)
                    and peak in neighbor_as.provider_asns):
                    inferred_providers[neighbor].add(peak)
                elif neighbor != as_obj.asn and peak != as_obj.asn:
                    ambiguous[neighbor].add(peak)
                    ambiguous[peak].add(neighbor)
            return

        return
    
    @staticmethod
    def _get_f_provider_cone(
        as_obj: "AS",
        engine: "SimulationEngine",
        inferred_provider_relationships: dict[int, frozenset[int]],
    ) -> tuple[dict[int, int], dict[int, frozenset[int]]]:
        """
        """
        as_dict = engine.as_graph.as_dict

        D_f: dict[int, int] = {}
        P_f: dict[int, set[int]] = {}

        current_layer: set[int] = set(as_obj.provider_asns)
        for p_asn in as_obj.provider_asns:
            D_f[p_asn] = 1
            P_f[p_asn] = {p_asn}

        current_dist = 1
        while current_layer:
            next_layer: set[int] = set()
            for provider_asn in current_layer:
                provider_as = as_dict.get(provider_asn)
                if provider_as is None:
                    continue

                candidate_providers: set[int] = set()
                if isinstance(provider_as.policy, ASPA):
                    candidate_providers.update(provider_as.provider_asns)
                for grandparent_asn in provider_as.provider_asns:
                    grandparent_as = as_dict.get(grandparent_asn)
                    if grandparent_as is not None and isinstance(grandparent_as.policy, ASRA):
                        candidate_providers.add(grandparent_asn)
                candidate_providers.update(
                    inferred_provider_relationships.get(provider_asn, frozenset())
                )

                for canidate_provider in candidate_providers:
                    new_dist = current_dist + 1
                    if canidate_provider not in D_f:
                        D_f[canidate_provider] = new_dist
                        P_f[canidate_provider] = set(P_f[provider_asn])
                        next_layer.add(canidate_provider)
                    elif new_dist < D_f[canidate_provider]:
                        D_f[canidate_provider] = new_dist
                        P_f[canidate_provider] = set(P_f[provider_asn]) 
                    elif D_f[canidate_provider] == new_dist:
                        P_f[canidate_provider].update(P_f[provider_asn])

            current_layer = next_layer
            current_dist += 1

        return D_f, {asn: frozenset(s) for asn, s in P_f.items()}
    
    @staticmethod
    def _compute_p_of_source(
        as_obj: "AS",
        source_asn: int,
        engine: "SimulationEngine",
        D_f: dict[int, int],
        P_f: dict[int, frozenset[int]],
        inferred_provider_relationships: dict[int, frozenset[int]],
        inferred_peer_relationships: dict[int, frozenset[int]],
        ambiguous_relationships: dict[int, frozenset[int]],
    ) -> frozenset[int] | None:
        """
        """
        as_dict = engine.as_graph.as_dict

        # source in provider cone of F
        if source_asn in P_f:
            result = set(P_f[source_asn])
            return frozenset(result)

        source_as = as_dict.get(source_asn)
        if source_as is None:
            return None

        max_dist_from_s: dict[int, int] = {source_asn: 0} # just for processing order
        s_providers_of: dict[int, set[int]] = {}
        current_layer: set[int] = set()

        # get direct providers of source
        direct_providers: set[int] = set()
        if isinstance(source_as.policy, ASPA):
            direct_providers.update(source_as.provider_asns)
        for grandparent_asn in source_as.provider_asns:
            grandparent_as = as_dict.get(grandparent_asn)
            if grandparent_as is not None and isinstance(grandparent_as.policy, ASRA):
                direct_providers.add(grandparent_asn)
        direct_providers.update(inferred_provider_relationships.get(source_asn, frozenset()))

        s_providers_of[source_asn] = direct_providers
        for p_asn in direct_providers:
            max_dist_from_s[p_asn] = 1
            current_layer.add(p_asn)

        # construct the provider cone of the source
        current_dist = 1
        while current_layer:
            next_layer: set[int] = set()
            for provider_asn in current_layer:
                provider_as = as_dict.get(provider_asn)
                if provider_as is None:
                    s_providers_of[provider_asn] = set()
                    continue

                candidate_providers: set[int] = set()
                if isinstance(provider_as.policy, ASPA):
                    candidate_providers.update(provider_as.provider_asns)
                for grandparent_asn in provider_as.provider_asns:
                    grandparent_as = as_dict.get(grandparent_asn)
                    if grandparent_as is not None and isinstance(grandparent_as.policy, ASRA):
                        candidate_providers.add(grandparent_asn)
                candidate_providers.update(
                    inferred_provider_relationships.get(provider_asn, frozenset())
                )

                s_providers_of[provider_asn] = candidate_providers

                for p_asn in candidate_providers:
                    if (p_asn not in max_dist_from_s) or (max_dist_from_s[p_asn] < current_dist + 1):
                        max_dist_from_s[p_asn] = current_dist + 1
                        next_layer.add(p_asn)

            current_layer = next_layer
            current_dist += 1

        P_s_confirmed: dict[int, set[int]] = {}
        P_s_ambiguous: dict[int, set[int]] = {}
        D_s_f: dict[int, int] = {}

        # determine the best path from the source to F
        for y_asn in sorted(max_dist_from_s, key=lambda x: max_dist_from_s[x], reverse=True):
            y_as = as_dict.get(y_asn)
            best_dist: int | None = None
            confirmed_p_f: set[int] = set()
            ambiguous_p_f: set[int] = set()

            # Case A: shared provider
            if y_asn in D_f:
                best_dist = D_f[y_asn]
                confirmed_p_f = set(P_f[y_asn])

            # Case B: bilateral peer
            if not confirmed_p_f:
                if y_as is not None and isinstance(y_as.policy, ASRA):
                    for peer_asn in y_as.peer_asns:
                        if peer_asn in D_f:
                            candidate_dist = D_f[peer_asn] + 1
                            if best_dist is None or candidate_dist < best_dist:
                                best_dist = candidate_dist
                                confirmed_p_f = set(P_f[peer_asn])
                            elif candidate_dist == best_dist:
                                confirmed_p_f.update(P_f[peer_asn])
                else:
                    for peer_asn in inferred_peer_relationships.get(y_asn, frozenset()):
                        if peer_asn in D_f:
                            candidate_dist = D_f[peer_asn] + 1
                            if best_dist is None or candidate_dist < best_dist:
                                best_dist = candidate_dist
                                confirmed_p_f = set(P_f[peer_asn])
                            elif candidate_dist == best_dist:
                                confirmed_p_f.update(P_f[peer_asn])

            # Case C: propagation
            if not confirmed_p_f:
                for p_asn in s_providers_of.get(y_asn, set()):
                    # NOTE: this can be modified/optimized slightly
                    ambiguous_p_f.update(P_s_ambiguous.get(p_asn, set()))
                    p_dist = D_s_f.get(p_asn)
                    if p_dist is None:
                        continue
                    candidate_dist = p_dist + 1

                    # algorithm a
                    if best_dist is None or candidate_dist < best_dist:
                        best_dist = candidate_dist
                        confirmed_p_f = set(P_s_confirmed[p_asn])
                    elif candidate_dist == best_dist:
                        confirmed_p_f.update(P_s_confirmed[p_asn])

                    # algorithm b
                    # if best_dist is None or candidate_dist < best_dist:
                    #     best_dist = candidate_dist
                    # confirmed_p_f.update(P_s_confirmed[p_asn])

            # y's own ambiguous connections
            y_asn_ambiguous_p_f = BAR_SAV_PI_PP._get_ambiguous_p_f(
                as_obj,
                y_asn,
                ambiguous_relationships,
            )
            if y_asn_ambiguous_p_f:
                ambiguous_p_f.update(y_asn_ambiguous_p_f)

            if confirmed_p_f:
                D_s_f[y_asn] = best_dist
                P_s_confirmed[y_asn] = confirmed_p_f
            if ambiguous_p_f:
                P_s_ambiguous[y_asn] = ambiguous_p_f

        # P(S) = the source's confirmed interfaces plus every ambiguous
        # interface accumulated anywhere along its provider cone
        result = set(P_s_confirmed.get(source_asn, set()))
        result |= set(P_s_ambiguous.get(source_asn, set()))

        if not result:
            return None
        return frozenset(result)

    @staticmethod
    def _get_ambiguous_p_f(
        as_obj: "AS",
        y_asn: int,
        ambiguous_relationships: dict[int, frozenset[int]],
    ) -> frozenset[int]:
        """
        """
        ambiguous_neighbors = ambiguous_relationships.get(y_asn)
        if not ambiguous_neighbors:
            return frozenset()

        result: set[int] = set()
        for provider_asn in as_obj.provider_asns:
            for ann_info in as_obj.policy.ribs_in.data.get(provider_asn, {}).values():
                if as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    as_path = ann_info.unprocessed_ann.as_path
                    if ambiguous_neighbors.intersection(as_path):
                        result.add(provider_asn)

        return frozenset(result)
