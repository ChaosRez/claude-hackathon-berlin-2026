# ADR 0001: Extract graphs by splitting once and voting on the labels

- **Status:** Accepted (2026-11-07).
- **Deciders:** the team, on the evidence below.
- **Slides:** https://claude.ai/artifact/H1ZsqFXDRduTyYT8QHYAKf (sources in [docs/presentation/approach-study/](../presentation/approach-study/)).
- **Evidence:** [experiments/approach_study/FINDINGS.md](../../experiments/approach_study/FINDINGS.md) (study), [reports/SOTA argument extraction.md](../../reports/SOTA%20argument%20extraction.md) (literature).

## Context

We turn each HC3 answer into a reasoning graph, then compare graph shapes between human and ChatGPT answers.
The extractor is an LLM, so its graphs carry two kinds of error:

- **Wrong graphs:** a piece gets the wrong type or the wrong parent.
- **Noisy graphs:** running the extractor twice on the same answer gives different graphs.

Noise matters as much as error here.
If two runs of the same answer differ, a small human-vs-ChatGPT difference can be noise.
Graph size is also one of our measures, so the way an answer is split into pieces must not change between texts or runs.

The literature has no single best method.
Trees with one parent per piece are the usual shape for short arguments, which matches the `primary` edges in `relation.yaml`.
For prompted LLMs, fixing the pieces first helps linking, and the classic way to get stable trees is to score parent choices and then pick the best tree in code.

## Options compared

All options use `entity_definition.yaml`, `relation.yaml`, `claude-opus-5-5` and effort `high`, unless noted.

| Option | What it does |
|---|---|
| A. One pass | One call splits, types and links (the extractor before this ADR). |
| A-son. One pass, Sonnet | The same with `claude-sonnet-5-5`. |
| S. Split, then label | One call splits; one call types and links the fixed pieces. |
| **V. Split, then vote** | One call splits; 5 calls type and link the fixed pieces; code keeps the majority type and the parent tree with the most votes. |
| P. Step by step | One call splits, one types, one links. |

We tested them on 20 arg-microtexts with hand-made graphs (accuracy) and on 20 HC3 answers run twice (stability, validity, cost).

## Decision

**Use V: split each answer once, save the split, label the fixed pieces 5 times, and combine the votes.**

- The split is saved in each graph file and reused; nothing is split twice.
- Each piece takes its majority type; the main claim is the majority choice.
- The primary edges are the tree with the most parent votes (a maximum spanning arborescence rooted at the main claim; `src/voting.py`).
- Extra, non-primary edges are kept when most samples drew them.
- Each graph file records how many samples agreed on each parent (`diagnostics.parent_share`), as a per-piece confidence.

`uv run python -m src.extract` now uses V by default; `--approach one-pass` keeps option A for comparison.

## Why

| | One call (S) | Votes (V) | Difference V − S (95% interval) |
|---|---|---|---|
| Right parent, microtexts | 0.83 | 0.83 | 0.00 |
| Same edges in two runs, HC3 | 0.72 | 0.89 | +0.17 (+0.11 to +0.23) |
| Same parent in two runs, HC3 | 0.94 | 0.97 | +0.04 (+0.02 to +0.06) |
| Cost per HC3 answer | $0.05 | $0.17 | ×3.5 |

- **Accuracy is the same for every option** (0.78–0.83 right parents; no paired difference is clear), and all are far above simple rules (0.47–0.65).
  So accuracy does not decide.
- **V is the only option that is clearly more stable.**
  The noise it removes is real ambiguity, mostly `supports` vs `elaborates` and which sentence is the main conclusion, not parsing errors.
- **Splitting once removes another source of noise.**
  One-pass extraction re-split 4 of 20 answers differently between runs, and the split changes graph size (10.3 to 12.3 pieces per answer across options).
- **Step by step (P) adds nothing** and produced the only invalid graphs.
- The cost is acceptable: about $34 for all 100 pairs (200 answers).

## Consequences

- Every graph measure must come from V graphs, all made with the same prompts (`prompts/segment_v1.md`, `prompts/label_v1.md`) and settings; mixing in one-pass graphs would mix graph sizes.
- The saved split can be shown to people who hand-label texts (Task 7), so people and extractor label the same pieces.
- A run costs about 3.5 times more and takes longer than one call per answer.
- Every approach is less stable on human answers than on ChatGPT answers (V: 0.85 vs 0.93 edge overlap).
  Results must be reported per source, as `CLAUDE.md` already asks.
- The extractor still needs a hand check on HC3 (Task 7) before any human-vs-ChatGPT claim; this ADR does not settle accuracy on HC3.

## Open questions

- `relation.yaml`: should list items be `elaborates` and never `supports`?
  Most disagreement between single runs is between these two relations.
- Is Sonnet good enough for the 5 label calls?
  It matched Opus in one-pass accuracy at about a third of the cost, but this study did not test it inside V.
- Revisit this decision when HC3 hand labels exist, or when `GUIDE.md` is marked final.
