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

