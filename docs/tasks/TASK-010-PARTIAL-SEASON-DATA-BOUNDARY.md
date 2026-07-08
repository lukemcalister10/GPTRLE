# TASK-010 — Partial-season exposure data boundary

## Status

Diagnostic data-boundary task. No model change.

## Finding

The repository stores annual player scoring aggregates (`year`, `avg`, `games`) and current 2026 partial totals, but it does not store the historical round/date origin or the number of team games available at that origin. The locked rolling-origin benchmark therefore represents season-end annual states, not comparable intra-season states.

Using a completed historical season average as though it were known partway through that season would leak future matches. A partial-season exposure rule cannot be accepted or rejected fairly from the current annual dataset.

## Required evidence

Before a model PR can proceed, reconstruct historical snapshots containing:

- stable player and club identity;
- as-of date or round;
- player games and scoring through the origin;
- team games available through the origin;
- future season-end outcomes strictly after the origin.

## Decision

Do not tune the frozen Claude `RL_M3_FE` convention or replace it with another calendar constant. Preserve the defect as a formal blocker until origin-safe intra-season evidence exists. Continue the independently testable zero-history, pedigree and demonstrated-ceiling hypotheses in separate PRs.
