# TASK-003H — Conditional regressor support diagnosis

## Scope

Diagnostic only. This task adds tooling to inspect whether zero-prior-games players, rucks and established regressing cohorts sit outside the support used by the conditional games and conditional average regressors.

No model fitting, validation protocol, production forecast, current value, keeper utility or UI behaviour is changed.

## Diagnostic question

Compare, for each legal fold, three populations:

1. meaningful fit rows used by the conditional games and conditional average regressors;
2. meaningful temporal calibration rows used for later residual/calibration diagnostics;
3. benchmark prediction rows for zero-prior-games, ruck and established-regressing cohorts.

The comparison is performed on raw features and on the transformed design matrix produced by the persisted fold preprocessor.

## Risk classes reported

- **Imputation risk:** probe missing rates are compared with reference missing rates for every numeric and categorical feature.
- **Scaling/extrapolation risk:** benchmark raw values outside meaningful-row minima/maxima and 1st/99th percentiles are counted.
- **Unseen-category risk:** benchmark categorical levels absent from the meaningful reference rows are listed; the current one-hot encoder ignores unknown categories at transform time.
- **Transformed-support risk:** nearest-neighbour distance and transformed-vector norm exceedances compare benchmark rows with meaningful reference rows after imputation, scaling and encoding.

## Reproduction

```bash
python vnext/analyse_task003h_support.py \
  --fold-dir build/task-003b-vnext-folds \
  --comparison-dir build/task-003e/comparison \
  --out build/task-003h
```

Expected outputs:

- `transformed_support_summary.csv`
- `raw_feature_support.csv`
- `support_diagnosis.md`
- `manifest.json`

## Interpretation guardrails

This is a support diagnostic, not a model selection result. It can identify plausible imputation, scaling, unseen-category and extrapolation risks, but it must not be used to tune named players or to change the locked validation protocol in the same pull request.
