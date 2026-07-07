# TASK-003K — Meaningful-season classifier model-family experiment

## State

`experiment` — not eligible for production.

## Question

TASK-003I showed that meaningful-season underprediction in 14 of the 15 locked material regression rows is already present in the raw classifier output. This experiment tests whether the current stochastic-gradient logistic classifier is the source of excessive probability compression.

## Single change

Replace only the meaningful-season event classifier:

- current: `SGDClassifier(loss="log_loss", alpha=0.0008)`;
- candidate: `LogisticRegression(C=0.35, solver="lbfgs", penalty="l2", max_iter=500)`.

The candidate specification is taken from the existing repository-backed model in `vnext/evaluate_v3_fast.py`. It is fixed before results and will not be tuned in this PR.

## Unchanged

- feature columns and preprocessing;
- temporal fit/calibration split;
- fold-specific isotonic event calibration;
- conditional games and conditional-average regressors;
- their residual scales;
- threshold classifiers and calibrators;
- quantile construction;
- historical cohorts, targets and 25 rolling-origin folds;
- metrics, locked slices and player-block bootstrap method;
- production, current values, keeper utility and UI.

The comparison fails if conditional games, conditional average or any threshold probability differs between current and candidate predictions.

## Required evidence

On the exact 20,094 locked rows:

- pooled, lead and fold raw event Brier, log loss, AUC and bias;
- the same metrics after temporal isotonic calibration;
- games and total-points MAE;
- paired player-block bootstrap intervals;
- reliability before and after calibration;
- all qualifying slice changes;
- explicit results for the original 15 regression rows;
- zero-history eventual-player versus eventual-zero results;
- largest current-board effects before any acceptance decision.

## Predeclared historical rules

Historical evidence is supportive only if:

1. calibrated meaningful-season Brier improves;
2. calibrated event log loss improves;
3. games MAE is not more than 1% worse;
4. total-points MAE is not more than 1% worse;
5. bootstrap evidence and fold stability do not contradict the pooled result;
6. established-player improvements are not purchased through unacceptable zero-history false positives;
7. no broad new subgroup regression is concealed by pooled improvement.

Passing the historical rules does not itself authorise acceptance. Current-board effects and the independent validation must also be reviewed.

## Rejection discipline

If the candidate fails, record the result and retain current fold-specific vNext. Do not tune `C`, class weights, solver choice, age offsets, slice corrections or a second classifier in this PR.

## Reproduction

```bash
python vnext/build_historical_cohorts.py --out build/task-003k-cohorts
python vnext/run_historical_folds.py \
  --out build/task-003k-current \
  --cohort-dir build/task-003k-cohorts
python vnext/run_task003k_folds.py \
  --out build/task-003k-candidate \
  --cohort-dir build/task-003k-cohorts
python vnext/run_task003k_comparison.py \
  --current-predictions build/task-003k-current/vnext_predictions.csv \
  --candidate-predictions build/task-003k-candidate/vnext_predictions.csv \
  --current-folds build/task-003k-current \
  --candidate-folds build/task-003k-candidate \
  --cohort-dir build/task-003k-cohorts \
  --out build/task-003k-comparison
```
