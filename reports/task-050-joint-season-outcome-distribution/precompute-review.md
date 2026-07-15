# TASK-050 pre-compute review and locked benchmark status

## Decision

TASK-050 is **not accepted** in this repository state. The locked TASK-050 benchmark could not be executed because this checkout does not contain TASK-050 fold-generation, audit or focused-test entrypoints, and the remote branch/PR comments could not be fetched in the non-interactive environment because no GitHub credentials are configured.

No model tuning, feature changes, threshold changes, pooling changes, sample-count changes, seed changes, target changes, benchmark changes or acceptance-gate changes were made after this result.

## Pre-compute review

Read and re-confirmed the locked instructions in:

- `AGENTS.md`
- `docs/current/HANDOVER.md`
- `docs/current/PROJECT_STATE.json`
- `docs/current/VALIDATION_PROTOCOL.md`
- `docs/tasks/TASK-050-JOINT-SEASON-OUTCOME-DISTRIBUTION.md`

The current checkout has TASK-047 tooling and TASK-050 documentation, but no TASK-050 implementation entrypoint was present under `vnext/` or `scripts/`.

## Commands and results

| Command | Result |
| --- | --- |
| `git fetch origin task050-joint-season-distribution-implementation` | Failed: repository had no configured `origin`; adding the HTTPS remote then failed with `could not read Username for 'https://github.com': No such device or address`. |
| `python -m pip install -r requirements-vnext.txt` | Passed; dependencies were already installed. |
| `python vnext/run_task047_pooled_ridge_folds.py` | Passed; regenerated TASK-047 fold artifacts under `build/task047-pooled-ridge-conditional-average/`. |
| TASK-050 fold generation | Not runnable in this checkout: no TASK-050 fold-generation entrypoint exists under `vnext/` or `scripts/`. |
| TASK-050 audit | Not runnable in this checkout: no TASK-050 audit entrypoint exists under `vnext/` or `scripts/`. |
| focused TASK-050 tests | Not runnable in this checkout: no TASK-050 focused tests exist under `vnext/tests/`. |
| `cd vnext && pytest -q tests/test_task047_pooled_ridge_conditional_average.py tests/test_task048_ridge_uncertainty_audit.py` | Passed: 9 tests. |
| `cd vnext && pytest -q` | Failed: 1 failed, 260 passed, 28 warnings. Existing failure is `tests/test_player_comparison_export.py::test_builds_three_values_from_one_forecast_vector`. |
| `python scripts/verify_legacy_manifest.py` | Passed when run separately after the full-suite failure: 10 legacy files unchanged. |
| `python scripts/generate_handover.py` | Passed when run separately after the full-suite failure. |

## Artifact hashes

Large row-level files remain uncommitted under `build/`.

| Artifact | Rows/bytes | SHA-256 |
| --- | ---: | --- |
| `build/task047-pooled-ridge-conditional-average/prediction_manifest.json` | 12,415 bytes | `0e2b386d2d3a3b45aefaf05dad199511d543b6a595c49b45d942f14284debb1f` |
| `build/task047-pooled-ridge-conditional-average/vnext_predictions.csv` | 6,225,888 bytes | `481485d84c0dddc05ef01a9ecd50c6be5092538b70064aba50a887a0812f43f4` |
| `build/task047-pooled-ridge-conditional-average/fold_failures.csv` | 24 bytes | `c986fc869936dccc77d50f22ad4be16a810246befe494f60913dfd0017f919bc` |
| `build/task-003-cohorts/manifest.json` | 2,631 bytes | `7233ddbd6a9cc64aba3232779087cd4b1940e149bb1b918039ba87a1ca9acb9f` |
| `build/task-003-cohorts/targets.csv` | 1,045,909 bytes | `e7bd7a101332b9384955cfd3fdbfa136812c7316c9a026e3e0a9eed52cff00f8` |

## Acceptance gates

Because no TASK-050 prediction artifact was generated, gates requiring measured TASK-050 benchmark output are recorded as failed/not met rather than inferred.

| Gate | Status | Evidence |
| ---: | --- | --- |
| 1 | Failed / not measured | No TASK-050 mean pinball or bootstrap artifact exists. |
| 2 | Failed / not measured | No TASK-050 CRPS/equivalent proper-score artifact exists. |
| 3 | Failed / not measured | No TASK-050 per-quantile pinball artifact exists. |
| 4 | Failed / not measured | No TASK-050 quantile-calibration artifact exists. |
| 5 | Failed / not measured | No TASK-050 interval-coverage artifact exists. |
| 6 | Failed / not measured | No TASK-050 meaningful/100+/110+ Brier artifact exists. |
| 7 | Failed / not measured | No TASK-050 total-points MAE artifact exists. |
| 8 | Failed / not measured | No TASK-050 games MAE or meaningful conditional-average MAE artifact exists. |
| 9 | Failed / not measured | No TASK-050 locked-subgroup artifact exists. |
| 10 | Failed / not measured | No TASK-050 state-probability calibration artifact exists. |
| 11 | Failed | Integrity cannot pass without exact TASK-050 keys, draws, draw-derived reconciliation and deterministic repeated generation artifacts. |

## CI status

CI is **not claimed green**. GitHub Actions issue #82 remains an external startup blocker, and this local full-suite run is not green because one test failed.
