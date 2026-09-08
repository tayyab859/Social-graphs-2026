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
