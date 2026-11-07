# CLAUDE.md

This file captures essential conventions, constraints, and anti-patterns for developers and AI agents working on this project.
Read `README.md` for the research question and the step-by-step plan.

## Conventions

### Markdown authoring

Markdown files use [semantic line breaks](https://sembr.org/):
break a line after each sentence,
and optionally at clause boundaries within a long sentence,
so that diffs stay meaningful and reviewable.
Never reflow or hard-wrap paragraphs to a fixed column limit.

Use simple, short sentences.
Teammates come from different fields.

### Working with AI agents

- In Claude Code "auto mode", never commit on your own — leave changes in the working tree for developer review, and commit only when explicitly asked.
- All research experiments must maintain an evidence chain: Claim -> Experiment Plan -> Audit -> Findings.
- Keep agent state in files: record hypotheses and run logs in `JOURNAL.md` and active work items in `TASKS.md`.
- Never use LLM arithmetic or heuristics to compute summary statistics; write and run deterministic Python analysis scripts instead.
- Check all claims against code and artifacts in the repository before reporting conclusions.

### Project rules

- `GUIDE.md` is the team's agreed definition of a correct graph.
  Never edit it on your own; suggest changes and let the team decide.
- Nodes are reasoning entities (claim, reason, refutation, ...) and edges are relations, both defined in `GUIDE.md`.
  Use only the types listed there.
  If one seems missing, tell the user instead of inventing it.
- Until `GUIDE.md` exists and is marked final, the entity and relation types are still being brainstormed (Tasks 2 and 3).
  Help with the brainstorm and with tasks that don't depend on it (data, drawing), but don't run the extractor on the full dataset.
- Check `TASKS.md` for task owners before starting a task, so two people don't do the same work.
- Graph comparisons use node roles and edge types only, never the sentence text.
- Every human-vs-LLM result must be shown next to a human-vs-human baseline.
- Every reported result must state how well the extractor matched the hand labels in `annotations/`, separately for human and LLM texts.
  The extractor is itself an LLM and may read LLM text more easily.
- Before claiming a difference, read 3 real example pairs and confirm it is not an extractor error.
- When the extractor prompt changes, save it as a new version in `prompts/` and re-run the hand check.

### Data

- Use HC3 `finance` only, and keep pairs whose human and ChatGPT answers differ by at most 15 words.
  Unequal lengths would bias graph size.
- HC3 is CC BY-SA 4.0, so derived data (paired texts, graphs, annotations) must stay CC BY-SA 4.0, not the repository's default CC BY 4.0.

## Anti-patterns to avoid

- Do not invent, extrapolate, or impute missing measurements.
  If data is corrupted or incomplete, explicitly report `INCONCLUSIVE` or `INVALID`.
- Do not inflate context by adding codebase overviews or listings that are discoverable by reading the source code.
- Do not remove failed, errored, or timed-out test runs from denominators when computing success or throughput rates.
- Do not silently drop graphs that fail validation: count them and report them.
