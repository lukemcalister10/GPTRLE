# TASK-045 — Conditional-average compression audit

## Status

Diagnostic audit completed. No model, validation protocol, keeper utility, export path, production board or frozen legacy file is changed.

## Objective

Test whether the accepted conditional-average layer systematically compresses established elite players, especially at lead one and especially for rucks, using the locked rolling-origin historical benchmark rather than any named current player.

## Evidence source

The audit consumes leakage-safe TASK-012 fold predictions and the locked TASK-003 target table:

```bash
python vnext/run_task012_established_ceiling_folds.py --out build/task012-candidate
python vnext/analyse_task045_conditional_compression.py \
  --predictions build/task012-candidate/vnext_predictions.csv \
  --targets build/task-003-cohorts/targets.csv \
  --features build/task012-candidate/training_dataset.csv \
  --out reports/task-045-conditional-average-compression-audit
```

The audit includes only rows with meaningful realised target seasons for conditional-average scoring. It checks 10,848 meaningful target rows from 20,094 locked prediction rows. Fold target failures remain zero.

## Whole-population result

The conditional-average layer is materially biased low on meaningful target seasons:

- overall conditional-average MAE: 14.61;
- overall bias, predicted minus actual: -6.54;
- average shrinkage from recent demonstrated average to predicted conditional average: -1.11.

Bias worsens with forecast lead:

| Lead | Rows | MAE | Bias | Actual avg | Predicted avg | Shrinkage from recent avg |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3,489 | 11.82 | -3.79 | 71.31 | 67.52 | -0.96 |
| 2 | 2,774 | 13.75 | -5.17 | 72.18 | 67.01 | +0.10 |
| 3 | 2,107 | 15.68 | -7.33 | 73.08 | 65.75 | -0.62 |
| 4 | 1,489 | 17.66 | -10.01 | 74.11 | 64.10 | -2.36 |
| 5 | 989 | 20.01 | -13.17 | 74.64 | 61.47 | -4.20 |

## Upper-tail compression

The audit strongly supports upper-tail compression. Players with recent demonstrated averages of at least 105 are underpredicted at every lead:

| Lead | Rows | MAE | Bias | Actual avg | Predicted avg | Shrinkage from recent avg |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 103 | 13.15 | -10.55 | 108.35 | 97.80 | -13.12 |
| 2 | 87 | 17.41 | -14.28 | 105.21 | 90.93 | -20.23 |
| 3 | 70 | 18.80 | -14.78 | 101.18 | 86.40 | -25.01 |
| 4 | 54 | 20.77 | -14.60 | 97.94 | 83.35 | -27.97 |
| 5 | 39 | 21.11 | -11.41 | 94.14 | 82.72 | -28.26 |

The pattern is not a named-player anomaly: it appears historically across the locked folds and broadens with lead through increasing shrinkage from demonstrated scoring.

## Ruck-specific finding

The audit also supports a distinct ruck problem. Ruck conditional averages are underpredicted much more than other broad positions:

| Lead | Ruck rows | Ruck MAE | Ruck bias | Actual avg | Predicted avg | Shrinkage from recent avg |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 196 | 21.56 | -20.45 | 86.10 | 65.65 | -14.00 |
| 2 | 171 | 28.09 | -27.35 | 85.74 | 58.38 | -13.66 |
| 3 | 139 | 33.74 | -33.27 | 86.44 | 53.17 | -12.86 |
| 4 | 101 | 40.10 | -39.43 | 88.95 | 49.53 | -15.00 |
| 5 | 68 | 47.63 | -46.90 | 91.46 | 44.56 | -14.72 |

This is large enough that the first corrective modelling hypothesis should consider a position-aware conditional-average mechanism, not a player-specific override.

## Interpretation

The model appears to:

- compress the upper tail;
- underpredict historically demonstrated elite producers;
- underpredict rucks as a broad position group;
- increasingly regress conditional averages downward at longer leads;
- leave enough evidence that the current named-player ruck concern is probably a visible instance of a broader historical mechanism, not an isolated case.

The audit alone does not prove which repair should be accepted. The next PR should test one isolated corrective hypothesis, with the current evidence pointing most defensibly toward a position-aware and demonstrated-scoring-aware conditional-average repair learned inside each training fold.

## Artifacts

The report under `reports/task-045-conditional-average-compression-audit/` contains:

- `summary.json`;
- `metrics_by_lead.csv`;
- `calibration_by_predicted_avg_band.csv`;
- `error_by_prior_avg_band.csv`;
- `error_by_establishment.csv`;
- `error_by_elite_prior.csv`;
- `error_by_position.csv`;
- `error_by_age_band.csv`;
- `shrinkage_by_prior_avg_band.csv`;
- `largest_underpredictions.csv` and `largest_overpredictions.csv` as diagnostics only.

## Decision

Proceed to a separate single-hypothesis candidate experiment. Do not tune to Tristan Xerri or any current named player. Do not combine this with future option value.
