# TASK-038 — Positive exponential risk discount

## Status

Accepted diagnostic alternative. No production board, forecast or frozen Claude file changed.

## Hypothesis

Replace the linear risk penalty with a positive monotone discount:

`adjusted utility = expected utility × exp(−risk aversion × uncertainty / expected utility)`

For zero expected utility, adjusted utility remains zero.

## Properties

- Never negative.
- Equals expected utility when uncertainty is zero.
- Approaches zero continuously as relative uncertainty increases.
- Preserves scale: doubling mean and uncertainty doubles adjusted utility.
- Approximates the current linear penalty when uncertainty is small relative to the mean.
- Does not require a mechanical floor that creates tied zero values.

## Full 804-player diagnostic

Negative values under every lens: zero.

Exact zero values under every lens: zero.

Minimum values:

- contender: 0.0000008;
- balanced: 0.0000160;
- rebuilder: 0.0001201.

Rank correlation with the current linear baseline:

- contender: 0.99884;
- balanced: 0.99979;
- rebuilder: 0.99995.

Top-100 overlap:

- contender: 100;
- balanced: 99;
- rebuilder: 100.

Top-200 overlap:

- contender: 199;
- balanced: 200;
- rebuilder: 200.

Maximum rank movement is larger in the low-value contender tail—83 places—because the current linear formula orders many low-probability players by differing negative values. Median movement is only two places for contender and one for the other lenses.

## Cohort health

- 178 zero-history players retain 172 distinct values.
- 199 established low-ceiling players retain 199 distinct values.
- No tied zero tail is introduced.

## Interpretation

The exponential form resolves the sign defect while leaving the top of the player market almost unchanged. Most movement occurs where the old formula's negative values had no accepted economic interpretation.

## Decision

Accept as the preferred diagnostic risk transform.

Do not yet replace the existing strategy-lens function in production. First rerun the combined scarcity calculation on the positive-risk values and confirm that KDEF/RUC scarcity remains modest, budget-conserving and stable.

## Acceptance rule

Accepted because it removes all negative values, preserves differentiation, is monotone and transparent, and changes almost none of the top-200 market while correcting the pathological low-value tail.