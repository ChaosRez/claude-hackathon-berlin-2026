Team 2 graph theory and graph reasoning, eva

Autonomous scientific research loop developed for the Claude Impact Lab Berlin 2026 (co-hosted by Foresight Institute).

## Structure & Conventions

- **`CLAUDE.md`**: Project conventions, evidence chain rules, and constraints for AI agents.
- **`JOURNAL.md`**: Append-only ledger recording research hypotheses, experiment runs, and evidence audits.
- **`TASKS.md`**: Active task ledger and milestones for the team and agents.
- **`.claude/skills/judge-submissions/`**: Submission evaluator skill based on the official hackathon rubric.

## Working with Claude Code

To run Claude Code with your research loop:

```bash
# Goal-directed loop: runs until condition is met
/goal all tests pass and findings are recorded in JOURNAL.md

# Scheduled loop: periodically monitors and records progress
/loop 10m check experiment output and log new results to JOURNAL.md

# Self-evaluate project against the hackathon rubric
/judge-submissions
```

## Licenses

This project is dual-licensed:
- **Code**: [Apache License 2.0](LICENSE)
- **Documentation & Written Materials**: [Creative Commons Attribution 4.0 International](LICENSE-docs)
