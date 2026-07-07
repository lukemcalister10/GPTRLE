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

The existing PR is stacked on `agent/task003k-event-logistic`. In GitHub Actions the stacked PR checkout already contains the TASK-003K candidate code and evidence, so the validator does not require a local base branch. The dedicated TASK-003L workflow checks out `vnext` separately to build unchanged current-vNext folds, builds candidate folds from the stacked PR checkout, runs the validator with `--require-complete`, runs the vNext test suite, and uploads validation outputs as a workflow artifact. With `--require-complete`, the workflow verdict is always either `independent validation passed` or `independent validation failed`.

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
  --require-complete
```
