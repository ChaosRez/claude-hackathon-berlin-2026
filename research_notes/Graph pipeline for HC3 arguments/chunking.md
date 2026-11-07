# Chunking short answers into graph nodes

Scope: how to cut HC3 `finance` / `wiki_csai` answers (~200 words) into nodes for argument graphs.
Researched 2026-11-07.
Repo metadata was pulled live with `gh api` on that date.
Items marked **(unverified)** come from memory or snippets and were not checked against a primary source.

## Which unit to use: sentences, clauses, EDUs, ADUs, or atomic propositions?

### Takeaway
Sentence nodes are the only choice that is cheap, hand-checkable, and decided by a deterministic tool.
Finer units (EDUs, propositions) roughly double node counts and make the count depend on the segmenter, not on the writer.
ADUs are the "right" unit for argument graphs, but boundary agreement is weak even among trained annotators.
Recommendation: one sentence = one node, plus three fixed rules for the edge cases (below), with clause splitting only as a sensitivity check.

### Cited Findings
- HC3 answer lengths are close in the two allowed subsets: finance human 202.07 vs ChatGPT 226.01 words (3,933 questions; 4,503 ChatGPT answers); wiki_csai human 229.34 vs ChatGPT 208.33 words (842 questions) — [Guo et al. 2023, HC3 paper](https://ar5iv.labs.arxiv.org/html/2301.07597)
- HC3 authors describe ChatGPT answers as organized: define the concept, go step by step, end with a summary, and use transitions like "Firstly…, Secondly…, Finally" and "In general" — [Guo et al. 2023](https://ar5iv.labs.arxiv.org/html/2301.07597)
- Human HC3 answers are more colloquial and succinct, with slang and abbreviations, and use more exclamation marks, question marks, ellipses, and brackets — [Guo et al. 2023](https://ar5iv.labs.arxiv.org/html/2301.07597)
- The HC3 paper does not discuss lists or markdown explicitly — [Guo et al. 2023](https://ar5iv.labs.arxiv.org/html/2301.07597)
- Propositions (Dense X Retrieval) are defined by three principles: each is a distinct piece of meaning and together they cover the text; each is minimal; each is self-contained, with coreferences resolved — [Chen et al., Dense X Retrieval](https://arxiv.org/html/2312.06648v3)
- In FactoidWiki, sentences average 21.0 words and propositions 11.2 words; one sentence yields 2.3 propositions on average — [Chen et al.](https://arxiv.org/html/2312.06648v3)
- The Propositionizer is Flan-T5-Large distilled from GPT-4 output on 42,857 passage→proposition pairs; dev F1 0.822; manual check of 50 passages found 1.3% unfaithful, 2.0% not minimal, 3.1% not stand-alone — [Chen et al.](https://arxiv.org/html/2312.06648v3)
- Propositions are rewritten text, not spans: they add resolved referents, so they do not map 1:1 to source characters — [Chen et al.](https://arxiv.org/html/2312.06648v3) (definition implies this; inference on span mapping is mine)
- ADU / argument unit segmentation: Ajjour et al. 2017 split argumentative text into argument and non-argument units; best in-domain F1 up to 88.54; cross-domain transfer "remains hard"; structural features generalize best — [Ajjour et al. 2017](https://aclanthology.org/W17-5115/)
- On persuasive essays, P/R/F1 and Krippendorff's α gave inconsistent agreement for the same text because unit boundaries are fuzzy — [Ghosh et al., via search snippet](https://rutgers.academia.edu/DebanjanGhosh) **(snippet only, unverified)**
- A 2025 essay study evaluated agreement at the sentence level "as an approximation" because rater segmentation differences made alignment hard; weighted kappa for claims was 0.17 — [Frontiers in Education 2025](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1569529/pdf) **(snippet only, unverified)**
- EDUs (RST) are roughly clause-sized units; RST-DT and GUM define them by guidelines that split most finite clauses and some adjuncts **(unverified; from background knowledge of RST-DT/GUM guidelines)**
- FActScore splits generations into "atomic facts" with an LLM (InstructGPT in the original paper) **(unverified, not fetched)**; the repo is MIT-licensed, last push 2025-04-13 — [shmsw25/FActScore](https://github.com/shmsw25/FActScore)

### Inferences
- Node count scales with unit granularity: ~1 node per 21 words for sentences, ~1 per 11 words for propositions (Wikipedia numbers). For a 200-word answer that is ~10 vs ~20 nodes. Depth and branching metrics will shift with this.
- The bias risk is asymmetric. Human Reddit/FiQA answers have run-on sentences and odd punctuation, so sentence splitting gives them *fewer, longer* nodes. ChatGPT text has clean, uniform sentences and list items, so it gets *more, shorter* nodes. A size difference could then be a punctuation artifact, not an argument difference.
- Proposition or EDU splitting reduces that artifact (it looks inside sentences) but adds a new one: an LLM propositionizer may read clean LLM text more easily, which is exactly the extractor bias CLAUDE.md warns about.
- ADU segmentation is the theoretically correct unit but the hand-labels in `annotations/` would be hard to agree on in a hackathon; sentence-level agreement is the fallback even researchers use.
- Recommendation for this project (sentence + fixed rules):
  1. **Base unit = sentence**, split by one pinned tool (see next section).
  2. **Two ideas in one sentence** ("X is cheap, but Y is faster"): keep as one node. Record a per-node flag `multi_claim: true` instead of splitting. This keeps nodes deterministic and lets you run a sensitivity check later (split flagged nodes at the connective, recompute metrics, see if conclusions change).
  3. **Very short sentences** ("Yes.", "Good question.", "Hope this helps!"): keep as nodes but give them a role like `non-argumentative` / `filler`; exclude them from depth/size metrics, and report how many were excluded per side. Don't merge them into neighbours; merging is a judgment call that hurts reproducibility.
  4. **Bullet/numbered list items**: each item = one node, even without a final period. The lead-in line ("There are several reasons:") = its own node. Pre-split on newlines before running the sentence splitter, so list items never merge.
  5. Report node count and mean words per node, human vs ChatGPT, next to every structural result, so readers can see the granularity gap.

### Gaps
- No source found that measures sentence-length distributions for HC3 finance / wiki_csai specifically. Compute it ourselves with a deterministic script.
- I did not get the Stab & Gurevych (2017) α_U figure for component boundaries (PDF could not be parsed); Lawrence & Reed (2019) and Stede & Schneider (2018) were not read. Their claims are not included.
- No direct study found on how unit choice biases human-vs-LLM graph comparisons. This seems open.

## Which tools exist, and how robust are they on informal text?

### Takeaway
For sentences, use **wtpsplit SaT (`sat-3l-sm` or `sat-12l-sm`)**: MIT, very active, robust to missing punctuation, and deterministic for a pinned model version.
spaCy or NLTK punkt are fine fallbacks on clean text but rely on punctuation.
EDU segmenters work on news/GUM-style text (91–98 F1) but are heavier, and the best English one (isanlp_rst) is the only one still maintained.

### Cited Findings
Repo status (live `gh api`, 2026-11-07):

| Tool | Unit | License | Stars | Last push | Notes |
|---|---|---|---|---|---|
| [segment-any-text/wtpsplit](https://github.com/segment-any-text/wtpsplit) | sentence (SaT) | MIT | 1,379 | 2026-11-05 | release 2.2.2 on 2026-09-25 |
| [explosion/spaCy](https://github.com/explosion/spaCy) | sentence | MIT | 34,034 | 2026-10-27 | |
| [nltk/nltk](https://github.com/nltk/nltk) | sentence (punkt) | Apache-2.0 | 14,767 | 2026-11-05 | |
| [nipunsadvilkar/pySBD](https://github.com/nipunsadvilkar/pySBD) | sentence (rules) | MIT | 943 | 2024-08-20 | stale |
| [tchewik/isanlp_rst](https://github.com/tchewik/isanlp_rst) | EDU + RST tree | MIT | 65 | 2026-09-15 | Python 3.12, Docker |
| [seq-to-mind/DMRST_Parser](https://github.com/seq-to-mind/DMRST_Parser) | EDU + RST tree | **none** | 45 | 2023-01-26 | no license → not reusable |
| [PKU-TANGENT/NeuralEDUSeg](https://github.com/PKU-TANGENT/NeuralEDUSeg) | EDU | Apache-2.0 | 103 | 2023-03-24 | stale |
| [disrpt/sharedtask2025](https://github.com/disrpt/sharedtask2025) | data + eval | none listed | 8 | 2026-03-18 | |
| [chentong0/factoid-wiki](https://github.com/chentong0/factoid-wiki) | propositions | Apache-2.0 | 172 | 2024-01-08 | Propositionizer |
| [shmsw25/FActScore](https://github.com/shmsw25/FActScore) | atomic facts | MIT | 460 | 2025-04-13 | needs LLM API |

Sentence splitters (English macro F1, clean text, from the SaT paper):
- NLTK 94.1, spaCy (monolingual) 94.5, spaCy (dependency) 92.9, **pySBD 69.6**, WtP 93.9, SaT 93.6, **SaT+SM 96.5**, Llama 3 8B 95.2 — [Frohmann et al., SaT, EMNLP 2024](https://arxiv.org/html/2406.16678v2)
- Rule-based tools (NLTK, spaCy, pySBD) were *not* tested on punctuation-stripped text — [SaT paper](https://arxiv.org/html/2406.16678v2)
- Tweets (share of perfectly segmented sequences, 12-layer): SaT 80.5/75.5, SaT+SM 78.0/72.9, SaT+LoRA 87.2/89.1, Llama 3 8B 73.4/76.0 — [SaT paper](https://arxiv.org/html/2406.16678v2)
- TED talks with no punctuation or casing: SaT+SM 92.5% perfect, Llama 3 8B 94.8% — [SaT paper](https://arxiv.org/html/2406.16678v2)
- LLM splitters alter the input text (Llama 3 8B changed ~1.5% of characters on lyrics) — so an LLM is a poor splitter if node text must map back to the source — [SaT paper](https://arxiv.org/html/2406.16678v2)
- SaT on very short inputs needs lookahead context; 3-layer SaT without lookahead got 4.4% perfect on sentence pairs vs 56.9% with 48-token lookahead — [SaT paper](https://arxiv.org/html/2406.16678v2)
- 3-layer SaT segments ~1,000 sentences in ~0.5 s on a GTX 2080 Ti — [SaT paper](https://arxiv.org/html/2406.16678v2)
- README model table: `sat-3l-sm` 96.5, `sat-6l-sm` 96.9, `sat-12l-lora` 97.3 (first score column; matches the paper's English numbers); authors recommend `-sm` models for general use; `SaT("sat-3l-sm").split(text)` is the API; ONNX inference supported — [wtpsplit README](https://github.com/segment-any-text/wtpsplit)

EDU segmenters:
- DISRPT 2025: 39 datasets, 16 languages; best EDU segmentation mean F1 91.57 (treebanked track, DiscUT/MELODI) and 87.38 (plain-text track, SeCoRel/AU-KBC) — [DISRPT 2025 overview](https://aclanthology.org/2025.disrpt-1.1), [AU-KBC page](https://au-kbc.org/disrpt.html). MELODI's own paper reports 90.19/86.89; the gap is unexplained — [search summary](https://aclanthology.org/volumes/2025.disrpt-1/)
- isanlp_rst end-to-end segmentation F1: 97.8 on RST-DT, 95.5 on GUM; full-parse scores are much lower (53.9 RST-DT, 48.7 GUM) — [isanlp_rst README](https://github.com/tchewik/isanlp_rst)
- Cross-corpus EDU segmentation (DisCoDisCo, DISRPT 2021 winner) on GUM v8: ~89.6–92.6; degradation described as modest — [Liu & Zeldes 2023, arXiv 2302.06488](https://arxiv.org/pdf/2302.06488)
- GUM contains a Reddit genre; in one GUM-based study Reddit caused nearly 20% of parsing errors (unusual vocabulary and constructions) — [SCiL paper](https://openpublishing.library.umass.edu/scil/article/1054/galley/1004/download) **(snippet only, the parse type is unclear)**

### Inferences
- `sat-12l-sm` (or `sat-3l-sm` if speed matters) is the best fit: it is trained to work without punctuation, which matters for Reddit-style human answers, and it is not an LLM, so it does not favour LLM text the way an LLM extractor might.
- Pin the wtpsplit version and model name in the repo; record the splitter output (sentence spans) as data so the hand check and the graph extractor both see the same nodes.
- Per-text SaT should get the whole answer at once (not sentence pairs), because it needs context on both sides.
- EDU segmentation via isanlp_rst is feasible as a sensitivity check but adds Docker and model weight overhead; 95% segmentation F1 on GUM still means about one boundary error per 20 boundaries, i.e. ~1 per answer.
- No ready-made, maintained English ADU segmenter turned up in this search.

### Gaps
- No published score for SaT, spaCy or punkt on Reddit/FiQA-style English specifically.
- No per-genre (Reddit) EDU segmentation numbers found for DISRPT 2025.
- I did not check pip install success or compute needs for isanlp_rst or SaT on the team machines.

## What are the known pitfalls?

### Takeaway
The big risks are list/markdown handling, run-on human sentences, filler sentences, and error propagation: a wrong boundary changes which nodes exist, so relation labels downstream cannot be right.

### Cited Findings
- Segmentation differences between raters make agreement hard to even compute; researchers fall back to sentence-level agreement — [Frontiers in Education 2025](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1569529/pdf) **(snippet only)**
- Argument unit segmentation transfers poorly across domains — [Ajjour et al. 2017](https://aclanthology.org/W17-5115/)
- RST parsing scores drop steeply after segmentation: isanlp_rst gets 95.5 segmentation but 48.7 full-parse F1 on GUM — [isanlp_rst README](https://github.com/tchewik/isanlp_rst)
- Human HC3 answers use ellipses, brackets, and many question/exclamation marks — the same marks that confuse punctuation-based splitters — [Guo et al. 2023](https://ar5iv.labs.arxiv.org/html/2301.07597)

### Inferences
- **Lists:** sentence splitters often merge "1. Foo 2. Bar" or split after "1." Pre-split on newlines and list markers with a regex, then run the splitter inside each line.
- **Abbreviations and numbers** in finance text ("e.g.", "$1.5", "U.S.", "401(k)") are classic false boundaries; spot-check them.
- **Error propagation:** the extractor labels edges *between* nodes; if one human run-on sentence holds a claim and its premise, the support edge disappears inside the node. That lowers human edge counts and depth for a reason unrelated to argument style. The `multi_claim` flag lets you measure how often this happens per side.
- Hand check for segmentation: before any graph work, have two teammates check the splitter on ~10 human and ~10 ChatGPT answers and count boundary errors per side. Report the two error rates separately (CLAUDE.md requires extractor accuracy per side; the splitter is part of the extractor).

### Gaps
- No quantitative study found on how segmentation errors propagate into argument relation F1 in short web texts.

## Does unit choice bias human vs LLM comparisons?

### Takeaway
No direct study was found.
The indirect evidence (HC3 style differences, propositions ≈ 2.3 per sentence) suggests sentence nodes will under-count human ideas relative to ChatGPT ideas, so always report granularity stats and a clause-split sensitivity check.

### Cited Findings
- ChatGPT answers: formal, structured, transition-heavy; human answers: colloquial, succinct, emotive punctuation — [Guo et al. 2023](https://ar5iv.labs.arxiv.org/html/2301.07597)
- Sentence-to-proposition ratio is 2.3 on Wikipedia, so sentence count is an imprecise proxy for idea count — [Chen et al.](https://arxiv.org/html/2312.06648v3)

### Inferences
- If human sentences are longer on average, sentence nodes give humans fewer but denser nodes; graph-size differences would partly reflect sentence length.
- Two cheap controls: (a) report words per node per side; (b) re-run metrics with flagged `multi_claim` nodes split, and with filler nodes kept vs removed. If conclusions hold under all variants, the unit choice is not driving them.
- An LLM-based proposition splitter would equalize granularity but may decompose clean LLM text better than messy human text; treat it as a comparison, not the main pipeline.

### Gaps
- No measured sentence-length or sentences-per-answer stats for HC3 finance / wiki_csai were found; compute them with a script before deciding.
- No literature found comparing argument graph size of human vs LLM text under different unit choices.
