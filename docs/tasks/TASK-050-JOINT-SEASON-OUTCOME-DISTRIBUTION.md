# TASK-050 — Joint season-outcome distribution

## Status

Protocol locked before outcome inspection. This is one forecast-layer hypothesis. It replaces the detached point-estimate-plus-uncertainty construction with one coherent season-outcome distribution whose state probabilities, expected outcomes, quantiles and scoring thresholds are all derived from the same simulated draws.

TASK-047 remains the accepted point-forecast benchmark. TASK-048 and TASK-049 remain rejected uncertainty evidence. TASK-050 cannot promote keeper utility, the current board or production.

## Hypothesis

A low-complexity joint three-state season model—zero game, short positive season, and meaningful season—will improve proper distributional score and calibration while preserving acceptable point accuracy because it removes row-level moment forcing and models games and scoring jointly within each realised state.

## Exact model change

TASK-050 may change only the forecast distribution layer used to produce season outcomes.

For every legal rolling-origin fold and lead, fit using information available strictly before the validation origin:

1. **State probabilities**
   - zero game / zero points;
   - one-to-five games with positive points;
   - six-plus games.
   - Use one fixed low-complexity multinomial logistic model with the existing origin-safe TASK-012 feature set.
   - Select regularisation strength only through fold-local temporal calibration on a predeclared grid.

2. **Short-season outcome distribution**
   - Games are integers 1–5.
   - Fit a regularised conditional scoring-rate mean using short-season training rows only.
   - Generate positive paired games/scoring outcomes from fold-local empirical residual support.

3. **Meaningful-season outcome distribution**
   - Games are constrained to 6–23.
   - Conditional games and conditional average means use the accepted TASK-047 model forms and feature preprocessing.
   - Generate games and scoring jointly using fold-local paired residual resampling so their historical dependence is retained.

4. **Coherent outputs**
   - Draw one deterministic state and outcome sample per Monte Carlo draw.
   - Derive `exp_games`, `cond_games`, `cond_avg`, `exp_points`, q10/q25/q50/q75/q90/q97 and 80+/90+/100+/110+/120+ probabilities from those same draws.
   - Do not force the simulated mean back to TASK-047 `exp_points`.
   - Do not independently calibrate or overwrite quantiles or threshold probabilities after generation.

## Fixed implementation choices

- Monte Carlo sample count: 4,096 draws per prediction row.
- Deterministic seed contract: `sha256("TASK-050|player_key|origin_year|lead")`.
- Multinomial regularisation grid: `C in (0.03, 0.1, 0.3, 1.0, 3.0)`.
- Conditional Ridge alpha grid: use the locked TASK-047 grid and fold-local selection procedure.
- Residual generation: paired empirical residual resampling within fold and lead, with broad-position pooling used only when a declared cell has fewer than 100 training rows; otherwise no position routing.
- No validation-result-dependent threshold, feature, model-family or pooling changes.

## Forbidden changes

Do not change in this task:

- benchmark rows, targets, fold definitions or target cutoffs;
- authoritative player reconciliation;
- keeper utility, owner policy or board currency;
- legacy production files;
- named-player rules or market-derived targets;
- post-hoc quantile calibration, conformal correction, manual offsets or blending;
- current partial-season evidence;
- the validation protocol.

## Baselines

Compare on the exact locked benchmark:

- strongest declared simple baseline;
- accepted TASK-047 point forecasts with its existing uncertainty outputs;
- TASK-050 joint distribution.

Use exactly 20,094 player-origin-lead rows, 5,622 player-origin snapshots and 25 legal rolling-origin folds. Use locked `targets.csv` values directly.

## Required evidence

### State and event probability

- multiclass log loss and Brier components for zero, short and meaningful states;
- calibration intercept/slope and reliability tables;
- meaningful-season Brier versus TASK-047;
- 80+/90+/100+/110+/120+ probability calibration and Brier score;
- proof that threshold probabilities equal frequencies from the same stored draw distribution.

### Continuous and distributional outcomes

- games MAE;
- conditional-average MAE on meaningful rows;
- total-points MAE;
- mean and per-quantile pinball loss;
- CRPS or the repository's declared equivalent proper score;
- q25–q75, q10–q90 and q10–q97 coverage and width;
- all metrics overall, by lead and by fold.

### Required subgroups

Report every locked subgroup with eligible sample sizes, including broad position, prior history, age, tenure, draft type and pick band. Separately report realised zero, short and meaningful cohorts.

### Integrity

Prove:

- exact prediction keys and row counts;
- zero target and fold failures from generated artifacts;
- no silent row drops;
- deterministic repeated generation;
- non-negative, non-crossing quantiles;
- games constraints by state;
- finite positive scoring draws for positive states;
- no post-generation mean forcing;
- expected values and threshold probabilities recompute from the stored draws within numerical tolerance;
- no model fitting during current-board inference or export;
- frozen legacy files unchanged.

### Statistical uncertainty

Persist fold-level differences and a deterministic pooled row-weighted player-block bootstrap with 2,000 replications and seed 50050. The bootstrap observed statistic must equal the corresponding pooled table statistic within numerical tolerance.

## Acceptance gates

TASK-050 is accepted as the forecast-distribution challenger only if every gate passes:

1. Mean pinball improves by at least 2% versus TASK-047, with bootstrap median favouring TASK-050 and the 95% interval not supporting more than 1% degradation.
2. CRPS/equivalent proper score improves by at least 1% versus TASK-047.
3. No individual quantile worsens overall pinball loss by more than 2%.
4. Mean absolute quantile-calibration error is no greater than 0.05 and improves by at least 25% versus TASK-047.
5. Overall q25–q75 coverage lies in 0.46–0.54 and q10–q90 coverage lies in 0.76–0.84.
6. Meaningful-season Brier does not worsen by more than 1%; no 100+ or 110+ Brier worsens by more than 2%.
7. One-year total-points MAE does not worsen by more than 2%, overall total-points MAE does not worsen by more than 1%, and no lead worsens by more than 5%.
8. Games MAE and meaningful conditional-average MAE each do not worsen by more than 2% overall.
9. No eligible locked subgroup with `n >= 200` regresses by more than 5% on the primary proper-score or total-points metric without a separately accepted football explanation and compensating overall gain.
10. Zero, short and meaningful state probabilities each have finite support and improve or preserve multiclass calibration versus the corresponding TASK-047-derived state probabilities.
11. All integrity checks pass, including exact draw-derived reconciliation of expected values, quantiles and threshold probabilities.

Failure of any gate rejects TASK-050. Do not tune or repair the model within the same PR after inspecting validation outcomes.

## Current partial-season evidence

Historical partial-season snapshots are not available and therefore cannot enter TASK-050 training, validation or acceptance evidence.

A separate current-board inference adapter may later use current-season games without making retrospective validation claims. Its locked minimum policy will be:

- one current-season game has an evidence weight at least equal to one game from the immediately prior completed season;
- missed-game fraction is not used as a direct scoring penalty;
- current scoring rate and future availability are updated separately;
- the current-season update must be transparent, removable and reported as a separate component;
- sensitivity must be reported for current-game weight multipliers 1.0, 1.25 and 1.5 before any production use.

This adapter is explicitly outside TASK-050 and cannot affect its historical comparison.

## Required outputs

Persist concise evidence under:

`reports/task-050-joint-season-outcome-distribution/`

Keep row-level predictions and draws under `build/`; commit aggregate tables, hashes, reproduction commands and gate decisions only.

## Decision boundary

If accepted, TASK-050 may replace the vNext forecast distribution only. It does not approve keeper utility, current-board partial-season adjustment, player/pick currency or production release.

If rejected, record the evidence and stop. A follow-up model requires a new predeclared hypothesis.
