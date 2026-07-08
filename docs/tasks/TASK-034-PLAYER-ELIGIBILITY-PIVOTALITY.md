# TASK-034 — Player eligibility pivotality

## Status

Accepted as diagnostic infrastructure and rejected as a directly additive player premium.

## Hypothesis tested

For each player, block their ability to fill currently binding KDEF or RUC constrained slots while preserving access to unrestricted scoring slots, then re-optimise the full league.

The resulting loss measures whether that player's positional eligibility is pivotal to the current 368-slot optimum.

## Full 804-player result

Exactly 48 players had positive pivotality under each strategy lens.

Maximum individual loss:

- contender: 67.74;
- balanced: 62.60;
- rebuilder: 91.66.

However, many selected players independently inherited the same full replacement loss. In the balanced view, 38 players each recorded the same 62.60-point loss.

Summed individual losses were:

- contender: 2,953.84;
- balanced: 2,720.68;
- rebuilder: 3,561.90.

These totals greatly exceed the actual full league cost of all KDEF and RUC constraints:

- contender: 307.78;
- balanced: 249.65;
- rebuilder: 463.85.

## Interpretation

The diagnostic correctly identifies which players are pivotal, but individual counterfactual losses overlap. Each player is evaluated against a league where every other player retains full eligibility, so multiple players can each appear responsible for the same finite scarcity cost.

This is useful for identifying eligible players who matter to the constrained optimum. It is not an additive accounting system.

## Decision

Do not add raw player pivotality losses to TASK-031 intrinsic values.

Retain the diagnostic for:

- identifying which current eligibilities are actually binding;
- checking asymmetric DPP value;
- constructing auditable weights for a finite scarcity budget;
- detecting players whose positional label has zero current league effect.

## Next hypothesis

Allocate each position's finite full-relaxation scarcity budget across players using normalized pivotality weights. The allocated premiums must sum exactly to the measured league constraint cost rather than multiplying it across many players.

## Acceptance rule

Accepted only as diagnostic infrastructure because it is owner-independent, exact and assignment-invariant. Rejected as a direct premium because overlapping counterfactual losses violate budget conservation and would materially overstate scarcity.