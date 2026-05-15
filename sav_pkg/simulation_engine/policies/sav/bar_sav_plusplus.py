import ipaddress
from collections import deque, defaultdict
from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class BAR_SAV_PI_PlusPlus(BaseSAVPolicy):
    name: str = "BAR-SAV-PI++"

    def validate(
        self,
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario,
    ) -> bool:
        # BAR-SAV++ is applied only to provider interfaces
        if prev_hop.asn not in as_obj.provider_asns:
            return True
        return BAR_SAV_PI_PlusPlus._validate(as_obj, source_prefix, prev_hop, engine, scenario)

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ) -> bool:
        # Find the origin AS of the source prefix via the ribs_in
        origin = BAR_SAV_PI_PlusPlus._get_origin(as_obj, source_prefix)
        if origin is None:
            return False

        origin_as = engine.as_graph.as_dict.get(origin)
        if origin_as is None:
            return False

        # Step 2.2: BFS upward from F to compute D_F and P_F for all ASes in F's provider cone.
        # D_F[asn]: shortest hop-distance from F upward to asn
        # P_F[asn]: frozenset of F's direct providers that lie on some shortest path to asn
        D_F, P_F = BAR_SAV_PI_PlusPlus._compute_provider_cone_dp(as_obj, engine)

        # Steps 2.3-2.5: Compute P_O for origin's provider cone (including origin itself),
        # processed top-down (providers before customers) using bi-peer bridges to F's cone.
        P_O = BAR_SAV_PI_PlusPlus._compute_origin_cone_dp(origin_as, D_F, P_F, engine)

        # Step 3: Allow iff prev_hop (p) is in P(O)
        if origin not in P_O:
            return False
        return prev_hop.asn in P_O[origin]

    @staticmethod
    def _get_origin(as_obj: "AS", source_prefix: str) -> int | None:
        """
        Find the origin ASN for the most specific valid route matching source_prefix
        across all ribs_in entries.
        """
        src_ip = ipaddress.ip_network(source_prefix)
        best_prefix_len = -1
        origin = None
        for prefix_dict in as_obj.policy._ribs_in.data.values():
            for ann_info in prefix_dict.values():
                if not as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    continue
                try:
                    ann_prefix = ipaddress.ip_network(ann_info.unprocessed_ann.prefix)
                except ValueError:
                    continue
                if src_ip.subnet_of(ann_prefix) and ann_prefix.prefixlen > best_prefix_len:
                    best_prefix_len = ann_prefix.prefixlen
                    origin = ann_info.unprocessed_ann.origin
        return origin

    @staticmethod
    def _compute_provider_cone_dp(
        as_obj: "AS",
        engine: "SimulationEngine",
    ) -> tuple[dict, dict]:
        """
        BFS upward from F through provider links.

        Returns:
            D_F: asn -> shortest distance from F to that AS going upward
            P_F: asn -> frozenset of F's direct provider ASNs on some shortest path to that AS
        """
        D_F: dict[int, int] = {}
        P_F: dict[int, frozenset] = {}
        queue: deque[int] = deque()

        for p_asn in as_obj.provider_asns:
            D_F[p_asn] = 1
            P_F[p_asn] = frozenset({p_asn})
            queue.append(p_asn)

        while queue:
            asn = queue.popleft()
            as_x = engine.as_graph.as_dict.get(asn)
            if as_x is None:
                continue
            new_dist = D_F[asn] + 1
            for provider in as_x.providers:
                p_asn = provider.asn
                if p_asn not in D_F:
                    D_F[p_asn] = new_dist
                    P_F[p_asn] = frozenset(P_F[asn])
                    queue.append(p_asn)
                elif D_F[p_asn] == new_dist:
                    # Multiple shortest paths — merge the provider sets
                    P_F[p_asn] = frozenset(P_F[p_asn] | P_F[asn])

        return D_F, P_F

    @staticmethod
    def _compute_origin_cone_dp(
        origin_as: "AS",
        D_F: dict,
        P_F: dict,
        engine: "SimulationEngine",
    ) -> dict:
        """
        Compute P_O for origin and all ASes in its provider cone, processed top-down
        (providers before customers) so that step 2.5 can rely on already-computed values.

        For each AS y processed:
          - B(y) = bi-peers of y that are in F's provider cone (i.e., in D_F)
          - If B(y) non-empty (step 2.4):
              D_O[y] = 1 + min D_F[x] for x in B(y)
              P_O[y] = union of P_F[x] for x in B(y) achieving the minimum
          - Else (step 2.5):
              U(y) = providers of y that already have D_O defined
              D_O[y] = 1 + min D_O[u] for u in U(y)
              P_O[y] = union of P_O[u] for u in U(y) achieving the minimum

        Returns P_O: asn -> frozenset of F's direct providers on shortest paths from F to asn.
        """
        # BFS upward from origin to collect S_O (origin's provider cone + origin itself)
        S_O: set[int] = {origin_as.asn}
        bfs_queue: deque = deque([origin_as])
        while bfs_queue:
            current = bfs_queue.popleft()
            for provider in current.providers:
                if provider.asn not in S_O:
                    S_O.add(provider.asn)
                    bfs_queue.append(provider)

        # Topological sort of S_O via Kahn's algorithm so providers are processed first.
        # Edge semantics: y depends on its providers in S_O (providers must come before y).
        # in_degree[y] = number of y's providers that are in S_O.
        in_degree: dict[int, int] = {asn: 0 for asn in S_O}
        children_in_S: dict[int, set] = defaultdict(set)
        for asn in S_O:
            as_y = engine.as_graph.as_dict.get(asn)
            if as_y is None:
                continue
            for provider in as_y.providers:
                if provider.asn in S_O:
                    in_degree[asn] += 1
                    children_in_S[provider.asn].add(asn)

        topo_queue: deque[int] = deque(asn for asn in S_O if in_degree[asn] == 0)
        topo_order: list[int] = []
        while topo_queue:
            asn = topo_queue.popleft()
            topo_order.append(asn)
            for child_asn in children_in_S.get(asn, set()):
                in_degree[child_asn] -= 1
                if in_degree[child_asn] == 0:
                    topo_queue.append(child_asn)

        D_O: dict[int, int] = {}
        P_O: dict[int, frozenset] = {}

        for asn in topo_order:
            as_y = engine.as_graph.as_dict.get(asn)
            if as_y is None:
                continue

            # Step 2.3: B(y) = bi-peers of y in F's provider cone
            B_y = {peer_asn for peer_asn in as_y.peer_asns if peer_asn in D_F}

            if B_y:
                # Step 2.4: bridge via bi-peer to F's provider cone
                min_d = min(D_F[x] for x in B_y)
                D_O[asn] = 1 + min_d
                P_O[asn] = frozenset().union(*(P_F[x] for x in B_y if D_F[x] == min_d))
            else:
                # Step 2.5: no bi-peer bridge; use providers already computed top-down
                U_y = {
                    provider.asn
                    for provider in as_y.providers
                    if provider.asn in D_O
                }
                if not U_y:
                    continue
                min_d = min(D_O[u] for u in U_y)
                D_O[asn] = 1 + min_d
                P_O[asn] = frozenset().union(*(P_O[u] for u in U_y if D_O[u] == min_d))

        return P_O
