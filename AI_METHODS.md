# AI Methods — Week 1

An AI coding agent assisted with the research framing, HTML/CSS/JavaScript, and the
small Python reproduction script. The question—reciprocity and one-way attention—was
chosen after reviewing the themes already used by other groups, so this post would
not merely repeat another hub or connected-component story.

The AI was not treated as a source of network measurements. The published page
downloads the official frozen Week 1 node and edge files and calculates its results
from those files. It performs visible checks for the core invariants supplied by the
course. The independent `analysis.py` script checks 303 nodes, 1,784 edges, 350
mutual pairs, and 17 isolates.

Interpretive claims are deliberately limited. A Wikipedia link is described as an
editorial link between articles—not as proof of friendship, importance in Marvel
canon, or a real social relationship. The page also states the snapshot date and the
main data-collection choices that constrain its conclusions.

# Week 6 and course website

An AI coding agent implemented the Week 1–8 navigation and Week 6 analysis and post.
It trained Word2Vec on the official frozen Marvel corpus, calculated all published
rankings and aggregate metrics, and inspected stored source passages for selected
cases. These were AI-assisted checks, not a blinded human annotation study. The
student should read and discuss the interpretations before presenting them.

The analysis compares TF-IDF with TF-IDF-weighted word-vector averages and uses
Wikipedia links as a structural comparison, not a relevance gold standard. It
includes seed and context-window sensitivity checks. Input SHA-256 hashes are
stored in weeks/week6/results.json. Full source text is downloaded by the script;
only the original link tables and short inspection passages are included here.
No classmate code or results were copied. The classmate website informed the idea
of pairing a question-driven post with an interactive explorer.

## Week 6 editorial validation

The agent rechecked the frozen source text, corrected the Storm name claim,
and added attributed source paraphrases to the four case discussions.
The main overlap figure is calculated from the saved top-five sets for all
303 characters: counts for overlaps 0–5 are 26, 69, 73, 85, 45 and 5.
These checks are AI-assisted and do not imply student or group review.

## Week 2 — Triangle shuffle test

The user specified the question and degree-preserving comparison. The AI agent
read official exercise 2.11 and the course data documentation, inspected the
existing repository design, wrote and ran the analysis, and drafted the article.
No measurements were copied from illustrative course clustering values.

Executed checks:
- Downloaded both official frozen TSVs and confirmed byte equality with the repo copies.
- Kept all 303 node IDs before adding edges, including all 17 isolates.
- Merged either directed link into one unweighted undirected edge (1,434 total).
- Independently cross-checked 1,839 triangles via common-neighbour intersections.
- Compared each character’s degree by ID after every shuffle, not merely the distribution.
- Checked exact node set, edge count, no self-loops/multiedges and isolate IDs in 600 runs.
- Used reproducible, distinct seeds and fresh graph copies; saved all counts/seeds and hashes.
- Compared the primary 20m-swap ensemble with 100m-swap sensitivity runs.
- Checked the figure and article against saved results. The one-sided p-value uses
  the plus-one correction; it is not reported as zero or as the probability of the null.

Run with `pip install -r scripts/requirements-week2.txt` then
`python scripts/analyse_week2.py` from the repository root. See README for an
isolated output directory. The AI-assisted audit is not independent human review.
Students should inspect the plot, understand why direction is discarded and why
fixed degrees answer this question, and review the conclusion before presenting.
The result cannot establish friendship, causality or exact convergence of the
finite swap chains. No Teams message or peer feedback was sent by the agent.

## Week 3 — Fixed-ranking removal comparison

The user specified the question, equal-removal comparison, frozen rankings,
random baseline, and a character-level link inspection. The agent read official
exercise 3.12 and the data documentation, matched the existing site design,
wrote and executed scripts/analyse_week3.py, and drafted the explanation.

Verification: official TSV downloads matched the committed files byte-for-byte.
All 303 nodes and 17 isolates were retained; the undirected graph has 1,434 edges.
Exact normalized betweenness and degree use the same graph, ranked before removal
with deterministic alphabetical tie-breaking. Each run starts from a fresh copy.
200 random permutations use seeds 20261123–20261322. Independent BFS checks both
attack curves at nine cuts. Bounds, monotonicity and input hashes are asserted.
Rockman’s complete original incident edge list and The Witness’s degree-one
attachment were inspected and saved; no fictional friendship interpretation was
inferred. The script was rerun in an isolated output directory and outputs compared.
The plot uses a pointwise random variability band, not a mean confidence interval.
The text acknowledges crossing curves and the limitations of fixed rankings,
undirected links, and a single editorial snapshot. These checks are AI-assisted;
they do not imply student review. No Teams post or peer feedback was sent.

## Week 4 — Repeated links and philosopher communities

The user specified a weighted/unweighted Louvain question, repeated seeds, NMI, an
overlap figure and a link-level case inspection. The agent read official exercise
4.13 and the data documentation, reused the earlier communities/weights theme,
and performed a new executed comparison. Previous course-reference numbers were
not substituted for computed measurements. The existing site styles/navigation
were reused; other weeks were preserved.

The frozen 2026-09-15 inputs are saved with their provenance headers. Every directed
weight is positive and integral; reciprocal counts are summed and checked against
the original directed lookup. The largest component is selected once and both
treatments use the same node order, node set and edge set (1,374 / 9,139). Forty
partitions use seeds 0–19, resolution 1, explicit weight=None or weight="weight".
All labels and parameters are preserved. NMI uses arithmetic normalization.
An independent contingency-table calculation checks the seed-0 NMI; overlap
row/column counts and full partition coverage are validated. A second isolated
execution matches results, CSVs and the deterministic SVG.

The figure uses seed 0 by convention, with communities ordered by size and labelled
by a high-degree anchor, not asserted historical school names. Labels are arbitrary;
maximum-overlap matching is used only to screen case candidates, not to compute NMI.
Among the 30 highest-degree reference mismatches, Erasmus has the largest repeated
edge and was selected descriptively. All 51 incident edges were inspected/saved,
including original directions, summed weights and pairwise co-membership frequencies.
Erasmus→More is 18 and More→Erasmus is 6; they group together in 5/20 unweighted
and 20/20 weighted runs. The article also reports Erasmus–Luther’s 19/20 weighted
co-membership rather than presenting the illustrative seed’s separation as stable.

The agent visually inspected the generated figure and checked local links, article
values and output consistency. These are AI-assisted checks, not human validation.
Repeated hyperlinks are explicitly distinguished from mentions, citations, agreement
and influence. NMI is not a percentage correct; reused pairwise comparisons are not
independent samples; modularity scores from different weighting objectives are not
ranked against each other. No random-graph null, causal edge ablation, ground-truth
school validation, student review or Teams submission is claimed.
