# TASK-003H conditional magnitude calibration

## Decision

**Rejected in its current form.**

Temporally held-out isotonic calibration materially improved conditional games and conditional average errors among realised meaningful seasons, but worsened the unconditional objectives that the model must optimise.

Key results versus unchanged fold-specific vNext:

- meaningful-season Brier: unchanged;
- games MAE: **3.42% worse**;
- total-points MAE: **3.89% worse**;
- conditional-games MAE among meaningful outcomes: **10.94% better**;
- conditional-average MAE among meaningful outcomes: **13.97% better**;
- paired player-block total-points difference: **+17.60 points**, 95% interval **+13.29 to +22.47**; positive differences favour current vNext;
- 69 qualifying slice/lead rows were more than 3% worse on total-points MAE and none were more than 3% better.

The candidate increased conditional magnitudes for every player with a non-zero event probability. That reduced error for eventual players, but imposed a much larger false-positive cost on players who remained at zero. The zero-history slices worsened by 27.6% to 36.6% on total-points MAE across leads.

The evidence rejects unconditional post-hoc isotonic calibration of conditional means. It does not reject improving the underlying conditional models, support representation or state structure.

Files:

- `metrics_summary.csv`: pooled primary and conditional metrics;
- `metrics_by_lead.csv`: lead-level results;
- `player_block_bootstrap.csv`: paired player-block intervals versus current vNext;
- `original_15_slice_results.csv`: effects on the 15 regressions that motivated the experiment;
- `zero_history_outcome_split.csv`: eventual-player versus eventual-zero trade-off;
- `provenance.json`: workflow, artifact and protocol identifiers.
