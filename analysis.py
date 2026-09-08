"""Reproduce the Week 1 headline reciprocity statistics."""

from collections import Counter
from urllib.request import Request, urlopen

BASE = "https://sunelehmann.com/socialgraphs2026-web/data/"


def download(filename):
    request = Request(BASE + filename, headers={"User-Agent": "DTU-02805-link-mirror/1.0"})
    return urlopen(request).read().decode("utf-8")


nodes_text = download("week1_nodes.tsv")
edges_text = download("week1_edges.tsv")
node_lines = [line for line in nodes_text.splitlines() if line and not line.startswith("#")]
node_ids = [line.split("\t", 1)[0] for line in node_lines[1:]]
edges = {
    tuple(line.split("\t"))
    for line in edges_text.splitlines()
    if line and not line.startswith("#")
}

in_degree = Counter(target for source, target in edges)
out_degree = Counter(source for source, target in edges)
mutual_pairs = {
    tuple(sorted((source, target)))
    for source, target in edges
    if source != target and (target, source) in edges
}
isolates = [node for node in node_ids if in_degree[node] == 0 and out_degree[node] == 0]

print(f"Nodes: {len(node_ids)}")
print(f"Directed edges: {len(edges)}")
print(f"Mutual pairs: {len(mutual_pairs)}")
print(f"Reciprocated directed edges: {2 * len(mutual_pairs)}")
print(f"Global reciprocity: {2 * len(mutual_pairs) / len(edges):.4f}")
print(f"Isolates: {len(isolates)}")

assert len(node_ids) == 303
assert len(edges) == 1784
assert len(mutual_pairs) == 350
assert len(isolates) == 17

