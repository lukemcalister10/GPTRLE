# TASK-035 — Budget-conserving player scarcity allocation

## Status

Accepted diagnostic infrastructure. No production board, forecast or frozen Claude file changed.

## Hypothesis

The finite league-wide scarcity cost measured in TASK-033 can be allocated to individual players using exact position-specific pivotality from TASK-034, provided the allocation conserves the total position budget.

For each binding position:

`player premium = position budget × player pivotality / sum of position pivotality`

A player eligible at multiple binding positions may receive separately accounted components from each position. The sum of all player premiums must equal the measured KDEF and RUC scarcity budgets exactly.

## Full 804-player result

Total scarcity budgets:

- contender: 307.78;
- balanced: 249.65;
- rebuilder: 463.85.

Allocated totals matched those budgets exactly.

Exactly 48 players received positive premiums under each lens: 32 KDEF contributors and 16 RUC contributors, with overlap handled through separate position components.

Maximum player premium:

- contender: 9.30;
- balanced: 8.27;
- rebuilder: 13.58.

Maximum premium share of combined value:

- contender: 2.72%;
- balanced: 2.46%;
- rebuilder: 4.03%.

Maximum absolute rank movement against TASK-031:

- contender: 7 places;
- balanced: 6 places;
- rebuilder: 9 places.

Top-100 membership remained unchanged under every lens.

## Interpretation

This resolves the over-allocation defect in raw player pivotality. Scarcity remains a small additive adjustment rather than replacing intrinsic forecast value.

The premium is:

- league-wide;
- owner-independent;
- based only on current official eligibility and the current 368-slot rules;
- exactly budget-conserving;
- zero for positions whose constraint has no measured league cost;
- asymmetric for multi-position eligibility.

## Limitations

The allocation is proportional to one-at-a-time pivotality, not a full Shapley-value calculation across all eligibility coalitions. It is therefore an auditable approximation to fair allocation, not a unique mathematical truth.

Players outside the current optimal allocation receive no scarcity premium, but they retain their complete TASK-031 intrinsic value. There is therefore no zero-value tail in combined rankings.

## Decision

Accept as the preferred scarcity-combination diagnostic. Do not yet promote into production until the combined 804-player export is reviewed for player-level anomalies and sensitivity to official position changes.

## Acceptance rule

Accepted because the method conserves the measured league budget exactly, keeps scarcity below 4.1% of any player's combined value in the current run, produces modest rank movement, preserves top-100 membership and remains independent of current ownership.