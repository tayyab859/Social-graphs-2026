"""Run from any directory: python3 weeks/week8/check_dataset.py.

Standard library only. Checks existing frozen course files; no network access.
Prints deterministic JSON. This is a feasibility check, not the proposed analysis.
"""
import csv
import hashlib
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/week4"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader((line for line in stream if not line.startswith("#")), delimiter="\t", quoting=csv.QUOTE_NONE))


nodes_path = DATA / "week4_philosophers_nodes.tsv"
edges_path = DATA / "week4_philosophers_edges.tsv"
nodes, edges = read_tsv(nodes_path), read_tsv(edges_path)
ids = {row["node_id"] for row in nodes}
endpoints = {row[key] for row in edges for key in ("source", "target")}
lengths = [len(re.findall(r"[^\W\d_]+", row["description"], flags=re.UNICODE)) for row in nodes]
result = {
    "scope": "Frozen philosophers TSV feasibility check only; no communities or TF-IDF computed",
    "snapshot_date": "2026-09-15",
    "node_rows": len(nodes),
    "unique_node_ids": len(ids),
    "directed_edge_rows": len(edges),
    "unknown_edge_endpoints": sorted(endpoints - ids),
    "duplicate_directed_edges": len(edges) - len({(r['source'], r['target']) for r in edges}),
    "self_loops": sum(r['source'] == r['target'] for r in edges),
    "nodes_without_incident_edges": len(ids - endpoints),
    "nonempty_descriptions": sum(bool(row['description'].strip()) for row in nodes),
    "nonempty_era_labels": sum(bool(row['era'].strip()) for row in nodes),
    "description_word_count": {"min": min(lengths), "median": statistics.median(lengths), "max": max(lengths)},
    "word_count_rule": "Unicode alphabetic runs; digits and underscores excluded; hyphens split",
    "examples": [{key: row[key] for key in ('node_id', 'description', 'era')} for row in nodes if row['node_id'] in ('Abhinavagupta', 'Abraham_Tucker')],
    "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (nodes_path, edges_path)},
}
assert len(nodes) == len(ids), "Duplicate node IDs"
assert not endpoints - ids, "Edge endpoint missing from roster"
assert all(int(r['weight']) > 0 for r in edges), "Invalid edge weight"
print(json.dumps(result, indent=2, ensure_ascii=False))
