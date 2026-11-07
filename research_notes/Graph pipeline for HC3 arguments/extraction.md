# Extracting argument graphs from short HC3 answers

Scope: which paradigm, schema, tools and validation fit the question "Do LLMs argue like humans?".
Researched 2026-11-07.
GitHub data was checked with `gh api` on that date.
Items marked UNVERIFIED come from background knowledge and were not confirmed by a fetched source.

## Paradigms and fit: argument mining vs discourse parsing vs entity/relation KGs

### Takeaway
Argument mining (claim/premise, support/attack) captures *how an argument is built*.
Entity/relation KGs capture *what it is about*.
RST/PDTB discourse relations sit in between: they cover every sentence (including non-argumentative ones like "explains" or "example"), which our draft schema needs.
Recommended: an argument layer as the primary graph (sentence nodes, Peldszus–Stede-style typed edges), with discourse-style labels for non-argumentative links; an entity layer is optional and should only be a secondary analysis, never the basis of the human-vs-LLM structure comparison.

### Cited Findings
- The arg-microtexts corpus (Peldszus & Stede) is the closest existing scheme to our setup: 112 short texts, 576 ADUs, labels for central claim, role (proponent/opponent), function (support, attack, none) and attachment — [arXiv 2411.05639](https://arxiv.org/pdf/2411.05639v1).
- Microtext relation distribution: support 281 (55.2%), rebutting attack 110 (21.6%), undercutting attack 65 (12.8%), support-by-example 9 (1.8%), joint links 44 (8.6%) — [HF dataset card DFKI-SLT/argmicro](https://huggingface.co/datasets/DFKI-SLT/argmicro/blob/refs%2Fpr%2F1/README.md).
- Microtext gold was produced by one expert annotator plus a reconciliation phase, not a multi-annotator aggregate — [HF dataset card](https://huggingface.co/datasets/DFKI-SLT/argmicro/blob/refs%2Fpr%2F1/README.md).
- A classical parsing approach (Evidence Graphs, Peldszus & Stede 2015) converts argument graphs into dependency trees whose arc labels are functions like "support" or "attack" — [End-to-End Argument Mining over Varying Rhetorical Structures, arXiv 2401.11218](https://arxiv.org/pdf/2401.11218). This matches our "one sentence = one node, one outgoing edge" design.
- Stab & Gurevych persuasive essays use major claim / claim / premise with support/attack relations — [arXiv 1604.07370](https://arxiv.org/pdf/1604.07370).
- Discourse relation classification is now standardised across corpora: DISRPT 2025 used a unified set of 17 relation labels across 39 corpora in 16 languages — [DISRPT 2025 proceedings](https://aclanthology.org/2025.disrpt-1/).
- LLM text differs structurally from human text: "Argument Collapse" (EMNLP 2026) reports LLM responses more often open with a thesis, move to support, end with a proposal, while humans mix in more exposition; 65.3% of human main arguments are unique within a debate vs 3.4% for LLMs — [arXiv 2606.01736](https://arxiv.org/pdf/2606.01736); [ACL Anthology 2026.emnlp-main.1039](https://aclanthology.org/2026.emnlp-main.1039).
- A 2026 originality study found AI essays reach structural complexity comparable to human essays, but claim rarity about one fifth of human levels — [arXiv 2602.01560](https://arxiv.org/html/2602.01560v2).
- Text-to-KG extraction tools (e.g. LangExtract) have no formal relation/graph model for argument structure; relationships appear only as an extraction class — [google/langextract README](https://github.com/google/langextract).

### Inferences
- The research question is about structure, so the comparison graph must be the argument layer.
  "Argument Collapse" shows the expected differences are exactly structural (thesis-first templates, less exposition), which an argument + discourse label set can capture and an entity KG cannot.
- Our draft labels map cleanly: supports → microtext `sup` / S&G `support` / RST Evidence/Justify; attacks → microtext `reb`/`und` / S&G `attack` / RST Antithesis/Concession; example → microtext `exa` / RST Elaboration(example) / PDTB Expansion.Instantiation; explains → RST Elaboration/Explanation / PDTB Contingency.Cause or Expansion; restates → RST Restatement/Summary / PDTB Expansion.Equivalence; main claim → microtext central claim / S&G major claim.
  (Mapping is our inference; RST/PDTB label names are UNVERIFIED against the DISRPT 17-label list.)
- Two-layer graph is feasible: argument nodes = sentences; entity nodes linked to sentences by "mentions".
  Use it only for a side question ("do humans cite more concrete finance entities?"), consistent with the "Argument Collapse" finding that humans are more topic-specific.
  Keep it out of the main metric because CLAUDE.md requires comparisons on roles and edge types only.
- Collapse microtext rebut/undercut into one "attacks" label: the counts above show attacks are rare even in argumentative texts; in HC3 explanatory answers they will be rarer still.

### Gaps
- No source found that directly evaluates argument mining on HC3 or on Q&A-style explanatory answers.
- The 17 DISRPT unified labels were not retrieved by name.

## Crafting the schema and expected agreement

### Takeaway
Keep 5–6 edge types and 2–3 node roles, write decision rules for the confusable pairs (explains vs supports, restates vs supports), and expect human-human agreement around alpha 0.7–0.8 for components and lower for the "claim"-like middle role.
Pilot with 2 annotators on ~10 texts and report kappa before trusting the extractor.

### Cited Findings
- Stab & Gurevych journal version: joint unitized agreement αU = .767 over all components; per type αU .810 major claim, .524 claim, .824 premise; Fleiss κ .877 major claim, .833 premise, .635 claim (three annotators) — [arXiv 1604.07370](https://arxiv.org/pdf/1604.07370).
- Stab & Gurevych COLING 2014: αU = 0.72 for components and α = 0.81 for argumentative relations — [C14-1142](https://preview.aclanthology.org/fix_video/C14-1142.pdf).
- The same authors state human annotators can reliably distinguish supporting vs attacking claims — [arXiv 1604.07370](https://arxiv.org/pdf/1604.07370).
- Finer-grained multi-layer annotation of English microtexts is reported to yield reliable agreement (Peldszus 2014), but no numbers were retrieved — [Stede et al., ISA 2022 / related](https://aclweb.org/anthology/2022.isa-1.9.pdf).
- Agreement in argument mining is usually reported with Cohen's κ, Fleiss' κ or Krippendorff's α; Duthie et al. (2016) question plain Cohen's κ for argument structure — [ISA 2022 paper](https://aclweb.org/anthology/2022.isa-1.9.pdf).
- Peldszus & Stede 2013 "Ranking the annotators" is an agreement study on argumentation structure (LAW 2013) — [W13-2324](https://aclanthology.org/W13-2324/); values not retrieved.

### Inferences
- The weakest human agreement is on the middle role ("claim", κ .635 / αU .524).
  Our schema should avoid a separate "sub-claim" role; use main claim vs other, and let the edge type carry the function.
- Since sentences are pre-segmented (one sentence = one node), we avoid unitizing disagreement; plain Cohen's κ (2 annotators) or Krippendorff's α (nominal) on per-sentence role and per-sentence edge label is appropriate.
- Target human-human κ ≥ 0.6 on edge types before using the hand labels as gold; if lower, merge labels (e.g. explains + example).

### Gaps
- Peldszus microtext κ values (2013, 2014) not retrieved.
- No published agreement for an "explains/example/restates" label set on short Q&A answers.

## LLM-based argument mining and discourse parsing (2023–2026)

### Takeaway
Prompted LLMs are decent at classifying relations between given units but weak at end-to-end structure, and generally trail fine-tuned models.
Because our nodes are fixed sentences (no span detection), we are in the easier regime; still, a hand-check against gold is mandatory.
No study was found that measures whether LLM extractors parse LLM-written text more accurately: this is an open risk we must measure ourselves.

### Cited Findings
- Chen et al. (ACL 2024) evaluated ChatGPT, Flan and LLaMA2 zero/few-shot on 14 standardised computational argumentation datasets; LLMs show "commendable performance across most of the datasets" (no numbers in abstract) — [arXiv 2311.09022](https://arxiv.org/abs/2311.09022).
- **Correction (2026-11-07):** these numbers are from Pirozelli et al., arXiv 2605.13793, Table 2 (link F1 20.82 vs 39.74), not arXiv 2603.03095; see `reports/SOTA argument extraction.md`.
- A 2026 LLM argument mining pipeline on AbstRCT reportedly reaches span F1 ≈ 60 and link F1 ≈ 21, vs ≈ 71 / ≈ 39 for fine-tuned Morio et al. (2022); gold components lift results, so span detection is the bottleneck. Model name not confirmed; numbers from a search snippet, not the full paper — [arXiv 2603.03095](https://arxiv.org/pdf/2603.03095v1.pdf). (The separate arXiv 2605.13793, Pirozelli et al., May 2026, claims "reasonable performance" without numbers in the abstract — [arXiv 2605.13793](https://arxiv.org/abs/2605.13793).)
- Gorur, Rago & Toni (COLING 2025): with few-shot priming, Llama 2 70B and Mixtral 8x7B beat a fine-tuned RoBERTa baseline on macro F1 for support/attack classification across ten datasets; GPT-3.5-turbo and GPT-4o-mini also tested — [2025.coling-main.569](https://aclanthology.org/2025.coling-main.569.pdf); [arXiv 2402.11243](https://arxiv.org/html/2402.11243v1). Per-dataset numbers not retrieved.
- Finance domain: GPT-4 zero-shot argument relation identification on FinArg reached Macro-F1 86.9% (10th of 52) — [FinNLP 2024.finnlp-1.12](https://aclanthology.org/2024.finnlp-1.12.pdf) (number from search snippet).
- Legal domain: small domain-specific models beat GPT-3.5/GPT-4 on premise and conclusion F1 by 1.9% and 12%; GPT results vary noticeably with prompt formulation — [Frontiers in AI 2023](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2023.1278796/pdf).
- Few-shot task context is the most effective enrichment for LLM component-relation classification, ahead of KG, sentiment or chain-of-thought — [C4AI repo](https://github.com/C4AI/llm_component_relation_classification).
- Discourse: in DISRPT 2025, CLaC found prompted Claude Opus 4.0 (zero- and few-shot) "lag significantly" behind fine-tuned transformers on unified relation classification; best systems reached 71.19% mean relation accuracy (DeDisCo, Qwen-based, 71.28 macro-accuracy) — [DISRPT 2025](https://aclanthology.org/2025.disrpt-1/).
- RST parsing with LLMs: Maekawa et al. (EACL 2024) fine-tuned Llama 2 70B (QLoRA, bottom-up) to state of the art on RST-DT, Instr-DT and GUM — not a zero-shot result — [arXiv 2403.05065](https://arxiv.org/pdf/2403.05065).
- LLM essays follow more predictable templates than human essays — [arXiv 2606.01736](https://arxiv.org/pdf/2606.01736). ArguGPT: a fine-tuned RoBERTa detects GPT essays with > 90% accuracy, human instructors 61% at first — [arXiv 2304.07666](https://arxiv.org/abs/2304.07666v2).

### Inferences
- With sentence nodes given, our task resembles relation classification (where LLMs do well) more than end-to-end mining (where they do poorly).
  The weakest step will be attachment (which sentence a node links to), not the label.
- Template-like LLM answers plausibly make extraction easier on LLM text (thesis-first, explicit connectives).
  This could inflate apparent structural differences, so extractor accuracy must be reported separately for human and LLM texts (as CLAUDE.md already requires).
- Few-shot examples in the guide prompt (one human, one ChatGPT HC3 answer, fully labelled) are the best-supported prompt enrichment.

### Gaps
- No Claude-specific argument mining F1 found; no direct study of "LLM extractors parse LLM text more easily".
- No zero-shot RST tree parsing numbers for GPT-4/Claude found.
- Exact numbers for Chen et al. 2024 and Gorur et al. 2025 not retrieved.

## Open-source tools to reuse

### Takeaway
No argument-mining toolkit is a drop-in for prompted Claude extraction; the practical stack is Pydantic schema + Anthropic structured output (or `instructor`) + our own validator.
Reuse existing corpora (arg-microtexts) for prompt sanity checks, and optionally `isanlp_rst` as an independent non-LLM discourse baseline.

### Cited Findings
GitHub facts via `gh api repos/...` on 2026-11-07 (license, last push, stars):

| Repo | License | Last push | Stars | Fit |
|---|---|---|---|---|
| [567-labs/instructor](https://github.com/567-labs/instructor) | MIT | 2026-11-06 | 14.1k | Pydantic-validated LLM output with retries; supports Anthropic (UNVERIFIED from README). Best fit. |
| [dottxt-ai/outlines](https://github.com/dottxt-ai/outlines) | Apache-2.0 | 2026-09-21 | 16.0k | Constrained decoding; mainly for local models, less useful with Claude API. |
| [google/langextract](https://github.com/google/langextract) | Apache-2.0 | 2026-11-07 | 39.3k | Char-offset grounding, few-shot examples, attributes; Gemini/OpenAI/Ollama built in, Claude needs a provider plugin; no relation model — [README](https://github.com/google/langextract). |
| [neo4j-labs/llm-graph-builder](https://github.com/neo4j-labs/llm-graph-builder) | Apache-2.0 | 2026-11-01 | 5.3k | Entity KG with schema; wrong layer for argument structure. |
| [stair-lab/kg-gen](https://github.com/stair-lab/kg-gen) | none detected by API | 2026-03-24 | 1.3k | Entity KG; license unclear → avoid for CC BY-SA outputs until checked. |
| [ArneBinder/pytorch-ie](https://github.com/ArneBinder/pytorch-ie) / [pie-modules](https://github.com/ArneBinder/pie-modules) | MIT | 2025-09 | 76 / 1 | Argument-mining dataset loaders/metrics (incl. argmicro via DFKI-SLT HF datasets); useful for loading corpora, heavy for a hackathon. |
| [uhh-lt/targer](https://github.com/uhh-lt/targer) | MIT | 2023-05 | 30 | Token-level claim/premise tagger; stale. |
| [tchewik/isanlp_rst](https://github.com/tchewik/isanlp_rst) | MIT | 2026-09-15 | 65 | Maintained RST parser; candidate independent baseline. |
| [seq-to-mind/DMRST_Parser](https://github.com/seq-to-mind/DMRST_Parser) | none detected | 2023-01 | 45 | Multilingual RST parser; stale, unclear license. |
| [rknaebel/discopy](https://github.com/rknaebel/discopy) | MIT | 2023-06 | 26 | PDTB shallow parser; stale. |
| [UKPLab/acl2017-neural_end2end_am](https://github.com/UKPLab/acl2017-neural_end2end_am) | NOASSERTION | 2021-01 | 59 | Old end-to-end AM; not recommended. |
| [disrpt/sharedtask2025](https://github.com/disrpt/sharedtask2025) | none detected | 2026-03 | 8 | Data/eval scripts for unified discourse relations. |

- Data: arg-microtexts on Hugging Face as `DFKI-SLT/argmicro` (viewer disabled; requires running a loading script) — [HF](https://huggingface.co/datasets/DFKI-SLT/argmicro).
- TARGER and ArgumenText public demos: activity/availability not verified (TARGER repo last pushed 2023).

### Inferences
- Pipeline: Pydantic models `Node(id, sentence_idx, role)` and `Edge(src, dst, type ∈ {supports, attacks, explains, example, restates})` → Claude structured output / tool use → deterministic validator (every sentence exactly one node, known types only, no self-loops, exactly one main claim, graph is a tree/DAG) → count and report failures.
- LangExtract's grounding is unnecessary because nodes are pre-segmented sentences; its value is low here.
- Load `DFKI-SLT/argmicro` with `python -I` in an isolated directory (it runs remote code).

### Gaps
- Claude support in instructor and LangExtract not verified from docs in this session.
- kg-gen and DMRST license status unclear (API returned none).

## Validation: extracted vs hand-labelled graphs, and run stability

### Takeaway
Because nodes are fixed sentences, evaluation is simple: main-claim accuracy, per-sentence role κ, and edge F1 at two strictness levels (unlabelled attachment; labelled attachment + type).
Run the extractor ≥3 times per text and report run-to-run κ as a stability measure.

### Cited Findings
- Component and relation (link) F1 are the standard end-to-end argument mining metrics (e.g. AbstRCT span F1 / link F1 comparison) — [arXiv 2603.03095](https://arxiv.org/pdf/2603.03095v1.pdf).
- Microtext evaluation splits into central claim, role, function and attachment levels — [arXiv 2411.05639](https://arxiv.org/pdf/2411.05639v1).
- Krippendorff's αU is used when unit boundaries differ; α/κ when units are fixed — [arXiv 1604.07370](https://arxiv.org/pdf/1604.07370).
- Cohen's κ, Fleiss' κ, Krippendorff's α are the usual agreement measures; Duthie et al. (2016) caution about Cohen's κ for argument structure — [ISA 2022](https://aclweb.org/anthology/2022.isa-1.9.pdf).
- Prompt formulation causes noticeable variance in GPT argument mining results — [Frontiers in AI 2023](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2023.1278796/pdf).

### Inferences
- Report per text type (human / LLM): main-claim accuracy; role κ; unlabelled edge F1 (src→dst); labelled edge F1 (src→dst+type); per-type confusion matrix; validation failure count.
- Compare each extractor-vs-gold number to human-vs-human agreement on the same texts as the ceiling.
- Stability: same prompt, ≥3 runs (temperature fixed), pairwise labelled-edge F1 and role κ between runs; flag texts with low stability.
- Bootstrap confidence intervals over texts, not edges, because edges within a text are dependent.

### Gaps
- CAS (Combined Argument Similarity, Duthie et al. 2016) and CEAF-style graph alignment metrics: not retrieved in this session (UNVERIFIED); with fixed sentence nodes they are likely unnecessary.
- No published run-to-run stability numbers for LLM argument extraction were found.
