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
Week 3’s fixed-ranking removal experiment is published at `weeks/week3/`.
Week 4’s weighted-versus-unweighted philosopher comparison is published at `weeks/week4/`.
Week 5’s hyphen-tokenization comparison is published at `weeks/week5/`.
Weeks 7–8 remain unpublished placeholders.

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

## Week 3 — Hubs or bridges?

Exercise 3.12: compare fixed degree-first and exact betweenness-first removals on
the same full undirected Marvel graph (303 nodes, 1,434 edges; initial LCC 277).
Both rankings are computed once, with node-ID alphabetical tie-breaking.
Random baseline: 200 permutations, seeds 20261123–20261322.
At 100 removals the LCC is 77 (degree), 58 (betweenness), 178.27 (random mean).
The targeted curves cross: betweenness does not dominate at every count.
Rockman’s frozen links explain his degree rank 256 versus betweenness rank 59.

```bash
pip install -r scripts/requirements-week3.txt
python scripts/analyse_week3.py
python scripts/analyse_week3.py --output-dir /tmp/week3-check
```

Outputs under `weeks/week3/`: SVG/PNG chart, rankings CSV, removal-curves CSV,
and results.json (all 200 random curves, orders, input hashes, software versions).
The script checks input hashes/counts, monotonicity, remaining-node bounds and
Rockman’s links; an independent BFS checks both orders at nine cut points.
The static article must be reconciled if parameters change. Publish through
the existing GitHub Pages main-branch deployment. No Teams post is sent.

## Week 4 — One link or twenty-four?

Exercise 4.13: do repeated Wikipedia links change philosophers’ communities?
Uses the official frozen 2026-09-15 philosopher node/weighted-edge TSVs committed
under `data/week4/`. Directions are summed, then the same giant component is
used for both treatments: 1,374 nodes, 9,139 edges, total weight 15,757.
The same 68 isolates and separate two-node component are excluded from both.

```bash
python3 -m venv .venv-week4
source .venv-week4/bin/activate
pip install -r scripts/requirements-week4.txt
python scripts/analyse_week4.py
python scripts/analyse_week4.py --output-dir /tmp/week4-check
```

Louvain runs at resolution 1 with seeds 0–19, weight=None versus weight="weight".
Mean NMI: 0.658 across all 400 cross-treatment pairs, versus 0.720/0.756 across
different seeds within unweighted/weighted runs. The reused pairs are descriptive,
not independent observations. Seed 0 is fixed for the overlap figure (NMI 0.637).
Erasmus–More has weight 24 (18+6) and co-membership 5/20 unweighted versus 20/20
weighted. This is an exploratory selected case, not a causal single-edge test.

Outputs in `weeks/week4/`: SVG/PNG overlap figure, results.json with all 40 labelings,
community_overlap.csv, memberships.csv, seed_agreement.csv and case_links.csv.
The graph’s edges and node order are identical between treatments; software versions
and SHA-256 hashes are saved. The script validates hashes, counts, directed-weight
sums, partition coverage, overlap totals, and NMI via an independent calculation.
The static page matches these saved outputs; reconcile it if rerunning with changes.
Use the existing GitHub Pages deployment from main, then verify the page, figure
and homepage card. No Teams message or peer feedback is sent.


## Week 5 — A small hyphen, a different vocabulary

Exercise 5.9: compare the same 303 frozen Marvel articles with internal ASCII
hyphens retained versus split. Only the hyphen rule changes. Both use Python
Unicode word characters excluding digits/underscore, lowercase, retain single
letters and stopwords, and do no lemmatization. Other punctuation is a boundary.
Keep: 27,711 types, 10,621 hapax (38.33%). Split: 25,302 types, 8,741 hapax (34.55%).
The reduction is 1,880 hapax (17.70%), or 3.78 percentage points of vocabulary.

```bash
python3 -m venv .venv-week5
source .venv-week5/bin/activate
pip install -r scripts/requirements-week5.txt
python scripts/analyse_week5.py
python scripts/analyse_week5.py --output-dir /tmp/week5-check
```

The script downloads `data/marvel_pages.zip` when missing and enforces SHA-256
`36023ca077053b3df5bd55630754cb514c3f9dbecbd70afcb2283e5bcc0017ee`.
Source: https://sunelehmann.com/socialgraphs2026-web/data/marvel_pages.zip
Snapshot: 2026-08-26. All 303 decoded IDs are checked against the node TSV.
Outputs under `weeks/week5/`: results.json, both ranked frequency CSVs,
hyphen_audit.csv, document_counts.csv, and rank-frequency.svg/.png.
An isolated rerun reproduces outputs; the article is static and must be updated
if rules change. Both curves have separate ranks, raw counts and log-log axes;
no exact Zipf fit or significance claim is made. Passage examples link to source
articles and preserve frozen-text offsets in results.json. All text is attributed
to Wikipedia contributors; the full archive is not committed.
Publish through existing GitHub Pages from main. Teams posting/peer feedback are
separate; the agent did not send messages to classmates.
