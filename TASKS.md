# Project Task Ledger

Prioritized task list for the research loop.
Keep this updated as work progresses.
Put your name after a task when you take it: `(owner: name)`.
Steps refer to the plan in `README.md`.

## Priority 0 (Core)

- [Done] Task 1: Get the data (Step 1)
  - `scripts/get_data.py` downloads HC3 `finance` and writes `data/finance-filtered.jsonl`.
  - Open: record in `JOURNAL.md` how many pairs pass the filter.
  - Open: the script does not yet prefer opinion questions (see `data_exploration.ipynb` section 10).
- [Eva] Task 2: Decide the entities (Step 2)
  - Draft: `entity_definition.yaml` v0.1 (11 types, coverage rule, `main` and `hedged` flags), copied into `GUIDE.md`.
  - Open: team review, then mark `GUIDE.md` FINAL.
- [ ] Task 3: Decide the relations (Step 2)
  - Draft: `relation.yaml` v0.1 (9 relations, primary edges), copied into `GUIDE.md`.
  - Open: two people hand-label the same 2 texts and compare; fix the rules.
  - Open: mark `GUIDE.md` FINAL.
- [Done] Task 4: Code that builds the graph (Step 3)
  - `src/extract.py`: text + `entity_definition.yaml` + `relation.yaml` → entities and relations as YAML, using Claude.
  - `src/validate.py`: all graph rules, including the coverage check; used by the extractor and by `src/measure.py`.
    Tests in `tests/test_validate.py` and `tests/test_measure.py`.
  - Open: the team decides how to measure graphs with `implicit_main` (no main claim); `src/measure.py` counts them as invalid for now.
- [ ] Task 5: Code that draws a graph (Step 3)
  - Done: `src/draw.py` makes a Graphviz drawing (one color per family of entity types, labeled arrows), shown in `app.py`.
  - Open: save a PNG.
- [ ] Task 6: Define the analysis (Step 5)
  - Draft: measures and comparison method in `criteria.yaml` v0.1, computed by `src/measure.py`.
  - Wider brainstorm in `analyse logic.md`.
  - Open: choose the human-vs-human baseline (split-half, or second FiQA human answer; see `README.md` Step 6).
  - Open: write the agreed plan in `JOURNAL.md`.

## Priority 1 (Checking and results)

- [ ] Task 7: Hand-label 10 blind texts in `annotations/`; score extractor vs people, and people vs people (Step 4)
- [ ] Task 8: Check fairness (human vs ChatGPT accuracy) and stability (two runs on 20 texts) (Step 4)
- [ ] Task 9: Run the analysis from Task 6 with `src/measure.py` (Step 6)
- [ ] Task 10: Read 3 example pairs for the biggest difference (Step 6)
- [ ] Task 11: Write `results/RESULTS.md` and the findings entry in `JOURNAL.md` (Step 7)

## Priority 2 (Stretch)

- [ ] Task 12: Count small patterns (motifs) per graph
- [ ] Task 13: Graph edit distance on labels only
- [ ] Task 14: Graph-theory shape questions: tree or not, cycles, isolated claims
