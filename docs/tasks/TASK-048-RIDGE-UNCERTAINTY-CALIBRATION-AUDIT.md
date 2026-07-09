# TASK-048 — Ridge uncertainty calibration audit

## Status

Protocol locked before TASK-048 outcome inspection. This is an evaluation-only task. It must not change the accepted TASK-047 pooled Ridge point forecasts, residual-scale estimator, quantile generator, benchmark cohorts, target definitions, keeper utility or production export.

## Context

TASK-047 is accepted for conditional-average point forecasts only. Its point quantiles remain blocked because the Ridge estimator changes the conditional-average residual scale used by the existing two-part uncertainty generator.

The current generator also treats `1 - p_meaningful` as exact zero-point mass. The locked target defines meaningful as at least six games but preserves real points from one-to-five-game seasons. TASK-048 must quantify the effect of that structural approximation rather than silently scoring those seasons as zero.

## Audit question

Do the unchanged two-part point-quantile mechanics, when supplied with TASK-047 Ridge conditional averages and residual scale, produce sufficiently calibrated and useful point distributions to accept uncertainty outputs?

## Compared forecasts

Use the locked rolling-origin predictions and exact common keys for:

- accepted TASK-012 point distributions;
- accepted TASK-047 point-forecast candidate distributions.

Use the existing locked `targets.csv` `points` column as realised total points for every row. Do not reconstruct points from the conditional-average target.

Required population remains:

- 5,622 player-origin snapshots;
- 20,094 player-origin-lead rows per model;
- 25 legal rolling-origin folds;
- zero target failures;
- zero fold failures.

## Required metrics

### Proper quantile scores

For q10, q25, q50, q75, q90 and q97, report:

- pinball loss overall;
- pinball loss by lead;
- TASK-047 minus TASK-012 absolute and percentage difference;
- fold-level differences;
- player-block bootstrap 95% confidence interval for the pooled difference.

Also report the unweighted mean pinball loss across the six declared quantiles as the primary uncertainty score.

### Quantile calibration

For every declared quantile, report empirical `P(actual_points <= predicted_quantile)` against its nominal level:

- overall;
- by lead;
- by broad position;
- by prior-history cohort: zero prior games, under 50 prior games, and 50-plus prior games.

Report signed calibration error and absolute calibration error. Ties at an exact forecast quantile must be handled consistently and documented.

### Interval coverage and sharpness

Report coverage and mean width for:

- q25–q75, nominal 50%;
- q10–q90, nominal 80%;
- q10–q97, nominal 87%, explicitly labelled asymmetric.

Report overall, by lead and by broad position. Coverage without width is insufficient.

### Structural zero-mass diagnostic

Using locked target games and points, report by lead:

- actual zero-game/zero-point rows;
- actual one-to-five-game rows with positive points;
- meaningful rows with at least six games;
- proportion of each predicted quantile equal to zero;
- pinball loss and empirical quantile calibration separately for those three realised cohorts.

Explicitly assess whether using `1 - p_meaningful` as exact zero-point mass is compatible with the locked total-points target.

### Integrity checks

Prove:

- prediction keys are identical between TASK-012, TASK-047 and targets;
- target `points` is used directly;
- quantiles are non-negative and non-crossing;
- point forecasts and every non-uncertainty output are unchanged from merged TASK-047;
- the audit creates no model artifacts and performs no fitting.

## Predeclared acceptance gates

TASK-047 uncertainty outputs may be accepted only if all of the following hold:

1. Primary mean pinball loss does not worsen versus TASK-012 by more than 1% overall, and its player-block bootstrap interval does not support a material degradation greater than 1%.
2. No individual declared quantile worsens pinball loss by more than 5% overall.
3. Overall absolute quantile calibration error averages no more than 0.03 across the six quantiles.
4. Overall q25–q75 coverage lies within 0.47–0.53 and q10–q90 coverage lies within 0.77–0.83.
5. No lead has q25–q75 or q10–q90 absolute coverage error greater than 0.06.
6. No broad-position or prior-history subgroup with `n >= 200` has absolute coverage error greater than 0.10 for either central interval.
7. The one-to-five-game positive-points cohort does not reveal a structural incompatibility that makes the reported quantiles misleading.

Failure of any gate keeps uncertainty blocked. Do not repair, recalibrate, blend or change the distribution in TASK-048. Record the failed gate and formulate one separate TASK-049 hypothesis if a repair is justified.

## Required outputs

Add:

- `vnext/analyse_task048_ridge_uncertainty.py`;
- focused tests under `vnext/tests/`;
- concise evidence under `reports/task-048-ridge-uncertainty-calibration-audit/`;
- reproduction commands and an artifact manifest;
- a task conclusion in this document;
- durable project-state and decision-log updates after the result is known.

Do not commit bulky duplicate prediction files when they can be rebuilt from existing commands.

## Testing

Run:

```bash
python vnext/run_task012_established_ceiling_folds.py --out build/task012-candidate --rebuild
python vnext/run_task047_pooled_ridge_folds.py --out build/task047-pooled-ridge-conditional-average --rebuild
python vnext/analyse_task048_ridge_uncertainty.py --baseline build/task012-candidate/vnext_predictions.csv --candidate build/task047-pooled-ridge-conditional-average/vnext_predictions.csv --targets build/task-003-cohorts/targets.csv --features build/task047-pooled-ridge-conditional-average/training_dataset.csv --out reports/task-048-ridge-uncertainty-calibration-audit
cd vnext && pytest -q
python scripts/verify_legacy_manifest.py
python scripts/generate_handover.py --check
```

The known unrelated `tests/test_player_comparison_export.py::test_builds_three_values_from_one_forecast_vector` failure must be reported explicitly if it remains, but TASK-048-specific tests must pass.
