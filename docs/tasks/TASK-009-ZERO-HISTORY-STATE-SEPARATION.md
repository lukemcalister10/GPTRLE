# TASK-009 — Origin-safe zero-history state separation

## Status

Single-hypothesis forecast experiment. No production or utility change.

## Context

TASK-008 confirms 111 current zero-history players. TASK-003J found that zero-history rows are generally inside numeric training support; the defect is state collapse, not ordinary extrapolation. The repository does not contain origin-safe historical intra-season snapshots, so partial-season model changes remain deferred rather than being validated with leaked full-season averages.

## Hypothesis

Adding an explicit, origin-safe representation of zero AFL history — combining observed zero games, tenure, broad entry pathway and pick bucket — will improve meaningful-season event discrimination for zero-history players without materially regressing the accepted TASK-003Q model overall or for players with AFL history.

## Single change

Only the feature representation used by TASK-003Q's two meaningful-season event classifiers changes.

Unchanged:

- event model families and hyperparameters;
- temporal calibration method;
- conditional games and average models;
- threshold models;
- residual scales and quantile method;
- TASK-003Q age/lead blend policy;
- cohorts, targets, folds and training cutoffs;
- keeper utility, capital allocation, export and UI;
- frozen Claude files.

## Candidate features

All are known at the origin:

- `zero_history_flag`: observed total AFL games equals zero;
- `zero_history_tenure`: tenure bucket `t0`, `t1`, `t2`, `t3+`, or `played`;
- `zero_history_state`: interaction of zero-history tenure, broad entry pathway and pick bucket; all non-zero-history rows map to `played`.

No current list status, retirement flag, future position, post-origin scoring or named-player label is used.

## Evidence and gates

Compare the candidate directly with accepted TASK-003Q on the locked 25 rolling-origin folds and 20,094 rows.

Required to pass:

1. zero-history Brier and log loss improve;
2. zero-history games and points MAE do not regress by more than 1%;
3. no pooled metric regresses by more than 0.5%;
4. no played-history metric regresses by more than 1%;
5. zero-history probability dispersion increases;
6. player-block bootstrap median Brier difference favours the candidate.

A pass makes the feature hypothesis eligible for review, not automatic production promotion. A rejection remains useful evidence and is not to be tuned using named players.
