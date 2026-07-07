# TASK-003E — Formal vNext comparison

## Decision

**Continue vNext development; do not replace the production model yet.**

The merged-state rolling-origin benchmark confirms that fold-specific vNext materially outperforms the recent-scoring baseline on pooled primary metrics and on total-points MAE at every forecast lead. However, 15 qualifying slice/lead combinations remain more than 3% worse on total-points MAE, and a leakage-safe formal frozen-legacy comparison remains unavailable.

## Locked evaluation

- 5,622 unique player-origin snapshots
- 20,094 player-origin-lead rows per model
- 25 legal origin/lead folds
- 0 target-data failures
- 0 fold failures
- models compared:
  - `baseline_recent_scoring`
  - `vnext_fold_specific`
- formal frozen-legacy evidence included: **no**

Every vNext fold enforced:

```text
training_origin + lead < test_origin
```

The current production artifact was not reused for historical predictions.

## Pooled primary results

| Metric | Baseline | vNext | Relative improvement |
|---|---:|---:|---:|
| Meaningful-season Brier | 0.2543 | 0.1776 | 30.1% |
| Games MAE | 6.6610 | 5.8820 | 11.7% |
| Total-points MAE | 522.97 | 452.37 | 13.5% |
| Median-points pinball | 261.48 | 226.39 | 13.4% |
| q90-points pinball | 245.34 | 153.74 | 37.3% |

All five primary player-block bootstrap intervals favoured vNext.

## Total-points MAE by lead

| Lead | Relative improvement |
|---:|---:|
| 1 | 3.8% |
| 2 | 9.7% |
| 3 | 12.8% |
| 4 | 19.8% |
| 5 | 27.4% |

## Remaining blockers

The formal decision is not to replace production yet because:

1. **Material subgroup regressions remain.** Fifteen qualifying slice/lead combinations were more than 3% worse on total-points MAE. These must be investigated without named-player tuning.
2. **No acceptance-grade frozen-legacy benchmark is available.** TASK-003C proved that the available legacy seam is a lead-invariant diagnostic peak proxy and depends on current learned assets without historical cutoffs.
3. **Current production behaviour has not been changed.** This benchmark establishes evidence for further development, not a deployment approval.

## Reproduction

The read-only workflow `.github/workflows/task-003e-formal-vnext-comparison.yml`:

1. rebuilds the locked historical cohort;
2. trains all legal vNext folds;
3. regenerates all 20,094 vNext predictions;
4. runs the baseline-versus-vNext comparison with 2,000 paired player-block bootstrap repetitions;
5. validates pooled and per-lead improvements;
6. preserves subgroup regressions and the missing formal legacy comparison as explicit blockers;
7. uploads the complete evidence package.

## Evidence identifiers

- workflow run: `28858912803`
- workflow artifact: `8134823849`
- artifact archive SHA-256: `fd66faf3a20a73991e49129b4beceb285e31ad8b0a00d09e8c9e90992a945fe3`
- vNext predictions SHA-256: `0453d4ad942aaa75a4c1e5f96ce9ceb7c8656ca847cc2c85390e2178c12f0c7c`
- combined predictions SHA-256: `f65a77c241917dcab20935f886c6b7443792105dd4bd58ae28bab5bb01e4f082`
- metrics summary SHA-256: `c6ea871e94706dfa6d58491dfc9770374fa4061a11f150a416d0831333d75af9`
- player-block bootstrap SHA-256: `63a676a9f983e53a32f4119f7972ef974bc34dfad0046a40cebde22305bfbf13`
- slice metrics SHA-256: `413707ccc3922cea8c1d9911eef9663e166e946f10b014ce047a7455adb0a5ab`

## Next engineering stage

Investigate the material subgroup regressions using fold-level and slice-level evidence. Changes must remain general, leakage-safe and justified by repeated rolling-origin improvement. Do not tune to named players or modify the production forecast layer until a separate deployment decision is approved.
