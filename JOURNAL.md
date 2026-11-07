# Research Journal

Append-only ledger of research hypotheses, decisions, experiment runs, and evidence audits.

## Template Entry Format

### Entry [Number] — [YYYY-MM-DDTHH:MM:SSZ]
- **Hypothesis / Question**: What open scientific question or problem is being addressed?
- **Action / Experiment**: What was run, changed, or analyzed?
- **Evidence**: Links to data artifacts, log files, or code outputs.
- **Findings & Honesty**: What succeeded, what failed, where the agent got stuck, and confidence level.
- **Next Steps**: What the loop needs next.

### Entry 1 — 2026-11-07T15:23:30Z
- **Hypothesis / Question**: Can HC3 `finance` give a same-question human-vs-human baseline?
- **Action / Experiment**: `data_exploration.ipynb` section 11 matched HC3 `finance` questions to FiQA, its source.
- **Evidence**: Notebook output (section 11): 100.0% of HC3 finance questions found in FiQA; 100.0% of HC3 human answers are exactly one FiQA answer; 61.9% of questions have 2+ FiQA answers. After the opinion and 100-300 word filters, 68 questions have a second human answer.
- **Findings & Honesty**: HC3 alone has one human answer per question, but FiQA adds a second one for most questions. `criteria.yaml` and `src/measure.py` currently use a split-half baseline instead, so the two plans disagree. The opinion filter in the notebook is a regex first pass, not checked by reading.
- **Next Steps**: The team picks one baseline method. The number of pairs from `scripts/get_data.py` is not recorded yet.

### Entry 2 — 2026-11-07T15:23:30Z
- **Hypothesis / Question**: Which entity types, relation types and measures capture how humans and ChatGPT build arguments?
- **Action / Experiment**: Drafted `entity_definition.yaml` v0.1, `relation.yaml` v0.1 and `criteria.yaml` v0.1. Wrote `src/measure.py` (validation, measures, split-half baseline) and `tests/test_measure.py`. Synced `GUIDE.md` with the YAML drafts.
- **Evidence**: The files above. No graphs exist yet, so no measure has been computed on real data.
- **Findings & Honesty**: All three YAML files are drafts, not agreed by the team. `GUIDE.md` is still DRAFT. No extractor exists, so nothing here is a result.
- **Next Steps**: Team review of `GUIDE.md`; two people hand-label the same 2 texts (Task 3); build `src/extract.py` (Task 4).


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

### Entry 3 — 2026-11-07T15:19:02Z
- **Action / Experiment**: Switched the extractor to the team's `relation.yaml` (9 relations, several edges per node, one `primary` edge per node, primary edges form a tree rooted at the main claim).
  Removed my draft `relation_definition.yaml`.
  New prompt version `prompts/extract_v2.md`; graph files now use `nodes` and `edges`, the format `src/measure.py` reads.
  `src/measure.py` now also reads `.yaml` graphs.
  Ran `uv run python -m src.extract --limit 2` (4 texts), API backend, `claude-opus-5-5`, effort `high`.
- **Evidence**: `results/extraction/20261107T151902Z/`.
- **Findings & Honesty**: 4 of 4 valid on the first attempt under `src/validate.py`; `src/measure.py` also reports 4 valid, 0 invalid.
  Measures were computed but not interpreted: 2 pairs is far too few, and there is no hand check against `annotations/` yet.
  `networkx` does not import on the project's Python 3.14.1, so `measure.py` and its tests were run under Python 3.13 (`uv run --no-project --python 3.13 ...`).
- **Next Steps**: Stability check (Task 8) and hand labels (Task 7) before larger runs.

### Entry 4 — 2026-11-07T15:51:21Z
- **Hypothesis / Question**: Do the extractor and `src/measure.py` agree on which graphs are valid?
- **Action / Experiment**: Compared the two validators and found they disagreed.
  `src/validate.py` accepted `implicit_main` graphs and checked coverage; `check()` in `src/measure.py` rejected every graph without exactly one main node and did not check coverage.
  `check()` in `src/measure.py` now calls `validate()` from `src/validate.py`, so there is one set of rules.
  `src/measure.py` reads the entity and relation types from the YAML files instead of hard-coding them.
  The node id rule in `src/validate.py` changed from "ids are 1..n" to "ids are unique and increase", to match the example in `GUIDE.md` section 8 (filler has id 0 there).
- **Evidence**: `uv run pytest tests`: 47 passed (Python 3.15.1, networkx 3.7), including a test that an extractor YAML graph is measured.
- **Findings & Honesty**: No graph data changed and no model was called; this only changes which graphs count as valid.
  Graphs with `implicit_main` are still counted as invalid by `src/measure.py`, now with an explicit message, because `depth`, `main_position` and `main_in_degree` need a main claim; the team has not decided how to handle them.
  `src/measure.py` now needs the `answer` field in each graph for the coverage check; `GUIDE.md` section 8 does not show that field yet.
  Correction to Entry 3: networkx now imports on the project's Python (3.15.1 in `.venv`), so `measure.py` and its tests no longer need Python 3.13.
  The run folders cited in Entries 1 and 3 (`results/extraction/20261107T150706Z/`, `results/extraction/20261107T151902Z/`) are not in the repository, so those results cannot be checked from it.
- **Next Steps**: The team decides on `implicit_main` and on adding `answer` to `GUIDE.md` section 8; whoever has the run folders commits them (CC BY-SA 4.0, see `LICENSE-data`).

### Entry 5 — 2026-11-07
- **Hypothesis / Question**: Which way of asking Claude for a reasoning graph is most accurate and most stable: one pass, split then label, split then vote (5 samples), or step by step?
- **Action / Experiment**: Approach study, plan in `experiments/approach_study/PLAN.md`.
  5 approaches and 2 rule baselines on 20 arg-microtexts with hand-made graphs (accuracy; CC BY-NC-SA 4.0, kept local) and on 20 HC3 answers (10 pairs, seed 2026), each approach run twice (stability).
  300 tasks, $13.82 in API calls; scripts `run_study.py`, `analyze.py`, `audit.py`, `examples.py`.
- **Evidence**: `experiments/approach_study/FINDINGS.md`, `experiments/approach_study/results/summary.yaml`, `results/per_text.csv`.
- **Findings & Honesty**: No approach is measurably more accurate (0.78–0.83 right parents; all paired intervals include 0); all beat the rule baselines (0.47–0.65).
  Only voting is clearly more stable: edge overlap between runs 0.89 vs 0.72 for one call (paired +0.17, 95% interval +0.11 to +0.23).
  Confounds stated in FINDINGS: one-pass splits on its own, while the others reuse one saved or hand-made split.
  298 of 300 graphs valid; the 2 invalid (step-by-step, one human answer) stay in all denominators.
  Read 3 least-stable examples: disagreements are real ambiguity (`supports` vs `elaborates`, choice of main conclusion), not parsing.
  Every approach is less stable on human answers than on ChatGPT answers.
  No HC3 accuracy: there are still no hand labels.
- **Decision**: `docs/adr/0001-extraction-approach.md`: split once, then 5 votes (`--approach voted`, now the default).
  Smoke test of the new default on pair 0: 2 of 2 valid.
  `networkx` imports on Python 3.14.10; the earlier failure was specific to Python 3.14.1.
- **Next Steps**: Hand labels on the saved splits (Task 7); team decision on `supports` vs `elaborates` for list items.
