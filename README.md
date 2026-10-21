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
Weeks 2–5 and 7–8 are explicitly marked as unpublished placeholders.

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
