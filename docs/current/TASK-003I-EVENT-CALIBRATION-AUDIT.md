# TASK-003I — Meaningful-season event calibration audit

## Scope

Diagnostic only. No model fitting, validation protocol, production forecast, value, keeper utility or UI change. No named-player tuning.

## Question

TASK-003G identified meaningful-season probability as one contributor to established-player opportunity underprediction. This audit tests whether the shortfall originates in the raw meaningful-season classifier scores or in the temporal isotonic calibration layer.

## Result

Established-player underprediction is primarily visible before isotonic calibration. Across the 15 locked material slice/lead rows, 14 have raw classifier mean probability more than one percentage point below the realised meaningful-season rate. The exception is zero prior games at lead 1, where both raw and calibrated probabilities exceed the realised rate.

Temporal isotonic calibration is not the main source of the established-player shortfall. It moves pooled locked-slice probabilities downward in nine rows and upward in six, but the raw classifier is already low for the career-stage, ruck and late/undrafted slices of concern.

The largest raw probability gaps include:

- age 24–26, lead 3: **−13.0 percentage points**;
- tenure 4–5, lead 4: **−10.4 points**;
- age 24–26, lead 4: **−11.0 points**;
- late/undrafted, lead 1: **−10.8 points**.

Isotonic calibration can improve Brier score despite leaving or increasing mean underprediction, because it changes row-level probability shape rather than merely shifting the mean.

## Decision implications

1. Do not pursue an event-calibrator-only model change as the primary remedy for these regressions.
2. A future event-probability experiment should target classifier signal, specification or model family while retaining leakage-safe temporal calibration.
3. Keep event-classifier changes separate from conditional magnitude or feature-support changes.
4. Do not introduce slice-specific probability offsets or named-player rules.

No model change is authorised by this audit.

## Evidence

The original generated evidence remains under `reports/task-003h/` so its committed hashes and reproduction record are preserved:

- `locked_slice_summary.csv`;
- `locked_slice_fold_summary.csv`;
- `fold_lead_summary.csv`;
- `provenance.json`.

That directory is historical evidence for TASK-003I; TASK-003H is now reserved for the conditional-magnitude calibration experiment.

## Reproduction

```bash
python vnext/build_historical_cohorts.py --out build/task-003i/cohorts
python vnext/run_historical_folds.py \
  --cohort-dir build/task-003i/cohorts \
  --out build/task-003i/vnext
python vnext/run_comparison.py \
  --out build/task-003i/comparison \
  --vnext-predictions build/task-003i/vnext/vnext_predictions.csv \
  --bootstrap-repetitions 100
python vnext/analyse_task003h_calibration.py \
  --comparison-dir build/task-003i/comparison \
  --folds-dir build/task-003i/vnext \
  --out build/task-003i/calibration
```

The diagnostic script retains its original filename to preserve the committed evidence provenance; its authoritative task designation is TASK-003I.
