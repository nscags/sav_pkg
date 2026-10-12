"""Precompute every AS's RIBs-In on one pinned CAIDA graph.

Goal: for every AS, all routes it receives from all of its neighbors (not
just its best one), with every AS except IXPs announcing.

Every AS except IXPs announces; origins are processed in batches (one batch
= one bgpy propagation, each origin announcing its own prefix).

How it is stored: what AS F receives from neighbor N for origin O is always
N's own chosen route to O (when N exports it to F). So instead of writing
every AS's RIBs-In (~1.8e10 paths, mostly the same tables repeated to every
customer), each AS's chosen next hop toward each origin is saved once, and
F's RIBs-In is read out by looking up each neighbor's route. --verify-sample
checks this read-out against bgpy's actual RIBs-In.

Output (under --out):
    metadata.json                 CAIDA file + sha256, ASN column order, batching
    shards_b<B>/batch_<n>.npz     origins (uint32[k]) and nh (uint32[k, num_asns]);
                                  nh[i, j] = next hop of ASN asns[j] toward
                                  origins[i], the origin itself at the origin,
                                  0 if no route
    bench/<run id>.jsonl          one line of timings/memory per batch
    bench/<run id>_summary.json   totals and projections for this run

Resumable: origins are sorted by ASN and cut into fixed batches; a batch whose
shard exists is skipped, and shards are written to a temp name then renamed,
so an interrupted batch is simply redone. Re-running the same command picks
up where the last run stopped; --num-origins N limits a run to the next N
origins not done yet.

Parallelism: --workers processes per job (each builds its own graph), and
SLURM array tasks split the batches round-robin (batch b goes to task
b % num_tasks).

Benchmark run (see the printed projection):
    python3 precompute_routes.py --num-origins 400 --workers 4
"""



import argparse
import hashlib
import json
import os
import resource
import time
from datetime import datetime
from ipaddress import IPv4Network
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

# NOTE: bgpy is imported inside functions, not here. Importing
# bgpy.simulation_framework parses sys.argv for its own --trials flag, which
# would swallow this script's --help.

# Pinned CAIDA snapshot: bgpy downloads serial-2 <dl_time:%Y%m01>, so any day
# in September 2026 gives the 20260901 file (bgpy cache name 2026.09.24)
CAIDA_DL_TIME = datetime(2026, 9, 24)

POLICIES = ("bgp", "bgpfull")


def policy_cls(name: str):
    from bgpy.simulation_engine import BGP, BGPFull

    return {"bgp": BGP, "bgpfull": BGPFull}[name]


#########
# Graph #
#########

def build_as_graph(caida_dir: Path):
    from bgpy.as_graphs import CAIDAASGraphConstructor

    return CAIDAASGraphConstructor(
        as_graph_collector_kwargs={"dl_time": CAIDA_DL_TIME, "cache_dir": caida_dir},
    ).run()


def caida_file(caida_dir: Path) -> Path:
    from bgpy.as_graphs import CAIDAASGraphCollector

    return CAIDAASGraphCollector(dl_time=CAIDA_DL_TIME, cache_dir=caida_dir).run()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def batch_prefix(i: int) -> str:
    """i-th /24 inside 10.0.0.0/8, unique within a batch (i < 65536)"""
    return str(IPv4Network(((10 << 24) + (i << 8), 24)))


class _AllAnnounceScenario:
    """The two things SimulationEngine.setup/run need from a scenario"""

    def __init__(self, PolicyCls, announcements):
        self.PolicyCls = PolicyCls
        self.announcements = announcements

    def get_policy_cls(self, as_obj):
        return self.PolicyCls


###########
# Workers #
###########

_W: dict = {}


def _init_worker(caida_dir, policy, origins, asns, batch_size, shard_dir, deadline,
                 verify_sample):
    from bgpy.simulation_engine import Announcement, SimulationEngine

    t0 = time.perf_counter()
    as_graph = build_as_graph(caida_dir)
    # Same pinned file in every process, so the same sorted ASN order
    assert np.array_equal(asns, np.array(sorted(as_graph.as_dict), dtype=np.uint32))
    _W.update(
        engine=SimulationEngine(as_graph),
        PolicyCls=policy_cls(policy),
        Announcement=Announcement,
        origins=origins,
        as_objs=[as_graph.as_dict[int(a)] for a in asns],
        col_of={int(a): i for i, a in enumerate(asns)},
        num_asns=len(asns),
        verify_sample=verify_sample,
        batch_size=batch_size,
        shard_dir=shard_dir,
        deadline=deadline,
        graph_build_s=time.perf_counter() - t0,
        first_batch=True,
    )


def reconstruct_path(asn: int, row: np.ndarray, col_of: dict[int, int]) -> tuple[int, ...] | None:
    """AS path from asn to the row's origin by following next hops, None if no route"""

    path = [asn]
    while True:
        nxt = int(row[col_of[path[-1]]])
        if nxt == 0:
            return None
        if nxt == path[-1]:          # reached the origin
            return tuple(path)
        path.append(nxt)


def reconstruct_ribs_in(as_obj, row: np.ndarray, col_of: dict[int, int]) -> dict[int, tuple]:
    """
    Neighbor -> AS path that as_obj holds in its RIBs-In for this row's origin

    bgpy sends every AS's best route to all customers, and its origin or
    customer routes (next hop is itself or one of its customers) to peers
    and providers as well, without skipping the neighbor it was learned from.
    So what as_obj received from neighbor n is n's best path whenever n would
    export it to as_obj.
    """
    ribs_in = {}
    for n in (*as_obj.providers, *as_obj.peers, *as_obj.customers):
        path = reconstruct_path(n.asn, row, col_of)
        if path is None:
            continue
        n_customers = n.customer_asns
        nh = path[1] if len(path) > 1 else n.asn
        if as_obj.asn in n_customers or nh == n.asn or nh in n_customers:
            ribs_in[n.asn] = path
    return ribs_in


def _verify_ribs_in(batch, nh, prefix_row) -> tuple[int, list]:
    """Compares bgpy's actual RIBs-In with the reconstruction for sampled ASes"""

    rng = np.random.default_rng(batch)
    sample = rng.choice(len(_W["as_objs"]), size=_W["verify_sample"], replace=False)
    checked, mismatches = 0, []
    for idx in sample:
        as_obj = _W["as_objs"][int(idx)]
        actual: dict[tuple[int, str], tuple] = {}
        for neighbor, prefixes in as_obj.policy.ribs_in.data.items():
            for prefix, ann_info in prefixes.items():
                actual[(neighbor, prefix)] = tuple(ann_info.unprocessed_ann.as_path)
        expected: dict[tuple[int, str], tuple] = {}
        for prefix, row_i in prefix_row.items():
            for neighbor, path in reconstruct_ribs_in(as_obj, nh[row_i], _W["col_of"]).items():
                expected[(neighbor, prefix)] = path
        checked += len(actual)
        for key in actual.keys() | expected.keys():
            if actual.get(key) != expected.get(key):
                mismatches.append({"as": as_obj.asn, "neighbor": key[0], "prefix": key[1],
                                   "actual": actual.get(key), "expected": expected.get(key)})
    return checked, mismatches


def _run_batch(batch: int) -> dict:
    if _W["deadline"] and time.time() > _W["deadline"]:
        return {"batch": batch, "skipped": "time budget"}

    engine = _W["engine"]
    start = batch * _W["batch_size"]
    origins = _W["origins"][start:start + _W["batch_size"]]
    prefix_row = {batch_prefix(i): i for i in range(len(origins))}
    metrics = {"batch": batch, "num_origins": len(origins), "pid": os.getpid()}
    if _W["first_batch"]:
        metrics["graph_build_s"] = round(_W["graph_build_s"], 2)
        _W["first_batch"] = False

    t = time.perf_counter()
    anns = tuple(
        _W["Announcement"](prefix=batch_prefix(i), as_path=(int(o),), timestamp=0)
        for i, o in enumerate(origins)
    )
    scenario = _AllAnnounceScenario(_W["PolicyCls"], anns)
    engine.setup(scenario)
    metrics["setup_s"] = time.perf_counter() - t

    t = time.perf_counter()
    engine.run(propagation_round=0, scenario=scenario)
    metrics["propagate_s"] = time.perf_counter() - t

    t = time.perf_counter()
    nh = np.zeros((len(origins), _W["num_asns"]), dtype=np.uint32)
    num_routes = 0
    for col, as_obj in enumerate(_W["as_objs"]):
        for prefix, ann in as_obj.policy.local_rib.items():
            nh[prefix_row[prefix], col] = ann.as_path[1] if len(ann.as_path) > 1 else as_obj.asn
            num_routes += 1
    metrics["extract_s"] = time.perf_counter() - t
    metrics["num_routes"] = num_routes

    if _W["verify_sample"]:
        t = time.perf_counter()
        checked, mismatches = _verify_ribs_in(batch, nh, prefix_row)
        metrics["verify_s"] = time.perf_counter() - t
        metrics["verify_ribs_in_entries"] = checked
        metrics["verify_mismatches"] = len(mismatches)
        if mismatches:
            metrics["verify_examples"] = mismatches[:3]

    t = time.perf_counter()
    shard = _W["shard_dir"] / f"batch_{batch:05d}.npz"
    tmp = shard.with_name(shard.name + ".tmp.npz")
    np.savez_compressed(tmp, origins=origins, nh=nh)
    tmp.rename(shard)
    metrics["write_s"] = time.perf_counter() - t
    metrics["shard_mb"] = shard.stat().st_size / 2**20

    metrics["total_s"] = sum(metrics[k] for k in ("setup_s", "propagate_s", "extract_s", "write_s"))
    metrics["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    return {k: round(v, 3) if isinstance(v, float) else v for k, v in metrics.items()}


########
# Main #
########

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=Path("~/sav/routes/caida_20260901"))
    ap.add_argument("--caida-dir", type=Path, default=Path("~/sav/caida"),
                    help="Fixed cache dir for the pinned CAIDA file")
    ap.add_argument("--batch-size", type=int, default=100,
                    help="Origins per propagation (changing it starts a new shards_b<B> dir)")
    ap.add_argument("--policy", choices=POLICIES, default="bgp",
                    help="bgp keeps only the local RIB (fast); bgpfull also keeps RIBs-In, "
                    "is ~8x slower, and is only needed for --verify-sample. Both pick the "
                    "same best routes, so shards from either can be mixed")
    ap.add_argument("--workers", type=int,
                    default=int(os.environ.get("SLURM_NTASKS", max(cpu_count() - 1, 1))))
    ap.add_argument("--task-index", type=int, default=int(os.environ.get("SLURM_ARRAY_TASK_ID", 0)))
    ap.add_argument("--num-tasks", type=int, default=int(os.environ.get("SLURM_ARRAY_TASK_COUNT", 1)))
    ap.add_argument("--num-origins", type=int, default=None,
                    help="Announce at most this many origin ASes in this job, taking the "
                    "next ones not done yet (rounded up to whole batches). Default: all")
    ap.add_argument("--time-budget-h", type=float, default=None,
                    help="Stop starting new batches after this many hours")
    ap.add_argument("--verify-sample", type=int, default=0,
                    help="Per batch, check the RIBs-In rebuilt from the next hops against "
                    "bgpy's actual RIBs-In for this many random ASes (needs --policy bgpfull)")
    args = ap.parse_args()
    if args.verify_sample and args.policy != "bgpfull":
        raise SystemExit("--verify-sample needs --policy bgpfull (bgp keeps no RIBs-In)")

    start_wall = time.time()
    out = args.out.expanduser().resolve()
    caida_dir = args.caida_dir.expanduser().resolve()
    shard_dir = out / f"shards_b{args.batch_size}"
    bench_dir = out / "bench"
    for d in (shard_dir, bench_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Download / locate the pinned file once, before any worker reads it
    caida_path = caida_file(caida_dir)
    caida_sha = sha256(caida_path)

    t = time.perf_counter()
    as_graph = build_as_graph(caida_dir)
    main_graph_build_s = time.perf_counter() - t
    asns = np.array(sorted(as_graph.as_dict), dtype=np.uint32)
    origins = np.array(sorted(a.asn for a in as_graph if not a.ixp), dtype=np.uint32)
    num_ixps = len(asns) - len(origins)
    del as_graph

    num_batches = -(-len(origins) // args.batch_size)
    metadata = {
        "caida_file": str(caida_path),
        "caida_sha256": caida_sha,
        "caida_dl_time": CAIDA_DL_TIME.isoformat(),
        "batch_size": args.batch_size,
        "num_asns": len(asns),
        "num_origins": len(origins),
        "num_ixps_skipped": num_ixps,
        "num_batches": num_batches,
        "asns": asns.tolist(),
    }
    meta_path = out / "metadata.json"
    if meta_path.exists():
        old = json.loads(meta_path.read_text())
        for key in ("caida_sha256", "num_asns"):
            if old.get(key) != metadata[key]:
                raise SystemExit(f"{meta_path} has {key}={old.get(key)!r}, this run has "
                                 f"{metadata[key]!r}; use a different --out")
    else:
        meta_path.write_text(json.dumps(metadata))

    mine = [b for b in range(num_batches) if b % args.num_tasks == args.task_index]
    todo = [b for b in mine if not (shard_dir / f"batch_{b:05d}.npz").exists()]
    already_done = len(mine) - len(todo)
    if args.num_origins is not None:
        todo = todo[:-(-args.num_origins // args.batch_size)]
    deadline = start_wall + args.time_budget_h * 3600 if args.time_budget_h else None

    run_id = f"{datetime.now():%Y%m%d_%H%M%S}_task{args.task_index}"
    print(f"CAIDA {caida_path.name} (sha256 {caida_sha[:12]}...), {len(asns)} ASes, "
          f"{len(origins)} origins ({num_ixps} IXPs skipped)")
    print(f"policy={args.policy} batch_size={args.batch_size} -> {num_batches} batches total; "
          f"task {args.task_index}/{args.num_tasks} owns {len(mine)}, {already_done} "
          f"already done, running {len(todo)} with {args.workers} workers", flush=True)
    if not todo:
        print("Nothing to do.")
        return

    results = []
    with Pool(
        processes=min(args.workers, max(len(todo), 1)),
        initializer=_init_worker,
        initargs=(caida_dir, args.policy, origins, asns,
                  args.batch_size, shard_dir, deadline, args.verify_sample),
    ) as pool, (bench_dir / f"{run_id}.jsonl").open("w") as log:
        for m in pool.imap_unordered(_run_batch, todo):
            log.write(json.dumps(m) + "\n")
            log.flush()
            results.append(m)
            if "skipped" not in m:
                print(f"  batch {m['batch']:>5}: {m['num_origins']} origins  "
                      f"setup {m['setup_s']:.1f}s  propagate {m['propagate_s']:.1f}s  "
                      f"extract {m['extract_s']:.1f}s  write {m['write_s']:.1f}s  "
                      f"total {m['total_s']:.1f}s  rss {m['peak_rss_mb']:.0f}MB  "
                      f"shard {m['shard_mb']:.1f}MB"
                      + (f"  verify {m['verify_ribs_in_entries']} RIBs-In entries, "
                         f"{m['verify_mismatches']} mismatches ({m['verify_s']:.1f}s)"
                         if "verify_s" in m else ""), flush=True)

    done = [m for m in results if "skipped" not in m]
    wall_s = time.time() - start_wall
    done_total = sum(1 for b in range(num_batches) if (shard_dir / f"batch_{b:05d}.npz").exists())
    summary = {
        "run_id": run_id,
        "policy": args.policy,
        "workers": args.workers,
        "batches_run": len(done),
        "batches_skipped_time_budget": len(results) - len(done),
        "wall_s": round(wall_s, 1),
        "main_graph_build_s": round(main_graph_build_s, 1),
        "batches_done_overall": done_total,
        "batches_total": num_batches,
    }
    if done:
        origins_done = sum(m["num_origins"] for m in done)
        core_s = sum(m["total_s"] for m in done)
        per_origin_s = core_s / origins_done
        remaining_origins = len(origins) - done_total * args.batch_size
        remaining_core_h = max(remaining_origins, 0) * per_origin_s / 3600
        summary.update({
            "mean_batch_s": round(core_s / len(done), 2),
            "mean_propagate_s": round(sum(m["propagate_s"] for m in done) / len(done), 2),
            "mean_extract_s": round(sum(m["extract_s"] for m in done) / len(done), 2),
            "per_origin_core_s": round(per_origin_s, 4),
            "max_peak_rss_mb": round(max(m["peak_rss_mb"] for m in done)),
            "mean_shard_mb": round(sum(m["shard_mb"] for m in done) / len(done), 2),
            "projected_total_core_h": round(len(origins) * per_origin_s / 3600, 1),
            "projected_remaining_core_h": round(remaining_core_h, 1),
            "projected_remaining_wall_h_at_these_workers": round(remaining_core_h / args.workers, 2),
            "projected_total_disk_gb": round(sum(m["shard_mb"] for m in done) / len(done)
                                             * num_batches / 1024, 1),
        })
        if args.verify_sample:
            summary["verify_ribs_in_entries"] = sum(m["verify_ribs_in_entries"] for m in done)
            summary["verify_mismatches"] = sum(m["verify_mismatches"] for m in done)
    (bench_dir / f"{run_id}_summary.json").write_text(json.dumps(summary, indent=2))

    print("\nSummary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("\n(Projections assume one job with this many workers; with an array of N "
          "such jobs divide the remaining wall time by N.)")


if __name__ == "__main__":
    main()
