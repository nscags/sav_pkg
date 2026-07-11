import ipaddress
from collections import defaultdict, deque
from typing import TYPE_CHECKING

from bgpy.simulation_engine import ASPA, ASRA
from bgpy.shared.enums import ASGroups
from bgpy.simulation_engine.policies.policy import Policy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario



class BAR_SAV_PI_PP:
    name: str = "BAR-SAV-PI++"

    def validate(
        self,
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
        # Get origin ASNs from announcements and ROAs
        origin_asns = BAR_SAV_PI_PP._get_origin_asns(
            as_obj, source_prefix, engine, scenario
        )
        if not origin_asns:
            # did not receive any announcement for prefix + no ROA
            # this is essentially Loose uRPF
            print("No Origin ASes. Disconnected.", flush=True)
            return False 
        # print(f"Origin ASNs: {origin_asns}", flush=True)

        # Assume all ASes know the set of tier 1 ASes
        tier1_asns = frozenset(engine.as_graph.asn_groups[ASGroups.INPUT_CLIQUE.value])
        # print(f"Tier-1 ASes: {tier1_asns}", flush=True)

        # infer relationships from BGP announcements, ASPA, and ASRA
        inferred_relationships, ambiguous_relationships = BAR_SAV_PI_PP._infer_relationships_from_paths(
            as_obj, engine, tier1_asns
        )
        # print(f"Inferred Relationships: {inferred_relationships}", flush=True)
        # print(f"Ambiguous Relationships: {ambiguous_relationships}", flush=True)

        # Build D_f and P_f for F's provider cone                   
        D_f, P_f = BAR_SAV_PI_PP._get_provider_cone(
            as_obj, engine, tier1_asns, inferred_relationships
        )
        # print(f"D_f: {D_f}", flush=True)
        # print(f"P_f: {P_f}", flush=True)

        # For each origin compute P(O) and check prev_hop
        for origin_asn in origin_asns:
            p_of_o = BAR_SAV_PI_PP._compute_p_of_origin(
                origin_asn, as_obj, engine, D_f, P_f, tier1_asns, inferred_relationships, ambiguous_relationships
            )
            if p_of_o is None:
                return True
            if prev_hop.asn in p_of_o:
                return True

        return False 

    @staticmethod
    def _get_origin_asns(
        as_obj: "AS",
        source_prefix: str,
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ) -> frozenset[int]:
        """
        Returns every ASN that could legitimately originate source_prefix. 
        Combines ROAs and RIBs-In.
        """
        origin_asns: set[int] = set()

        # TODO: Add Aggregator Prefix Authorization (APA) here
        # check and allow origins in which the validaing AS has 
        # received an announcement for source prefix. 
        # Add any ASes which have a ROA for the source prefix.
        # If there exists an APA for the source prefix: 
        #   add any ASes which are authorized
        #   remove ASes which have BGP announcement for source prefix, but not authorized with ROA or APA

        net = ipaddress.ip_network(source_prefix, strict=False)
        for roa in Policy.roa_checker.get_relevant_roas(net):
            origin_asns.add(roa.origin)

        for ann_info in as_obj.policy.ribs_in.get_ann_infos(source_prefix):
            origin_asns.add(ann_info.unprocessed_ann.origin)
        
        # print(f"Origin ASNs: {origin_asns}")
        return frozenset(origin_asns)

    @staticmethod
    def _infer_relationships_from_paths(
        as_obj: "AS",
        engine: "SimulationEngine",
        tier1_asns: frozenset[int],
    ) -> dict[int, frozenset[int]]:

        as_dict = engine.as_graph.as_dict
        inferred: dict[int, set[int]] = defaultdict(set)
        ambiguous: dict[int, set[int]] = defaultdict(set)

        # get all AS paths from announcements received on a provider interface
        as_paths: set[tuple[int, ...]] = set()
        for provider_asn in as_obj.provider_asns:
            provider_rib = as_obj.policy.ribs_in.data.get(provider_asn, {})
            for ann_info in provider_rib.values():
                if as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    as_paths.add(ann_info.unprocessed_ann.as_path)

        for as_path in as_paths:
            # ignore da obvious 
            if len(as_path) < 2:
                continue

            path_asns = set(as_path)
            confirmed_peak = False

            # 1. Shared Provider w/ ASPA/ASRA records
            for i in range(len(as_path) - 2):
                left_asn = as_path[i]
                left_as = as_dict.get(left_asn)
                mid_asn = as_path[i + 1]
                mid_as = as_dict.get(mid_asn)
                right_asn = as_path[i + 2]
                right_as = as_dict.get(right_asn)

                left_up = (
                    (left_as is not None
                    and isinstance(left_as.policy, ASPA)
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
                    confirmed_peak = True
                    for j in range(i + 1):
                        inferred[as_path[j]].add(as_path[j + 1])
                    for j in range(i + 1, len(as_path) - 1):
                        inferred[as_path[j + 1]].add(as_path[j])
                    # print(inferred, flush=True)
                    break

            # we have determined the peak in the path, we do not need to check the other potential peaks
            if confirmed_peak:
                continue

            # 2. Bilateral Peer connections w/ ASRA or two peak ASes in the path
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
                    confirmed_peak = True
                    for j in range(i):
                        inferred[as_path[j]].add(as_path[j + 1])
                    for j in range(i + 1, len(as_path) - 1):
                        inferred[as_path[j + 1]].add(as_path[j])
                    break

            if confirmed_peak:
                continue

            # 3. Peak ASes in the path through 2 Tier-1 or ASPA ASes

            # Find peak ASes in the path: either Tier-1 ASes, or ASes with ASPA
            # records listing none of their path neighbors as providers
            top_indices = []
            for i, asn in enumerate(as_path):
                as_obj_i = as_dict.get(asn)
                if asn in tier1_asns:
                    top_indices.append(i)
                elif (as_obj_i is not None
                    and isinstance(as_obj_i.policy, ASPA)
                    and len(as_obj_i.provider_asns & path_asns) == 0):
                    # ASPA published but no path neighbors are providers
                    top_indices.append(i)

            if len(top_indices) == 2:
                # Bilateral peer: two top ASes connected by a peer link
                # All links to the left of the first top AS are UP
                # All links to the right of the last top AS are DOWN
                peak_left = top_indices[0]
                peak_right = top_indices[-1]

                # the two top ASes must be adjacent in the path
                if peak_right - peak_left != 1:
                    raise ValueError(
                        f"Two top ASes found at indices {peak_left} and {peak_right} but they are not adjacent in the path: {as_path}"
                    )

                for i in range(peak_left):
                    inferred[as_path[i]].add(as_path[i + 1])
                for i in range(peak_right, len(as_path) - 1):
                    inferred[as_path[i + 1]].add(as_path[i])
                continue
            elif len(top_indices) > 2:
                raise ValueError(f"More than 2 top ASes in the path? {top_indices}")

            # 4. Partial peak found via 1 Tier-1 or ASPA AS in path 

            elif len(top_indices) == 1:
                # Partial peak: one top AS confirmed as part of peak
                # Immediate left and right neighbor links remain AMBIGUOUS
                # All links further left (beyond immediate left neighbor) are UP
                # All links further right (beyond immediate right neighbor) are DOWN
                peak_idx = top_indices[0]
                for i in range(peak_idx - 1):
                    inferred[as_path[i]].add(as_path[i + 1])
                for i in range(peak_idx + 1, len(as_path) - 1):
                    inferred[as_path[i + 1]].add(as_path[i])

            # 5. Directional inference
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
                    if (as_path[i + 1] not in inferred.get(as_path[i], set())
                        and as_path[i] not in inferred.get(as_path[i + 1], set())):
                        ambiguous[as_path[i]].add(as_path[i + 1])
                        ambiguous[as_path[i + 1]].add(as_path[i])

            # Find the leftmost confirmed DOWN link
            # Everything from here to the end of the path is DOWN since
            # DOWN -> UP -> DOWN would be a valley
            leftmost_down: int | None = None
            for i, lt in enumerate(link_types):
                if lt == "down":
                    leftmost_down = i
                    break

            # Find the rightmost confirmed UP link
            # Everything from the start to here is UP since
            # UP -> DOWN -> UP would also be a valley
            rightmost_up: int | None = None
            for i in range(len(link_types) - 1, -1, -1):
                if link_types[i] == "up":
                    rightmost_up = i
                    break

            # Record DOWN relationships from leftmost_down to end of path
            if leftmost_down is not None:
                for i in range(leftmost_down, len(as_path) - 1):
                    inferred[as_path[i + 1]].add(as_path[i])

            # Record UP relationships from start of path to rightmost_up
            if rightmost_up is not None:
                for i in range(rightmost_up + 1):
                    inferred[as_path[i]].add(as_path[i + 1])

        return (
            {asn: frozenset(providers) for asn, providers in inferred.items()},
            {asn: frozenset(neighbors) for asn, neighbors in ambiguous.items()}
        )

    @staticmethod
    def _get_provider_cone(
        as_obj: "AS",
        engine: "SimulationEngine",
        tier1_asns: frozenset[int],
        inferred_relationships: dict[int, frozenset[int]],
    ) -> tuple[dict[int, int], dict[int, frozenset[int]]]:

        as_dict = engine.as_graph.as_dict

        D_f: dict[int, int] = {}
        P_f: dict[int, set[int]] = {}

        current_layer: set[int] = set(as_obj.provider_asns)
        for p_asn in as_obj.provider_asns:
            D_f[p_asn] = 1
            P_f[p_asn] = {p_asn}

        dist = 1

        while current_layer:
            next_layer: set[int] = set()

            for provider_asn in current_layer:
                provider_as = as_dict.get(provider_asn)
                if provider_as is None:
                    continue

                candidate_providers: set[int] = set()

                # provider has ASPA record
                if isinstance(provider_as.policy, ASPA):
                    candidate_providers.update(provider_as.provider_asns)

                # provider's provider has an ASRA record
                for grandparent_asn in provider_as.provider_asns:
                    grandparent_as = as_dict.get(grandparent_asn)
                    if (grandparent_as is not None and isinstance(grandparent_as.policy, ASRA)):
                        candidate_providers.add(grandparent_asn)

                # relationship was inferred from BGP announcements, ASPA, and ASRA 
                candidate_providers.update(
                    inferred_relationships.get(provider_asn, frozenset())
                )

                for grandparent_asn in candidate_providers:
                    new_dist = dist + 1
                    if grandparent_asn not in D_f:
                        D_f[grandparent_asn] = new_dist
                        P_f[grandparent_asn] = set(P_f[provider_asn])
                        next_layer.add(grandparent_asn)
                    elif D_f[grandparent_asn] == new_dist:
                        P_f[grandparent_asn].update(P_f[provider_asn])

            current_layer = next_layer
            dist += 1

        return D_f, {asn: frozenset(s) for asn, s in P_f.items()}

    @staticmethod
    def _compute_p_of_origin(
        origin_asn: int,
        as_obj: "AS",
        engine: "SimulationEngine",
        D_f: dict[int, int],
        P_f: dict[int, frozenset[int]],
        tier1_asns: frozenset[int],
        inferred_relationships: dict[int, frozenset[int]],
        ambiguous_relationships: dict[int, frozenset[int]],
    ) -> frozenset[int] | None:

        as_dict = engine.as_graph.as_dict

        # Shortcut origin is directly in F's provider cone
        if origin_asn in P_f:
            return P_f[origin_asn]

        # Build O's provider cone
        o_dist: dict[int, int] = {}
        o_dist[origin_asn] = 0
        current_layer: set[int] = set()

        origin_as = as_dict.get(origin_asn)
        if origin_as is None:
            return None

        direct_providers: set[int] = set()
        if isinstance(origin_as.policy, ASPA):
            direct_providers.update(origin_as.provider_asns)
        for grandparent_asn in origin_as.provider_asns:
            grandparent_as = as_dict.get(grandparent_asn)
            if grandparent_as is not None and isinstance(grandparent_as.policy, ASRA):
                direct_providers.add(grandparent_asn)
        direct_providers.update(inferred_relationships.get(origin_asn, frozenset()))
        # Ambiguous neighbors of origin are treated as potential providers
        direct_providers.update(ambiguous_relationships.get(origin_asn, frozenset()))

        for p_asn in direct_providers:
            o_dist[p_asn] = 1
            current_layer.add(p_asn)

        dist = 1
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

                candidate_providers.update(inferred_relationships.get(provider_asn, frozenset()))
                # Ambiguous neighbors are treated as potential providers
                candidate_providers.update(ambiguous_relationships.get(provider_asn, frozenset()))

                for p_asn in candidate_providers:
                    if p_asn not in o_dist:
                        o_dist[p_asn] = dist + 1
                        next_layer.add(p_asn)

            current_layer = next_layer
            dist += 1

        # Process O's provider cone top-down (furthest from origin first)
        D_o: dict[int, int] = {}
        P_o: dict[int, set[int]] = {}

        for y_asn in sorted(o_dist, key=lambda x: o_dist[x], reverse=True):
            y_as = as_dict.get(y_asn)
            best_dist: int | None = None
            best_providers: set[int] = set()

            # Case A: Shared provider (customer route) always preferred
            # If y is in F's provider cone, F is reachable from y via a customer link.
            if y_asn in D_f:
                best_dist = D_f[y_asn]
                best_providers = set(P_f[y_asn])

            # Case B: Bilateral peer only if Case A did not apply
            # Peer routes are preferred over provider routes but not customer routes
            if not best_providers:
                if y_as is not None and isinstance(y_as.policy, ASRA):
                    for peer_asn in y_as.peer_asns:
                        if peer_asn in D_f:
                            candidate_dist = D_f[peer_asn] + 1
                            if best_dist is None or candidate_dist < best_dist:
                                best_dist = candidate_dist
                                best_providers = set(P_f[peer_asn])
                            elif candidate_dist == best_dist:
                                best_providers.update(P_f[peer_asn])

            # Case C: Propagation only if neither Case A nor Case B applied.
            # Inherit the best route from y's provider in O's cone already processed.
            if not best_providers:
                for p_asn, p_dist in o_dist.items():
                    if p_dist == o_dist[y_asn] + 1 and p_asn in D_o:
                        candidate_dist = D_o[p_asn] + 1
                        if best_dist is None or candidate_dist < best_dist:
                            best_dist = candidate_dist
                            best_providers = set(P_o[p_asn])
                        elif candidate_dist == best_dist:
                            best_providers.update(P_o[p_asn])

            # Case D: handling ambiguous relationships
            for amb_asn in ambiguous_relationships.get(y_asn, frozenset()):
                if amb_asn in D_f:
                    best_providers.update(P_f[amb_asn])
                    if best_dist is None:
                        best_dist = 0
                elif amb_asn in P_o and P_o[amb_asn]:
                    best_providers.update(P_o[amb_asn])
                    if best_dist is None:
                        best_dist = 0

            if best_dist is not None:
                D_o[y_asn] = best_dist
                P_o[y_asn] = best_providers

        if origin_asn in P_o:
            return frozenset(P_o[origin_asn])

        return None