"""Precomputed background routes, made by scripts/precompute_routes.py and
merged by scripts/merge_routes.py.

The scenario only propagates its own announcements (victim, reflectors,
attacker). With SAVScenarioConfig.routes_dir set, the SAV policies also read
the routes every AS would hold in its RIBs-In if every non-IXP AS announced a
prefix. Those are not stored directly: nh.npy holds, for every origin, every
AS's next hop toward it, and what AS F holds in its RIBs-In from neighbor N
for origin O is always N's best path to O, whenever N exports it to F
(see background_ribs_in).
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import numpy as np

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

NH_FILE = "nh.npy"
ORIGINS_FILE = "origins.npy"
MAX_PATH_LEN = 64
# Background routes were precomputed with prefixes inside 10.0.0.0/8, which no
# scenario issues a ROA for, so ROV (inherited by ASPA/ASRA) sees them as
# unknown rather than invalid, exactly as during the precompute
BACKGROUND_PREFIX = "10.0.0.0/8"


class BackgroundAnn:
    """The fields of a received announcement that _valid_ann reads (BGP, ROV, ASPA, ASRA)"""

    __slots__ = ("as_path", "next_hop_asn", "origin")
    prefix = BACKGROUND_PREFIX

    def __init__(self, as_path: tuple[int, ...]):
        self.as_path = as_path
        self.next_hop_asn = as_path[0]
        self.origin = as_path[-1]


class RouteStore:
    """Memory-mapped next-hop table: nh[origin row, AS column] = next hop ASN"""

    _stores: dict[str, "RouteStore"] = {}

    @classmethod
    def get(cls, routes_dir: str) -> "RouteStore":
        """One store per worker process, the file is shared through the page cache"""

        key = str(Path(routes_dir).expanduser().resolve())
        if key not in cls._stores:
            cls._stores[key] = cls(Path(key))
        return cls._stores[key]

    def __init__(self, routes_dir: Path):
        meta = json.loads((routes_dir / "metadata.json").read_text())
        self.caida_sha256: str = meta["caida_sha256"]
        self.asns = np.array(meta["asns"], dtype=np.uint32)
        self.origins = np.load(routes_dir / ORIGINS_FILE)
        self.nh = np.load(routes_dir / NH_FILE, mmap_mode="r")
        assert self.nh.shape == (len(self.origins), len(self.asns)), (
            f"{routes_dir / NH_FILE} has shape {self.nh.shape}, expected "
            f"{(len(self.origins), len(self.asns))}"
        )
        self._col_of = {int(a): i for i, a in enumerate(self.asns)}
        self._checked_graphs: set[int] = set()
        # An AS's paths never change during a run; cache the most recent ones
        self.paths_from = lru_cache(maxsize=32)(self._paths_from)

    def check_graph(self, engine: "SimulationEngine") -> None:
        """The simulation must run on the graph the routes were computed on"""

        graph_id = id(engine.as_graph)
        if graph_id in self._checked_graphs:
            return
        graph_asns = np.array(sorted(engine.as_graph.as_dict), dtype=np.uint32)
        assert np.array_equal(graph_asns, self.asns), (
            "The AS graph differs from the one the background routes were "
            f"computed on (CAIDA sha256 {self.caida_sha256[:12]}...). Pin the "
            "simulation to that CAIDA file."
        )
        self._checked_graphs.add(graph_id)

    def _paths_from(self, asn: int) -> tuple[tuple[int, ...], ...]:
        """asn's best path to every origin it has a route to, asn first, origin last"""

        first_hops = np.asarray(self.nh[:, self._col_of[asn]])
        rows = np.flatnonzero(first_hops)
        n = len(rows)
        if n == 0:
            return ()
        origins = self.origins[rows]

        paths = np.zeros((n, MAX_PATH_LEN), dtype=np.uint32)
        paths[:, 0] = asn
        lengths = np.ones(n, dtype=np.int64)
        alive = origins != asn
        k = 1
        while alive.any():
            if k == MAX_PATH_LEN:
                raise ValueError(f"Path from AS {asn} longer than {MAX_PATH_LEN}")
            idx = np.flatnonzero(alive)
            if k == 1:
                nxt = first_hops[rows[idx]]
            else:
                cols = np.searchsorted(self.asns, paths[idx, k - 1])
                nxt = np.asarray(self.nh[rows[idx], cols])
            if not nxt.all():
                raise ValueError(f"Broken next-hop chain on a path from AS {asn}")
            paths[idx, k] = nxt
            lengths[idx] += 1
            alive[idx] = nxt != origins[idx]
            k += 1

        return tuple(
            tuple(row[:length]) for row, length in zip(paths.tolist(), lengths.tolist())
        )


def background_ribs_in(
    as_obj: "AS",
    engine: "SimulationEngine",
    scenario,
    neighbors: str = "all",
) -> Iterator[tuple[int, BackgroundAnn, Relationships]]:
    """
    (neighbor ASN, announcement, relationship) for every background route
    as_obj holds in its RIBs-In, or nothing if the scenario has no routes_dir

    neighbors="providers" limits it to routes received from providers.

    Matches bgpy's export rules: N sends every best route to its customers,
    and to peers and providers only the routes it originated or learned from
    a customer. bgpy does not skip the neighbor a route was learned from, so
    paths containing as_obj itself are included, as in BGPFull's RIBs-In;
    callers filter them with _valid_ann like any other RIBs-In entry.
    """
    routes_dir = getattr(scenario.scenario_config, "routes_dir", None)
    if not routes_dir:
        return
    store = RouteStore.get(routes_dir)
    store.check_graph(engine)

    groups = [(as_obj.providers, Relationships.PROVIDERS)]
    if neighbors == "all":
        groups += [
            (as_obj.peers, Relationships.PEERS),
            (as_obj.customers, Relationships.CUSTOMERS),
        ]
    elif neighbors != "providers":
        raise ValueError(f"neighbors must be 'all' or 'providers', not {neighbors!r}")

    for neighbor_objs, rel in groups:
        for n in neighbor_objs:
            n_customers = n.customer_asns
            exports_everything = rel == Relationships.PROVIDERS
            for path in store.paths_from(n.asn):
                if (
                    exports_everything
                    or len(path) == 1
                    or path[1] in n_customers
                ):
                    yield n.asn, BackgroundAnn(path), rel


def scenario_cache(scenario) -> dict:
    """Per-scenario memo: RIBs-In and adopters are fixed once the scenario is set up"""

    cache = getattr(scenario, "_sav_policy_cache", None)
    if cache is None:
        cache = {}
        scenario._sav_policy_cache = cache
    return cache
