# TASK-047 pooled Ridge conditional average

Candidate benchmark comparison against accepted TASK-012. The isolated change replaces the accepted pooled conditional-average `SGDRegressor` with a pooled `Ridge` estimator tuned on each fold-local temporal calibration split.

Key outputs are in `summary.json` and the CSV evidence tables, including selected Ridge alpha by fold/lead, conditional-average MAE and bias by cohort, end-to-end expected-points metrics, residual standard deviation by lead, unchanged-output invariants, uncertainty-output diagnostic movement plus an explicit uncertainty acceptance blocker, and current-board rise/fall diagnostics from the authoritative 804-player rollup.

Decision note: the candidate materially improves whole-population, ruck and elite-prior conditional-average MAE and slightly improves full-population expected-points MAE while introducing moderate positive conditional-average bias. Current-player movements are diagnostics only. Uncertainty outputs are not accepted by this PR because point-quantile calibration/coverage requires a separate locked acceptance protocol.
