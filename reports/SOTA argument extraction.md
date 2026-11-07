# State of the art in LLM argument extraction: topology, pipeline, reliability

> Note (2026-11-07): written before the extractor switched to the team's `relation.yaml`.
> The `edge_optional` rule and `relation_definition.yaml` it mentions no longer exist; every non-main piece now needs an edge.
> Its recommendation was tested in [the approach study](../experiments/approach_study/FINDINGS.md) and adopted in [ADR 0001](../docs/adr/0001-extraction-approach.md).

**TL;DR.**
There is no single state-of-the-art topology, but trees with one outgoing edge per unit are the long-standing default for short argumentative texts (microtexts, persuasive essays); general graphs (AIF, CDCP) are used when texts are messier.
There is no settled winner between one-pass and step-by-step extraction either: fine-tuned one-pass generators hold the best published scores, while for prompted LLMs the published evidence favours separate steps.
The classic way to get valid, stable trees is not "ask for a tree" but "score candidate links, then decode the best tree" (MST or ILP), and that is cheap to copy with LLM votes.
In our own two runs, segmentation was identical and most edge-count changes came from entity-type flips into or out of the `edge_optional` types, not from linking alone.
Recommendation: freeze segmentation, sample typing and linking 5 times, and decode one tree from the votes; then sanity-check on arg-microtexts against a trivial "attach to preceding" baseline.

Scope.
This report adds to two earlier reports and does not repeat them.
[Graph pipeline for HC3 arguments](Graph%20pipeline%20for%20HC3%20arguments.md) (Step 3) already covers the microtext-style schema, LLM relation-classification results (Gorur et al., FinArg), extractor bias, and per-side metrics.
[Reasoning schema frameworks for extraction](Reasoning%20schema%20frameworks%20for%20extraction.md) already covers structured outputs, the validator and a blind gold set.
Everything marked "Our judgement" is mine, not from a paper.

## 1. Topology: trees are the default, and they lose little on short texts

**What the papers use.**

- *Microtexts (Peldszus & Stede).*
  The annotated graphs include undercuts (edges that attack other edges) and linked premises.
  For parsing, Peldszus & Stede rewrite edge-targeting relations to point at the source node of the target edge.
  They call this "a loss-less mapping, given that every segment has only one outgoing arc (as generally done in argumentation models)" ([EMNLP 2015, D15-1110](https://aclanthology.org/D15-1110/)).
  So "one outgoing edge per unit, giving a tree" is the standard reading of this corpus.
- *Persuasive essays (Stab & Gurevych).*
  They model each paragraph as a tree, and the essay as a set of such trees under one major claim.
  They argue that a tree excludes "divergent" arguments (one premise backing two claims) and cycles.
  They justify this with essay-writing practice and with the only study they found: 5.26% of arguments in political speeches were divergent ([CL 2017, arXiv 1604.07370](https://arxiv.org/pdf/1604.07370)).
  Their ILP decoder enforces at most one outgoing relation per component, at least one root, and no self-loops.
- *CDCP (Park & Cardie; Niculae, Park & Cardie).*
  User comments on a US Consumer Financial Protection Bureau rule about debt collection.
  Here relations "need not form a tree" in over 20% of documents, so Niculae et al. use a factor graph instead of tree decoding ([ACL 2017, P17-1091](https://aclanthology.org/P17-1091/)).
- *AIF (Argument Interchange Format).*
  A general graph with information nodes and scheme nodes for inference, conflict and rephrase.
  It allows several outgoing edges, edges onto edges, and dialogue structure.
  It is used by the Dundee/ARG-tech corpora; see the survey by Lawrence & Reed ([CL 2019, J19-4006](https://aclanthology.org/J19-4006/)).
  The node details here are from background knowledge, not a fetched source.
- *LLM pipelines (2026).*
  The multi-stage GPT pipeline of Pirozelli et al. outputs a DAG (directed acyclic graph), and keeps it acyclic by only linking to unvisited components ([arXiv 2605.13793](https://arxiv.org/html/2605.13793v2)).
- *RST* gives one tree over the whole text, including non-argumentative links; *Toulmin* is a per-argument template (claim, data, warrant, backing, qualifier, rebuttal), not a document graph.
  The earlier reports already discuss both as schema sources.

**Is "one outgoing edge, so a tree" standard?**
Yes, for short monological texts.
It is the microtext convention and the essay convention, and most decoders since 2015 enforce it.

**What it loses.**

1. *Divergent support*: one sentence that backs two claims must pick one.
2. *Linked premises*: two reasons that only work together become two separate edges.
   Microtexts mark these as "joint" links (8.6% of relations, per the earlier report).
3. *Undercuts*: an attack on the link "A supports B" becomes an attack on A.
   Peldszus & Stede accept this loss.
4. *Free-floating context*: a tree forces every non-root unit to attach somewhere.
   Our schema escapes this with `edge_optional`, which makes the graph a forest, not a tree.

Our judgement: for 100–200 word finance answers, losses 1–3 are small, and the gain is big.
A tree makes every graph comparable, makes tree edit distance and depth well defined, and turns linking into "pick one parent per node", which is easy to vote on and decode.
Loss 4 matters more for us, see section 5.

## 2. Pipeline: one pass vs step by step

The classic task has four steps: segment, classify components, identify links, label relations.

**What papers report.**

| Approach | Example | Result |
|---|---|---|
| Pipeline + global decoding | Peldszus & Stede 2015, MST over an "evidence graph" | Joint scores for role, function, central claim and attachment, then Chu-Liu-Edmonds decoding; attachment F1 0.502 (English) vs 0.452 for "attach to preceding" and 0.478 for an unconstrained classifier ([D15-1110](https://aclanthology.org/D15-1110/)) |
| Pipeline + ILP | Stab & Gurevych 2017 | ILP raises relation macro F1 from 0.717 to 0.751 (not significant); human upper bound 0.854 ([arXiv 1604.07370](https://arxiv.org/pdf/1604.07370)) |
| One-pass generation, fine-tuned | Kawarada et al., EACL 2024 (FLAN-T5 XXL, text-to-text) | State of the art on AAEC, AbstRCT and CDCP; on AAEC 80.15 component F1, 61.19 relation F1 ([2024.eacl-long.121](https://aclanthology.org/2024.eacl-long.121)) |
| One-pass generation, fine-tuned LLMs | Cabessa et al., COLING 2025 (Llama-3, Gemma-2, Qwen-2, ...) | Models sub-tasks and the joint task as generation; claims state of the art on PE, AbstRCT, CDCP (numbers not checked) ([2025.coling-main.442](https://aclanthology.org/2025.coling-main.442/)) |
| Pipeline vs joint, fine-tuned LLMs | Alzaidee et al., CMNA 2025 (Llama-3, Mistral) | Pipeline beat multi-task joint for all models; best 80.02 component, 60 relation F1 on AAEC ([CEUR Vol-4166](https://ceur-ws.org/Vol-4166/paper4.pdf)) |
| Prompted multi-stage LLM | Pirozelli et al., arXiv 2026 (GPT-4.1, GPT-5) | 12 stages ending in a DAG; AbstRCT link F1 20.82 vs 39.74 for a fine-tuned model, rising to 51.51 with gold components; AAEC link F1 0.41 ([arXiv 2605.13793](https://arxiv.org/html/2605.13793v2)) |
| Prompted pair classification | Gorur et al., COLING 2025 | Pairs are given; binary support/attack; Llama-2-70B 75 macro F1 vs 68 for RoBERTa ([arXiv 2402.11243](https://arxiv.org/html/2402.11243v1)) |
| Constrained, schema-validated LLM | Tran et al., ArgMining 2026 shared task | Retrieval, constrained decoding, a "debate" only for uncertain cases, and schema validation; ranked 1st ([arXiv 2607.20430](https://arxiv.org/abs/2607.20430)) |

Notes on the table.
The earlier report attributed the AbstRCT "link F1 ≈ 21 vs ≈ 39" numbers to arXiv 2603.03095 from a snippet.
They are in fact from Pirozelli et al., arXiv 2605.13793, Table 2, read in full here.
arXiv 2603.03095 is a different preprint (Elguendouze et al., "compact prompting" for one-pass component detection, under review), and its abstract gives no numbers.
One-pass generative models with a constrained pointer decoder also exist (BART-CPM, Bao et al. 2022, 50.08 relation F1 on AAEC, cited via Alzaidee et al.).
The 2025 survey by Li et al. reviews the field's shift to prompting but gives no head-to-head LLM pipeline vs one-pass numbers ([arXiv 2506.16383](https://arxiv.org/abs/2506.16383v6)).

**What this means.**

- The best published end-to-end scores come from *fine-tuned* one-pass generators.
  We cannot fine-tune Claude, so those results do not transfer to us directly.
- For *prompted* LLMs, the evidence points to splitting: gold (fixed) components lifted Pirozelli's link F1 from 21 to 52 on AbstRCT, and they name span detection "the main bottleneck".
  The earlier report made the same point: fixed units turn the task into relation classification, where LLMs do well.
- Joint *scoring* helps linking: Peldszus & Stede found that knowing a unit's role and function improves where it attaches.
  So "split everything into four calls" is not the lesson.
  The lesson is: fix the units, then choose type and parent together, and enforce the tree at the end.
- Without a decoder, pairwise predictions rarely form trees.
  Peldszus & Stede's unconstrained classifier produced valid trees for only 10.7% of English texts; the most common violation was "more than one outgoing edge".
  Our one-pass Claude call plus validator plus retry avoids this, but it fixes the tree by re-asking, not by optimising.

I found no paper that combines LLM link scores with MST decoding for argument mining.
Our judgement: it is a direct port of Peldszus & Stede, and section 5 suggests a cheap version.

## 3. Reliability: making links stable, and measuring agreement

**What we see in our own runs.**
I compared the two runs in `results/extraction/` (4 texts, 37 entities) with a throwaway script.
This is a tiny sample, so read it as a hint, not a result.

- Segmentation was identical in all 4 texts: same number of entities, same text.
- 5 of 37 entities changed type, e.g. `background` → `reason`, `caveat` → `condition`, `counterpoint` → `condition`.
- Edges: 20 in run A, 23 in run B, 16 shared.
- Every change in edge *count* came from a type flip into or out of an `edge_optional` type (`background`, `caveat`).
  Example: in `finance_0001_human`, entities 5 and 6 were `background` (no edge) in run A and `counterpoint`/`reason` (with edge) in run B.
- Two edges changed only their parent (e.g. entity 9 → 3 vs 9 → 1), which is the classic attachment ambiguity.

So the "relation count" instability is mostly a typing instability that the `edge_optional` rule turns into a structure change.
This matters for the research question: graph size and density would vary between runs for reasons unrelated to the author.

**Methods from the literature.**

- *Self-consistency.*
  Sample several outputs and take the majority answer ([Wang et al., arXiv 2203.11171](https://arxiv.org/abs/2203.11171)).
  For free-form outputs, "universal self-consistency" asks the LLM to pick the most consistent sample ([Chen et al., arXiv 2311.17311](https://arxiv.org/abs/2311.17311)).
  I found no paper that tests voting on argument links.
  Pirozelli et al. report "considerable variability" across runs and suggest generating several candidates, but did not test it.
- *Score then decode.*
  Turn pairwise scores into a best tree with Chu-Liu-Edmonds (MST) or ILP, as in section 2.
  This guarantees a valid tree and makes a small change in scores produce a small change in the tree.
- *Selective escalation.*
  Spend extra calls only on uncertain items, as the 2026 shared-task winner did with its "debate" step.
- *Validators and retries.*
  We already have these; they fix validity, not stability.

**How to measure agreement.**
The earlier report already lists per-side metrics (main-claim accuracy, role κ, unlabelled and labelled edge F1, confusion matrix).
Additions from the literature:

- With fixed units and one parent per node, the dependency-parsing metrics fit exactly: *attachment accuracy* (share of nodes with the right parent) and *labelled attachment* (right parent and right relation).
  Peldszus & Stede report attachment F1 and Cohen's κ; Stab & Gurevych report macro F1 for "linked" vs "not linked" pairs.
- If units can differ (our extractor segments), match units first; [CASS](https://aclanthology.org/W16-2805/) (Duthie et al., ArgMining 2016) combines segmentation, proposition and relation agreement into CASS-κ and CASS-F1.
- Always show a trivial baseline.
  "Attach each unit to the preceding one" reached 0.452 attachment F1 on English microtexts, against 0.502 for the best 2015 model.
  A Claude extractor that cannot beat this baseline on our gold set is not adding much.
- Use the same metrics for run-vs-run stability as for extractor-vs-human, so the two numbers sit side by side.

## 4. Benchmarks for a sanity check

| Corpus | Texts | Structure | Fit for us | License |
|---|---|---|---|---|
| [arg-microtexts](https://github.com/peldszus/arg-microtexts) (Peldszus & Stede) | 112 short texts, English and German | Tree, one outgoing edge, support/rebut/undercut/example | Best fit: short, same tree rule, similar length to HC3 answers | CC BY-NC-SA 4.0 (repo and [HF card](https://huggingface.co/datasets/DFKI-SLT/argmicro)) |
| [CDCP](https://huggingface.co/datasets/DFKI-SLT/cdcp) (Park & Cardie 2018) | 731 comments on a CFPB debt-collection rule | Non-tree graph; reason/evidence links | Finance-adjacent, informal, close to human HC3 answers | Not stated on the HF card; not verified |
| [AAEC v2](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/2422) (Stab & Gurevych) | Persuasive student essays | Tree per paragraph, major claim / claim / premise | Longer texts; many published baselines | Research use only, no redistribution, per a UKP licence template (not verified against the current record) |
| [AbstRCT](https://gitlab.com/tomaye/abstrct) (Mayer et al.) | 659 clinical-trial abstracts | Evidence/claim, support/attack | Wrong domain and register; skip | CC BY-NC-SA 4.0 per the GitLab page |

All candidate corpora are non-commercial or unclear.
Our judgement: use them only as local sanity checks, keep them out of the repository, and do not mix them into our CC BY-SA data.
The `argmicro` loader runs remote code; the earlier report already says to load it with `python -I` in an isolated folder.

Mapping microtexts to our schema (our judgement): central claim → `main`; support → `supports`; example → `illustrates`; rebut and undercut → `attacks`; opponent units → `counterpoint`.
Score only main-claim accuracy, attachment accuracy and support-vs-attack, since our finer types do not exist there.

## 5. Recommendation for this project

**Keep one call per answer for now, but split it into two stages and decode the tree in code.**
The literature does not show that one pass is wrong.
It shows that prompted LLMs link better on fixed units, and that trees are best made by decoding, not by asking.
Our runs show segmentation is already stable, while typing and linking are not.

Three changes worth doing in a hackathon:

1. **Freeze segmentation, then sample typing and linking 5 times, and decode one tree from the votes.**
   - Stage 1: run the current prompt once and keep only the entity texts (or use the SaT splitter from the earlier report).
     Save them; never re-segment.
   - Stage 2: send the fixed, numbered entities and ask only for type, flags and parent edge.
     Run it 5 times.
   - Aggregate in Python: majority type per entity; edge weight = number of runs that chose that parent; pick the tree with `networkx.maximum_spanning_arborescence` rooted at the voted main claim; edge label = majority label on the chosen edge.
   - Keep the vote shares as a per-node confidence, and report the share of nodes with a 5/5 vote.
   - Cost is about 5× stage 2 for 800 texts; the earlier report estimated about $55 per 3 Opus runs, so roughly $100 more.
2. **Make "no edge" an explicit, voted choice, and ask the team about `edge_optional`.**
   Today a `background` ↔ `reason` flip silently changes the edge count.
   In the vote, treat "no edge" as a virtual parent, so it competes with real parents and is counted.
   Then report edge counts both with and without the optional nodes, so graph-size results cannot come from typing noise.
   Whether to add a relation like `context_for` is already an open question in `relation_definition.yaml`; it is the team's call, per `CLAUDE.md`.
3. **Run a 20-text sanity check on English arg-microtexts before the full HC3 run.**
   Compare against "attach to preceding" (0.452 attachment F1 in 2015) and report run-to-run attachment agreement next to extractor-vs-gold attachment accuracy.
   This is a cheap, external check that the linker is better than a trivial rule.
   It does not replace the hand-labelled HC3 gold set, which is still the main check per `CLAUDE.md`.

What I would *not* do now: a full four-step pipeline, AIF-style general graphs, or LLM-scored all-pairs matrices.
For a 10-entity answer, all-pairs scoring is 90 judgments per text; votes over parent choices give a similar signal for far fewer calls.

## Gaps

- No paper found that measures run-to-run stability of LLM argument extraction, or that tests voting or MST decoding on LLM link outputs.
- No zero-shot or few-shot Claude result on arg-microtexts attachment was found.
- Cabessa et al. (COLING 2025) and Kawarada et al. (EACL 2024) were read from abstracts and citing papers; their own tables were not checked.
- CDCP and AAEC licences were not confirmed from the original download pages.
- The run comparison in section 3 covers only 2 runs on 4 texts and was done with an unsaved script; rerun it with a saved script before quoting it.
