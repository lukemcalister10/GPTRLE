# TASK-003G — Regression component attribution

## Scope

Diagnostic only. No model, protocol, production, value, keeper utility or UI change. No named-player tuning.

The accepted TASK-003E evidence was decomposed into meaningful-season probability, conditional games and conditional average.

## Findings

For age, tenure and late-draft slices, all three components underpredict. Meaningful-season probability is often the largest contributor, with conditional games second. Ruck lead 1 differs: conditional average is the largest contributor.

For players with no prior AFL games, meaningful-season probability is approximately correct or sometimes too high. The severe underprediction is in conditional games and conditional average among those who later produce meaningful seasons. At lead 5, realised meaningful outcomes averaged 17.3 games and 66.9 points per game; vNext predicted 7.3 conditional games and 24.3 conditional average.

The zero-history baseline predicts zero for everyone. It is perfect for those who remain at zero and very poor for those who later play. vNext improves error among eventual players at every lead, but not enough to offset its false-positive cost among those who remain at zero.

## Architecture diagnosis

The current model uses a globally calibrated meaningful-season classifier and uncalibrated linear Huber regressors for conditional games and conditional average. The regressors are trained only on meaningful outcomes.

The evidence supports two general causes:

1. probability calibration may compress established-player opportunity estimates in some career-stage slices;
2. conditional regressors shrink unfamiliar zero-history profiles too strongly toward low games and low average.

## Recommended experiment order

First, test leakage-safe temporal calibration of conditional games and conditional average without changing the event classifier, features or validation protocol. This directly targets zero-history, ruck and career-stage underprediction while preserving probability calibration.

Second, in a separate PR, test whether global event calibration over-compresses established-player opportunity.

## Decision

Proceed next with one model hypothesis: leakage-safe conditional magnitude calibration. Do not introduce slice-specific overrides, named-player rules or production changes.
