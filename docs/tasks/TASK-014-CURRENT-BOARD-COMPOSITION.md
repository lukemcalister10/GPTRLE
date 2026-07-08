# TASK-014 — Accepted-stack current-board composition review

## Status

Completed diagnostic-only composition validation. No new modelling hypothesis, utility change, export change or production promotion.

## Objective

Generate production-style predictions for the accepted TASK-009 and TASK-012 forecast stacks, then compare them across the complete authoritative 804-player 2026 universe.

This closes the review loop after locked historical acceptance by reporting current-board effects only after both components were independently selected.

## Compared stacks

- **Baseline:** accepted TASK-009 zero-history state separation.
- **Candidate:** TASK-009 plus accepted TASK-012 evidence-weighted demonstrated-ceiling conditional average.

## Verified invariants

Across 4,020 player-lead rows per stack:

- exactly 804 players and five leads each;
- meaningful-season probabilities are exactly unchanged;
- conditional games and expected games are exactly unchanged;
- all elite-threshold probabilities are exactly unchanged;
- TASK-006 is not used;
- no keeper utility, board value, rank capital or production export is calculated.

## Current-board effects

- mean absolute five-year expected-points change: 16.71;
- median five-year change: -0.48;
- range: -99.42 to +149.03;
- 384 players increase and 420 decrease;
- mean absolute expected-points rank movement: 1.55;
- maximum rank movement: 9;
- top-100 overlap: 99 of 100.

The reporting-only established low-ceiling cohort contains 39 current players. Across its 195 player-lead rows, mean conditional average increases by 0.115 points and mean expected points changes by -0.073 per row. The threshold is diagnostic only and is not supplied to TASK-012.

## Evidence route

New GitHub-hosted jobs failed before step 1 while older jobs continued to complete. The report was reproduced locally from the successful TASK-003N artifact generated on PR #40, using its hashed annual dataset and authoritative registry plus the merged deterministic TASK-009 and TASK-012 modules. The exact source hashes and model blob IDs are recorded under `reports/task-014-current-board-composition/`.

The executable workflow remains in the repository for hosted regeneration when runners resume. The locally reproduced evidence satisfies the full-population reporting requirement without changing or tuning the accepted model.
