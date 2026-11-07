# Approach study: findings

Date: 2026-11-07.
Plan: [PLAN.md](PLAN.md).
Numbers come from `analyze.py` (tables, bootstrap intervals) and `audit.py` (checks); raw scores are in [results/](results/).
Decision record: [docs/adr/0001-extraction-approach.md](../../docs/adr/0001-extraction-approach.md).

## Short answer

- **Accuracy:** all five Claude approaches are equally accurate on texts with hand-made graphs.
  They link about 4 in 5 pieces to the right parent (0.78–0.83), far above simple rules (0.47–0.65).
  No approach is measurably better than another.
- **Stability:** only one change clearly helps: label the fixed pieces 5 times and vote (approach V).
  Two runs of V share 0.89 of their edges, against 0.72 for one call (paired difference +0.17, 95% interval +0.11 to +0.23).
- **Cost:** voting costs about 3.5 times more ($0.17 vs $0.05 per HC3 answer).
  The whole study cost $13.82.
- **Recommendation:** split each answer once and save the split, then label it with 5 votes (V) for every text we measure.

## What was run

| Code | Approach | Calls per text |
|---|---|---|
| A | One pass with Opus: split, type and link in one call (the current extractor) | 1 |
| A-son | Same as A, with Sonnet 5.5 | 1 |
| S | Split once, then type and link the fixed pieces in one call | 1 + 1 |
| V | Split once, then type and link 5 times; majority type, best tree from the votes | 1 + 5 |
| P | Split once, then a type call, then a link call | 1 + 2 |
| B1 | No LLM: each piece points to the piece before it | 0 |
| B2 | No LLM: each piece points to the main claim | 0 |

Model `claude-opus-5-5` (except A-son), effort `high`, schemas `entity_definition.yaml` and `relation.yaml`, prompts `prompts/extract_v2.md`, `segment_v1.md`, `label_v1.md`, `type_v1.md`, `link_v1.md`.

Data:

- **arg-microtexts, 20 English texts** with hand-made graphs (Peldszus & Stede; about 5 pieces each), for accuracy.
  S, V, P and the baselines get the hand-made split; A and A-son split the text themselves.
- **HC3 finance, 10 pairs (20 answers)** picked with seed 2026, for stability, validity and cost.
  Every approach ran twice.
  There are no hand labels for HC3 yet, so HC3 gives no accuracy numbers.

## Accuracy on arg-microtexts

Pooled rates with 95% bootstrap intervals over the 20 texts.

| Approach | Main claim | Attachment | Labelled attachment | Opponent F1 | $/text |
|---|---|---|---|---|---|
| A | 0.95 [0.85–1.00] | 0.78 [0.69–0.87] | 0.78 [0.69–0.87] | 0.80 | 0.02 |
| A-son | 0.95 [0.85–1.00] | 0.78 [0.70–0.86] | 0.76 [0.67–0.84] | 0.75 | 0.01 |
| S | 0.95 [0.85–1.00] | 0.83 [0.73–0.91] | 0.83 [0.73–0.91] | 0.80 | 0.02 |
| V | 0.95 [0.85–1.00] | 0.83 [0.73–0.91] | 0.83 [0.73–0.91] | 0.80 | 0.07 |
| P | 0.95 [0.85–1.00] | 0.83 [0.74–0.91] | 0.83 [0.74–0.91] | 0.82 | 0.02 |
| B1 | 0.95* | 0.47 [0.39–0.54] | 0.20 [0.14–0.28] | – | 0 |
| B2 | 0.95* | 0.65 [0.55–0.75] | 0.47 [0.38–0.55] | – | 0 |

\* Baselines use the main claim chosen by S.

- *Attachment* = share of pieces whose primary parent matches the hand-made graph.
  *Labelled* also needs the same direction (support or attack).
- B1 scores 0.47; Peldszus & Stede (2015) report 0.45 for the same rule on the same corpus, which is a check that our scoring matches theirs.
- Paired differences (per text, 95% bootstrap): S − A +0.05 (−0.01 to +0.11); V − S 0.00; P − S 0.00 (−0.04 to +0.04); A − A-son 0.00 (−0.08 to +0.08); S − B2 +0.18 (+0.05 to +0.31).
  Only the gap to the baseline is clear.

## Stability on HC3 (two runs of each approach, 20 answers)

| Approach | Valid runs | Same main claim | Same type (κ) | Same parent | Edge overlap (Jaccard) | $/answer | Pieces | Edges |
|---|---|---|---|---|---|---|---|---|
| A | 40/40 | 1.00 | 0.89 | 0.92 [0.87–0.95] | 0.71 [0.64–0.79] | 0.04 | 11.7 | 11.2 |
| A-son | 40/40 | 0.95 | 0.91 | 0.86 [0.79–0.92] | 0.69 [0.57–0.80] | 0.01 | 10.3 | 9.6 |
| S | 40/40 | 0.95 | 0.91 | 0.94 [0.89–0.97] | 0.72 [0.66–0.79] | 0.05 | 12.3 | 12.0 |
| V | 40/40 | 1.00 | 0.95 | 0.97 [0.95–0.99] | 0.89 [0.83–0.94] | 0.17 | 12.3 | 11.9 |
| P | 38/40 | 0.95 | 0.95 | 0.91 [0.88–0.95] | 0.79 [0.73–0.85] | 0.05 | 12.3 | 12.3 |

Costs for S, V and P include their share of the split call.

Paired differences in edge overlap: V − S +0.17 (+0.11 to +0.23); P − S +0.07 (−0.01 to +0.15); S − A +0.01 (−0.06 to +0.08); A − A-son +0.03 (−0.12 to +0.17).
Same parent: V − S +0.04 (+0.02 to +0.06).
Only voting is a clear gain.

By source (edge overlap):

| Approach | Human answers | ChatGPT answers |
|---|---|---|
| A | 0.70 | 0.72 |
| A-son | 0.56 | 0.81 |
| S | 0.66 | 0.78 |
| V | 0.85 | 0.93 |
| P | 0.73 | 0.86 |

Every approach is less stable on human answers than on ChatGPT answers.

## Audit

- **Main claim.** All five approaches miss the same one text (`micro_b016`).
  It has two "therefore" conclusions; the model picks the one the annotators did not.
  This is a hard case, not a scoring error.
- **Splitting is a confound for A.**
  On microtexts, A's own split had the same number of pieces as the hand-made one in 12 of 20 texts (A-son: 8 of 20).
  So part of A's lower attachment (0.78 vs 0.83) comes from splitting, not linking; the paired difference is not clear either way.
  On HC3, A split identically in both runs for 16 of 20 answers (A-son: 14 of 20), while S, V and P reuse one saved split by design.
  Their higher stability includes the benefit of freezing the split, which is part of the approach, not a measurement trick.
- **Invalid runs.** P failed validation on one human answer in both runs: the type step made a piece a `claim` that the link step then left without an edge, and the retry did not fix it.
  These 2 runs stay in all denominators.
- **Voting.** No chosen tree edge lacked votes (0 of all primary edges); all 300 voting samples were valid.
- **Retries.** A-son needed a retry 6 times; P twice; A, S and V never.
- **Three examples read** (the HC3 answers where S was least stable, `examples.py`).
  In all three, the two S runs disagree on real ambiguities, not on parsing:
  list items labelled `supports` in one run and `elaborates` in the other, and a different sentence chosen as the main conclusion.
  Between its two runs, S differed in 10, 7 and 6 edges on these answers; V differed in 0, 4 and 2.

## What this means

1. **Fix the split once.**
   Splitting differs between runs in about 1 in 5 answers, and it changes graph size: one pass with Sonnet gives 10.3 pieces per answer, Opus 11.7, the separate split step 12.3.
   Graph size is one of our measures, so all texts must use the same split method.
2. **Vote on labels and links.**
   It does not raise accuracy, but it removes most run-to-run noise; noise would blur any human-vs-ChatGPT difference.
3. **Report fairness.**
   The extractor is less stable on human text in every approach.
   Results must show human and ChatGPT texts separately, as `CLAUDE.md` asks.
4. **The step-by-step pipeline (P) adds nothing** here: same accuracy, middling stability, and the only invalid graphs.
5. **Sonnet is as accurate as Opus in one pass** on microtexts, at a third of the cost, but it splits less consistently.
   It could be tried for the label step of V; this study did not test that.

## Limits

- 20 texts per dataset; intervals are wide.
- Microtexts are short (5 pieces), not about finance, and not answers to a question; HC3 answers are about 12 pieces.
- No HC3 accuracy yet: that needs hand labels (Task 7).
- Microtext relations were mapped to two families (support, attack); our finer relation types were not scored.
- One effort level (`high`), one prompt wording per approach, Opus for the split.

## Reproduce

```
uv run --no-project --python 3.13 --with anthropic,pyyaml,networkx python experiments/approach_study/run_study.py --budget 60
uv run --no-project --python 3.13 --with pyyaml python experiments/approach_study/analyze.py
uv run --no-project --python 3.13 --with pyyaml python experiments/approach_study/audit.py
```

It needs `data/external/argmicro_en_sample20.jsonl`, built by `prepare_microtexts.py` from the arg-microtexts repository (CC BY-NC-SA 4.0, local only).
The study ran on Python 3.13 because `networkx` did not import on Python 3.14.1; Python 3.14.10 fixes that, so plain `uv run` also works there.
