# TASK-003K — Independent validation scaffold

## Scope

This branch is an independent, read-only validation scaffold for the TASK-003K candidate. It does not modify model fitting, preprocessing, feature construction, validation protocol, production forecasts, values, keeper utility or UI behaviour.

The candidate branch/PR was not available in this environment because GitHub authentication was unavailable, so all candidate-dependent checks are explicitly marked pending rather than inferred.

## Validation harness

`vnext/validate_task003k_candidate.py` compares an existing current vNext fold run with an existing TASK-003K fold run. When candidate artifacts are supplied it checks:

- the locked target cohort remains exactly 20,094 prediction rows;
- both prediction files exactly match the locked prediction key set;
- all 25 fold cutoffs match the locked rolling-origin protocol;
- only the meaningful-season `event_model` component changes across fold artifacts;
- current and candidate metrics are independently recomputed on identical targets;
- Brier score, log loss, AUC, games MAE and total-points MAE are written by lead and summary.

The scaffold also records pending status for candidate-only/manual checks that require candidate PR artifacts or provenance:

- raw event probability reproduction;
- player-block bootstrap reproduction;
- zero-history eventual-player versus eventual-zero trade-off;
- material subgroup regression audit;
- current-board tuning guard.

## Reproduction

Current-only scaffold run, useful before the TASK-003K candidate exists:

```bash
python vnext/validate_task003k_candidate.py \
  --out build/task-003k-validation \
  --current-run-dir build/task-003b-vnext-folds \
  --current-predictions build/task-003b-vnext-folds/vnext_predictions.csv
```

Candidate run once artifacts are available:

```bash
python vnext/validate_task003k_candidate.py \
  --out build/task-003k-validation \
  --current-run-dir build/task-003b-vnext-folds \
  --current-predictions build/task-003b-vnext-folds/vnext_predictions.csv \
  --candidate-run-dir build/task-003k-candidate-folds \
  --candidate-predictions build/task-003k-candidate-folds/vnext_predictions.csv
```

## Expected interpretation

A passing scaffold result is not evidence that TASK-003K is better. It only verifies protocol invariants and independently reproduces diagnostic metrics. Acceptance still requires the candidate PR's declared outcome-based validation evidence.
