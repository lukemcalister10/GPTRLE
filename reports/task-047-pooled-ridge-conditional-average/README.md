# TASK-047 pooled Ridge conditional average

Candidate benchmark comparison against accepted TASK-012. The isolated change replaces the accepted pooled conditional-average `SGDRegressor` with a pooled `Ridge` estimator tuned on each fold-local temporal calibration split.

Key outputs are in `summary.json` and the CSV evidence tables, including selected Ridge alpha by fold/lead, conditional-average MAE and bias by cohort, residual standard deviation by lead, and current-board rise/fall diagnostics from the authoritative 804-player rollup.

Decision note: the candidate materially improves whole-population, ruck and elite-prior MAE while introducing moderate positive whole-population bias. Current-player movements are diagnostics only.
