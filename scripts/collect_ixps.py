"""Collect IXP route-server ASNs from PeeringDB and check them against CAIDA.

Read-only: nothing here modifies the CAIDA topology. For every PeeringDB
network registered as a route server, it reports how that ASN appears in the
same CAIDA serial-2 file bgpy builds the simulation graph from.

Every network call this script makes (all plain GETs, no auth needed):
    https://www.peeringdb.com/api/ix?fields=id,name,city,country,net_count
    https://www.peeringdb.com/api/net?info_type=Route%20Server&fields=id,asn,name
    https://www.peeringdb.com/api/netixlan?fields=asn,ix_id
plus bgpy's CAIDAASGraphCollector, which downloads the CAIDA file only if it
isn't already in bgpy's cache for today.

PeeringDB rate-limits anonymous clients (HTTP 429), so each table is fetched
once and saved under <out>/peeringdb/. Re-runs reuse those files unless
--refresh is given.

Outputs, under --out (default: sav/ixps):
    peeringdb/{ix,route_servers,netixlan}.json  raw PeeringDB responses
    ixps.json   metadata + one record per route-server ASN
    ixps.csv    the same records, flat, for a spreadsheet

Usage:
    python3 collect_ixps.py
    python3 collect_ixps.py --caida-path ~/.cache/bgpy/<date>/CAIDAASGraphCollector_<date>.txt
"""
import argparse
import csv
import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

PEERINGDB_API = "https://www.peeringdb.com/api"

# table name -> (endpoint, query params)
PEERINGDB_TABLES = {
    "ix": ("ix", {"fields": "id,name,city,country,net_count"}),
    "route_servers": ("net", {"info_type": "Route Server", "fields": "id,asn,name"}),
    "netixlan": ("netixlan", {"fields": "asn,ix_id"}),
}

MAX_RETRIES = 20
RETRY_WAIT_S = 60


###############
# PeeringDB   #
###############

def fetch_peeringdb_table(name: str, cache_dir: Path, refresh: bool) -> list[dict]:
    """Returns one PeeringDB table, downloading it only if not cached"""

    path = cache_dir / f"{name}.json"
    if path.exists() and not refresh:
        print(f"  {name}: using cached {path}")
        return json.loads(path.read_text())["data"]

    endpoint, params = PEERINGDB_TABLES[name]
    url = f"{PEERINGDB_API}/{endpoint}"
    for attempt in range(1, MAX_RETRIES + 1):
        r = requests.get(url, params=params, timeout=300)
        if r.status_code == 429:
            print(f"  {name}: rate limited (429), retry {attempt}/{MAX_RETRIES} "
                  f"in {RETRY_WAIT_S}s")
            time.sleep(RETRY_WAIT_S)
            continue
        r.raise_for_status()
        cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(r.text)
        print(f"  {name}: downloaded {r.url}")
        return r.json()["data"]
    raise RuntimeError(f"PeeringDB kept rate limiting {url}")


##########
# CAIDA  #
##########

def get_caida_path(caida_path: Path | None) -> Path:
    """The CAIDA serial-2 file bgpy would use today (or the one given)"""

    if caida_path is not None:
        return caida_path.expanduser()
    from bgpy.as_graphs import CAIDAASGraphCollector

    return CAIDAASGraphCollector().run()


def parse_caida(path: Path) -> dict:
    """Parses relationships plus the input clique / IXP header lines

    Format: https://publicdata.caida.org/datasets/as-relationships/serial-2/
        <provider>|<customer>|-1|<source>
        <peer>|<peer>|0|<source>
    """
    customers: dict[int, set[int]] = defaultdict(set)
    providers: dict[int, set[int]] = defaultdict(set)
    peers: dict[int, set[int]] = defaultdict(set)
    asns: set[int] = set()
    input_clique: set[int] = set()
    caida_ixps: set[int] = set()

    with path.open() as f:
        for line in f:
            if line.startswith("# input clique"):
                input_clique = {int(x) for x in line.split(":")[-1].split()}
            elif line.startswith("# IXP ASes"):
                caida_ixps = {int(x) for x in line.split(":")[-1].split()}
            elif not line.startswith("#"):
                a, b, rel, _source = line.strip().split("|")
                a, b = int(a), int(b)
                asns.update((a, b))
                if rel == "-1":
                    customers[a].add(b)
                    providers[b].add(a)
                else:
                    peers[a].add(b)
                    peers[b].add(a)

    return {
        "customers": customers,
        "providers": providers,
        "peers": peers,
        "asns": asns,
        "input_clique": input_clique,
        "caida_ixps": caida_ixps,
    }


def customer_cone(roots, customers: dict[int, set[int]]) -> set[int]:
    """Every AS reachable by walking customer links down from roots"""

    seen: set[int] = set()
    stack = list(roots)
    while stack:
        asn = stack.pop()
        if asn not in seen:
            seen.add(asn)
            stack.extend(customers[asn])
    return seen


##########
# Report #
##########

def build_records(caida: dict, ixs: list, route_servers: list, netixlan: list) -> list[dict]:
    customers, providers, peers = caida["customers"], caida["providers"], caida["peers"]

    ix_by_id = {ix["id"]: ix for ix in ixs}
    members_of_ix: dict[int, set[int]] = defaultdict(set)
    ixs_of_asn: dict[int, set[int]] = defaultdict(set)
    for row in netixlan:
        members_of_ix[row["ix_id"]].add(row["asn"])
        ixs_of_asn[row["asn"]].add(row["ix_id"])

    records = []
    for rs in route_servers:
        asn = rs["asn"]
        ix_ids = sorted(ixs_of_asn[asn])
        members = set().union(*(members_of_ix[i] for i in ix_ids)) if ix_ids else set()
        rs_customers = customers[asn]
        rs_peers = peers[asn]

        cone = customer_cone(rs_customers, customers)
        # Reached by going IXP -> peer -> down. The peers themselves are left
        # out: they would receive the packet on a peer interface.
        via_peers = customer_cone(
            (c for p in rs_peers for c in customers[p]), customers
        ) - cone - rs_peers

        records.append({
            "asn": asn,
            "name": rs["name"],
            "peeringdb_net_id": rs["id"],
            "ixs": [ix_by_id[i]["name"] for i in ix_ids if i in ix_by_id],
            "peeringdb_ix_ids": ix_ids,
            "num_ix_members": len(members),
            "in_caida_ixp_header": asn in caida["caida_ixps"],
            "in_caida_links": asn in caida["asns"],
            "in_input_clique": asn in caida["input_clique"],
            "num_customers": len(rs_customers),
            "num_providers": len(providers[asn]),
            "num_peers": len(rs_peers),
            "num_customers_that_are_ix_members": len(rs_customers & members),
            "num_single_homed_customers": sum(
                1 for c in rs_customers if providers[c] == {asn}
            ),
            "customer_cone_size": len(cone - {asn}),
            "reached_via_peers_size": len(via_peers),
            "customers": sorted(rs_customers),
            "providers": sorted(providers[asn]),
        })

    records.sort(key=lambda r: (-r["num_customers"], -r["num_peers"], r["asn"]))
    return records


CSV_COLUMNS = (
    "asn", "name", "ixs", "num_ix_members", "in_caida_ixp_header",
    "in_caida_links", "in_input_clique", "num_customers", "num_providers",
    "num_peers", "num_customers_that_are_ix_members",
    "num_single_homed_customers", "customer_cone_size", "reached_via_peers_size",
)


def write_outputs(out_dir: Path, metadata: dict, records: list[dict]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "ixps.json"
    json_path.write_text(json.dumps({"metadata": metadata, "route_servers": records}, indent=2))

    csv_path = out_dir / "ixps.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow({**r, "ixs": "; ".join(r["ixs"])})

    print(f"\nWrote {json_path}\nWrote {csv_path}")


def print_summary(metadata: dict, records: list[dict]) -> None:
    print(f"\nCAIDA file: {metadata['caida_file']} ({metadata['num_caida_asns']} ASes)")
    print(f"PeeringDB route-server ASNs: {len(records)}")
    print(f"  not in any CAIDA link:  {sum(not r['in_caida_links'] for r in records)}")
    print(f"  with CAIDA customers:   {sum(r['num_customers'] > 0 for r in records)}")
    print(f"  peers only:             {sum(r['num_peers'] > 0 and not r['num_customers'] and not r['num_providers'] for r in records)}")
    print(f"  in CAIDA's IXP header:  {sum(r['in_caida_ixp_header'] for r in records)}")
    print(f"  in input clique:        {sum(r['in_input_clique'] for r in records)}")

    print("\nCAIDA '# IXP ASes' header line:")
    by_asn = {r["asn"]: r for r in records}
    for asn in metadata["caida_ixp_header_asns"]:
        r = by_asn.get(asn)
        name = r["name"] if r else "(not a PeeringDB route server)"
        print(f"  AS{asn:<7} {name}")

    print("\nRoute servers with CAIDA customers:")
    print(f"{'ASN':>8}  {'name':34} {'cust':>4} {'∈IX':>4} {'1-hm':>4} {'peer':>4} "
          f"{'prov':>4} {'cone':>6} {'+peers':>6}")
    for r in records:
        if r["num_customers"] == 0:
            continue
        print(f"{r['asn']:>8}  {r['name'][:34]:34} {r['num_customers']:>4} "
              f"{r['num_customers_that_are_ix_members']:>4} "
              f"{r['num_single_homed_customers']:>4} {r['num_peers']:>4} "
              f"{r['num_providers']:>4} {r['customer_cone_size']:>6} "
              f"{r['reached_via_peers_size']:>6}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--out", type=Path,
        # sav/sav_pkg/scripts/collect_ixps.py -> sav/ixps
        default=Path(__file__).resolve().parents[2] / "ixps",
        help="Output directory (default: sav/ixps)",
    )
    parser.add_argument(
        "--caida-path", type=Path, default=None,
        help="CAIDA serial-2 file to check against "
        "(default: the one bgpy's CAIDAASGraphCollector uses today)",
    )
    parser.add_argument(
        "--refresh", action="store_true",
        help="Re-download the PeeringDB tables even if cached",
    )
    args = parser.parse_args()
    out_dir = args.out.expanduser().resolve()

    print("PeeringDB:")
    pdb_dir = out_dir / "peeringdb"
    ixs = fetch_peeringdb_table("ix", pdb_dir, args.refresh)
    route_servers = fetch_peeringdb_table("route_servers", pdb_dir, args.refresh)
    netixlan = fetch_peeringdb_table("netixlan", pdb_dir, args.refresh)

    caida_path = get_caida_path(args.caida_path)
    print(f"\nCAIDA: parsing {caida_path}")
    caida = parse_caida(caida_path)

    records = build_records(caida, ixs, route_servers, netixlan)
    metadata = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "caida_file": str(caida_path),
        "num_caida_asns": len(caida["asns"]),
        "caida_ixp_header_asns": sorted(caida["caida_ixps"]),
        "input_clique": sorted(caida["input_clique"]),
        "num_peeringdb_ixs": len(ixs),
        "peeringdb_tables": {
            name: f"{PEERINGDB_API}/{endpoint}" for name, (endpoint, _) in PEERINGDB_TABLES.items()
        },
    }
    print_summary(metadata, records)
    write_outputs(out_dir, metadata, records)


if __name__ == "__main__":
    main()
