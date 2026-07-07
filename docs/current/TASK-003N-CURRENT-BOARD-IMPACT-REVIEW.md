# TASK-003N — Current-board impact review for TASK-003K

State: diagnostic workflow and comparison harness ready for the PR #19 stacked base.

## Scope

TASK-003N compares current merged vNext against the TASK-003K event-logistic candidate on the authoritative 804-player 2026 board. The review is diagnostic-only: it does not tune parameters, add named-player rules, alter production, values, keeper utility, or UI, and it does not approve or reject TASK-003K.

## Forecast-origin convention

The existing current-board pipeline uses the 2026 snapshot as the forecast origin and writes `forecast_year = 2026 + lead` for leads 1 through 5, so TASK-003N reports forecast years 2027 through 2031.

## GitHub Actions workflow

The dedicated workflow `.github/workflows/task-003n-current-board-review.yml` runs the end-to-end review on the correctly stacked PR base:

1. build the full-current annual dataset;
2. build unchanged full-current vNext artifacts with `model_artifacts` and target cutoff 2025;
3. build TASK-003K candidate artifacts with `model_artifacts_event_logistic` and target cutoff 2025;
4. run the real 804-player current-board comparison;
5. run `cd vnext && pytest -q`;
6. upload all generated board-review outputs.

## Local command equivalent

```bash
python vnext/build_annual_dataset.py \
  --data engine/rl_after/rl_model_data.json \
  --out build/task-003n/annual_rows.csv \
  --min-origin 2008 \
  --max-origin 2026

PYTHONPATH=vnext python vnext/train_model_artifacts.py \
  --dataset build/task-003n/annual_rows.csv \
  --out build/task-003n/artifacts-current \
  --module model_artifacts \
  --target-cutoff 2025

PYTHONPATH=vnext python vnext/train_model_artifacts.py \
  --dataset build/task-003n/annual_rows.csv \
  --out build/task-003n/artifacts-task003k \
  --module model_artifacts_event_logistic \
  --target-cutoff 2025

PYTHONPATH=vnext python vnext/review_task003n_current_board.py \
  --current-artifacts build/task-003n/artifacts-current \
  --candidate-artifacts build/task-003n/artifacts-task003k \
  --current-module model_artifacts \
  --candidate-module model_artifacts_event_logistic \
  --out reports/task-003n-current-board-impact
```

## Generated evidence

The comparison writes machine-readable CSV/JSON artifacts for exact 804-player coverage; duplicate-key, missing-value, non-finite, probability-bound, threshold-monotonicity and quantile non-crossing checks; current/candidate annual forecasts and deltas by lead; `p80`, `p90`, `p100`, `p110` and `p120`; expected games, expected average and expected points; largest increases and decreases; rank changes for `exp_points_5y`, `exp_games_5y`, `expected_meaningful_seasons_5y` and `p100_any_5y_independence`; position, age, tenure, draft-pathway and prior-games slices; age-30+ lead-5 detail; zero-history detail; artifact hashes; training-row counts; cutoffs; and single-change evidence.

Columns named `p*_any_5y_independence` use `1 - product(1 - annual_probability)` and are explicitly labelled as independence approximations, not true joint probabilities.

## Guardrail confirmation

The diagnostic comparison consumes persisted current and candidate artifacts. It rejects identical current/candidate inputs by default so a smoke test cannot be mistaken for the TASK-003K review. Current-board outputs are not used to tune TASK-003K.
