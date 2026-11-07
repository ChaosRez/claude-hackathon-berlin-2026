# Approach study: which extraction method is better?

Status: done (2026-11-07). Results in [FINDINGS.md](FINDINGS.md); decision in [ADR 0001](../../docs/adr/0001-extraction-approach.md).
Evidence chain: Claim → Plan (this file) → Audit → Findings (`FINDINGS.md`).

## Claim to test

Different ways of asking Claude for a reasoning graph give graphs of different quality.
"Better" means three things, in this order:

1. **Accurate**: the graph matches graphs made by people.
2. **Stable**: running the same method twice gives the same graph.
3. **Valid and cheap**: the graph passes `src/validate.py`, at a low cost per text.

## Approaches compared

All use `entity_definition.yaml` and `relation.yaml`, model `claude-opus-5-5`, effort `high`, unless noted.

| Code | Approach | Calls per text |
|---|---|---|
| A | One pass: split, type and link in one call (`prompts/extract_v2.md`, the current extractor). | 1 |
| A-son | Same as A, with `claude-sonnet-5-5` (cheaper model). | 1 |
| S | Two stages: split once, then type and link the fixed pieces in one call. | 1 + 1 |
| V | Two stages with voting: split once, then type and link 5 times; Python takes the majority type and picks the best tree from the votes (maximum spanning arborescence). | 1 + 5 |
| P | Step by step: split, then type, then link (three separate calls). | 1 + 2 |
| B1 | Baseline, no LLM: each piece points to the piece before it. | 0 |
| B2 | Baseline, no LLM: each piece points to the main claim. | 0 |

The split (stage 1) is made once per text and shared by S, V and P, so their differences come only from typing and linking.
Baselines use the shared split, and the main claim chosen by S.

## Data

1. **HC3 finance, 10 pairs (20 texts)**, chosen with a fixed random seed (`seed=2026`) from `data/finance-filtered.jsonl`.
   This is the 10-pair limit from `CLAUDE.md` while `GUIDE.md` is a draft.
   There are no hand labels yet, so HC3 measures stability, validity and cost, not accuracy.
2. **arg-microtexts (English), 20 texts**, a public set of short argument texts with hand-made graphs (Peldszus & Stede).
   Used as the accuracy check.
   License CC BY-NC-SA 4.0: kept local in `data/external/` (git-ignored), never committed; only our scores are published.
   Its pieces (ADUs) are given, so S, V, P and baselines use the gold split; A splits on its own and is matched by text overlap.

## Measures

Computed by deterministic scripts (`analyze.py`), never by hand.

- **Accuracy (microtexts)**: main claim correct; attachment accuracy (each piece's primary parent correct); labelled attachment (parent and support-vs-attack correct).
  Gold relations are mapped to ours: `sup`, `exa` → support; `reb`, `und` → attack; `add` → same parent as its partner; an undercut points to the source of the edge it attacks.
- **Stability (HC3)**: each approach runs twice.
  Main-claim agreement, type agreement (Cohen's κ), attachment agreement, edge overlap (Jaccard).
  A uses its own split each time, so its stability includes splitting; pieces are matched by text.
- **Validity**: share of texts valid under `src/validate.py`; invalid and errored texts stay in every denominator.
- **Cost**: tokens and dollars per text.
- Every HC3 result is shown separately for human and ChatGPT texts.

## Budget and limits

- Cap: $60 of API spend for the whole study; the harness stops when it is reached.
- At most 10 HC3 pairs.
- No HC3 accuracy claim without hand labels; this is stated on every slide that shows HC3 numbers.

## Audit before findings

- Read 3 real example graphs for the biggest difference found, and check it is not a parsing or matching error.
- Re-run `src/validate.py` and `src/measure.py` on all outputs.

## Output

- `FINDINGS.md`: results tables and conclusions.
- A slide presentation (claude.ai artifact) that says which approach is better and why.
- Open questions go to the Plannotator Inbox.
