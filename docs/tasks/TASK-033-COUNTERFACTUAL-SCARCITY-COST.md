# TASK-033 — Counterfactual scarcity cost

## Status

Accepted diagnostic infrastructure. No production board, forecast or frozen Claude file changed.

## Hypothesis

Positional scarcity can be measured by relaxing one or more constrained league slots to unrestricted eligibility and re-optimising the full 368-slot league.

The cost is:

`optimal utility after relaxation − optimal utility before relaxation`

This depends on the constraint itself, not on which equivalent player the optimiser labels as positional or free-choice.

## Full 804-player result

First-slot scarcity cost:

| Position | Contender | Balanced | Rebuilder |
|---|---:|---:|---:|
| GDEF | 0.00 | 0.00 | 0.00 |
| KDEF | 57.30 | 53.80 | 73.96 |
| MID | 0.00 | 0.00 | 0.00 |
| RUC | 52.25 | 14.55 | 54.91 |
| GFWD | 0.00 | 0.00 | 0.00 |
| KFWD | 0.00 | 0.00 | 0.00 |

Only key-defender and ruck constraints reduce optimal league utility in the current forecast and eligibility distribution.

## Relaxation curves

The first six KDEF relaxations continue to add utility under every lens, with declining marginal cost. Ruck scarcity is shallower: contender reaches its full gain after one relaxed slot, balanced after two, and rebuilder after two.

This is plausible and materially cleaner than TASK-032's assigned-cut-line artefact.

## Interpretation

A zero cost does not mean players at that position have zero value. It means the named positional constraint currently imposes no additional league-wide cost beyond the 80 unrestricted scoring slots.

The result is league-wide and owner-independent. It updates automatically when forecasts, official eligibility or lineup rules change.

## Deliberate limitation

This task measures position-level scarcity only. It does not allocate that cost to individual players or alter TASK-031 rankings.

A successor hypothesis must determine how to distribute KDEF and RUC constraint value across eligible players without double-counting intrinsic production, creating a hard selection cliff or awarding every eligible player the full shadow cost.

## Decision

Accept counterfactual relaxation cost as the authoritative scarcity diagnostic. Reject assigned slot-family minimums as scarcity evidence.

## Acceptance rule

Accepted because the measure is optimisation-invariant, owner-independent, non-negative under relaxation, interpretable across lenses and free of the pathological balanced GDEF result.