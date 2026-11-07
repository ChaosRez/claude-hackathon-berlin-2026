# Linguistic frameworks for the structure of reasoning in text, judged as an annotation/extraction schema

Scope: discourse and argumentation frameworks that could type the edges (and node roles) of sentence-level graphs built from HC3 `finance` / `wiki_csai` answers.
Verification status: items in "Cited Findings" were read in the primary PDF in this session unless marked *(snippet only)*.
Items from background knowledge that I could not verify in this session are in "Gaps" or marked **UNVERIFIED**.

## Q1. Which relation sets are easiest and most reliable for annotators and LLMs (coarse vs fine)?

### Takeaway
Agreement falls steadily as label sets get finer and as relations lose explicit connectives.
PDTB-2 reports 94% / 84% / 80% agreement at class / type / subtype, but implicit relations alone sit near κ≈0.5–0.6 even for experts.
In CCR, the binary primitive *polarity* (positive/negative, i.e. support-like vs contrast-like) is reliable even for untrained annotators (κ=.73), while *source of coherence* (content vs speech-act/epistemic) is not (κ=.31).

### Cited Findings
- PDTB-2.0 sense annotation by two annotators: agreement "ranging from 94% at the class level to 80% at the subtype level" — CLASS 94%, TYPE 84%, SUBTYPE 80% (percent agreement, not κ; explicit + implicit pooled). — [Prasad et al. 2008, LREC](https://aclanthology.org/L08-1093.pdf)
- PDTB-2.0 argument-span agreement: exact match 90.2% (Explicit) and 85.1% (Implicit); partial match 94.5% and 92.6%. — [Prasad et al. 2008](https://aclanthology.org/L08-1093.pdf)
- PDTB defines "36 DR sense labels arranged in a three-level hierarchy, which can be lexicalized by one of 184 connectives". — [Yung et al. 2024](https://arxiv.org/pdf/2402.04918)
- Implicit relations are much harder: expert agreement κ=0.58 (Hoek et al. 2021) and κ=0.47 (Zikánová et al. 2019); κ=0.55 between aggregated crowd and expert labels (Scholman et al. 2022). — as cited in [Yung et al. 2024](https://arxiv.org/pdf/2402.04918)
- With CCR, agreement is higher on explicit than implicit relations; relations marked with an ambiguous connective were not simply "in between". — [Hoek, Evers-Vermeul & Sanders, DiscAnn 2021](https://aclanthology.org/2021.discann-1.1.pdf)
- CCR primitives with 40 non-trained, non-expert annotators (inter-annotator κ): polarity .73, order .47, basic operation (causal vs additive) .42, source of coherence .31. — [Scholman, Evers-Vermeul & Sanders 2016, Dialogue & Discourse 7(2)](https://aclanthology.org/2016.dnd-7.7.pdf)
- Same study, agreement with the expert gold (κ): polarity .86, order .61, basic operation .49, source of coherence .31. — [Scholman et al. 2016](https://aclanthology.org/2016.dnd-7.7.pdf)
- Explicit instructions with substitution and paraphrase tests (e.g. "can you insert *because* / *but*?") raised agreement over implicit instructions. — [Scholman et al. 2016](https://aclanthology.org/2016.dnd-7.7.pdf)
- Crowd workers struggle with large label menus; DiscoGeM was therefore annotated by a "two-step connective insertion" method (free-text linking phrase, then pick among connectives). — [Yung et al. 2024](https://arxiv.org/pdf/2402.04918)
- RST relation and nuclearity labelling "remains prone to significant levels of annotator disagreement". *(snippet only)* — [Ignatev, Paperno & Poesio 2025, SCiL](https://aclanthology.org/2025.scil-1.2.pdf)
- For comparison only (diagram corpus, not text): RST relations in AI2D-RST reached marginal κ 0.733 / uniform κ 0.783. *(snippet only)* — [AI2D-RST, arXiv 1912.03879](https://arxiv.org/pdf/1912.03879)
- Microtext argument scheme (central claim, support/attack) was described by its authors as "shown to yield reliable agreement" (referring to Peldszus 2014). — [Stede et al. 2016, LREC](https://aclanthology.org/L16-1167.pdf)

### Inferences
- The easiest, most reliable distinctions are coarse and binary: positive vs negative polarity (≈ support vs attack/contrast) and causal vs additive.
  These map well onto the team's intuition (Reason ≈ positive-causal, Refutation ≈ negative).
- The hardest distinctions are exactly those the team's draft relies on: `explains` vs `supports` is a *source of coherence* distinction (content/objective cause vs epistemic/speech-act justification), the least reliable CCR primitive (κ≈.31).
  Expect low agreement there unless decision rules and substitution tests are written down.
- Sentence-to-sentence relations in HC3 answers will be mostly implicit (no connective between sentences), so expect PDTB-implicit-like agreement (κ≈0.5–0.6) at a ~10–14 label level.
  This is a planning inference, not a measured number for HC3.
- Connective-insertion tests ("could *because* / *for example* / *in other words* / *but* go here?") are a cheap, validated way to make both human annotators and LLMs more consistent.

### Gaps
- RST-DT inter-annotator κ for relations (Carlson, Marcu & Okurowski 2003) could not be retrieved in this session. **UNVERIFIED** recollection: κ around 0.6 for the full relation set, higher for nuclearity and spans. Do not cite without checking.
- PDTB-3 (Webber et al. 2019 manual) agreement figures were not retrieved.
- IAT agreement: **UNVERIFIED** — I recall reported κ values in roughly 0.6–0.9 range for illocutionary connections and argument relations on debate corpora (Budzynska et al., Janier/Reed); not checked.
- Argumentative zoning: **UNVERIFIED** — Teufel's AZ reported κ≈0.71 for 7 categories (Teufel & Moens 2002); not checked.
- No agreement data was found for any scheme on informal Q&A answers like HC3.

## Q2. Which framework gives a natural way to evolve the schema (hierarchical senses, decomposable primitives)?

### Takeaway
Two mechanisms are proven: PDTB's class → type → subtype tree (coarsen by truncating labels) and CCR's orthogonal primitives (refine by adding a dimension, coarsen by dropping one).
UniDim (Sanders et al. 2018) shows CCR dimensions can map PDTB, RST and SDRT labels into one space, and DISRPT 2025 shows a 17-label cross-framework set is workable.

### Cited Findings
- PDTB senses form a three-level hierarchy; Chan et al. exploited "label dependence" by predicting top-level and second-level together in the prompt, which "increases significantly" explicit top-level performance. — [Chan et al. 2023, arXiv 2304.14827](https://arxiv.org/pdf/2304.14827)
- PDTB-2 agreement was reported per hierarchy level, with disagreement counted only when labels differ at that level (class 94%, type 84%, subtype 80%). Hierarchy therefore gives a built-in way to report coarse and fine agreement from one annotation. — [Prasad et al. 2008](https://aclanthology.org/L08-1093.pdf)
- PDTB's hierarchy itself was described as data-driven: "the specific number of levels and tags in PDTB were guided by the data and the nature of the task". — [Prasad et al. 2008](https://aclanthology.org/L08-1093.pdf)
- CCR is "a taxonomy of coherence relations in terms of four cognitive primitives" (basic operation, polarity, order of segments, source of coherence); a step-wise annotation procedure asks one primitive at a time. — [Scholman et al. 2016](https://aclanthology.org/2016.dnd-7.7.pdf)
- UniDim ("Unifying dimensions in coherence relations") uses CCR dimensions plus finer framework-specific features to map PDTB, RST and SDRT; it was tested by converting PDTB and RST labels of the same newspaper texts into per-dimension values and measuring overlap. *(abstract / catalogue)* — [Sanders et al. 2018, Corpus Linguistics and Linguistic Theory, doi 10.1515/cllt-2016-0078](https://dspace.library.uu.nl/bitstream/1874/432153/1/10.1515_cllt-2016-0078.pdf); [SFB1102 page](https://sfb1102.uni-saarland.de/publication/unifying-dimensions-in-coherence-relations-how-various-annotation-frameworks-are-related/)
- DISRPT 2025 unified label set: 17 labels — ALTERNATION, ATTRIBUTION, CAUSE, COMMENT, CONCESSION, CONDITION, CONJUNCTION, CONTRAST, ELABORATION, EXPLANATION, FRAME, MODE, ORGANIZATION, PURPOSE, QUERY, REFORMULATION, TEMPORAL. — [Braud et al. 2025, DISRPT overview](https://aclanthology.org/2025.disrpt-1.1.pdf)
- The DISRPT mapping was set by five discourse experts from 306 distinct labels in the 2023 data; datasets contain 9–17 of the labels; it is "rather close to the ISO standard" (Bunt & Prasad 2016) with ATTRIBUTION, FRAME, COMMENT, ORGANIZATION added. — [Braud et al. 2025](https://aclanthology.org/2025.disrpt-1.1.pdf)
- DISRPT notes Attribution exists in RST corpora but is not a relation in PDTB, and dialogue Question-answer overlaps with PDTB-3 Hypophora; so some labels are absent from some frameworks by design. — [Braud et al. 2025](https://aclanthology.org/2025.disrpt-1.1.pdf)
- Stede et al. annotated the same 112 microtexts with argumentation, RST and SDRT layers on a shared segmentation, which makes cross-layer mapping computable. — [Stede et al. 2016, LREC](https://aclanthology.org/L16-1167.pdf)

### Inferences
- The team can design labels as a *hierarchy whose top level is CCR-like polarity*:
  `positive` → {`supports` (causal, epistemic), `explains` (causal, content), `example` (additive, specification), `restates` (additive, equivalence)} and `negative` → {`attacks`/`refutes`, `concedes`}.
  This lets every result be reported at two levels, and agreement at the coarse level will likely stay usable when fine labels disagree.
- Storing CCR features per edge (polarity, basic operation, order, source of coherence) rather than a single label makes later schema changes cheap: new labels are new feature combinations, old graphs can be re-labelled deterministically.
- The draft README labels map onto DISRPT-17 roughly as: `explains` ≈ EXPLANATION/CAUSE, `example` ≈ ELABORATION (PDTB Instantiation), `restates` ≈ REFORMULATION, `attacks` ≈ CONTRAST/CONCESSION, `supports` has no single discourse label (it is argumentative). This mapping is my inference, not from a source.
- A useful hedge-and-stance layer (Hyland) is better kept as a *node attribute*, not an edge type, since it is not relational. This is my suggestion; Hyland's taxonomy was not verified this session.

### Gaps
- PDTB-3 manual's exact L1/L2/L3 inventory (e.g. how many L2 senses, the new Hypophora and directional senses) was not fetched. Yung et al. use "14 Level-2 senses" for PDTB-3 classification experiments.
- GUM's coarse RST classes: **UNVERIFIED** — I believe GUM uses ~15 coarse classes (e.g. adversative, attribution, causal, context, contingency, elaboration, evaluation, explanation, joint, mode, organization, purpose, restatement, topic); check the GUM documentation.
- SDRT specifics (directed acyclic graphs with coordinating vs subordinating relations, right-frontier constraint) are background knowledge, not verified here. Stede et al. 2016 confirms an SDRT layer exists on microtexts.
- DISRPT 2023 label set size: one team paper reported 191 labels in 2023 *(snippet only)* while the overview says 306 distinct labels in 2023 data; the two numbers probably count differently, unresolved.
- Swales CARS / Teufel AZ and IAT were not checked in primary sources this session. They are genre-specific (research articles; dialogue) and seem less natural for 100–300-word Q&A answers.

## Q3. How does discourse structure relate to argument structure (Stede/Peldszus)?

### Takeaway
On the 112 microtexts, RST and argumentation agree on structure only partially: 60% of unlabeled edges are shared, the RST central nucleus matches the central claim in 85% of texts, and most rebuttals (72%) have no RST counterpart.
Discourse relations are a useful signal but not a substitute for an argument layer.

### Cited Findings
- "Ignoring the labels, 60% of the edges are common to both structures" (RST tree vs argumentation graph, same segmentation). — [Peldszus & Stede 2016, ArgMining workshop](https://aclanthology.org/W16-2812.pdf)
- Argumentative Support mostly corresponds to RST Reason or Justify, but 39% of Supports have no corresponding RST edge. — [Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)
- 72% of Rebuts and 33% of Undercuts have no corresponding RST edge. — [Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)
- The RST "strong nuclearity" segment equals the argumentative central claim in 95 of 112 texts (85%). Mismatches came from claims restated later (4 texts), implicit theses, Condition relations splitting the claim, and multinuclear relations triggered by coordinating conjunctions. — [Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)
- Of 261 Supports, 132 have an RST edge with a clearly compatible label (Reason, Justify, Evidence, Motivation, Cause); only 23% of texts contain only such "canonical" Supports. — [Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)
- 12 Supports correspond to "unexpected" RST labels (Elaboration, Background, Result, Interpretation, Antithesis, Concession, multinuclear), reflecting local coherence vs global argumentative function. — [Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)
- The authors note that "ARG analysis … encourages the annotator to abstract from linguistic realization", while RST decisions can follow surface cues like coordinating conjunctions. — [Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)
- Related positions: Azar (1999) treated five RST relations (Motivation, Antithesis, Concession, Evidence, Justify) as argumentative support; Green (2015) argued RST and argumentation are two levels that should be kept distinct; Kirschner et al. (2015) added RST-inspired Sequence and Detail to Support/Attack. — as summarized in [Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)
- A 2024 paper argues such RST–argument correlation analyses are biased by relying on a single RST annotation. *(snippet only)* — [arXiv 2401.11218](https://arxiv.org/pdf/2401.11218)

### Inferences
- A mixed edge set (argumentative `supports`/`attacks` plus discourse `explains`/`example`/`restates`) is defensible but should be framed as two layers: argument function and discourse relation.
  Annotators will otherwise conflate them, as the 39% unmatched Supports show.
- HC3 LLM answers often restate the thesis at the end; the microtext finding that restated theses cause central-claim disagreements predicts the same problem for HC3. A rule like "central claim = first full statement of the thesis; later paraphrase = `restates`" is needed.
- Attacks are the least recoverable from discourse structure, so the extractor needs explicit attack guidance; this matters because "fewer attacks in LLM text" is a likely hypothesis.

### Gaps
- Peldszus & Stede's quantitative results for predicting argumentation from RST features (tables in §5–6 of the paper) were not summarized in detail here.
- No study maps argumentation to RST on informal Q&A text; microtexts were written to a prompt by students and are tightly argumentative.

## Q4. Evidence on LLM performance on PDTB/RST/CCR classification, especially at coarse levels

### Takeaway
Zero/few-shot LLMs are weak on *implicit* fine-grained discourse senses (GPT-4: 36.84% accuracy on PDTB-3 Level-2) but much better at Level-1 (≈50%) and very good on *explicit* relations with in-context examples (ChatGPT 84.66% top-level accuracy).
Fine-tuned models still lead; DISRPT 2025 reports prompt-based LLMs underperforming fine-tuning.

### Cited Findings
- ChatGPT (gpt-3.5-turbo), PDTB-2 *explicit* relations (Ji test): top-level F1/Acc 34.94/39.38 (plain prompt), 69.26/70.21 (prompt engineering), 84.66/85.97 (in-context learning); second-level 60.68/63.47 with ICL; supervised SOTA top-level ≈95.6/96.7. — [Chan et al. 2023, arXiv 2304.14827](https://arxiv.org/pdf/2304.14827)
- ChatGPT, PDTB-2 *implicit* relations: top-level F1/Acc 36.11/44.18 with ICL (29.85/32.89 plain); second-level 16.20/24.54 with ICL; supervised SOTA 70.84/75.65 (top) and 49.03/64.58 (second). — [Chan et al. 2023](https://arxiv.org/pdf/2304.14827)
- ChatGPT sometimes answers "There doesn't appear to be a clear discourse relation" or defaults to Cause on implicit relations. — [Chan et al. 2023](https://arxiv.org/pdf/2304.14827)
- GPT-4, PDTB-3 implicit (Ji test), 14-way multiple-choice prompt: Level-1 (4-way) macro-F1 45.80, Acc 50.03; Level-2 (14-way) macro-F1 26.12, Acc 36.84. Supervised models: e.g. CP-KD Level-1 75.52/78.56, Level-2 52.16/67.84. — [Yung et al. 2024, arXiv 2402.04918](https://arxiv.org/pdf/2402.04918)
- "The inference accuracy hardly changes even with sophisticated prompt engineering"; per-class verification + MC reached 36.98% vs 36.84% for plain MC; two-step connective insertion prompting fell to 15.52%. — [Yung et al. 2024](https://arxiv.org/pdf/2402.04918)
- DISRPT 2025 Task 3 (17 unified labels, 38–39 corpora): best system DeDisCo (fine-tuned Qwen3-4B-derived model) mean accuracy 71.19 (reproduced; 71.28 in paper); English sets: PDTB 83.54, GUM-RST 76.50, RST-DT 73.09, STAC (SDRT) 77.04. — [Braud et al. 2025](https://aclanthology.org/2025.disrpt-1.1.pdf)
- In DISRPT 2025, CLaC's "prompt-based approaches underperformed compared to fine-tuning". — [Braud et al. 2025](https://aclanthology.org/2025.disrpt-1.1.pdf)
- Earlier repo report (not re-checked): prompted Claude Opus 4.0 "lagged significantly" behind fine-tuned models in DISRPT 2025. — [reports/Graph pipeline for HC3 arguments.md, citing DISRPT 2025 proceedings](https://aclanthology.org/2025.disrpt-1/)

### Inferences
- For the hackathon, a Claude extractor should be asked for a coarse label first (polarity / 4-way class) and a fine label second, with few-shot examples per label; both studies show coarse + examples is where LLMs are usable.
- Inter-sentence relations without connectives (implicit) are the weak spot. HC3 ChatGPT answers likely contain more explicit connectives ("However", "Additionally", "In conclusion") than human answers, so the extractor may be more accurate on LLM text. This is exactly the CLAUDE.md bias concern and must be measured separately per source with the hand labels.
- Published numbers are for GPT-3.5/GPT-4 on newswire; no published figures for current Claude models on PDTB/CCR levels were found.

### Gaps
- No LLM evaluation on CCR primitives (polarity, basic operation, etc.) was found in this session; if it exists it would be the best guide for a primitive-based schema.
- No LLM results on argument relation classification for microtexts were re-checked here (the earlier report cites FinArg GPT-4 86.9% macro-F1 from a snippet).
- No LLM results on IAT, argumentative zoning, or Hyland metadiscourse tagging were checked.
