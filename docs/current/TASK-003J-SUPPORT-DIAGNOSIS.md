# TASK-003J — Conditional regressor support diagnosis

## Scope

Diagnostic only. This task tests whether zero-prior-games players, rucks and career-stage regression cohorts lie outside the feature support used by the conditional games and conditional-average regressors.

No model fitting, validation protocol, production forecast, current value, keeper utility or UI behaviour is changed. No named-player tuning is used.

## Method

For every legal lead/origin fold, compare benchmark prediction rows with:

1. meaningful fit rows used to train the conditional regressors;
2. meaningful temporal calibration rows used for residual diagnostics.

The audit measures:

- raw numeric values outside reference minima/maxima and 1st/99th percentiles;
- missingness and unseen categorical levels;
- nearest-neighbour distance in the persisted transformed design matrix;
- transformed-vector norm exceedance versus the reference 99th percentile.

## Result

The regressions do not share one support mechanism.

### Zero prior games

Zero-history rows are numerically close to meaningful training support after preprocessing. Their weighted 90th percentile nearest-fit distance is 1.221 and none exceed the meaningful-fit transformed-norm 99th percentile. Numeric extrapolation is negligible.

The cohort does have categorical gaps: 15.8% contain at least one unseen position or draft-type level, principally newer MSD, PDN and SSP pathways and some unknown values.

The central zero-history problem is therefore unlikely to be ordinary numeric extrapolation. The current features map many materially different prospects to similar low-information vectors, leaving the model unable to distinguish eventual players from eventual zero outcomes.

### Rucks and age 27–29

These cohorts show the strongest support risk.

- Rucks: weighted 90th percentile nearest-fit distance 3.745; 18.0% exceed the reference transformed-norm 99th percentile.
- Age 27–29: weighted median distance 2.338; 32.4% exceed the reference transformed-norm 99th percentile.

The leading raw drivers are tenure, seasons observed, qualifying seasons and total games. These are career-exposure variables, consistent with later prediction rows extending beyond the mature histories available to some earlier rolling-origin fits.

### Other cohorts

- tenure 4–5 and age 21–23 are well within support;
- age 24–26 has moderate exposure extrapolation but substantially less than age 27–29;
- pick 61+ / undrafted has moderate transformed distance and a 15.1% unseen-category rate, again concentrated in newer draft pathways.

## Decision implications

1. Do not address zero-history with broad post-hoc magnitude inflation; TASK-003H demonstrated that this worsens unconditional MAE.
2. A future zero-history hypothesis should improve state separation or add leakage-safe pre-AFL information.
3. A separate ruck/older-career hypothesis may test more robust career-exposure representation or model structure.
4. Tenure 4–5 regressions require another explanation because those rows are not materially outside feature support.

No model change is authorised by this diagnostic.

## Evidence

Committed evidence is under `reports/task-003j-support-diagnosis/`.

## Reproduction

```bash
python vnext/analyse_task003j_support.py \
  --fold-dir build/task-003b-vnext-folds \
  --comparison-dir build/task-003e/comparison \
  --out build/task-003j-support
```

The full run writes:

- `transformed_support_summary.csv`;
- `raw_feature_support.csv`;
- `support_aggregate.csv`;
- `support_diagnosis.md`;
- `manifest.json`.
