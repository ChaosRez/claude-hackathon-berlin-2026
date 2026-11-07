# Project Task Ledger

Prioritized task list for the research loop.
Keep this updated as work progresses.
Steps refer to the plan in `README.md`.

## Priority 0 (Core MVP)

- [ ] Task 0.1: Brainstorm chunking rules and relations; write and freeze `GUIDE.md` (Step 1)
- [ ] Task 0.2: Two people hand-label 2 texts; compare and fix `GUIDE.md` (Step 1)
- [ ] Task 0.3: Build `data/pairs.jsonl`: 50 HC3 questions, human answers of 100–300 words, matched LLM answers (Step 2)
- [ ] Task 0.4: Write `src/split.py` and `src/validate.py`, with tests first (Step 3)
- [ ] Task 0.5: Write the extractor prompt (`prompts/extract_v1.txt`) and `src/extract.py` (Step 3)
- [ ] Task 0.6: Hand-label 10 blind texts in `annotations/`; score extractor vs people, and people vs people (Step 4)
- [ ] Task 0.7: Check fairness (human vs LLM accuracy) and stability (two runs on 20 texts) (Step 4)
- [ ] Task 0.8: Record the extractor check in `JOURNAL.md`

## Priority 1 (Analysis)

- [ ] Task 1.1: `src/measure.py`: nodes, depth, branching, relation shares, main-claim position (Step 5)
- [ ] Task 1.2: `src/compare.py`: human vs LLM, with human vs human baseline (Step 6)
- [ ] Task 1.3: Read 3 example pairs for the biggest difference (Step 6)
- [ ] Task 1.4: Write `results/RESULTS.md` and the findings entry in `JOURNAL.md` (Step 7)

## Priority 2 (Stretch)

- [ ] Task 2.1: Count small patterns (motifs) per graph
- [ ] Task 2.2: Graph edit distance on labels only
- [ ] Task 2.3: Graph-theory shape questions: tree or not, cycles, isolated claims
