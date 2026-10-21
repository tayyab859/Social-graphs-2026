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
