# TASK-003 benchmark scaffold implementation notes

## Architecture

TASK-003 adds a benchmark-only scaffold in `vnext/benchmark.py` so historical
legacy-vNext comparisons can be run without touching current-season source data,
current-universe logic, stable-ID ownership, player values, keeper utility, or
the frozen legacy engine.

The scaffold has five separable layers:

1. **Historical as-of contract** — `AsOfContract` defines an origin-year cutoff
   and the allowed source fields for a snapshot. Snapshot construction sanitizes
   source dictionaries before calling the shared snapshot builder, keeps only
   allowed fields, truncates scoring to the origin year, and excludes future list
   status, retirement status, club, current/future position fields, post-origin
   scoring and unknown current/future fields from the snapshot surface.
2. **Historical eligibility contract** — benchmark cohorts require an injected
   historical eligibility/list-status resolver, such as `StaticEligibilityResolver`,
   keyed by `player_key` and `origin_year`. Missing historical eligibility is
   reported as an exclusion and, by default, prevents the definitive benchmark
   from proceeding.
3. **Rolling-origin cohorts** — `LOCKED_FOLDS` encodes the locked folds from
   `docs/current/VALIDATION_PROTOCOL.md`: lead 1 origins 2018-2024, lead 2
   origins 2018-2023, lead 3 origins 2018-2022, lead 4 origins 2018-2021, and
   lead 5 origins 2018-2020. `build_evaluation_cohorts` creates included
   snapshots, excluded rows with reasons, and realised targets from the same
   player/origin/lead keys.
4. **Common prediction adapters** — `BaselineAdapter`, `LegacyAdapter` and
   `VNextAdapter` normalise predictions into one schema keyed by
   `player_key`, `origin_year` and `lead`. The schema distinguishes
   `p_meaningful`, `cond_games`, `cond_avg`, `exp_games`, `exp_points`, threshold
   event probabilities and explicit point quantiles. Legacy execution is injected
   as a callable so frozen legacy behaviour does not need to be modified.
5. **Common targets, metrics and artifacts** — `realised_targets` keeps zero-game
   and other short-career outcomes in the target table. `score_predictions`
   calculates the scaffolded metrics implemented now, and
   `write_benchmark_artifacts` writes folds, included rows, excluded rows,
   targets, normalised predictions, metrics and a JSON manifest with counts,
   model identifiers, target definitions, hashes and reproduction commands.

## Metrics implemented now

The current scaffold implements the TASK-003 reusable benchmark core metrics
needed for a first identical-row comparison:

- meaningful-season Brier score, log loss, AUC and logistic calibration
  intercept/slope;
- threshold-event Brier score and AUC for 80+, 90+, 100+, 110+ and 120+ average
  seasons;
- games MAE;
- total-points MAE;
- average MAE conditional on a realised meaningful season, scored against
  `cond_avg`;
- point-forecast quantile pinball loss for q10/q25/q50/q75/q90/q97, using the
  matching explicit `points_qXX` prediction column.

The deterministic baseline emits the same `exp_points` forecast into each
`points_qXX` column as an explicit degenerate distribution. The scoring function
requires those columns and does not substitute a mean forecast when they are
missing.

## Protocol components intentionally deferred

This scaffold does **not** yet implement the full locked validation protocol.
Deferred components include:

- reliability tables;
- multi-season events over three/five years;
- CRPS or full interval coverage/width reporting;
- keeper-utility metrics and utility transforms;
- required subgroup slices;
- fold-level difference summaries and block-bootstrap confidence intervals;
- current-board diagnostic movement reports.

Do not describe TASK-003 artifacts as a complete formal protocol result until
those components are implemented.

## TASK-002 boundaries

This implementation intentionally does not modify:

- `data/current/`;
- current-universe inclusion logic;
- stable-ID logic owned by TASK-002;
- `docs/current/HANDOVER.md`;
- `docs/tasks/TASK-002-ACTIVE-UNIVERSE.md`;
- legacy production engine behaviour under `engine/rl_after/`.

The only expected integration dependency is that future TASK-002 stable-ID work
may provide a stronger historical identifier source. The TASK-003 scaffold is
already keyed by `player_key` and can consume that identifier once available.
