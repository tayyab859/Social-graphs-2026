# Marvel Link Mirror

Week 1 group post for DTU course **02805 Social Graphs and Interactions**.

The project asks a directed-network question that is easy to lose when a graph is
collapsed to undirected edges: **which Marvel Wikipedia pages link back, and which
relationships remain one-way?**

The public page calculates its results from the official frozen Week 1 TSV files.
It includes:

- an interactive in-degree versus out-degree plot;
- linear and log–log views (the log view uses `k + 1`);
- a searchable character-level reciprocity inspector;
- rankings for one-way attention and one-way broadcasting;
- methods, interpretation, limitations, and an AI-use statement.

## Run locally

Because the page fetches the course TSV files, serve the folder rather than opening
`index.html` directly:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Reproduce the headline numbers

```bash
python3 analysis.py
```

## Author

- Muhammad Tayyab

## Course website (Weeks 1–8)

The root homepage now links to eight weekly subsections. Week 1's original post is
preserved at `weeks/week1/`. Week 6's **Marvel Matchmaker** is at `weeks/week6/`.
Week 2’s triangle shuffle test is published at `weeks/week2/`.
Weeks 3–5 and 7–8 remain unpublished placeholders.

Week 6 compares TF-IDF document similarity, TF-IDF-weighted Word2Vec document
vectors, and Wikipedia link neighbors. It includes a browser explorer, aggregate
comparison, source-text case checks, and seed/window sensitivity checks.

```bash
pip install -r requirements.txt
PYTHONHASHSEED=0 python scripts/analyse_week6.py
python -m http.server 8000
```

The analysis downloads the course archive when absent. It writes `results.json`
and `data/week6_audit.json`. The published site uses those saved results and needs
no Python server beyond ordinary static hosting. After rerunning with a different
environment, reconcile the article's displayed summary numbers with the new results.
Word2Vec runs may vary across package versions/platforms despite a fixed seed.

Data source: https://sunelehmann.com/socialgraphs2026-web/data/
The original Wikipedia article content remains attributable to its contributors
under Wikipedia's applicable licenses. Saved passages link back through character
URLs in results.json; the frozen full archive is not committed.

## Week 2 — Triangles beyond the hubs

Question: does the Marvel Wikipedia network have more triangles than expected
conditional on every character’s undirected degree? Source: official frozen
2026-08-26 Week 1 node and edge TSVs, already committed under `data/`.
No download or live Wikipedia crawl is needed. All 303 nodes and 17 isolates remain.

```bash
python3 -m venv .venv-week2
source .venv-week2/bin/activate
pip install -r scripts/requirements-week2.txt
python scripts/analyse_week2.py
python -m http.server 8000
```

Open http://localhost:8000/weeks/week2/ . The analysis takes a few minutes.
It regenerates `results.json`, `shuffle_counts.csv`, and SVG/PNG figures under
`weeks/week2/`. The committed SVG is used by the article. The static HTML summary
must be reconciled if analysis parameters change. Python and package versions are
recorded in results.json; use the pinned Week 2 requirements for reproducibility.
For an isolated rerun: `python scripts/analyse_week2.py --output-dir /tmp/week2-check`.
Compare its `results.json` with the committed file (Python version metadata may differ).

Checks: frozen SHA-256 hashes; node/edge/isolate counts; no unknown endpoints;
independent observed-triangle count; per-character degree equality, edge count,
simplicity and isolate-set preservation in all 600 shuffled graphs. The primary
ensemble uses 500 seeds starting at 20261123 and 20m successful swaps per run;
a separate 100-run sensitivity ensemble uses seeds starting at 30261123 and 100m
swaps. Every run starts from the observed graph. We report (b+1)/(B+1), upper-tail,
and do not claim exact null sampling or infer causality from the result.

Publishing uses the existing GitHub Pages build from `main`; no new hosting or
workflow is required. After pushing, verify the Week 2 page, SVG and homepage card.
