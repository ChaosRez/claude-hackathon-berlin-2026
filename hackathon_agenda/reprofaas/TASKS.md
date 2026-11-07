# ReproFaaS Task Ledger

## Priority 0 (Core MVP: Offline Deterministic Research Loop)
- [x] Task 0.1: Project initialization and directory layout
- [x] Task 0.2: Define core schemas (Claim, ExperimentPlan, PerRequestRecord, AuditResult)
- [ ] Task 0.3: Implement deterministic schema and safety validator (`src/controller/validator.py`)
- [ ] Task 0.4: Implement deterministic evidence auditor (`src/analysis/auditor.py`)
- [ ] Task 0.5: Implement Section 8 red-team tests (complete, missing arrivals, denominator error, corrupted digest)
- [ ] Task 0.6: Implement synthetic fixture runner (`src/controller/runner.py`)
- [ ] Task 0.7: Implement evidence-linked reporter (`src/analysis/reporter.py`)
- [ ] Task 0.8: Wire end-to-end CLI (`python -m reprofaas`) and verify full loop

## Priority 1 (FaaS Rollout & Concurrency Benchmark Cases)
- [ ] Task 1.1: Curate illustrative claims (`claims/illustrative_concurrency.yaml` & `claims/illustrative_rollout.yaml`)
- [ ] Task 1.2: Generate baseline and counter-experiment plans
- [ ] Task 1.3: Run synthetic experiments and verify agent critic revises/stops correctly

## Completed
- [x] Initial specification and architecture alignment with Claude Impact Lab 2026 rubric

