# TASK-003H — Meaningful-season probability calibration audit

## Scope

Diagnostic only. No model fitting change, validation protocol change, production forecast change, value change, keeper utility change or UI change. No named-player tuning.

## Question

TASK-003G identified probability calibration as one plausible contributor to established-player opportunity underprediction. TASK-003H tests whether that shortfall originates in the raw meaningful-season classifier scores or in the temporal isotonic calibration layer.

## Result

Established-player meaningful-season underprediction is primarily visible before isotonic calibration. On the locked material slice/lead rows, 14 of 15 rows underpredict at the raw classifier stage using a 1 percentage point tolerance. The only exception is zero prior games at lead 1, where probability is not underpredicted.

Temporal isotonic calibration is not the main source of the established-player shortfall. It sometimes moves probabilities downward and sometimes upward, but the raw classifier is already below realised meaningful-season rates for the career-stage slices of concern.

## Evidence

Committed evidence is in `reports/task-003h/`:

- `locked_slice_summary.csv`
- `locked_slice_fold_summary.csv`
- `fold_lead_summary.csv`
- `provenance.json`

## Decision

Do not modify calibration, classifier training, validation, production exports or valuation layers in this diagnostic PR. Any future model PR should test one general hypothesis at a time and keep classifier probability changes separate from conditional magnitude calibration.
