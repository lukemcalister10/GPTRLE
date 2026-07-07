# TASK-003J conditional-regressor support diagnosis

## Scope

Diagnostic only. No model, validation protocol, production forecast, current value, keeper utility or UI change. No named-player tuning.

The accepted TASK-003E cohort and current fold-specific vNext artifacts were compared with the meaningful fit and temporal calibration rows used by the conditional games and conditional-average regressors.

## Findings

### Zero-prior-games is not a general numeric extrapolation problem

Zero-history rows are the closest cohort to the meaningful training support after preprocessing:

- weighted median nearest-fit distance: **0.439**;
- weighted 90th percentile distance: **1.221**;
- transformed norm above the meaningful-fit 99th percentile: **0.0%**;
- numeric values outside meaningful-fit minima/maxima are negligible.

This rejects a simple explanation that zero-history conditional forecasts are low because their numeric feature vectors lie outside training support. Many zero-history profiles collapse to similar all-zero scoring-history vectors, so the likely issue is insufficient information and heterogeneous outcomes within an apparently well-supported feature pattern.

Categorical support is less complete: **15.8%** of zero-history probe rows contain at least one position or draft-type level unseen in the meaningful fit reference, principally newer draft pathways such as MSD, PDN and SSP and some `UNK` values.

### Rucks and older established players show the clearest support risk

Against meaningful fit rows:

- ruck weighted 90th percentile nearest distance: **3.745**; **18.0%** exceed the reference transformed-norm 99th percentile;
- age 27–29 weighted median distance: **2.338**; **32.4%** exceed the reference transformed-norm 99th percentile.

The main raw extrapolation drivers are tenure, seasons observed, qualifying seasons and total games. For age 27–29 rows, 30.1% are outside the meaningful-fit tenure range and 34.0% are outside the seasons-observed range. For rucks, the corresponding rates are 19.6% and 18.7%.

This is consistent with rolling-origin prediction rows containing more mature career histories than the meaningful rows available to some earlier fold fits.

### Other career-stage slices are mostly within support

- tenure 4–5 and age 21–23 are strongly within transformed and raw support;
- age 24–26 shows moderate exposure-history extrapolation, but far less than age 27–29;
- pick 61+ / undrafted has moderate transformed distance and a notable unseen-category rate of **15.1%**, mostly newer draft pathways.

## Interpretation

The 15 TASK-003F regressions do not share one support failure:

1. zero-history needs better state separation or informative pre-AFL features rather than broad magnitude inflation;
2. rucks and older established cohorts have a genuine career-exposure support issue worth addressing through a general model or feature hypothesis;
3. tenure 4–5 regressions cannot be explained by out-of-support inputs alone.

The rejected TASK-003H calibration experiment is consistent with this diagnosis: broad post-hoc increases improve eventual players but worsen the larger zero-outcome population.

## Evidence

- `support_aggregate.csv`: weighted transformed-support metrics by cohort and reference population;
- `raw_feature_drivers.csv`: leading raw numeric extrapolation features against meaningful fit rows;
- `categorical_unseen_summary.csv`: unseen categorical support by cohort;
- `provenance.json`: source artifacts and guardrails.

Full fold-level transformed and raw-feature tables are reproducible with `vnext/analyse_task003j_support.py`.
