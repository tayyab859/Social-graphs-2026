"""Reproduce Week 2 using the committed, hash-checked frozen course TSVs."""
import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path
import statistics

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://sunelehmann.com/socialgraphs2026-web/data/'

def load_graph():
    paths = [ROOT / 'data' / f'week1_{kind}.tsv' for kind in ('nodes', 'edges')]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert hashes == {
        'week1_nodes.tsv': 'a10ec309ac60ea8b72bcc1a18aba801414896676dac172619def0435e585391e',
        'week1_edges.tsv': '87be017a35e8f27a1f1bc0912ebb5723c0084e460cb2dbd0d2abd0e83fc644b2',
    }, 'Frozen data hash mismatch'
    node_lines = [x for x in paths[0].read_text().splitlines() if x and not x.startswith('#')]
    nodes = list(csv.DictReader(node_lines, delimiter='\t', quoting=csv.QUOTE_NONE))
    ids = [x['node_id'] for x in nodes]
    assert len(ids) == len(set(ids)) == 303
    edges = [tuple(x.split('\t')) for x in paths[1].read_text().splitlines() if x and not x.startswith('#')]
    assert all(len(e) == 2 and set(e) <= set(ids) for e in edges)
    directed = nx.DiGraph()
    directed.add_nodes_from(ids)
    directed.add_edges_from(edges)
    assert directed.number_of_edges() == 1784
    graph = nx.Graph()
    graph.add_nodes_from(ids)  # Include isolates before adding any edges.
    graph.add_edges_from((a, b) for a, b in directed.edges if a != b)
    assert graph.number_of_edges() == 1434
    assert nx.number_of_isolates(graph) == 17
    return graph, hashes, len(edges), nx.number_of_selfloops(directed)

def triangles(g):
    return sum(nx.triangles(g).values()) // 3

def ensemble(g, count, seed, multiplier):
    degrees = dict(g.degree())
    samples = []
    for i in range(count):
        h = g.copy()  # Separate seeded run, never continue the previous chain.
        swaps = multiplier * g.number_of_edges()
        nx.double_edge_swap(h, nswap=swaps, max_tries=100 * swaps, seed=seed + i)
        assert dict(h.degree()) == degrees, 'A character degree changed'
        assert set(h) == set(g) and h.number_of_edges() == g.number_of_edges()
        assert nx.number_of_selfloops(h) == 0 and not h.is_multigraph()
        assert set(nx.isolates(h)) == set(nx.isolates(g))
        samples.append({'seed': seed + i, 'triangles': triangles(h)})
    return samples

def summarize(samples, observed):
    values = [s['triangles'] for s in samples]
    mean, sd = statistics.mean(values), statistics.stdev(values)
    exceed = sum(v >= observed for v in values)
    return dict(mean=mean, sd=sd, minimum=min(values), maximum=max(values),
                exceedances=exceed, p_upper=(exceed + 1)/(len(values)+1),
                z=(observed-mean)/sd, observed_to_mean=observed/mean)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, default=ROOT/'weeks/week2')
    args = p.parse_args()
    out = args.output_dir; out.mkdir(parents=True, exist_ok=True)
    g, hashes, rows, selfloops = load_graph()
    observed = triangles(g)
    # Independent adjacency-intersection count, not nx.triangles.
    independent = sum(len(set(g[a]) & set(g[b])) for a,b in g.edges()) // 3
    assert independent == observed
    samples = ensemble(g, 500, 20261123, 20)
    sensitivity = ensemble(g, 100, 30261123, 100)
    stats = summarize(samples, observed)
    results = dict(question='Does the Marvel Wikipedia network have more triangles than expected given how many connections each character has?',
        source=SOURCE, snapshot_date='2026-08-26', input_sha256=hashes,
        nodes=len(g), directed_edge_rows=rows, removed_selfloops=selfloops,
        undirected_edges=g.number_of_edges(), isolates=nx.number_of_isolates(g),
        observed_triangles=observed, independent_triangle_count=independent,
        shuffles=500, swaps_per_shuffle=20*g.number_of_edges(), swap_multiplier=20,
        seed_start=20261123, degree_checks_passed=600, summary=stats, samples=samples,
        sensitivity=dict(shuffles=100, swap_multiplier=100, seed_start=30261123,
            summary=summarize(sensitivity, observed), samples=sensitivity),
        degrees_by_character=dict(g.degree()),
        environment=dict(python=platform.python_version(), networkx=nx.__version__, matplotlib=matplotlib.__version__))
    (out/'results.json').write_text(json.dumps(results, indent=2)+'\n')
    with (out/'shuffle_counts.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['ensemble','seed','triangles'])
        for name, rows in [('main_20m',samples),('sensitivity_100m',sensitivity)]:
            for r in rows:w.writerow([name,r['seed'],r['triangles']])
    plot_results(out, results)
    print(json.dumps({k:v for k,v in results.items() if k not in ['samples','degrees_by_character','sensitivity']},indent=2))
    print('Sensitivity:',results['sensitivity']['summary'])

def plot_results(out, results):
    observed = results['observed_triangles']
    samples = results['samples']
    stats = results['summary']
    plt.rcParams.update({'font.size':12,'svg.hashsalt':'week2-triangle-test'})
    fig, ax = plt.subplots(figsize=(11,5.5), layout='constrained', facecolor='#0d1a25')
    ax.set_facecolor('#0d1a25')
    ax.hist([s['triangles'] for s in samples], bins=22, color='#41d9d0', edgecolor='#0d1a25', label='500 degree-preserving shuffles')
    ax.axvline(observed,color='#ff8a5b',linewidth=3,label=f'Observed: {observed:,}')
    ax.set(xlabel='Number of undirected triangles',ylabel='Number of shuffled networks',title='Marvel triangles: observed network versus degree-preserving shuffles')
    ax.set_xlim(0,observed*1.1)
    ax.tick_params(colors='#eef6fb')
    for item in [ax.xaxis.label,ax.yaxis.label,ax.title]:item.set_color('#eef6fb')
    for spine in ax.spines.values():spine.set_color('#9db0be')
    legend=ax.legend(facecolor='#122432',edgecolor='#29404e',labelcolor='#eef6fb',loc='upper left')
    ax.text(.03,.72,f"Null mean: {stats['mean']:,.1f}\nRange: {stats['minimum']:,}–{stats['maximum']:,}\nAt least observed: {stats['exceedances']}/500\nOne-sided Monte Carlo p = {stats['p_upper']:.4f}",transform=ax.transAxes,ha='left',va='top',color='#eef6fb')
    fig.savefig(out/'triangle-shuffles.svg',metadata={'Date':None})
    fig.savefig(out/'triangle-shuffles.png',dpi=160)
    plt.close(fig)

if __name__ == '__main__':main()
