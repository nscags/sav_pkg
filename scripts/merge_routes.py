"""Merge the precompute_routes.py shards into one memory-mappable table.

Reads <routes dir>/shards_b<B>/batch_*.npz and writes, in the same dir:
    nh.npy        uint32[num_origins, num_asns], row i = origins[i], column j =
                  metadata asns[j], value = that AS's next hop toward the
                  origin (the origin itself at the origin, 0 if no route)
    origins.npy   uint32[num_origins], sorted

This is what sav_pkg/simulation_engine/background_routes.py loads
(SAVScenarioConfig.routes_dir). ~26 GB, built once; run it on the machine
that runs the simulations.

Usage:
    python3 merge_routes.py                                   # default dir
    python3 merge_routes.py --routes-dir ~/sav/routes/caida_20260901
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--routes-dir", type=Path, default=Path("~/sav/routes/caida_20260901"))
    args = ap.parse_args()
    routes_dir = args.routes_dir.expanduser().resolve()

    meta = json.loads((routes_dir / "metadata.json").read_text())
    batch_size, num_batches = meta["batch_size"], meta["num_batches"]
    num_asns, num_origins = meta["num_asns"], meta["num_origins"]
    shard_dir = routes_dir / f"shards_b{batch_size}"

    shards = [shard_dir / f"batch_{b:05d}.npz" for b in range(num_batches)]
    missing = [s.name for s in shards if not s.exists()]
    if missing:
        raise SystemExit(f"{len(missing)} shard(s) missing, e.g. {missing[:5]}; "
                         "finish precompute_routes.py first")

    out = routes_dir / "nh.npy"
    tmp = routes_dir / "nh.npy.tmp"
    print(f"Writing {out} ({num_origins} x {num_asns} uint32, "
          f"{num_origins * num_asns * 4 / 2**30:.1f} GB)", flush=True)
    nh = np.lib.format.open_memmap(tmp, mode="w+", dtype=np.uint32,
                                   shape=(num_origins, num_asns))
    origins = np.zeros(num_origins, dtype=np.uint32)

    t0 = time.time()
    for b, shard in enumerate(shards):
        d = np.load(shard)
        start = b * batch_size
        k = len(d["origins"])
        if d["nh"].shape != (k, num_asns):
            raise SystemExit(f"{shard.name} has shape {d['nh'].shape}, expected {(k, num_asns)}")
        nh[start:start + k] = d["nh"]
        origins[start:start + k] = d["origins"]
        if b % 50 == 0:
            print(f"  {b}/{num_batches} shards ({time.time() - t0:.0f}s)", flush=True)

    if start + k != num_origins:
        raise SystemExit(f"Shards cover {start + k} origins, metadata says {num_origins}")
    if not np.all(origins[:-1] < origins[1:]):
        raise SystemExit("Origins are not strictly increasing across shards")

    nh.flush()
    del nh
    tmp.rename(out)
    np.save(routes_dir / "origins.npy", origins)
    print(f"Done in {time.time() - t0:.0f}s: {out} and {routes_dir / 'origins.npy'}")


if __name__ == "__main__":
    main()
