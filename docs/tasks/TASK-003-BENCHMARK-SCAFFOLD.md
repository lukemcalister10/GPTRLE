# TASK-003 benchmark scaffold implementation notes

## Architecture

TASK-003 adds a benchmark-only scaffold in `vnext/benchmark.py` so historical
legacy-vNext comparisons can be run without touching current-season source data,
current-universe logic, stable-ID ownership, player values, keeper utility, or
the frozen legacy engine.

The scaffold has six separable layers:

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
3. **Rolling-origin fold plan** — `LOCKED_FOLDS` encodes the locked test origins
   from `docs/current/VALIDATION_PROTOCOL.md`, while `build_fold_plan` records
   each lead/test-origin pair, the permitted training origins and the maximum
   training target year. A training row is legal only when
   `training_origin + lead < test_origin`.
4. **Prediction-key-only adapter boundary** — `BaselineAdapter`, `LegacyAdapter`
   and `VNextAdapter` receive only sanitized historical snapshots and a key frame
   containing exactly `player_key`, `origin_year` and `lead`. Adapters never
   receive realised games, averages, points, meaningful flags or threshold
   outcomes. `LegacyAdapter` passes only those sanitized snapshots and keys to
   its injected runner.
5. **Model provenance enforcement** — `VNextAdapter` resolves artifacts by
   `(lead, test_origin)` or an injected resolver, validates artifact training
   cutoff metadata, and rejects artifacts whose training targets reach or pass
   the test origin. `LegacyAdapter` requires equivalent as-of provenance from an
   injected provenance resolver. Per-fold model/artifact identifiers, training
   cutoff years and quantile methods are recorded for artifact publication.
6. **Common targets, metrics and artifacts** — `realised_targets` keeps zero-game
   and other short-career outcomes in the target table. `score_predictions`
   calculates the scaffolded metrics implemented now, and
   `write_benchmark_artifacts` writes fold plans, included rows, excluded rows,
   target failures, targets, normalised predictions, metrics, per-fold model
   metadata and a JSON manifest with counts, model identifiers, target
   definitions, hashes and reproduction commands.

## Target-data failure handling

Target construction does not rely on silent target fallback behaviour:

- no scoring row for the exact target year is a legitimate zero-game outcome;
- exactly one valid row for the target year produces the realised target;
- malformed exact target-year rows are reported as target-data failures;
- duplicate exact target-year rows are reported as target-data failures.

Unexpected target-data failures prevent the definitive benchmark by default.
Callers may disable that guard only to publish or inspect the `target_failures`
artifact during investigation.

## Quantile provenance

The common prediction schema requires explicit `points_q10`, `points_q25`,
`points_q50`, `points_q75`, `points_q90` and `points_q97` columns.

- `BaselineAdapter` uses a documented degenerate distribution by emitting the
  same `exp_points` value into every quantile column.
- `VNextAdapter` requires artifact output or an injected prediction function to
  provide real quantile columns. It does not silently convert `exp_points` into
  all six quantiles.
- `LegacyAdapter` requires its injected runner to provide the full prediction
  schema.

Quantile method names are recorded per model and per fold so diagnostic or
degenerate quantiles cannot be mistaken for genuine distribution forecasts.

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

The scoring function requires quantile columns and does not substitute a mean
forecast when they are missing.

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
