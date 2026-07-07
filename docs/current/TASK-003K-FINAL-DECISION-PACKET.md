# TASK-003K final decision packet

## Decision required

TASK-003K is now technically validated and its current-board impact is known. The remaining blocker is a model-governance decision: whether to accept a small pooled historical gain despite a material regression in the locked age-30-plus, lead-5 critical subgroup.

## Historical result

On the exact 20,094 prediction rows across 25 legal rolling-origin folds, replacing only the meaningful-season SGD classifier with the predeclared logistic candidate produced:

- meaningful-season Brier: 0.47% better;
- meaningful-season log loss: 0.51% better;
- games MAE: 0.19% better;
- total-points MAE: 0.16% better.

The gain is concentrated at lead 4. Lead 2 is slightly worse, and lead 5 is mixed: log loss improves while Brier, games MAE and points MAE worsen slightly.

## Independent validation

TASK-003L independently confirmed:

- exactly 20,094 target rows;
- duplicate-free prediction keys;
- all 25 legal folds for both current and candidate runs;
- zero transformed-design mismatches;
- zero conditional games or conditional-average prediction mismatches;
- the event model changed in all 25 folds;
- the event calibrator changed in all 25 folds;
- committed decomposable pooled metrics reproduced within the locked tolerance;
- the full vNext test suite passed.

The red wrapper conclusion on the final TASK-003L workflow run is not a model or validation failure. The acceptance adjudication and tests both passed; the wrapper checked the legacy diagnostic step instead of the adjudication step.

## Critical subgroup blocker

The locked age-30-plus, lead-5 subgroup (`n=278`) worsened by:

- Brier: 8.96%;
- games MAE: 11.76%;
- total-points MAE: 9.52%.

Direction varies by origin, with substantial opportunity overprediction in the 2018 and 2019 origins and improvement in 2020. This is not a stable, benign trade-off that can be averaged away automatically.

## Current 2026 board impact

The hardened-registry current-board review completed on the authoritative 804-player universe and 4,020 annual rows per model.

Validation gates passed:

- zero critical identity-health issues;
- St Kilda Max King and Hawthorn Maxwell King remain distinct;
- no duplicate keys;
- no missing or non-finite forecasts;
- no probability-bound, threshold-order or quantile-crossing failures;
- five leads for every player.

Five-year board movement is broad but not one-directional:

- mean total-points change: -2.6 points;
- median total-points change: +1.0 points;
- 5th to 95th percentile total-points change: approximately -149 to +128;
- maximum increase: +287 points;
- maximum decrease: -421 points;
- maximum absolute five-year points-rank movement: 67 places;
- 95th percentile absolute points-rank movement: 25 places.

For current age-30-plus lead-5 rows, the candidate reduces meaningful-season probability by 1.55 percentage points on average and reduces expected points by about 550 in aggregate across the slice.

For current zero-history players, the candidate raises five-year expected points by about 47 points per player on average. The underlying zero-history information problem remains unresolved, so this movement should not be treated as independently validated improvement.

## Governance options

### Option A — reject TASK-003K

Retain the current merged vNext event classifier. This strictly respects the critical-subgroup rule. The cost is foregoing a small pooled gain that is concentrated at lead 4.

### Option B — defer TASK-003K

Keep PR #19 experimental and run one predeclared follow-up hypothesis aimed at old-player long-horizon event probability without slice-specific offsets or named-player rules. This is the recommended option.

### Option C — accept TASK-003K

Accept the small pooled gain and explicitly waive the critical-subgroup rule for age-30-plus lead 5 on keeper-relevance grounds. This requires an intentional user/model-governance decision and should not be done implicitly.

## Recommendation

**Defer TASK-003K.**

The candidate is real, reproducible and technically clean, but the pooled improvement is small and the locked critical-subgroup regression is material. The safest next experiment is a single, leakage-safe hypothesis addressing older-player long-horizon opportunity. Do not add an age-specific correction, named-player rule or post-hoc offset.

No production, value, keeper-utility or UI behavior should change until the governance decision is recorded.
