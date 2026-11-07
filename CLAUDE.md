# CLAUDE.md

This file captures essential conventions, constraints, and anti-patterns for developers and AI agents working on this project.

## Conventions

### Markdown authoring

Markdown files use [semantic line breaks](https://sembr.org/):
break a line after each sentence,
and optionally at clause boundaries within a long sentence,
so that diffs stay meaningful and reviewable.
Never reflow or hard-wrap paragraphs to a fixed column limit.

### Working with AI agents

- In Claude Code "auto mode", never commit on your own — leave changes in the working tree for developer review, and commit only when explicitly asked.
- All research experiments must maintain an evidence chain: Claim -> Experiment Plan -> Audit -> Findings.
- Keep agent state in files: record hypotheses and run logs in `JOURNAL.md` and active work items in `TASKS.md`.
- Never use LLM arithmetic or heuristics to compute summary statistics; write and run deterministic Python analysis scripts instead.
- Check all claims against code and artifacts in the repository before reporting conclusions.

## Anti-patterns to avoid

- Do not invent, extrapolate, or impute missing measurements.
  If data is corrupted or incomplete, explicitly report `INCONCLUSIVE` or `INVALID`.
- Do not inflate context by adding codebase overviews or listings that are discoverable by reading the source code.
- Do not remove failed, errored, or timed-out test runs from denominators when computing success or throughput rates.

