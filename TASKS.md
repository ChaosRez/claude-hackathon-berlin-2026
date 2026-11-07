# Project Task Ledger

Prioritized task list for the research loop.
Keep this updated as work progresses.
Put your name after a task when you take it: `(owner: name)`.
Steps refer to the plan in `README.md`.

## Priority 0 (Core)

- [Done] Task 1: Get the data (Step 1)
  - Load HC3 `finance`.
  - Keep 100 questions where the human and ChatGPT answers differ by at most 15 words (10 or less preferred).
  - If fewer than 100 exist, record the real number in `JOURNAL.md`.
  - Save to `data/pairs.jsonl`, with the script that builds it.
- [ ] Task 2: Decide the entities (Step 2)
  - Which parts of reasoning become nodes: claim, reason, refutation, rebuttal, condition, evidence, recommendation, or better ones?
  - Decide how big one entity is (sentence, clause, or span).
  - Write the result in `GUIDE.md`.
- [ ] Task 3: Decide the relations (Step 2)
  - Pick relations that capture the structure of thinking: supports, attacks, answers, illustrates, qualifies, concludes, or better ones.
  - Two people hand-label the same 2 texts and compare; fix the rules.
  - Write the result in `GUIDE.md` and mark it final.
- [ ] Task 4: Code that builds the graph (Step 3)
  - `src/extract.py`: text + `GUIDE.md` → entities and relations as JSON, using Claude.
  - `src/validate.py`: every link points to a real entity, every type is allowed, one main claim.
  - `src/build_graph.py`: JSON → `networkx` graph.
  - Tests first.
- [ ] Task 5: Code that draws a graph (Step 3)
  - `src/draw.py`: one color per entity type, labeled arrows, saves a PNG.
  - Can start now with the example JSON in `README.md`.
- [ ] Task 6: Brainstorm the analysis (Step 5)
  - How do we compare human and ChatGPT graphs? Start from the ideas in `README.md`.
  - Must include a human-vs-human baseline.
  - Write the plan in `JOURNAL.md`.

## Priority 1 (Checking and results)

- [ ] Task 7: Hand-label 10 blind texts in `annotations/`; score extractor vs people, and people vs people (Step 4)
- [ ] Task 8: Check fairness (human vs ChatGPT accuracy) and stability (two runs on 20 texts) (Step 4)
- [ ] Task 9: Run the analysis from Task 6 (Step 6)
- [ ] Task 10: Read 3 example pairs for the biggest difference (Step 6)
- [ ] Task 11: Write `results/RESULTS.md` and the findings entry in `JOURNAL.md` (Step 7)

## Priority 2 (Stretch)

- [ ] Task 12: Count small patterns (motifs) per graph
- [ ] Task 13: Graph edit distance on labels only
- [ ] Task 14: Graph-theory shape questions: tree or not, cycles, isolated claims
