# TASK-003L — Independent validation of TASK-003K

## Scope

TASK-003L is a diagnostic-only independent validation of the TASK-003K event-logistic candidate. It must not modify TASK-003K model code, model fitting, preprocessing, validation protocol, production forecasts, values, keeper utility or UI behaviour.

## Validator

`vnext/validate_task003l_independent.py` reads completed current and TASK-003K fold artifacts, predictions, the exact locked 20,094-row cohort and PR #19 evidence. It validates:

- exactly one prediction row per `player_key`, `origin_year`, `lead`;
- exact prediction-key equality against the locked cohort;
- all 25 legal rolling-origin folds;
- unchanged preprocessing, feature representation, conditional games model, conditional average model, threshold models, threshold calibrators, residual scales, cohorts, targets and fold protocol;
- allowed changes to the fitted event model and fitted event calibrator only;
- raw and calibrated meaningful-season Brier/log-loss, AUC, probability bias, games MAE and points MAE by fold and lead;
- paired player-block bootstrap intervals;
- zero-history eventual-player versus eventual-zero results;
- qualifying subgroup results, the original locked regression rows and the age-30+ lead-5 regression;
- explicit tolerance-based comparisons against PR #19 evidence.

## Current status

Latest review requested rebasing/retargeting onto `agent/task003k-event-logistic` and running against PR #19 actual code and evidence. In this workspace, fetching `agent/task003k-event-logistic`, PR #19, and PR #20 from GitHub failed because the repository requires credentials that are unavailable to the non-interactive environment. No local `agent/task003k-event-logistic` branch, `build/task-003k-candidate-folds`, or `reports/task-003k-event-logistic` directories existed. The committed machine-readable TASK-003L report is therefore `validation incomplete` with exact missing evidence and missing base branch, not a pass.

Do not interpret this as independent validation of TASK-003K. It is a reproducible validator plus an explicit incomplete status until the PR #19 branch/artifacts/evidence are present in the workspace or supplied as inputs.

## Reproduction

```bash
python vnext/validate_task003l_independent.py \
  --out reports/task-003l-independent-validation \
  --cohort-dir build/task-003b-cohorts \
  --current-run-dir build/task-003b-vnext-folds \
  --current-predictions build/task-003b-vnext-folds/vnext_predictions.csv \
  --candidate-run-dir build/task-003k-candidate-folds \
  --candidate-predictions build/task-003k-candidate-folds/vnext_predictions.csv \
  --evidence-dir reports/task-003k-event-logistic \
  --bootstrap-repetitions 1000 \
  --tolerance 1e-9 \
  --required-base-branch agent/task003k-event-logistic
```
