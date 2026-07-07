# Locked Validation Protocol — v1

## Objective
Evaluate whether a model predicts realised future SuperCoach outcomes and resulting keeper utility better than simple baselines and the legacy engine. Human trades, drafts, market prices, and named-player preferences are not training targets.

## Unit of prediction
A prediction row is a player state at an `origin_year`. It may use only information available at that origin. Every target is generated from seasons after the origin.

## Historical information boundary
Allowed where available at origin:
- draft year, type, pick, age, and drafted position;
- scoring and games through the origin;
- position eligibility known at the origin;
- list status known at the origin.

Forbidden unless reconstructed as-of origin:
- eventual/future position;
- current club or current-list flags;
- retirement or delisting known only later;
- post-origin scoring or games;
- later manual classifications;
- market decisions or retrospective expert labels.

Any unexpected row failure is fatal. No `except: continue` behaviour is permitted in validation.

## Cohort coverage
- Include national, rookie, preseason, and other draft types where data quality supports them; report them separately.
- Include zero-game careers, short careers, middle outcomes, and stars.
- Do not select test cohorts based on eventual outcome.
- Report missingness and exclusions with reasons before metrics.

## Evaluation design
Use strict rolling-origin outer folds. For each test origin `Y` and lead `L`, training may use only origins whose targets end before `Y`.

Recommended outer origins with the current complete target cutoff of 2025:
- lead 1: 2018–2024;
- lead 2: 2018–2023;
- lead 3: 2018–2022;
- lead 4: 2018–2021;
- lead 5: 2018–2020.

Hyperparameters and calibration are fit using earlier inner temporal folds only. The protocol is locked before the formal legacy-vNext head-to-head. Later protocol changes require their own PR and must show old and new results side by side.

Because earlier exploratory work has already inspected several historical origins, retrospective results are described as rolling-origin evidence, not a pristine untouched test. A prospective frozen forecast artifact should be retained for future seasons as the ultimate external check.

## Baselines
1. Pick × drafted position × draft age prior.
2. Recent scoring plus a simple position-specific age curve.
3. Low-complexity regularised hurdle/trajectory model.
4. Legacy production engine adapted to the same historical snapshot.

## Forecast metrics
### Event probability
- Brier score;
- log loss where stable;
- calibration intercept and slope;
- reliability tables;
- AUC as discrimination only, never as the sole criterion.

Events include:
- meaningful season;
- 80+, 90+, 100+, 110+, and 120+ average;
- at least one and multiple threshold seasons over three/five years.

### Continuous outcomes
- games MAE;
- average MAE conditional on meaningful season;
- total-points MAE;
- pinball loss for q10/q25/q50/q75/q90/q97;
- CRPS or an equivalent proper distributional score;
- interval coverage and width.

### Keeper outcomes
Using the same utility transform for all compared forecasts:
- one-, three-, and five-year discounted utility MAE;
- rank correlation as a secondary metric;
- top-decile future-utility recall;
- false-positive rate among predicted top-decile players;
- captaincy-calibre season probability calibration;
- seasons above replacement error.

## Primary model-selection criteria
A challenger is eligible to replace the forecast layer only if:
1. It beats the legacy engine on three- and five-year discounted utility error by at least 3% each, or beats it on the predeclared composite with statistical support and no material horizon failure.
2. It beats every simple baseline on the primary composite.
3. It does not worsen one-year total-points MAE by more than 2%.
4. It improves or preserves calibration for meaningful, 100+, and 110+ outcomes.
5. It has no unexplained subgroup regression greater than 5% where `n >= 200`.

The primary composite uses normalised skill relative to the strongest simple baseline:
- 20% one-year total-points error;
- 30% three-year discounted keeper-utility error;
- 35% five-year discounted keeper-utility error;
- 15% proper distributional/calibration score.

This composite may be changed only in a protocol-only PR before inspecting results from the proposed model change.

## Required slices
- position: MID, DEF, FWD, RUC, KPD, KPF;
- draft type;
- pick bands: 1–5, 6–10, 11–20, 21–40, 41–60, 61+ / undrafted;
- age bands;
- tenure 0, 1, 2, 3, 4–5, 6+;
- zero prior games versus established;
- partial-season versus complete-season origins where applicable.

## Uncertainty and significance
Report fold-level differences and block-bootstrap confidence intervals by player/draft cohort. Do not rely only on pooled row-level p-values, because rows for the same player and adjacent seasons are dependent.

## Current-board diagnostics
Current-player movements are diagnostic, not truth labels. Every candidate report includes:
- value-change distribution;
- largest rises and falls;
- changes by position, age, tenure, and pick band;
- component attribution;
- missing/new player reconciliation.

Named players may trigger investigation but cannot be hard-coded acceptance gates.
