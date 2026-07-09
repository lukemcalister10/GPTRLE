# TASK-047 — Pooled Ridge conditional-average candidate

## Status

Candidate evidence complete. The isolated modelling change replaces the accepted TASK-012 pooled conditional-average `SGDRegressor` with a pooled `Ridge` regressor. No position-specific models, position routing, residual correction, SGD blending, bias correction, player-specific logic, keeper-value change, production promotion or future option-value work is included.

The locked benchmark supports acceptance under the declared rule: whole-population conditional-average MAE improves materially, ruck and elite-prior defects improve materially, and the main trade-off is a moderate positive whole-population bias (+1.71) plus positive FWD/MID bias rather than the severe TASK-012 negative bias.

## Hypothesis

TASK-012's Huber SGD conditional-average layer over-shrinks meaningful-season averages. A pooled Ridge estimator on the unchanged TASK-012 feature representation should reduce upper-tail and ruck compression while keeping the forecast stack pooled and leakage-safe.

## Model layer changed

- Changed only the pooled conditional-average estimator in `vnext/model_artifacts_pooled_ridge_conditional_average.py`.
- Retained TASK-012 preprocessing and demonstrated-ceiling feature construction.
- Retained TASK-012 temporal fit/calibration split and meaningful-season target filtering.
- Retained meaningful-season event model, conditional-games model, threshold models, quantile simulation, keeper utility and current-board comparison stack.
- Ridge alpha grid: `[0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0]`. Alpha is selected inside each rolling-origin fold using only the fold-local temporal calibration split.

## Reproduction commands

```bash
python vnext/run_task012_established_ceiling_folds.py --out build/task012-candidate --rebuild
python vnext/run_task047_pooled_ridge_folds.py --out build/task047-pooled-ridge-conditional-average --rebuild
python vnext/build_annual_dataset.py --data engine/rl_after/rl_model_data.json --out build/task047-current/annual_rows.csv --min-origin 2008 --max-origin 2026
PYTHONPATH=vnext python vnext/train_model_artifacts.py --dataset build/task047-current/annual_rows.csv --out build/task047-current/task012 --module model_artifacts_established_ceiling --target-cutoff 2025
PYTHONPATH=vnext python vnext/train_model_artifacts.py --dataset build/task047-current/annual_rows.csv --out build/task047-current/task047 --module model_artifacts_pooled_ridge_conditional_average --target-cutoff 2025
PYTHONPATH=vnext python vnext/review_task003n_current_board.py --current-artifacts build/task047-current/task012 --candidate-artifacts build/task047-current/task047 --current-module model_artifacts_established_ceiling --candidate-module model_artifacts_pooled_ridge_conditional_average --out build/task047-current/review
python vnext/analyse_task047_pooled_ridge.py --baseline build/task012-candidate/vnext_predictions.csv --candidate build/task047-pooled-ridge-conditional-average/vnext_predictions.csv --targets build/task-003-cohorts/targets.csv --features build/task047-pooled-ridge-conditional-average/training_dataset.csv --current-board-rollup build/task047-current/review/player_rollup_rank_changes.csv --alpha-by-fold build/task047-pooled-ridge-conditional-average/selected_ridge_alpha_by_fold_lead.csv --out reports/task-047-pooled-ridge-conditional-average
```

## Overall before/after

|model|n|mae|bias|actual_avg|pred_avg|residual_sd|
|---|---|---|---|---|---|---|
|task012|10848|14.61|-6.54|72.56|66.02|17.92|
|task047|10848|11.65|1.71|72.56|74.27|14.64|

## Conditional average by lead

|model|lead|n|mae|bias|actual_avg|pred_avg|residual_sd|
|---|---|---|---|---|---|---|---|
|task012|1|3489|11.82|-3.79|71.31|67.52|14.81|
|task012|2|2774|13.75|-5.17|72.18|67.01|16.85|
|task012|3|2107|15.68|-7.33|73.08|65.75|18.57|
|task012|4|1489|17.66|-10.01|74.11|64.10|20.29|
|task012|5|989|20.01|-13.17|74.64|61.47|22.45|
|task047|1|3489|10.30|1.22|71.31|72.52|13.04|
|task047|2|2774|11.67|1.70|72.18|73.89|14.63|
|task047|3|2107|12.39|1.99|73.08|75.07|15.47|
|task047|4|1489|12.77|2.31|74.11|76.41|15.82|
|task047|5|989|13.11|1.92|74.64|76.56|16.24|

## Ruck by lead

|model|lead|n|mae|bias|actual_avg|pred_avg|residual_sd|
|---|---|---|---|---|---|---|---|
|task012|1|196|21.56|-20.45|86.10|65.65|16.09|
|task012|2|171|28.09|-27.35|85.74|58.38|17.20|
|task012|3|139|33.74|-33.27|86.44|53.17|17.34|
|task012|4|101|40.10|-39.43|88.95|49.53|19.27|
|task012|5|68|47.63|-46.90|91.46|44.56|24.43|
|task047|1|196|11.89|-4.82|86.10|81.28|14.32|
|task047|2|171|13.40|-4.53|85.74|81.21|16.08|
|task047|3|139|13.11|-4.83|86.44|81.61|16.07|
|task047|4|101|13.85|-6.65|88.95|82.31|16.30|
|task047|5|68|14.99|-7.75|91.46|83.72|17.19|

## Elite-prior by lead

|model|lead|n|mae|bias|actual_avg|pred_avg|residual_sd|
|---|---|---|---|---|---|---|---|
|task012|1|103|13.15|-10.55|108.35|97.80|12.72|
|task012|2|87|17.41|-14.28|105.21|90.93|15.88|
|task012|3|70|18.80|-14.78|101.18|86.40|17.56|
|task012|4|54|20.77|-14.60|97.94|83.35|21.08|
|task012|5|39|21.11|-11.41|94.14|82.72|23.63|
|task047|1|103|10.89|-6.15|108.35|102.20|12.55|
|task047|2|87|12.34|-5.37|105.21|99.84|14.95|
|task047|3|70|13.31|-3.42|101.18|97.77|16.62|
|task047|4|54|15.15|-2.13|97.94|95.81|19.42|
|task047|5|39|16.24|-0.68|94.14|93.46|20.96|


## End-to-end expected-points evidence

The accepted forecast stack computes expected points as meaningful-season probability × conditional games × conditional average. TASK-047 intentionally changes only the conditional-average estimator, so end-to-end expected-points movement is expected but must be measured on the full locked population, including non-meaningful outcomes as zero realised points.

### Whole population expected points

|model|n|mae|bias|actual_points|pred_points|
|---|---|---|---|---|---|
|task012|20094|455.52|-178.26|715.33|537.07|
|task047|20094|454.81|-138.84|715.33|576.49|

### Expected points by lead

|model|lead|n|mae|bias|actual_points|pred_points|
|---|---|---|---|---|---|---|
|task012|1|5622|405.22|-111.64|783.56|671.92|
|task012|2|4818|460.29|-153.46|741.89|588.44|
|task012|3|4016|493.53|-213.97|715.41|501.44|
|task012|4|3217|488.06|-234.59|651.52|416.93|
|task012|5|2421|456.51|-248.24|588.67|340.43|
|task047|1|5622|403.36|-83.87|783.56|699.70|
|task047|2|4818|457.60|-116.34|741.89|625.56|
|task047|3|4016|491.72|-168.72|715.41|546.68|
|task047|4|3217|491.49|-183.28|651.52|468.24|
|task047|5|2421|458.81|-202.67|588.67|386.00|

## Unchanged-output invariants

The review-required non-average forecast layers are unchanged. The locked historical predictions confirm exact equality at tolerance `1e-12` for meaningful-season probability, expected/conditional games and elite-threshold probabilities.

|column|max_abs_delta|rows_compared|violations_gt_1e_12|
|---|---|---|---|
|p_meaningful|0.00|20094|0|
|exp_games|0.00|20094|0|
|cond_games|0.00|20094|0|
|p_avg_ge_80|0.00|20094|0|
|p_avg_ge_90|0.00|20094|0|
|p_avg_ge_100|0.00|20094|0|
|p_avg_ge_110|0.00|20094|0|
|p_avg_ge_120|0.00|20094|0|

## Uncertainty evidence and blocker

TASK-047 changes the conditional-average residual scale and therefore point quantiles mechanically. This PR does not claim uncertainty-output acceptance because the locked benchmark does not define a point-quantile calibration or coverage acceptance rule.

|status|reason|required_follow_up|
|---|---|---|
|blocked_for_acceptance|TASK-047 changes the conditional-average residual scale and point quantiles mechanically, but the locked benchmark does not contain an acceptance rule for point-quantile calibration or coverage.|Before promoting uncertainty outputs, run a separate uncertainty-calibration task with coverage by lead and subgroup. Do not accept TASK-047 on uncertainty quality.|

The report includes `uncertainty_output_changes_by_lead.csv` to quantify quantile movement as diagnostic evidence only. The mean absolute point-quantile changes by lead/quantile are recorded for 30 rows.

## Current-board diagnostics

The current-board comparison contains exactly 804 players. Mean absolute five-year expected-points change is 254.77; mean signed change is 219.94; largest rise is 1684.87; largest fall is -779.23. Mean absolute rank movement is 18.56 and median absolute rank movement is 14.00.

Tristan Xerri diagnostic only: five-year expected points move from 3174.77 to 4107.93, delta 933.16; rank changes from 203 to 165. This is not an optimisation target.

## Artifact manifest

- `build/task047-pooled-ridge-conditional-average/prediction_manifest.json`
- `build/task047-pooled-ridge-conditional-average/vnext_predictions.csv`
- `build/task047-pooled-ridge-conditional-average/fold_artifact_manifest.csv`
- `build/task047-pooled-ridge-conditional-average/selected_ridge_alpha_by_fold_lead.csv`
- `build/task047-current/review/player_rollup_rank_changes.csv`
- `reports/task-047-pooled-ridge-conditional-average/summary.json` and CSV evidence tables

## Decision notes

Accepted as a candidate result for review. TASK-047 reduces whole-population MAE from 14.61 to 11.65, ruck MAE from 21.56–47.63 to 11.89–14.99 across leads, and elite-prior MAE from 13.15–21.11 to 10.89–16.24. The candidate introduces positive whole-population bias (+1.71) and positive FWD/MID bias, which should be monitored, but not enough to reject this isolated hypothesis.
