# TASK-042 — Frozen legacy and pathological-cohort comparison

## Status

Accepted diagnostic comparison. No production board, forecast or frozen Claude file changed.

## Objective

Compare the preferred positive-risk plus budgeted-scarcity balanced board with the frozen TASK-006 board and the previously documented defect cohorts.

Legacy values are comparison context only. They are not truth labels and no player-specific correction is inferred from disagreement.

## Whole-board result

Spearman rank correlation across all 804 players is 0.702.

The current board is therefore related to the legacy market but is not a rescaled or lightly reordered copy.

## Cohort results

| Cohort | Players | Legacy median rank | Current median rank | Current distinct values |
|---|---:|---:|---:|---:|
| Zero history | 111 | 481.0 | 666.0 | 105 |
| Established low ceiling | 119 | 697.0 | 530.0 | 119 |
| Partial season | 312 | 233.5 | 200.0 | 312 |
| Pathological zero cases | 5 | 802.0 | 748.0 | 5 |
| Pedigree persistence | 86 | 139.5 | 107.5 | 86 |

No audited player has an exact zero current value.

## Interpretation

### Zero history

The cohort moves lower overall, consistent with the accepted zero-history separation, while retaining 105 distinct values across 111 players. The model is not treating all unproven players as identical.

### Established low ceiling

These players move materially higher relative to legacy. All 119 have distinct current values, addressing the earlier tendency to underrate demonstrated but limited senior production.

### Partial season

The cohort moves higher and remains fully differentiated. This is consistent with the accepted asymmetric partial-season update rather than blanket extrapolation or blanket suppression.

### Pathological zero cases

The five documented cases now occupy five distinct values and ranks from 435 to 787. They no longer collapse into one unusable bottom bucket.

### Pedigree persistence

The cohort remains comparatively strong without requiring the rejected permanent pedigree-fade model. Current value can persist through demonstrated forecast evidence rather than an irreversible draft-status premium.

## Decision

Accept the current construction as structurally improved over the frozen legacy board for the audited cohorts.

Do not use the 0.702 correlation as an optimisation target. A higher correlation would not necessarily be better because several known legacy defects are expected to create material disagreement.

## Remaining boundary

This closes the principal structural comparison gates for the diagnostic value construction. Production promotion remains a separate decision and TASK-006 remains blocked.