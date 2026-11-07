# CLAUDE.md

This file captures essential conventions and constraints for agents working on ReproFaaS.

## Conventions

- Use semantic line breaks in Markdown files: break a line after each sentence or clause boundary.
- All experiments must follow the evidence chain: Claim -> Plan -> Audit -> Report.
- Never modify or overwrite raw JSONL request records after collection.
- Never use LLM arithmetic or heuristics to compute summary statistics; use deterministic Python code in `src/analysis/`.
- In Claude Code "auto mode", never commit without explicit approval; leave changes in working tree for review.

## Anti-patterns to Avoid

- Do not invent or impute missing measurements. If data is incomplete or corrupted, emit `INCONCLUSIVE` or `INVALID`.
- Do not pool correlated request latencies to claim artificial statistical power; aggregate across independent run units.
- Do not conflate client-side HTTP latency with server execution or scheduler latency.
- Do not remove timed-out or failed requests from the denominator when calculating success rate or throughput.

