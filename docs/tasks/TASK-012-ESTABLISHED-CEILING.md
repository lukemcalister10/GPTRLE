# TASK-012 — Evidence-weighted demonstrated ceiling

## Status

Single-hypothesis forecast experiment. No keeper-utility, export, UI or production change.

## Hypothesis

For established players, demonstrated AFL scoring should carry more weight than an unconstrained generic trajectory. Adding one smooth interaction between career-best scoring and observed career games to the conditional-average model will improve forecasts for established low-ceiling players without degrading the accepted TASK-009 event model or broader population.

## Single change

The conditional-average layer receives one additional origin-safe numeric feature:

`career_best_x_evidence = career_best * clip(total_games / 50, 0, 1)`

The 50-game evidence point matches the predeclared TASK-008 established cohort. No 65-point threshold is supplied to the model; `career_best < 65` is used only to report the already-declared low-ceiling audit cohort.

Unchanged:

- accepted TASK-009 meaningful-season probabilities;
- conditional games;
- elite-threshold probabilities;
- model families and regularisation;
- temporal split and targets;
- folds, cutoffs and quantile method;
- frozen Claude files and TASK-006 release block.

## Required evidence

- event, games and threshold outputs remain bit-identical to TASK-009;
- conditional-average and points MAE improve for established low-ceiling rows;
- no material regression for established players, under-50 players or the pooled population;
- player-block bootstrap medians favour the candidate.

A pass accepts this forecast representation only. It does not authorise a hard player markdown or any direct change to Claude value mechanics.
