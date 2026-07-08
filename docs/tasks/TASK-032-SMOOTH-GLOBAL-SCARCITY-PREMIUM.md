# TASK-032 — Smooth global scarcity premium

## Status

Rejected after the full 804-player diagnostic.

## Hypothesis tested

Positional scarcity would be represented by the difference between each assigned positional minimum and the assigned unrestricted-slot minimum, activated smoothly around the positional line.

For each eligible position:

`scarcity gap = max(0, assigned position minimum − assigned unrestricted minimum)`

The proposed player premium was the largest eligible gap multiplied by a logistic activation. Multiple position premiums were not summed, ownership was excluded and every player retained intrinsic value.

## Defect found

Assigned slot-family minimums are not invariant replacement lines when the optimiser contains both constrained and unrestricted scoring slots.

A player eligible for a constrained position can be assigned to a free slot while another equivalent player is assigned to the named slot. Different but equally optimal assignment labels can therefore change the recorded minimum for `GDEF`, `MID`, `FREE` or another family without changing total league utility.

This created a pathological balanced diagnostic:

- unrestricted assigned minimum: 310.36;
- GDEF assigned minimum: 394.63;
- resulting maximum scarcity premium: 84.27;
- maximum premium share of combined value: 13.6%;
- maximum rank movement: 24 places.

The contender and rebuilder views produced maximum premiums around 10 points. There is no credible structural reason for GDEF scarcity to become dramatically larger under only the balanced horizon weights. The result is an assignment-label artefact.

## Decision

Do not use assigned slot minima as replacement lines. Do not promote the proposed scarcity premium.

The code remains diagnostic evidence of the rejected formulation and must not be wired into comparison exports or production.

## Next hypothesis

Estimate scarcity from optimisation-invariant counterfactuals, such as the increase in optimal league utility when one constrained slot is relaxed to unrestricted eligibility. Counterfactual relaxation cost depends on the constraint itself rather than the arbitrary label assigned to equivalent optimal players.

Any successor must still remain:

- league-wide and owner-independent;
- additive rather than a replacement for intrinsic value;
- continuous below the optimal 368;
- asymmetric for current multi-position eligibility;
- modest relative to intrinsic forecast value.