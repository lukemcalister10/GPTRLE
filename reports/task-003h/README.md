# TASK-003I — Meaningful-season event calibration audit

## Historical evidence path

This directory retains its original generated path, `reports/task-003h/`, so the committed evidence hashes and reproduction record remain unchanged. Its authoritative task designation is now **TASK-003I**. TASK-003H is reserved for the separate conditional-magnitude calibration experiment.

## Scope

Diagnostic only. This audit separates fold-specific raw meaningful-season classifier output from the temporal isotonic calibrated output. It does not change model fitting, the locked validation protocol, production inference, values, keeper utility or UI, and it does not tune to named players.

## Finding

For the locked TASK-003F material slice/lead regressions, established-player underprediction is mostly already present in the raw classifier output. Isotonic calibration moves probabilities only a few points in either direction and does not explain the broad shortfall.

Across the 15 locked material slice/lead rows:

- 14 rows have raw classifier mean probability more than one percentage point below the realised rate;
- zero prior games at lead 1 is the exception, with both raw and calibrated probability above the realised rate;
- isotonic calibration moves pooled probability down for nine rows and up for six;
- the largest raw gaps include age 24–26 leads 3–4, tenure 4–5 leads 3–4 and late/undrafted lead 1.

## Evidence tables

- `locked_slice_summary.csv`: one row per locked material slice/lead, comparing actual rate, raw classifier mean, calibrated mean, Brier, log loss and AUC;
- `locked_slice_fold_summary.csv`: the same comparison split by legal origin fold;
- `fold_lead_summary.csv`: full fold/lead audit for all vNext predictions;
- `provenance.json`: reproduction commands and output hashes.

## Interpretation

The event-probability layer contributes to established-player underprediction, but the audit points to classifier signal/specification rather than isotonic calibration as the primary origin. A future model-changing PR should test classifier changes separately from conditional magnitude or feature-support changes and must not use slice-specific offsets.

## Reproduction

The evidence was originally generated under `build/task-003h/`; those commands remain recorded in `provenance.json`. Equivalent TASK-003I paths are documented in `docs/current/TASK-003I-EVENT-CALIBRATION-AUDIT.md`.
