# TASK-011 — Demonstrated-exposure pedigree fade

## Status

Single-hypothesis forecast experiment. No direct change to frozen Claude `pedDecay`, utility, export or production.

## Hypothesis

Draft pedigree should lose predictive influence as observed AFL evidence accumulates. Fading draft pick to a neutral value by 50 career games and mapping draft pathway to one established category at 50 games will improve future-outcome forecasts for established players without materially damaging younger or zero-history cohorts.

## Single change

Before fitting and prediction, and using only information known at the origin:

- draft pick is faded linearly toward pick 80 from 0 to 50 observed AFL games;
- at 50 games, draft type maps to `ESTABLISHED`;
- every other TASK-003Q feature, target, model family, hyperparameter, calibration, residual, quantile, fold and cutoff remains unchanged.

The 50-game point is declared before evaluation and matches the TASK-008 established-player audit definition. It is not tuned against current named players.

## Evidence

Compare directly with accepted TASK-003Q across all 25 locked rolling-origin folds and 20,094 rows, with separate 50+, 100+, under-50 and zero-history cohorts plus a player-block bootstrap.

A pass is evidence for the forecast representation only. It does not authorise changing the frozen Claude utility layer or promoting TASK-006.
