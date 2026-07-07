# TASK-002 — Authoritative player universe export

## Type
Data-contract and legacy adapter.

## Goal
Produce a side-effect-free, stable export of the exact player universe and position state used by the legacy board, resolving the current 752-versus-805 discrepancy.

## Required work
- Identify every transformation that creates or activates the legacy board population.
- Export stable player key, display name, draft facts, current eligibility, future-position field used by legacy, list status, and inclusion reason.
- Do not import or execute the entire patch chain merely to read the artifact at vNext inference time.
- Add uniqueness, missing-key, population-count, and deterministic-hash tests.
- Document the difference between raw JSON candidates and final legacy board inclusion.

## Acceptance criteria
- Export reproduces the authoritative legacy board population exactly.
- Repeated cold runs produce identical output.
- No player is keyed only by display name.
- No legacy valuation formula changes.
