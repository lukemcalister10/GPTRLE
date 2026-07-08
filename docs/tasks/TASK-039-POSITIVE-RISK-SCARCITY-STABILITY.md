# TASK-039 — Positive-risk scarcity stability

## Status

Accepted diagnostic stability gate. No production board, forecast or frozen Claude file changed.

## Objective

Recompute the full league allocation, counterfactual positional scarcity costs, player eligibility pivotality, budget-conserving scarcity premiums and combined rankings after replacing the negative linear risk tail with TASK-038's positive exponential discount.

## Full 804-player result

KDEF and RUC remain the only binding positional constraints. GDEF, MID, GFWD and KFWD continue to have zero separate constraint cost beyond the unrestricted scoring pool.

Total scarcity budgets under positive-risk values:

- contender: 313.25;
- balanced: 251.50;
- rebuilder: 461.48.

Change from the linear-risk diagnostic:

- contender: +1.78%;
- balanced: +0.74%;
- rebuilder: −0.51%.

Exactly 48 players continue to receive positive scarcity premiums under every lens.

Maximum player premium:

- contender: 9.55;
- balanced: 8.47;
- rebuilder: 13.50.

Maximum premium share of combined value:

- contender: 2.68%;
- balanced: 2.48%;
- rebuilder: 4.03%.

Maximum absolute rank movement from the positive intrinsic board:

- contender: 9 places;
- balanced: 10 places;
- rebuilder: 12 places.

Top-100 membership remains unchanged under every lens. Top-200 membership changes by only one player in the rebuilder view.

## Tail behaviour

The combined board contains:

- no negative values;
- no exact zero values;
- no tied zero-value tail.

The smallest combined values remain positive and differentiated.

## Interpretation

The scarcity mechanism is stable to correction of the risk transform. The negative linear tail was not responsible for the identification of KDEF and RUC as binding constraints, nor for the modest scale of player scarcity premiums.

This provides evidence that TASK-038 and TASK-035 are compatible rather than compensating errors.

## Decision

Accept the positive-risk intrinsic board plus budget-conserving scarcity as the preferred combined diagnostic construction.

Do not yet promote to production. Remaining gates are:

1. sensitivity to plausible official position updates;
2. comparison with the frozen legacy board and pathological cohorts;
3. a reproducible end-to-end export that preserves intrinsic, scarcity and combined components.

## Acceptance rule

Accepted because the corrected risk transform eliminates negative values while changing scarcity budgets by less than 1.8% in absolute terms, preserving the same binding positions, keeping premiums below 4.1% of combined value and leaving every top-100 unchanged.