# Build argument graphs, not knowledge graphs

**Summary.**
NVIDIA auto-ontology is the wrong tool for this project, and so is every entity-centred ontology or knowledge-graph (KG) tool.
Those tools model *what an answer is about*.
The team's question is *how an answer argues*.
What fits instead is a small, hand-checkable pipeline.
It has five parts.
First, a cleaned and length-matched HC3 sample.
Second, one sentence per node, split by a pinned non-LLM splitter (wtpsplit SaT).
Third, a tiny argument schema in the style of the Peldszus–Stede microtexts: 2–3 node roles and 5–6 edge types, extracted by Claude into a Pydantic schema and checked by a deterministic validator.
Fourth, size-normalised graph measures, typed motifs and tree edit distance, tested per question with paired statistics.
Fifth, a question-grouped "structure-only" authorship classifier that is always shown next to a size-only baseline.

Four blocking issues must be fixed before any result is trustworthy.
**HC3 has exactly 1 human answer per question** in both `finance` and `wiki_csai`, so a same-question human-vs-human baseline is impossible.
**About 90% of finance ChatGPT answers have glued sentences** such as `contacts.Consider`, so a naive splitter will under-count ChatGPT nodes.
**wiki_csai is purely definitional**: all 842 prompts read "Please explain what is X", so it is a low-argument control, not a second argument topic.
**Only about 7% of finance questions are advice or opinion questions**, so most finance answers are explanations too.
A fifth risk runs through every step: the extractor is itself an LLM, and it may parse tidy ChatGPT prose more easily than messy forum posts.

## Why auto-ontology, OntoCast, GraphRAG and cognee answer a different question

An earlier review of auto-ontology's code in this conversation found that it turns a SQL database schema into a business-terms semantic layer for text-to-SQL.
It has no free-text ingestion, no class hierarchy and no reasoner.
It cannot read an HC3 answer at all.

The wider family of ontology and KG builders can read free text, but they still extract the wrong thing.
They pull out entities (a fund, a tax rule, a company) and the facts that link them.
That graph describes the *topic* of an answer.
Two answers can mention the same entities and argue in opposite ways.
Two answers can argue in the same way about entirely different entities.
The project's own rule says comparisons must use node roles and edge types only, never the sentence text, and entity names are sentence text.

The notes checked a few of these tools directly.
Google LangExtract offers character-offset grounding and few-shot examples, but it has no formal relation or graph model, and relationships appear only as an extraction class ([LangExtract README](https://github.com/google/langextract)).
Neo4j's LLM Graph Builder builds an entity KG from a schema, which is the wrong layer for argument structure ([neo4j-labs/llm-graph-builder](https://github.com/neo4j-labs/llm-graph-builder)).
kg-gen also builds entity KGs, and the GitHub API reported no licence for it, which matters because derived data must stay CC BY-SA 4.0 ([stair-lab/kg-gen](https://github.com/stair-lab/kg-gen)).
OntoCast, Microsoft GraphRAG and cognee were not researched in the notes.
They belong to the same entity-and-fact category as far as the team knows (unverified).
GraphRAG and cognee aim at retrieval for question answering, not at describing how a text reasons (unverified).

An entity layer can still answer one side question: "Do humans cite more concrete finance entities than ChatGPT?"
That would echo the finding that human arguments are more topic-specific ([Argument Collapse, arXiv 2606.01736](https://arxiv.org/abs/2606.01736)).
Keep it out of the main comparison.

## Step 1: HC3 needs cleaning, length matching and a new baseline plan

**What the data really looks like.**
A deterministic script on the raw HC3 files gives these numbers ([HC3 on Hugging Face](https://huggingface.co/datasets/Hello-SimpleAI/HC3)).
Finance has 3,933 questions, each with exactly 1 human answer.
3,363 finance questions have 1 ChatGPT answer and 570 have 2.
wiki_csai has 842 questions with 1 human and 1 ChatGPT answer each.
The ChatGPT answers come from the December 2022 ChatGPT (GPT-3.5) ([HC3 GitHub README](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection)).

| | Finance human | Finance ChatGPT | wiki_csai human | wiki_csai ChatGPT |
|---|---|---|---|---|
| Mean words | 175.6 | 203.8 | 195.5 | 185.3 |
| Median words | 129 | 205 | 166 | 187.5 |
| 10th percentile words | 40 | 124 | 61 | 119 |
| Answers with glued sentences | 31 of 3,933 | 4,069 of 4,503 (90.4%) | – | 20 |

These script means differ from the HC3 paper's means (finance 202 vs 226 words; wiki_csai 229 vs 208) ([HC3 paper](https://arxiv.org/html/2301.07597)).
The notes do not explain the gap.
More important, the averages hide a large per-question spread.
In finance the median ChatGPT/human length ratio is **1.52**, and only **33%** of questions (1,286) have a ratio between 0.67 and 1.5.
In wiki_csai the median ratio is 1.12, and 40% (338) fall in that band.
So "finance and wiki_csai have similar lengths" is true on average but false for most single questions.

**Quality problems to fix.**
Glued sentences appear in 90% of finance ChatGPT answers, probably because line breaks were removed (the cause is inferred, not documented).
Insert a space at `([a-z0-9][.!?])([A-Z])` before splitting, then check by hand, because "U.S." and tickers can break.
2,286 finance human answers contain double spaces, likely collapsed line breaks.
262 human answers contain links.
About 55–68 ChatGPT finance answers are refusals ("I'm sorry, but …").
Flag them and keep them in the denominator.
wiki_csai has 62 groups of identical human answers (71 extra copies), because different titles map to the same Wikipedia lead.
Treat each group as one item.

Finance human answers are informal forum posts.
They often reply to other answers ("… Dynas' answer above") or tell personal stories.
That is a different discourse situation from ChatGPT answering the question directly.
An "attacks another answer" edge has no ChatGPT counterpart.

ChatGPT giveaway phrases are frequent.
"It's important to" appears in 1,573 ChatGPT answers versus 15 human ones, and "Overall" in 778 versus 76.
Those phrases will shape the graph too, for example as trailing `restates` nodes.

**Recommendation for the 200 questions.**
Take 100 finance questions, stratified as about 50 advice/opinion questions and 50 explanatory ones.
The advice pool holds only about 277 questions (a regex estimate, not hand labels), so 50 is feasible.
Take 100 wiki_csai questions and label them openly as the **definitional control**.
Restrict both samples to a length ratio of 0.67–1.5 and set a minimum human length of about 60 words, because very short human answers give tiny graphs.
In finance, use the first ChatGPT answer as the main LLM answer.
The 570 questions with a second ChatGPT answer give a free ChatGPT-vs-ChatGPT baseline.

**The baseline problem.**
The project rule requires every human-vs-LLM result to sit next to a human-vs-human baseline.
HC3 cannot give one on the same question.
The applications notes assumed that some questions have several human answers; the data script shows they do not.
Three workable substitutes exist.
A cross-question baseline compares human answers to different questions, d(human_q, human_q′), against d(LLM_q, LLM_q′) and d(human_q, LLM_q′).
That tests "LLMs are more alike than humans" without needing two humans per question.
An annotation baseline compares the two hand-labelled graphs of the same text, which gives the noise floor of the labels themselves.
A second human source with several human replies per prompt would give a true same-question baseline.

**Fresh LLM answers.**
The README plans new answers from a current model such as Claude.
Ask for a target length.
Treat any difference against 2022 ChatGPT as a "generation shift" (era, model and prompt all changed), not a pure model difference.

**Second argument topic, for the team to decide.**
If the team wants a real second argument domain, the best paired source is r/ChangeMyView.
Options include the `cmv` domain of MAGE/DeepfakeTextDetect, which Threads of Subtlety also used ([arXiv 2402.10586](https://arxiv.org/html/2402.10586v2)), and the human-versus-LLM counter-arguments of Dönmez et al. ([ACL Anthology](https://aclanthology.org/2025.emnlp-main.1755/)).
Licences, pair counts and per-item pairing are not verified for either.
The current CLAUDE.md data rule allows only finance or wiki_csai, so this is a rule change.

**Licence caveat.**
The HC3 authors list the finance human answers (from FiQA) with licence "Unknown" ([HC3 GitHub README](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection)).
The CC BY-SA assumption holds for wiki_csai (Wikipedia) but is not settled for finance.

## Step 2: One sentence per node, split by a non-LLM tool

**Recommendation.**
Keep the README's rule: one sentence is one node.
It is cheap, easy to check by hand, and set by a deterministic tool.
Finer units shift the numbers.
In the Dense X Retrieval data, one sentence yields 2.3 propositions on average, so a 200-word answer gives about 10 sentence nodes but about 20 proposition nodes ([Chen et al.](https://arxiv.org/html/2312.06648v3)).
Argument units (ADUs) are the theoretically correct unit, but their boundaries are hard to agree on, and cross-domain segmentation "remains hard" ([Ajjour et al. 2017](https://aclanthology.org/W17-5115/)).

**Tool.**
Use wtpsplit SaT, model `sat-3l-sm` or `sat-12l-sm`, pinned by version ([wtpsplit](https://github.com/segment-any-text/wtpsplit)).
It is MIT-licensed and maintained (release 2.2.2 on 2026-09-25).
On clean English, SaT+SM scores 96.5 F1, against 94.1 for NLTK and 94.5 for spaCy ([SaT paper](https://arxiv.org/html/2406.16678v2)).
It is trained to work without punctuation, which suits Reddit-style human posts.
On TED talks with no punctuation or casing it segmented 92.5% of sequences perfectly ([SaT paper](https://arxiv.org/html/2406.16678v2)).
Feed it the whole answer at once, because it needs context on both sides: 3-layer SaT got 4.4% perfect on bare sentence pairs but 56.9% with 48 tokens of lookahead ([SaT paper](https://arxiv.org/html/2406.16678v2)).
Do not use an LLM as the splitter.
Llama 3 8B changed about 1.5% of characters on lyrics, so nodes would no longer map back to the source text ([SaT paper](https://arxiv.org/html/2406.16678v2)).
An LLM splitter could also favour LLM text, the same bias the project already worries about in the extractor.

**Fixed rules for edge cases** (suggestions for GUIDE.md, see the last section).
A sentence with two ideas stays one node but gets a `multi_claim: true` flag.
Very short filler sentences ("Yes.", "Hope this helps!") stay as nodes with a `filler` role and are excluded from depth and size metrics, with the excluded count reported per side.
Each list item is one node, and the lead-in line is its own node; pre-split on newlines and list markers before running SaT.
Run the glued-sentence fix before everything else.

**Caveats.**
The bias is asymmetric.
Human answers have run-on sentences and odd punctuation, so they get fewer, longer nodes.
ChatGPT text has clean, even sentences, so it gets more, shorter nodes.
A size difference may then be a punctuation artefact.
If one human run-on sentence holds both a claim and its reason, the support edge disappears inside the node, which lowers human depth for a reason unrelated to argument style.
Report node count and words per node for each side next to every structural result.
Run two sensitivity checks: split flagged `multi_claim` nodes at the connective, and keep versus drop filler nodes.
Before any graph work, have two teammates check the splitter on about 10 human and 10 ChatGPT answers and report boundary errors per side.
No published SaT score exists for Reddit or FiQA-style English, so this hand check is the only evidence the team will have.

## Step 3: A microtext-style schema, extracted by Claude and checked by code

**Which paradigm.**
Three families exist.
Argument mining (claim and premise, support and attack) captures how an argument is built.
Discourse parsing (RST, PDTB) labels every sentence, including non-argumentative links like elaboration.
Entity KGs capture what the text is about.
The team needs the first two and not the third.
The README's draft relations already mix them: `supports` and `attacks` come from argument mining, while `explains`, `example` and `restates` come from discourse.

The closest existing scheme is the Peldszus–Stede arg-microtexts corpus: 112 short texts with 576 argument units, labelled for central claim, role, function and attachment ([arXiv 2411.05639](https://arxiv.org/pdf/2411.05639v1)).
Its classic parser turns each argument into a dependency tree whose arcs carry labels like "support" or "attack" ([arXiv 2401.11218](https://arxiv.org/pdf/2401.11218)).
That matches "one sentence, one node, one outgoing edge".
In the microtexts, support makes up 55.2% of relations, rebutting attack 21.6%, undercutting attack 12.8% and support-by-example only 1.8% ([DFKI-SLT/argmicro](https://huggingface.co/datasets/DFKI-SLT/argmicro/blob/refs%2Fpr%2F1/README.md)).
Those are argumentative texts by design; in HC3's explanatory answers attacks will be rarer still.

**Schema recommendation.**
Use 2–3 node roles: main claim, other, and filler.
Avoid a separate "sub-claim" role.
In the Stab & Gurevych essays, the middle "claim" role had the weakest agreement (αU .524, Fleiss κ .635), against αU .810 for major claims and .824 for premises ([arXiv 1604.07370](https://arxiv.org/pdf/1604.07370)).
Use the README's edge types: `supports`, `attacks`, `explains`, `example`, `restates`, and `none`.
Merge rebut and undercut into one `attacks` label.
Write decision rules for the confusable pairs: `explains` versus `supports`, and `restates` versus `supports`.
Pilot with two annotators on about 10 texts and aim for κ ≥ 0.6 on edge types before treating hand labels as gold.
If agreement is lower, merge labels, for example `explains` with `example`.
Because the nodes are fixed sentences, plain Cohen's κ or nominal Krippendorff's α applies; there is no unit-boundary disagreement to handle.

**Tools.**
No argument-mining toolkit is a drop-in replacement for prompted extraction.
The practical stack is a Pydantic schema, Claude structured output or tool use (or `instructor`, MIT-licensed and active), and a deterministic validator ([instructor](https://github.com/567-labs/instructor)).
`instructor`'s Anthropic support was read from its README only (unverified).
The validator checks that every sentence has exactly one node, that only known types appear, that there are no self-loops, that there is exactly one main claim, and that the graph is a tree or DAG.
Count every failure and report it per side.
Put one fully labelled human HC3 answer and one ChatGPT answer in the prompt as few-shot examples.
Few-shot task context was the most effective prompt enrichment for LLM relation classification, ahead of KG, sentiment or chain-of-thought additions ([C4AI repo](https://github.com/C4AI/llm_component_relation_classification)).
For sanity checks, load `DFKI-SLT/argmicro` with `python -I` in an isolated folder, since its loader runs remote code.
As an optional independent non-LLM baseline, `isanlp_rst` is the only maintained English RST parser in the notes; it segments at 95.5 F1 on GUM but parses full trees at only 48.7 ([isanlp_rst](https://github.com/tchewik/isanlp_rst)).

**How good can the extractor be?**
Fixed sentence nodes make the task look like relation classification, where LLMs do fairly well, rather than end-to-end mining, where they do poorly.
With few-shot priming, Llama 2 70B and Mixtral 8x7B beat a fine-tuned RoBERTa on support/attack classification across ten datasets ([Gorur, Rago & Toni, COLING 2025](https://aclanthology.org/2025.coling-main.569.pdf)).
GPT-4 zero-shot reached 86.9% macro-F1 on finance argument relations (FinArg) ([FinNLP 2024](https://aclanthology.org/2024.finnlp-1.12.pdf)); that number comes from a search snippet.
End-to-end is much weaker: one 2026 LLM pipeline reached link F1 of 20.82 on AbstRCT, against 39.74 for a fine-tuned model (Pirozelli et al., [arXiv 2605.13793](https://arxiv.org/html/2605.13793v2), Table 2; corrected 2026-11-07, earlier cited as arXiv 2603.03095 from a snippet).
On discourse relations, prompted Claude Opus 4.0 "lagged significantly" behind fine-tuned models in DISRPT 2025 ([DISRPT 2025](https://aclanthology.org/2025.disrpt-1/)).
Expect attachment (which earlier sentence a node links to) to be the weak step, not the label.

**Extractor bias is a live risk.**
LLMs classify argument schemes better on generated arguments than on human ones ([Findings ACL 2025](https://aclanthology.org/2025.findings-acl.702.pdf)); this was read from a search summary only.
No study measures directly whether an LLM extractor parses LLM-written text more accurately.
The team has to measure it.
Report, separately for human and LLM texts: main-claim accuracy, role κ, unlabelled edge F1, labelled edge F1, a per-type confusion matrix and the validation failure count.
Put each number next to the human-vs-human annotator agreement on the same texts, which is the ceiling.
Run the extractor at least 3 times per text and report run-to-run agreement, because prompt wording alone moves argument-mining results noticeably ([Frontiers in AI 2023](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2023.1278796/pdf)).
Bootstrap confidence intervals over texts, not edges, because edges in one text depend on each other.

## Step 4: Normalise by size, test per question, and expect degenerate metrics

**Measures.**
Use a small fixed set: depth, width, branching factor, leaf ratio, chain-ness, relative main-claim position, relation-type shares, share of backward links and normalised link distance.
Almost every raw count grows with node count.
Report each measure divided by node count (or by n−1 edges), and check that the group effect survives a model with log(n) as a covariate and a subset where the two answers differ by at most 2 nodes.
Threads of Subtlety did not pair or length-match its texts and leaned on size-robust measures instead, and its detection improved with longer texts ([arXiv 2402.10586](https://arxiv.org/html/2402.10586v2)).
Use networkx and pin its version; 3.7 is current and needs Python ≥3.12 ([PyPI](https://pypi.org/pypi/networkx/json)).

**Degeneracy.**
If the extractor must attach each sentence to exactly one earlier sentence, the graph is a tree by construction.
Then the edge count equals n−1, tree-ness is always 1, and isolates are always 0.
Only shape and relation-type shares carry signal.
Before testing, print for each measure the share of graphs at its minimum or maximum value.
Drop measures that sit at one value more than 90% of the time, and list what was dropped.
Measure how often each side's nodes simply attach to the previous sentence; that "chain" default is a likely extractor shortcut.

**Motifs.**
With at most 20 nodes, count typed motifs exactly with a few lines of Python.
Count typed 2-paths (for example example → reason → claim), typed sibling pairs, and the multiset of edge types into the main claim.
For larger patterns use networkx `DiGraphMatcher` with role and type matching, or key all 3-node subgraphs by `weisfeiler_lehman_graph_hash` ([networkx docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.graph_hashing.weisfeiler_lehman_graph_hash.html)).
WL hashes for directed graphs changed in networkx 3.5, so never compare hashes across versions.
Report motif rates per edge, not raw counts.
Classic rewiring null models break the tree rule on such small graphs.
A type-shuffle null keeps the topology and permutes edge labels within a graph instead.
Keep only motifs present in at least about 10% of graphs, and fix that list in advance.

**Whole-graph distance.**
For trees, use tree edit distance with APTED or zss, rooted at the main claim, with each node labelled `role|type_to_parent` and children ordered by sentence position ([apted](https://pypi.org/project/apted/)).
Normalise by the total node count of both trees.
Exact graph edit distance is slow: in one local test it hit a 20-second timeout at 12 nodes and above (networkx 3.2.1, one run per size, not a benchmark).
If graphs are DAGs, use it with a timeout, log every timeout per group, and keep those pairs.
For a distribution-level view, use a bag of networkx WL subgraph hashes per graph with cosine similarity.
This avoids GraKeL, which needs Python <3.13 while networkx 3.7 needs ≥3.12 ([PyPI grakel](https://pypi.org/pypi/grakel/json)).
Avoid Graph2Vec in karateclub: it pins `scipy<1.13` and is unmaintained ([karateclub setup.py](https://raw.githubusercontent.com/benedekrozemberczki/karateclub/master/setup.py)).

**Statistics.**
The question is the unit of analysis.
For each measure, take the per-question difference (LLM minus human) and use a Wilcoxon signed-rank test with `zero_method='zsplit'` and a permutation method, or a sign-flip permutation test.
SciPy's default silently drops zero differences, which will be common with discrete measures ([SciPy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html)).
Report the median paired difference with a bootstrap CI over questions.
Group tests into families (descriptive measures, relation shares, motifs, distances) and apply Benjamini–Hochberg within each ([SciPy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html)).
Name one or two primary outcomes in advance.
With about 100 pairs per topic, only medium-small paired effects are detectable (d_z ≈ 0.28 at 80% power, a rule of thumb, unverified), so report CIs instead of "no difference".

For the human-vs-human baseline, use the cross-question design from Step 1.
If the team uses MMD with a WL kernel as a global test, fix the kernel settings before looking at results and report one alternative setting.
MMD rankings of graph sets can flip with the kernel and its parameters ([O'Bray et al., arXiv 2106.01098](https://arxiv.org/abs/2106.01098)).

**A noise trap.**
Extractor noise usually inflates distances.
If the extractor is less accurate on human text, human-human distances grow, which can fake an "LLMs are more uniform" result.
Run the same distance test on the hand-labelled gold graphs as a check.

## Step 5: Predict authorship from structure, but beat a size-only baseline

**Realistic accuracy.**
Structure alone is a weak detector on HC3.
The closest prior work parsed HC3 into RST discourse motifs and reached F1 0.55 with a Random Forest on motifs, 0.67 with a graph attention network and 0.73 with both, against 0.97 for a Longformer text model ([Threads of Subtlety, arXiv 2402.10586](https://arxiv.org/html/2402.10586v2)).
Text classifiers reach F1 99.8 on HC3 ([HC3 paper](https://arxiv.org/html/2301.07597)).
Even after ±20% word-count matching, a 22-feature classical set still reached AUROC 0.888–0.977 in-distribution, dropping to 0.63–0.78 across domains ([arXiv 2603.17522](https://arxiv.org/html/2603.17522v1)).
Expect roughly 0.55–0.75 accuracy from about 10 graph features.
Treat anything near 0.9 as a likely leak from length, sentence count or extractor artefacts.

**Protocol.**
Group by question so that both answers to a question are always in the same fold; use 5-fold `StratifiedGroupKFold`, repeated with several seeds.
Optionally freeze a 20% question-level hold-out and touch it once.
Run a paired task too: given the two graphs for one question, which is the LLM?
Chance is 50%, and length and topic are controlled inside the pair.
Use a ladder of feature sets with the same simple classifier.

| Set | Features | Role |
|---|---|---|
| B0 | majority class | chance |
| B1 | node count only | size baseline |
| B2 | word count only | length baseline (text allowed for baselines only) |
| B3 | counts of each edge type | bag of relations |
| M1 | about 10 size-normalised structural features | main model |
| M2 | M1 + node count | does structure add over size? |
| T | TF-IDF + logistic regression on text | text ceiling |

The key claims are M1 against B1 and M2 against B1, not M1 against chance.
Also train on finance and test on wiki_csai, and the reverse.
ChatGPT is longer in finance on average but shorter in wiki_csai, so a size-driven model should collapse across domains.
The applications notes proposed a "human answer 1 vs human answer 2" classifier as a control; HC3 cannot support it, so use the cross-question distance baseline instead.
Use a permutation test that shuffles labels within question pairs.

**How big the uncertainty is.**
A deterministic script gave Wilson 95% intervals for small samples.
On 80 held-out texts, 0.75 accuracy has a CI of about 0.65–0.83, and 0.60 has about 0.49–0.70, which is not distinguishable from chance.
Beating chance at p < 0.05 needs at least 0.60 on 80 texts or 0.5425 on 400.
Paired answers share a question, so pooled cross-validation intervals are optimistic.

**Other applications.**
The cheapest high-value add-on is a structural homogenisation test: are LLM graphs more alike than human graphs?
Prior work found strong collapse in *content*: 65.3% of human main arguments were unique within a debate against 3.4% for LLMs ([Argument Collapse, arXiv 2606.01736](https://arxiv.org/abs/2606.01736)).
A 2026 essay study found AI essays reached structural complexity comparable to human essays but much lower claim rarity ([arXiv 2602.01560](https://arxiv.org/html/2602.01560v2)); the notes link a similar finding to arXiv 2603.21228 as well, so the attribution is unverified.
So structure may not collapse even if content does, and either outcome is interesting.
A second add-on compares human, 2022 ChatGPT and fresh Claude answers three ways.
A side-by-side graph explorer makes the best demo, but it must not be the only result.

**Leakage checklist.**
The extractor sees the text and may impose a cleaner template on ChatGPT style.
Re-run after stripping giveaway phrases ("It's important to", "Overall", "As an AI") and check whether results survive.
Count refusal sentences per side and re-run without them.
Fix the feature list in `JOURNAL.md` before running.
Count validation failures per class; an unequal failure rate is itself a leak.

## Prior work: discourse, content and quality differ, but typed argument graphs are open

Prior work points to three structural differences.
LLM texts have less varied discourse structure: human texts show more structural variability in RST motifs ([Threads of Subtlety](https://arxiv.org/html/2402.10586v2)).
LLM arguments converge on few main arguments and follow a fixed arc of direct claim then proposals ([Argument Collapse](https://arxiv.org/abs/2606.01736)).
LLM arguments are "textbook": ChatGPT essays are highly structured, with identical openings of their concluding sections ([Herbold et al. 2023](https://www.nature.com/articles/s41598-023-45644-9)), and LLM counter-arguments on r/ChangeMyView are more cogent and respectful, with lower lexical diversity ([Dönmez et al., EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1755/)).
The HC3 authors themselves describe ChatGPT answers as defining the core concept, explaining step by step and ending with a summary ([HC3 paper](https://arxiv.org/html/2301.07597)).

These findings give testable hypotheses.
LLM graphs should vary less in shape across questions.
They should end more often with a `restates` node pointing back to the main claim.
They should place the main claim first more often.
They should have more `explains` edges and fewer `attacks` edges outside formulaic "However," patterns.
Write these into `JOURNAL.md` before running.

The notes found no paper that builds typed argument graphs for human and LLM answers to the same questions and compares their topology against a human-vs-human baseline.
That is a "not found", not proof of absence.
Threads of Subtlety is the closest work and already used HC3, so the team should cite it and draw the contrast: discourse-level and detection-oriented there, argument-level and descriptive here.

## Suggested changes to GUIDE.md and CLAUDE.md, for the team to decide

GUIDE.md does not exist yet in the repository, and CLAUDE.md says only the team may change it.
Everything below is a suggestion.

For GUIDE.md, the team could adopt five rules.
Fix glued sentences with a regex before splitting, then hand-check abbreviations like "U.S.".
Treat each list item as one node and the lead-in line as its own node.
Keep two-idea sentences as one node with a `multi_claim` flag.
Keep filler sentences as nodes with a `filler` role, and flag refusals the same way.
Use only "main claim" and "other" as argument roles, merge rebut and undercut into `attacks`, and write explicit tie-break rules for `explains` versus `supports` and `restates` versus `supports`.

For the CLAUDE.md data rule, the team could make three changes.
Add a per-question length filter (ChatGPT/human word ratio 0.67–1.5) and a minimum human length, because the "similar length" premise holds only on averages.
State that wiki_csai is a definitional control, not an argument topic, and optionally allow a paired r/ChangeMyView source as a second argument domain after a licence check.
Spell out how to meet the human-vs-human baseline rule when each question has one human answer: a cross-question baseline plus the annotator-agreement baseline.

## Conclusion

The tool question hid a framing question.
Ontology and KG builders fail here not because they are weak, but because they encode content, and this project is about form.
Once the graph is defined by roles and edge types, the hard part moves from tooling to measurement: the splitter, the extractor and graph size can each create a human-versus-LLM "difference" on their own.

The most defensible headline is therefore a calibrated one.
It reads "structure alone separates ChatGPT from humans at X%, Y points above size alone, with extractor accuracy Z on each side", or "once size is controlled, structure carries no reliable signal".
Either is a real finding.
The fixes that make it possible are cheap: a regex for glued sentences, a length filter, a cross-question baseline and a ten-text hand check.
They should come before any graph is drawn.
