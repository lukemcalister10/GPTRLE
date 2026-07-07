# TASK-003 benchmark scaffold implementation notes

## Architecture

TASK-003 adds a benchmark-only scaffold in `vnext/benchmark.py` so historical
legacy-vNext comparisons can be run without touching current-season source data,
current-universe logic, stable-ID ownership, player values, keeper utility, or
the frozen legacy engine.

The scaffold has five separable layers:

1. **Historical as-of contract** — `AsOfContract` defines an origin-year cutoff
   and the allowed source fields for a snapshot. Snapshot construction uses only
   draft facts and scoring rows at or before the origin year. Future list status,
   retirement status, club, current/future position fields and post-origin
   scoring are excluded from the snapshot surface.
2. **Rolling-origin cohorts** — `LOCKED_FOLDS` encodes the locked folds from
   `docs/current/VALIDATION_PROTOCOL.md`: lead 1 origins 2018-2024, lead 2
   origins 2018-2023, lead 3 origins 2018-2022, lead 4 origins 2018-2021, and
   lead 5 origins 2018-2020. `build_evaluation_cohorts` creates included
   snapshots, excluded rows with reasons, and realised targets from the same
   player/origin/lead keys.
3. **Common prediction adapters** — `BaselineAdapter`, `LegacyAdapter` and
   `VNextAdapter` normalise predictions into one schema keyed by
   `player_key`, `origin_year` and `lead`. Legacy execution is injected as a
   callable so frozen legacy behaviour does not need to be modified.
4. **Common targets and metrics** — `realised_targets` keeps zero-game and other
   short-career outcomes in the target table. `score_predictions` calculates the
   scaffolded validation metrics: event Brier/log loss/calibration/AUC,
   games/points MAE, conditional average MAE, threshold-event Brier/AUC and
   pinball losses for the protocol quantiles.
5. **Deterministic artifacts** — `write_benchmark_artifacts` writes folds,
   included rows, excluded rows, targets, normalised predictions, metrics and a
   JSON manifest with counts, model identifiers, target definitions, hashes and
   reproduction commands.

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
