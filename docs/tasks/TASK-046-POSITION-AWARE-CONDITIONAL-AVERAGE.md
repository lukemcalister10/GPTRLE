# TASK-046 — Position-aware conditional-average candidate

## Status

Candidate complete against the locked rolling-origin benchmark. This PR changes only the conditional-average model layer under `vnext/` and adds benchmark evidence under `reports/task-046-position-aware-conditional-average/`.

## Hypothesis

The TASK-012 conditional-average model has a systematic broad-position defect, especially for rucks. The isolated candidate fits broad-position conditional-average regressors inside every rolling-origin training fold, with a pooled regressor available as the fallback when a position-fold meaningful-season sample is insufficient.

## Model layer changed

- Conditional-average regressor only: `vnext/model_artifacts_position_aware_conditional_average.py`.
- Locked fold runner only wires that model into the existing benchmark: `vnext/run_task046_position_aware_folds.py`.
- The meaningful-season event model, conditional-games model, benchmark protocol, keeper utility, replacement-aware value, future option value, legacy engine and frozen Claude files are unchanged.

## Reproduction commands

```bash
python vnext/run_task012_established_ceiling_folds.py --out build/task012-candidate
python vnext/run_task046_position_aware_folds.py --out build/task046-position-aware-conditional-average --rebuild
python vnext/analyse_task046_position_aware.py \
  --baseline build/task012-candidate/vnext_predictions.csv \
  --candidate build/task046-position-aware-conditional-average/vnext_predictions.csv \
  --targets build/task-003-cohorts/targets.csv \
  --features build/task046-position-aware-conditional-average/training_dataset.csv \
  --out reports/task-046-position-aware-conditional-average
```

## Overall before/after

|model|n|mae|bias|actual_avg|pred_avg|
|---|---|---|---|---|---|
|task012|10848|14.61|-6.54|72.56|66.02|
|task046|10848|11.90|2.22|72.56|74.79|

## Ruck before/after by lead

|model|lead|n|mae|bias|actual_avg|pred_avg|
|---|---|---|---|---|---|---|
|task012|1|196|21.56|-20.45|86.10|65.65|
|task012|2|171|28.09|-27.35|85.74|58.38|
|task012|3|139|33.74|-33.27|86.44|53.17|
|task012|4|101|40.10|-39.43|88.95|49.53|
|task012|5|68|47.63|-46.90|91.46|44.56|
|task046|1|196|11.73|-1.98|86.10|84.12|
|task046|2|171|13.37|-2.13|85.74|83.61|
|task046|3|139|13.93|-2.10|86.44|84.33|
|task046|4|101|14.08|-4.99|88.95|83.97|
|task046|5|68|16.09|-9.62|91.46|81.85|

## Elite-prior before/after by lead

|model|lead|n|mae|bias|actual_avg|pred_avg|
|---|---|---|---|---|---|---|
|task012|1|103|13.15|-10.55|108.35|97.80|
|task012|2|87|17.41|-14.28|105.21|90.93|
|task012|3|70|18.80|-14.78|101.18|86.40|
|task012|4|54|20.77|-14.60|97.94|83.35|
|task012|5|39|21.11|-11.41|94.14|82.72|
|task046|1|103|11.10|-7.15|108.35|101.20|
|task046|2|87|12.80|-6.94|105.21|98.27|
|task046|3|70|13.94|-6.10|101.18|95.09|
|task046|4|54|16.36|-7.28|97.94|90.66|
|task046|5|39|18.68|-6.83|94.14|87.30|

## Required evidence artifacts

The report directory contains concise CSV tables for:

- conditional-average MAE and bias by lead;
- whole-population MAE and bias;
- ruck MAE and bias by lead;
- DEF, MID and FWD results by lead;
- established-player results;
- elite-prior results;
- calibration by predicted-average band;
- position-by-lead diagnostics;
- target and fold failures in `summary.json`;
- largest current-board rises and falls as diagnostics only.

## Decision notes

The candidate materially improves ruck MAE and bias at every lead and improves the upper-tail elite-prior slice while also improving whole-population MAE. Whole-population bias moves from underprediction to mild overprediction, so review should focus on calibration-band and non-ruck position tables before acceptance.
