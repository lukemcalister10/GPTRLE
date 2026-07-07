# TASK-003H — Meaningful-season probability calibration audit

## Scope

Diagnostic only. This audit separates fold-specific raw meaningful-season classifier output from the temporal isotonic calibrated output. It does not change model fitting, the locked validation protocol, production inference, values, keeper utility or UI, and it does not tune to named players.

## Finding

For the locked TASK-003F material slice/lead regressions, established-player underprediction is mostly already present in the raw classifier output. Isotonic calibration usually moves probabilities only a few points and sometimes improves the raw classifier underprediction, but it does not explain the established-player shortfall.

Across the 15 locked material slice/lead rows:

- 14 rows were classified as `raw_classifier_underpredicts` at a 1 percentage point tolerance.
- 1 row, zero prior games at lead 1, was not a material probability-underprediction case; raw and calibrated probabilities were both above the realised event rate.
- Isotonic calibration moved the pooled locked-slice probability down for 9 rows and up for 6 rows.
- The largest established-player gaps were age 24-26 lead 3, age 24-26 lead 4, tenure 4-5 lead 4 and tenure 4-5 lead 3; all were raw-classifier underprediction cases before calibration.

## Evidence tables

- `locked_slice_summary.csv`: one row per locked TASK-003F material slice/lead, comparing actual event rate, raw classifier mean, calibrated mean, Brier, log loss and AUC.
- `locked_slice_fold_summary.csv`: same comparison split by origin fold.
- `fold_lead_summary.csv`: full fold/lead audit for all vNext locked predictions, not limited to material slices.
- `provenance.json`: reproduction commands and output hashes.

## Interpretation

The probability layer still contributes to established early/mid-career opportunity underprediction, but this audit points to the classifier score itself rather than temporal isotonic calibration as the primary origin. A later model-changing PR should therefore treat classifier signal/specification and conditional magnitude calibration as separate hypotheses, and should not patch this with slice-specific overrides.

## Reproduction

```bash
python vnext/build_historical_cohorts.py --out build/task-003h/cohorts
python vnext/run_historical_folds.py --cohort-dir build/task-003h/cohorts --out build/task-003h/vnext
python vnext/run_comparison.py --out build/task-003h/comparison --vnext-predictions build/task-003h/vnext/vnext_predictions.csv --bootstrap-repetitions 100
python vnext/analyse_task003h_calibration.py --comparison-dir build/task-003h/comparison --folds-dir build/task-003h/vnext --out build/task-003h/calibration
```
