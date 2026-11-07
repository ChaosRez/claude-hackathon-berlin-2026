# Research Journal

Append-only ledger of research hypotheses, decisions, experiment runs, and evidence audits.

## Template Entry Format

### Entry [Number] — [YYYY-MM-DDTHH:MM:SSZ]
- **Hypothesis / Question**: What open scientific question or problem is being addressed?
- **Action / Experiment**: What was run, changed, or analyzed?
- **Evidence**: Links to data artifacts, log files, or code outputs.
- **Findings & Honesty**: What succeeded, what failed, where the agent got stuck, and confidence level.
- **Next Steps**: What the loop needs next.


### Entry 1 — 2026-11-07T15:07:06Z
- **Hypothesis / Question**: Can the extractor turn an answer into entities and relations that follow `entity_definition.yaml` (v0.1, draft) and `relation_definition.yaml` (v0.1, draft)?
- **Action / Experiment**: Built `src/extract.py`, `src/validate.py`, `src/schema.py`, `src/build_graph.py` and prompt `prompts/extract_v1.md`.
  Ran `uv run python -m src.extract --limit 2` (pairs 0 and 1, human and ChatGPT, 4 texts), model `claude-opus-5-5`, effort `high`, API backend.
  This is a smoke test only: `GUIDE.md` is still a draft, so the extractor caps runs at 10 pairs.
- **Evidence**: `results/extraction/20261107T150706Z/` (`run.json`, `graphs/`, `entities.csv`, `relations.csv`).
- **Findings & Honesty**: 4 of 4 texts valid on the first attempt, 0 invalid, 0 errored.
  An earlier run of the same 4 texts errored 4 of 4 because of a bug in my result handling (`_request_id` missing on streamed responses), not the model; the bug was fixed and that run's folder deleted.
  "Valid" only means the rules are met (coverage, one main claim, allowed types, edge counts); no hand check against `annotations/` yet, so accuracy is unknown.
  Observed: `background` and `caveat` nodes often have no edge (allowed by `edge_optional`), so some graphs are forests, not trees.
  `finance_0000_chatgpt` labels "the ticker symbol may vary..." as `counterpoint`; `caveat` is arguable.
- **Next Steps**: Team decides on `edge_optional` and the `refutation`→`counterpoint` rename; hand-label texts (Task 7) before any larger run.

### Entry 2 — 2026-11-07
- **Action**: Output format changed to YAML (schema YAML in, graph YAML out).
  The files of run `20261107T150706Z` were converted from JSON/CSV to `graphs/*.yaml` and `run.yaml`, without new model calls.
  `src/validate.py` still finds 4/4 valid.
