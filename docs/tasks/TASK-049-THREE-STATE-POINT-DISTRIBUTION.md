# TASK-049 — Three-state point distribution

## Status

Protocol locked before outcome inspection. This is one isolated uncertainty-model hypothesis. It must not change accepted TASK-047 point forecasts, Ridge fitting, event probabilities, conditional games, conditional averages, benchmark cohorts, targets, keeper utility or production exports.

## Hypothesis

Replacing the current two-state point distribution—exact zero points for every non-meaningful season and a simulated six-plus-game branch—with a target-compatible three-state distribution improves quantile calibration and interval coverage:

1. zero games / zero points;
2. one-to-five games / positive points;
3. six-plus games / meaningful-season points.

The accepted TASK-047 `exp_points` point forecast must remain exactly unchanged for every prediction key.

## Allowed modelling change

Only the point-distribution generator may change.

For each legal rolling-origin fold and lead:

- retain the accepted TASK-047 `p_meaningful`, `cond_games`, `cond_avg`, residual scales and point forecast;
- estimate the split of the existing non-meaningful probability mass between zero-game and one-to-five-game states using training data available strictly before the validation origin;
- estimate the short-season games distribution on integers 1–5 and positive short-season scoring-rate distribution from the same fold-local training data;
- generate deterministic Monte Carlo draws for the three states;
- apply one transparent moment-preserving adjustment so the simulated distribution mean equals the accepted TASK-047 `exp_points` for every row within numerical tolerance;
- preserve non-negative, non-crossing q10/q25/q50/q75/q90/q97 outputs.

The fold-local short-season split may depend on lead and origin-safe existing features only if a declared, fixed model is used. Do not tune feature sets, thresholds or model families against validation results. Prefer the simplest empirical fold/lead estimate unless a feature-dependent split is justified before results are inspected.

## Forbidden changes

Do not change:

- TASK-047 point forecasts or any non-uncertainty output;
- Ridge alpha selection or fitted conditional-average model;
- meaningful-season classifier or calibration;
- conditional-games model;
- benchmark protocol, target definitions or cohorts;
- quantile levels;
- keeper-value or production logic;
- named-player rules, position-specific offsets, post-hoc quantile calibration, conformal correction or blending.

## Baselines

Compare:

- accepted TASK-047 two-state uncertainty distribution;
- TASK-049 three-state candidate.

Use the exact locked 20,094 rows, 5,622 player-origin snapshots and 25 legal folds. Use `targets.csv` `points` directly.

## Required evidence

Report all TASK-048 metrics and integrity checks, including:

- mean and per-quantile pinball loss overall, by lead and by fold;
- deterministic pooled row-weighted player-block bootstrap intervals;
- empirical quantile calibration overall, by lead, broad position and prior-history cohort;
- q25–q75, q10–q90 and q10–q97 interval coverage and width;
- separate evidence for zero-game, one-to-five-game positive-point and meaningful cohorts;
- predicted state probabilities versus realised state frequencies;
- short-season games and scoring-rate calibration;
- proportion of zero quantiles by lead;
- exact point-forecast preservation and distribution-mean reconciliation;
- zero target and fold failures from generated artifacts;
- identical keys and unchanged non-uncertainty outputs.

## Acceptance gates

Accept TASK-049 uncertainty outputs only if every gate passes:

1. Primary mean pinball loss improves by at least 1% versus TASK-047, with the pooled player-block bootstrap median favouring TASK-049 and the 95% interval not supporting a degradation greater than 1%.
2. No declared quantile worsens overall pinball loss by more than 2%.
3. Overall mean absolute quantile-calibration error is no greater than 0.05 and improves by at least 25% versus TASK-047.
4. Overall q25–q75 coverage lies within 0.46–0.54 and q10–q90 coverage within 0.76–0.84.
5. No lead has central-interval absolute coverage error above 0.08.
6. No broad-position or prior-history subgroup with `n >= 200` has central-interval absolute coverage error above 0.12.
7. The one-to-five-game positive-point cohort has finite non-zero predictive support, and its mean pinball loss improves versus TASK-047 at four or more of six quantiles without worsening any quantile by more than 5%.
8. Candidate distribution means equal accepted TASK-047 `exp_points` within `1e-8` for every row, and every non-uncertainty output is exactly unchanged.
9. Quantiles are deterministic, non-negative and non-crossing; prediction keys, row counts, fold counts and failure counts remain exact.

Failure of any gate rejects the candidate. Do not tune or repair within TASK-049 after seeing results.

## Required outputs

Add candidate generation, focused tests and concise evidence under:

`reports/task-049-three-state-point-distribution/`

Persist reproduction commands, input hashes, artifact hashes, state-probability diagnostics, moment-preservation checks and the gate decision. Do not commit bulky duplicate predictions when they can be regenerated.

## Decision boundary

TASK-049 can accept uncertainty outputs only. It cannot promote keeper utility, the current board or production. If rejected, record the evidence and stop before another uncertainty hypothesis.

## Conclusion

TASK-049 is complete and rejected. The implementation replaced only the point-distribution generator with a fold-local empirical three-state generator, preserved accepted TASK-047 point forecasts through moment reconciliation within `1e-8`, and kept non-uncertainty outputs unchanged.

The locked comparison evaluated exactly 20,094 rows per model, 5,622 player-origin snapshots and 25 legal folds against `targets.csv` `points`, using deterministic pooled row-weighted player-block bootstrap seed `49049` with 2,000 replications. The primary mean pinball loss worsened from 141.11 for TASK-047 to 141.65 for TASK-049. Gates 1, 2, 3, 4, 5, 6 and 7 failed; gates 8 and 9 passed. Uncertainty outputs remain blocked, and this task does not promote keeper utility, current-board production or release.

Recommended subsequent hypothesis: at most one separately locked distribution-shape repair audit; do not tune or repair TASK-049 in this PR.
