# TASK-037 — Negative risk-value audit

## Status

Defect confirmed. No production board, forecast or frozen Claude file changed.

## Finding

The current utility aggregation uses a linear downside penalty:

`weight × (expected utility − risk aversion × uncertainty)`

With the current meaningful-season mixture proxy:

- expected utility is approximately `p × conditional points`;
- uncertainty is approximately `conditional points × sqrt(p × (1 − p))`.

The annual adjusted value becomes negative whenever:

`p < risk_aversion² / (1 + risk_aversion²)`

This occurs below approximately:

- 10.9% meaningful-season probability for the contender lens;
- 5.9% for balanced;
- 3.1% for rebuilder.

## Full 804-player result

Negative combined intrinsic values:

- contender: 54 players;
- balanced: 29 players;
- rebuilder: 14 players.

Minimum values:

- contender: −12.63;
- balanced: −3.43;
- rebuilder: −1.77.

## Economic interpretation

The primary player-value layer contains no explicit salary, contract cost, draft cost or roster-slot charge. A highly uncertain player can have very little value, but the model has not defined a mechanism through which owning that player creates negative asset value.

The negative sign is therefore a mathematical artefact of the linear risk penalty rather than an accepted keeper-economy concept.

## Cohort health

The current board does not repeat the earlier zero-value collapse:

- 178 zero-history players occupy 172 distinct combined values;
- 199 established low-ceiling players occupy 199 distinct combined values;
- no player has an exact zero value.

A simple floor at zero would undo that progress by creating a new tied tail.

## Decision

Treat negative primary values as a utility-layer defect.

Do not:

- interpret them as a real player liability;
- floor them mechanically at zero;
- alter forecasts to solve a utility-transform problem.

Test a separate positive, monotone risk-discount hypothesis that preserves ordering information near zero while ensuring adjusted value remains non-negative.

## Acceptance rule

This audit is accepted because the negative threshold follows directly from the declared formula, the issue affects 14–54 current players depending on lens, and no accepted economic cost justifies the sign.