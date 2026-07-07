# TASK-003H — Conditional magnitude calibration experiment

## State

`rejected experiment` — not eligible for production or integration into the active vNext model.

## Hypothesis

The current conditional games and conditional average regressors systematically underpredict some meaningful outcomes. Applying monotonic calibration learned only from the existing temporally held-out calibration rows might reduce games and total-points error without changing meaningful-season probabilities, features, cohorts or the rolling-origin protocol.

## Single model change tested

For each legal lead/origin fold:

1. train the existing event, games, average and threshold models unchanged;
2. use the existing temporal calibration partition;
3. restrict conditional calibration to rows with a realised meaningful season;
4. fit separate monotonic isotonic mappings for raw conditional games and raw conditional average;
5. recompute conditional residual scales after calibration.

No slice-specific or named-player rules were used.

## Unchanged layers

- meaningful-season classifier and isotonic probability calibrator;
- threshold classifiers and calibrators;
- feature set and preprocessing;
- authoritative historical cohorts and targets;
- 25 legal rolling-origin folds and 20,094 rows per model;
- unchanged current fold-specific vNext comparator;
- scoring metrics, locked slices and player-block bootstrap method;
- legacy production engine, current values, keeper utility and UI.

All meaningful-season and threshold probability outputs matched current vNext exactly.

## Predeclared decision rules

The candidate could advance only if pooled total-points MAE improved with a paired player-block 95% interval wholly below zero, pooled games MAE did not worsen, no lead was more than 3% worse on total-points MAE, and subgroup and zero-history trade-offs remained acceptable.

Failure of the primary total-points bootstrap rule rejected the hypothesis in its tested form.

## Result

The calibrators worked mechanically on the conditional targets but failed the unconditional forecasting objectives.

| Metric | Current vNext | Candidate | Change |
|---|---:|---:|---:|
| Meaningful-season Brier | 0.17762 | 0.17762 | unchanged |
| Games MAE | 5.88199 | 6.08317 | **3.42% worse** |
| Total-points MAE | 452.366 | 469.970 | **3.89% worse** |
| Conditional-games MAE, meaningful outcomes | 5.24118 | 4.66777 | **10.94% better** |
| Conditional-average MAE, meaningful outcomes | 14.55972 | 12.52581 | **13.97% better** |

Paired player-block bootstrap differences are candidate minus current:

- games MAE: **+0.201**, 95% interval **+0.157 to +0.251**;
- total-points MAE: **+17.604**, 95% interval **+13.294 to +22.471**;
- probability candidate is better on either primary MAE: **0.0%** across 1,000 draws.

Total-points MAE worsened at every lead:

- lead 1: 1.92%;
- lead 2: 2.99%;
- lead 3: 3.23%;
- lead 4: 6.71%;
- lead 5: 6.87%.

The candidate created 69 qualifying slice/lead regressions greater than 3% and no improvements greater than 3%.

## Why the hypothesis failed

The candidate increased conditional magnitudes for every player carrying non-zero meaningful-season probability. This helped rows that later produced meaningful outcomes, but also increased forecasts for the much larger set of players who remained at zero.

The zero-history trade-off is decisive:

- eventual players improved at every lead;
- eventual-zero players received much larger positive forecasts;
- pooled zero-history total-points MAE rose from 181.98 to 238.79;
- the locked zero-history slices worsened by 27.6% to 36.6% across leads.

This demonstrates that calibrating conditional means independently of the latent playing state is not sufficient. The conditional target sample is selected, while the final forecast is an unconditional mixture. Improving conditional fit can therefore worsen the proper operational objectives.

## Decision

Reject unconditional post-hoc isotonic calibration of conditional games and conditional average.

Do not tune calibration strength, slice rules or named-player exceptions against these results. The next model investigation should use the independent audits to decide between:

1. improving raw classifier and conditional-model representation;
2. introducing a better state or hurdle structure for zero-history and low-support profiles;
3. changing conditional model families rather than applying broad post-hoc mean inflation.

The current fold-specific vNext model remains unchanged.

## Evidence

Compact accepted evidence is under `reports/task-003h-conditional-calibration/`.

Source workflow run: `28862889443`.

Artifact SHA-256 values:

- cohorts: `f86eb007a0e53f586ef976a3082055445eb4801b148d4f5c6cf541c9e1e192a2`;
- unchanged current vNext: `422596a97bb931286974385a7351e992ddbbad5d5408313176a341de78f7f028`;
- calibrated candidate: `0fe2d1c08ae9aeb89c1f6497c1458f1465498cc95ff6fe3304eedebed17fe55b`.

## Reproduction

```bash
python vnext/build_historical_cohorts.py --out build/task-003h-cohorts
python vnext/run_historical_folds.py \
  --out build/task-003h-current \
  --cohort-dir build/task-003h-cohorts
python vnext/run_task003h_folds.py \
  --out build/task-003h-candidate \
  --cohort-dir build/task-003h-cohorts
python vnext/run_task003h_comparison.py \
  --current-predictions build/task-003h-current/vnext_predictions.csv \
  --candidate-predictions build/task-003h-candidate/candidate_predictions.csv \
  --cohort-dir build/task-003h-cohorts \
  --out build/task-003h-comparison
```
