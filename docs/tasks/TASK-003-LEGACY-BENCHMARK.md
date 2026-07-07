# TASK-003 — Leakage-safe legacy benchmark

## Type
Validation adapter.

## Goal
Evaluate the legacy engine and vNext against identical historical snapshots, player cohorts, horizons, and realised outcomes.

## Required work
- Build or adapt a legacy evaluation interface that accepts an explicit as-of snapshot.
- Remove future list status, retirement, position, club, and scoring leakage.
- Use the locked rolling-origin folds in `VALIDATION_PROTOCOL.md`.
- Include all eligible cohort outcomes, including zero-game careers.
- Fail loudly on every row error and publish an exclusion report.
- Produce baseline, legacy, and current vNext metrics in one comparison artifact.

## Acceptance criteria
- Identical cohort keys and targets across compared models.
- Zero silent failures.
- Reproduction command and artifact manifest included.
- No model tuning based on named-player outputs.
