# TASK-003H — Conditional magnitude calibration experiment

## State

`experiment` — not eligible for production.

## Hypothesis

The current conditional games and conditional average regressors systematically underpredict some meaningful outcomes. Applying monotonic calibration learned only from the existing temporally held-out calibration rows will reduce games and total-points error without changing meaningful-season probabilities, features, cohorts or the rolling-origin protocol.

## Single model change

For each legal lead/origin fold:

1. train the existing event, games, average and threshold models unchanged;
2. use the existing temporal calibration partition;
3. restrict conditional calibration to rows with a realised meaningful season;
4. fit separate monotonic isotonic mappings for raw conditional games and raw conditional average;
5. recompute conditional residual scales after calibration.

No slice-specific or named-player rules are permitted.

## Unchanged layers

- meaningful-season classifier and isotonic probability calibrator;
- threshold classifiers and calibrators;
- feature set and preprocessing;
- authoritative historical cohorts and targets;
- 25 legal rolling-origin folds;
- current vNext comparator;
- scoring metrics, slices and player-block bootstrap method;
- legacy production engine, current values, keeper utility and UI.

## Leakage guardrail

Each conditional calibrator is fitted only on the fold's existing temporal calibration rows. Those rows already satisfy the locked requirement that their target seasons end before the test origin. Candidate and current probability outputs must match to within `1e-12` on every prediction row.

## Predeclared decision rules

The candidate may advance from `experiment` only if all of the following hold:

1. meaningful-season and threshold probability outputs are unchanged;
2. pooled total-points MAE improves and its paired player-block bootstrap 95% interval is wholly below zero versus current vNext;
3. pooled games MAE does not worsen, with particular attention to its paired bootstrap interval;
4. no lead is more than 3% worse on total-points MAE;
5. no qualifying locked slice is more than 5% worse on total-points MAE without a documented broad mechanism;
6. conditional games and average calibration evidence supports the proposed mechanism;
7. zero-history eventual-player improvement is not achieved through an unacceptable increase for players who remain at zero;
8. full-population current-board effects are reviewed before acceptance.

Failure of the primary total-points bootstrap rule rejects the hypothesis in its current form. Results will not be tuned to individual players or selected slices.

## Evidence outputs

The workflow produces:

- pooled and lead metrics;
- fold differences versus unchanged current vNext;
- paired player-block bootstrap intervals;
- probability and conditional reliability tables;
- conditional games and average bias/MAE;
- locked slice differences and material regression counts;
- zero-history results split by eventual playing outcome;
- artifact manifests and deterministic input/output hashes.

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
