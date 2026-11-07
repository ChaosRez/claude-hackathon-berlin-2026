# Evolvable schema and tooling for LLM extraction of reasoning units and relations

Scope: HC3 answers (~100–300 words), one sentence = one node, Claude extractor, Python validator, hand labels in `annotations/`, prompts in `prompts/`.
Builds on Step 3 of `reports/Graph pipeline for HC3 arguments.md` (Pydantic + Claude structured output or `instructor` + validator; 2–3 roles; `supports`/`attacks`/`explains`/`example`/`restates`/`none`).
Repo check (2026-11-07): `GUIDE.md`, `prompts/` and `annotations/` do not exist yet, so nothing below conflicts with an existing schema.
Researched 2026-11-07, about 15 tool calls.

## Schema design patterns for evolution

### Takeaway
Make the schema a single data file with a small, stable coarse layer (what all comparisons use) and an optional fine layer (`coarse.fine`, PDTB-style), plus an `other` value with a free-text note to discover new types.
Version it, and keep a mapping table from every fine label and every old version to the current coarse labels, so old graphs are projected rather than re-labelled.

### Cited Findings
- PDTB 3.0 uses 36 sense labels in a three-level hierarchy, which makes LLM classification "particularly challenging" compared with typical text classification — [Prompting Implicit Discourse Relation Annotation, arXiv 2402.04918](https://ar5iv.labs.arxiv.org/html/2402.04918).
- That hierarchy lets studies report results at both the 4 top-level and ~20 second-level senses of the same annotations (e.g., a 2025 CODI paper evaluating LLMs at both levels) — [search snippet of CODI 2025 paper](https://preview.aclanthology.org/ingest-emnlp/2025.codi-1.13.pdf) (PDF returned 404 when fetched; numbers not verified).
- Flat, unstructured label lists become more problematic for zero-shot LLM classification as the label set grows; the authors propose shrinking the label space first — [Label Space Reduction, arXiv 2502.08436](https://arxiv.org/html/2502.08436v2).
- Zero-shot prompting with a large, structured label space performs poorly in hierarchical classification — [TELEClass, arXiv 2403.00165](https://arxiv.org/html/2403.00165v2).
- In the microtexts scheme, support is 55.2% of relations, rebut 21.6%, undercut 12.8%, example 1.8% — so fine attack/example subtypes will be sparse — [DFKI-SLT/argmicro README](https://huggingface.co/datasets/DFKI-SLT/argmicro/blob/refs%2Fpr%2F1/README.md) (via earlier report).
- Middle-level "claim" role had the weakest agreement in Stab & Gurevych (αU .524) vs major claim .810 and premise .824 — [arXiv 1604.07370](https://arxiv.org/pdf/1604.07370) (via earlier report).
- Claude structured outputs do not support recursive schemas, `minLength`/`maxLength`, numeric `minimum`/`maximum`, or array `minItems` beyond 0/1; enums must be primitive values; at most 24 optional parameters and 16 union-type parameters across schemas; enum casing is not guaranteed, so compare case-insensitively — [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
- Changing schema structure invalidates the compiled-grammar cache (24 h); changing only `name`/`description` does not — [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

### Inferences
- **Coarse + fine (hierarchical labels).** Store relations as `kind.subtype`, e.g. `attacks.rebut`, `attacks.undercut`, `supports.reason`, `supports.example`, `elaborates.restates`.
  All headline comparisons and gold checks use the part before the dot.
  Adding, splitting or merging subtypes then never breaks results, because the coarse label of every old edge is still defined.
- **Mapping the user's intuition onto this.** "Argument", "Claim", "Reason", "Refutation" mix two dimensions.
  Claim is a node *role*; Reason and Refutation are *edge kinds* (support vs attack); "Argument" is a subgraph (a claim plus its reasons), not a node label.
  Suggest: roles `main_claim | claim | other | filler`; edges `supports | attacks | elaborates | none` with optional subtypes.
  This is a suggestion for `GUIDE.md`; per CLAUDE.md the team decides.
- **Decomposed features.** Optionally store per-edge dimensions instead of (or alongside) a flat label: `polarity: + | − | 0`, `function: evidence | example | restate | concede | other`.
  Flat labels can be derived deterministically, and new flat labels become new combinations rather than new columns.
  Keep this to 2 dimensions in the hackathon; more dimensions = more agreement problems.
- **Discovery slot.** Allow `other` in each enum plus `note: str` (short).
  Count `other` uses per version; when one recurring note hits a threshold (e.g., ≥5% of edges), propose a new subtype to the team.
  Never promote it to a coarse type without a team decision.
- **Schema-as-data.** One `schema/schema_vX.Y.yaml` holds: roles, coarse relations, subtypes with parent, one-line definitions, decision rules, and `maps_from` entries for older versions.
  A small Python script generates (a) the Pydantic model / JSON schema with `Literal` enums, (b) the label section of the prompt, (c) validator lists, (d) the annotation-tool config (e.g., Label Studio XML).
  This removes drift between guide, prompt and validator.
  Because Claude structured outputs reject recursion and length constraints, keep the output flat (a list of per-sentence objects), and enforce "exactly one main claim", tree/DAG and parent-index range in Python.
- **Versioning.** Semantic-version style: MAJOR = coarse layer changes (comparisons break; requires re-projection or re-labelling); MINOR = subtype added or definitions tightened (old data still valid at coarse level); PATCH = wording/examples only.
  Store `schema_version` and `prompt_version` in every graph JSON and every annotation file.
- **Mapping tables.** `mappings/vA_to_vB.csv` with `old_label,new_label,lossless(bool)`.
  Many-to-one merges are lossless projections; one-to-many splits are not, so split labels need re-annotation of only the affected edges (filter by old label), not all texts.

### Gaps
- No study found that tests "hierarchical vs flat" label prompting for argument relations specifically.
- CODI 2025 coarse vs fine PDTB numbers could not be read (404); level-by-level LLM numbers unverified.

## LLM extraction practicalities

### Takeaway
Use Claude structured outputs (`output_config.format` with a JSON schema, now stable, no beta header) or `instructor`; send numbered sentences; get one object per sentence with role, parent index, relation, short rationale.
Run 3 times via the Batch API; total cost for 800 texts × 3 runs is tens of dollars on Sonnet/Opus and ~$1–2 on Haiku.

### Cited Findings
- Structured outputs are `stable`; schema goes in `output_config.format` with `type: "json_schema"`; strict tool use is `strict: true` on a tool; the old `output_format` parameter is deprecated and needs beta header `structured-outputs-2025-11-13` — [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
- Python SDK: `client.messages.parse(output_format=PydanticModel)` returns `parsed_output`; `transform_schema()` shows the transformed schema; helpers move unsupported constraints into field descriptions and validate against the original schema — [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
- Supported models include claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5, claude-haiku-4-5 and Opus/Sonnet 4.5+ — [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
- Caveats: `stop_reason: "refusal"` is billed and may not match the schema; asking for step-by-step reasoning inside a property can trigger a `reasoning_extraction` refusal, so ask for a short explanation instead; `max_tokens` cut-offs give invalid output; required properties are emitted before optional ones regardless of schema order — [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
- Batch API gives 50% off input and output. Batch prices per MTok (in/out): Opus 5.5 $2/$10, Sonnet 5.5 $1/$5, Haiku 5.5 $0.05/$0.25 (prompts ≤100k tokens); standard Sonnet 5.5 is $2/$10, cache hits $0.10 — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- `instructor`: MIT, ~14.1k stars, pushed 2026-11-06, latest release v1.17.0 (2026-09-09); README shows `instructor.from_provider("anthropic/claude-sonnet-5")` — [GitHub 567-labs/instructor](https://github.com/567-labs/instructor) (checked with `gh api`).
- Few-shot task context was the most effective prompt enrichment for LLM argument relation classification — [C4AI repo](https://github.com/C4AI/llm_component_relation_classification) (via earlier report).
- Open-weight LLMs on argument-quality annotation were stable across runs (<7.75% of cases changed label); authors recommend majority vote and few-shot for large models — [arXiv 2404.09696](https://arxiv.org/abs/2404.09696v1) (from search summary; not fetched).
- Majority vote, Dawid-Skene and MACE gave near-identical consensus labels in an emotion task; main error was shared bias, and high inter-LLM agreement did not replace human validation — [ACL CAS 2026](https://aclanthology.org/2026.cas-1.11/) (search summary only).
- Plain majority voting assumes a discrete label set and does not directly apply to structured outputs like graphs — [arXiv 2601.16800](https://www.alphaxiv.org/abs/2601.16800) (search summary only).

### Inferences
- **Cost (deterministic calc, `python3`).** Assumed 4,000 input tokens (guide + 2 few-shot examples + text) and 1,500 output tokens per call, 800 texts × 3 runs = 2,400 calls: Opus 5.5 batch ≈ $55, Sonnet 5.5 batch ≈ $28, Haiku 5.5 batch ≈ $1.4, Sonnet 5.5 standard ≈ $55.
  Token counts are assumptions; prompt caching of the guide would lower input cost further.
  Cost is not a constraint; pick the model by gold-set accuracy.
- **Output shape** (flat, fits structured-output limits):
  `{"schema_version": "...", "nodes": [{"i": 3, "role": "claim", "parent": 1, "relation": "supports", "subtype": "reason", "note": "", "rationale": "≤20 words", "confidence": "high|med|low"}]}`.
  Use `parent: 0` or `-1` for root, and check range in Python (numeric `minimum`/`maximum` are not allowed in the schema).
  Put `rationale` before label fields only if required-ordering allows; the docs say required properties come first, so make rationale required too.
- **Prompt input.** Pre-split sentences in Python (the agreed chunker), number them `[1] … [n]`, and give the model no freedom to re-segment; validator checks `len(nodes) == n` and indices `1..n` exactly once.
- **Self-consistency for graphs.** Vote per sentence: majority role, majority (parent, relation) pair; report run-to-run agreement per side (human vs ChatGPT texts).
  Agreement is a stability measure, not validity; still compare to gold.
- **Confidence.** Verbal confidence is cheap but uncalibrated; prefer disagreement across 3 runs as the uncertainty signal (inference; no source checked on calibration).
- **instructor vs native.** Native `messages.parse` now covers the main need (Pydantic in, parsed object out) with no extra dependency; `instructor` adds automatic retry with validation-error feedback, useful if Python-side graph checks should trigger a re-ask.

### Gaps
- Could not verify whether Batch API and structured outputs combine without restrictions (the docs' "Feature compatibility" section was truncated; the summary says batch is listed as compatible).
- No published number for Claude 5.x on sentence-level argument relations; must be measured on the gold set.

## Annotation tools for the gold set

### Takeaway
For a one-day hackathon, the fastest path is a spreadsheet/JSON per text (one row per sentence: `i, text, role, parent, relation, subtype, note`), generated from the schema file.
If a GUI is wanted, Label Studio (Apache-2.0, very active) with `Paragraphs` + `ParagraphLabels` per sentence and `Relations` is the quickest to stand up; INCEpTION is more powerful (relation layers, agreement, curation) but slower to configure.

### Cited Findings
- Label Studio: Apache-2.0, ~28.6k stars, pushed 2026-11-06, release 1.23.2 (2026-09-29) — [GitHub HumanSignal/label-studio](https://github.com/HumanSignal/label-studio) (`gh api`).
- Label Studio `Relations` tag creates relations between labelled regions, typed via `<Relation value="..."/>` children, `choice="single|multiple"`; the page does not state directionality or how label changes after annotation are handled — [Label Studio docs: Relations](https://labelstud.io/tags/relations).
- Label Studio has `Paragraphs` with `ParagraphLabels` (e.g., dialogue layout), which fits sentence-as-unit labelling — [Label Studio repo docs/tags/paragraphs.md](https://github.com/HumanSignal/label-studio/blob/develop/docs/source/tags/paragraphs.md) (`gh api`).
- INCEpTION: Apache-2.0, repo now `eclipse-inception/inception`, pushed 2026-11-05, release inception-42.2 (2026-10-27) — [GitHub inception-project/inception](https://github.com/inception-project/inception) (`gh api`). Its user guide URL returned 404, so feature claims (relation layers, agreement, LLM recommenders) are unverified here.
- doccano: MIT, ~10.8k stars, last push 2026-04-14, release v1.8.5 (2026-01-11) — [GitHub doccano/doccano](https://github.com/doccano/doccano) (`gh api`); slowing activity.
- Argilla: Apache-2.0, pushed 2026-11-02, latest release v2.8.0 (2025-03-11) — [GitHub argilla-io/argilla](https://github.com/argilla-io/argilla) (`gh api`); only a closed "Relation Extraction Task" issue found on relations — [issue #1839](https://github.com/argilla-io/argilla/issues/1839). Span-to-span relations appear unsupported (unverified).
- brat: no SPDX license detected by GitHub, last push 2024-07-03 — [GitHub nlplab/brat](https://github.com/nlplab/brat) (`gh api`); effectively unmaintained.
- OVA3 (arg-tech): online at ova.arg.tech, natively AIF, collaborative; released Dec 2022; code said to be CC-BY-SA — [arg.tech OVA3 release](https://www.arg.tech/?p=2678); repo last push 2025-05-22, 14 stars, no license detected by GitHub — [GitHub arg-tech/OVA3](https://github.com/arg-tech/OVA3) (`gh api`).

### Inferences
- Because nodes are fixed sentences, no span selection is needed; a table with a dropdown per column captures everything and is trivially regenerated when the schema changes (new dropdown values from the YAML).
  It also maps 1:1 to the extractor's JSON, so agreement code is shared.
- Label Studio is worth it only if visual arrows help annotators; the XML config can be generated from the schema YAML.
- OVA3 is argument-native (AIF, rebut/undercut), but uses its own segmentation and export format; converting to the team's per-sentence JSON costs time. Not recommended for a hackathon.
- Store gold as JSON with `schema_version`; on a MINOR change, project old gold to coarse labels via the mapping table; only edges whose old label was split need re-checking.

### Gaps
- Did not verify INCEpTION features (docs 404) or how Label Studio handles renamed labels on existing annotations.

## Evidence: coarse vs fine schemas, and pre-annotation bias

### Takeaway
Indirect evidence says LLMs do worse as label sets grow and become fine-grained, so headline results should use the coarse layer.
Pre-annotation causes humans to adopt model labels; since the gold set judges the extractor, label gold without seeing LLM output.

### Cited Findings
- Zero-shot ChatGPT on implicit PDTB 2.0 relations was reported at under 20% accuracy (e.g., 24.54% acc / 16.20% F1 in another report), far below supervised models; sophisticated prompting barely helped in 14-way experiments — [arXiv 2402.04918](https://ar5iv.labs.arxiv.org/html/2402.04918) (via search summary).
- Explicit connectives make relation classification close to 95% accurate — [search summary citing arXiv 2311.00451](https://arxiv.org/pdf/2311.00451) (not verified in full text).
- GoLLIE sometimes defaults to broader categories despite fine-grained guidelines — [alphaXiv summary of arXiv 2310.03668](https://alphaxiv.org/overview/2310.03668v5) (secondary).
- Crowdworker study (>7,000 annotations, 410 workers): LLM suggestions did not speed annotation but raised confidence and led to substantial uptake of model labels — [chatpaper summary](https://chatpaper.com/paper/178676) (secondary; primary paper not identified).
- Expert topic annotation with LLM suggestions was faster but showed anchoring: annotators heavily agreed with the LLM — [summary of arXiv 2410.04699 (EMNLP 2024)](https://deep-paper.org/en/paper/2410.04699) (secondary).
- Annotators biased toward parser pre-annotations inflated parser accuracy estimates (EMNLP 2016) — [Liner summary](https://liner.com/review/anchoring-and-agreement-in-syntactic-annotations) (secondary).
- Two-round study: reviewing LLM pre-annotations led to convergence of annotations and erosion of human subjectivity — [ACL Anthology listing (Francis, Leuzinger et al.)](https://aclanthology.org/people/celine-leuzinger/unverified/) (abstract only).
- "Bias in the Loop" (2,784 participants): requiring a correction to flag an error reduced corrections and increased acceptance of wrong suggestions; pro-AI attitudes predicted more undercorrection; errors needing knowledge of annotation rules were caught only 31% of the time vs ~82% for spelling errors; first-three-items correctness had no effect — [arXiv 2509.08514](https://arxiv.org/html/2509.08514v1).

### Inferences
- The 31% catch rate for rule-dependent errors is the relevant one: argument-relation errors are rule-dependent, so humans correcting Claude's graphs would miss most errors and inflate measured extractor accuracy.
- Rule: gold labels in `annotations/` are made blind to LLM output. LLM pre-annotation may be used only for non-gold bulk data or for speeding up adjudication after blind double labelling.
- Report extractor accuracy at the coarse level as primary; fine-level as exploratory, each next to the human-human baseline at the same level.

### Gaps
- No direct study of coarse vs fine accuracy for LLM argument-relation labels; the team should measure both levels on the gold set.
- Primary papers for the crowdworker and EMNLP 2024 anchoring studies were not read.

## Recommended minimal end-to-end design

### Takeaway
One YAML schema → generated Pydantic model, prompt label block, validator enums, annotation template; every artifact stamped with schema and prompt version; comparisons only at the coarse layer via mapping tables; re-run the LLM (cheap) on every change, re-label humans only for split labels.

### Cited Findings
- Structured-output limits that force the flat design (no recursion, no length/number constraints, ≤24 optional params) — [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
- Batch pricing that makes full re-runs cheap — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing).

### Inferences
- **Files.**
  - `schema/schema_v1.0.yaml` — roles, coarse relations, subtypes (`parent:`), definitions, decision rules, `other` allowed, `maps_from:` older versions.
  - `schema/build.py` — emits `schema/generated/models_v1_0.py` (Pydantic), `prompts/labels_v1_0.md`, `annotations/template.csv`, optional Label Studio XML.
  - `prompts/extract_vN.md` — guide text + `{labels}` + 2 few-shot examples (one human, one ChatGPT); new file per change (CLAUDE.md rule).
  - `mappings/v1.0_to_v1.1.csv` — `old,new,lossless`.
  - `graphs/{model}/{prompt_v}/{schema_v}/{text_id}_run{k}.json` and `annotations/{annotator}/{text_id}.json` both carrying `schema_version`, `prompt_version`.
  - `validate.py` — sentence coverage, enum membership (case-insensitive), parent range, no self-loop, one main claim, acyclic; writes a failure count per side.
- **Example YAML sketch.**
  ```yaml
  version: 1.1.0
  roles: [main_claim, claim, other, filler]
  relations:
    supports:   {subtypes: [reason, example, evidence, other]}
    attacks:    {subtypes: [rebut, undercut, concede, other]}
    elaborates: {subtypes: [restates, explains, other]}
    none:       {subtypes: []}
  maps_from:
    "1.0.0": {explains: elaborates.explains, example: supports.example, restates: elaborates.restates}
  ```
  (Illustrative only; labels must come from the team's `GUIDE.md`.)
- **Re-run policy.**
  - PATCH: re-run LLM only if prompt text changed; no human work.
  - MINOR (subtype added/merged): re-run LLM on everything; project gold via mapping; human re-check only edges with split labels.
  - MAJOR (coarse layer changed): re-run LLM; re-label gold for affected labels; old results are not comparable — mark them by version, never mix.
  - Every change: re-run the gold-set check separately for human and ChatGPT texts, plus 3-run stability.
- **Comparisons** read only `role` and coarse `relation` after projection to the current version, matching the CLAUDE.md rule of roles and edge types only.

### Gaps
- The design is a synthesis; no single published system implements exactly this for argument graphs (none found).
