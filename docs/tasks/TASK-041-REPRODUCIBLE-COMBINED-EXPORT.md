# TASK-041 — Reproducible combined comparison export

## Status

Implementation candidate. No production board, forecast or frozen Claude file changed.

## Objective

Provide one deterministic command that rebuilds the preferred diagnostic comparison surface from the accepted annual candidate artifact.

The runner performs:

1. strict 804-player and five-year input validation;
2. meaningful-season mixture uncertainty construction;
3. positive exponential risk discount under contender, balanced and rebuilder lenses;
4. full 368-slot league allocation using the exact current eligibility snapshot;
5. full KDEF and RUC constraint relaxation budgets;
6. exact player eligibility pivotality;
7. budget-conserving scarcity allocation;
8. combined values and deterministic ranks;
9. persisted output, eligibility snapshot and run manifest.

## Command

```bash
python vnext/run_task041_combined_export.py \
  --annual-candidate-csv <candidate_board_annual.csv> \
  --output-dir reports/task-041-combined-export
```

## Outputs

`combined_player_comparison_804.csv` contains:

- stable player id;
- player name;
- current positions;
- current owner as display metadata only;
- intrinsic value, scarcity premium, combined value and rank for each lens.

`eligibility_snapshot_804.csv` preserves the exact player-position input used.

`summary.json` records:

- input SHA-256;
- forecast horizon;
- risk transform and uncertainty proxy;
- KDEF and RUC scarcity budgets;
- positive pivotality counts;
- negative and exact-zero value counts;
- output filenames.

## Failure conditions

The run fails explicitly for:

- fewer or more than 804 players;
- incomplete or additional forecast years;
- missing annual rows;
- player metadata changing across forecast years;
- invalid meaningful-season probabilities;
- missing required columns;
- incomplete eligibility;
- an unfillable league allocation.

## Ownership guardrail

Current owner is copied to the output only after all values are calculated. It is never supplied to intrinsic aggregation, league optimisation, pivotality, scarcity allocation or ranking.

## Position-update guardrail

The eligibility snapshot is persisted with every run. A changed official position file must produce a new snapshot and full scarcity recomputation rather than reusing prior premiums.

## Decision

Accept as the required diagnostic export path once repository tests pass. This does not promote the resulting board to production.

## Remaining validation

The next gate is comparison against the frozen legacy board and the documented pathological cohorts, using the complete reproducible output rather than named-player preferences as truth labels.