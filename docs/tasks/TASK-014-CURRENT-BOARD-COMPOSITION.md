# TASK-014 — Accepted-stack current-board composition review

## Status

Diagnostic-only composition validation. No new modelling hypothesis, utility change, export change or production promotion.

## Objective

Generate persisted production-style artifacts for the accepted TASK-009 and TASK-012 forecast stacks, then compare them across the complete authoritative 804-player 2026 universe.

This closes the review loop after locked historical acceptance by reporting current-board effects only after both components have been independently selected.

## Compared stacks

- **Baseline:** accepted TASK-009 zero-history state separation.
- **Candidate:** TASK-009 plus accepted TASK-012 evidence-weighted demonstrated-ceiling conditional average.

## Required invariants

Across 4,020 player-lead rows per stack:

- exactly 804 players and five leads each;
- no duplicate identities, missing values, non-finite values, invalid probabilities, threshold crossings or quantile crossings;
- meaningful-season probabilities remain exactly unchanged;
- conditional games and expected games remain exactly unchanged;
- all elite-threshold probabilities remain exactly unchanged;
- TASK-006 is not used;
- frozen Claude files remain byte-identical;
- no keeper utility, board value, rank capital or production export is calculated.

## Required reporting

- full annual and five-year player-level deltas;
- all-player, zero-history, under-50, established 50+, established low-ceiling and established-other cohorts;
- five-year expected-points and rank-movement distributions;
- top-100 overlap under expected five-year points;
- largest increases and decreases as diagnostic evidence only.

The predeclared `career_best < 65` threshold is used solely to report the TASK-008 low-ceiling cohort. It is not supplied to TASK-012 and cannot be used to tune the accepted model.
