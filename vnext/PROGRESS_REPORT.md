# AFL RL vNext — first working challenger

## What has been built

This package is a clean, separate challenger. It does not modify the current RL engine.

1. `snapshot.py`
   - Creates historical player snapshots using only draft facts and scoring seasons available by the nominated origin year.
   - Deliberately ignores current club, current position, future position, retirement status, current list status and later scoring.
   - Includes regression tests proving those future-derived fields cannot alter a historical snapshot.

2. `build_dataset.py`
   - Generated 30,746 player-origin rows covering 2,634 players from 2008–2025.
   - Includes players with no later scoring record, rather than conditioning only on established players.
   - Produces next-season establishment, games, average and threshold outcomes.

3. `evaluate_v1.py`
   - Implements rolling-origin evaluation. Every test origin is trained only on outcomes completed before that origin.
   - Compares an honest low-complexity baseline with a first nonlinear hurdle challenger.
   - The challenger separately estimates:
     - probability of a meaningful season (6+ games); and
     - SuperCoach average conditional on a meaningful season.

4. `analyse_results.py`
   - Reports performance for all players, draft-time rows, early-tenure players, established players and draft-pick bands.
   - Produces reliability tables rather than relying only on rank discrimination.

## First results

Evaluation covers 18,130 player-origin observations across the 2018–2025 test origins.

| Metric | Naive baseline | vNext tree hurdle | Change |
|---|---:|---:|---:|
| Meaningful-season Brier score | 0.0878 | 0.0607 | 30.8% lower |
| Meaningful-season AUC | 0.9438 | 0.9676 | higher |
| Unconditional next-year average MAE | 12.06 | 8.31 | 31.1% lower |
| Conditional scoring MAE | 14.32 | 9.57 | 33.2% lower |

The challenger also improves the Brier score for reaching 90, 100 and 110, although these threshold probabilities are currently approximate and need their own calibrated classifiers.

## Important draft-time finding

At draft time, the challenger is substantially better at ranking establishment probability and predicting scoring conditional on playing, but its total unconditional-average error is currently worse than the naive baseline:

| Draft-time metric | Naive | vNext |
|---|---:|---:|
| Establishment Brier | 0.1920 | 0.1600 |
| Establishment AUC | 0.6857 | 0.7741 |
| Conditional scoring MAE | 23.94 | 10.56 |
| Unconditional average MAE | 15.65 | 18.09 |

This is not being hidden. The cause is that the first hurdle model slightly overestimates immediate first-year participation at draft time: predicted 31.3% versus an observed 27.0%. More importantly, next-season participation is not the right sole target for draftees; delayed establishment is valuable in this league. The next model therefore needs explicit 3-year and 5-year establishment and trajectory targets rather than treating a quiet first season as failure.

## What these results do and do not mean

The results show that a clean, relatively ordinary model can beat the initial naive baseline materially for next-season outcomes. They do not yet show that it beats the current RL engine, because the current engine has not yet been run through the same leakage-safe snapshot interface.

They also do not yet establish better keeper values. This version forecasts one-year performance only and has not been passed through the existing replacement/captaincy/runway utility layer.

## Next implementation steps

1. Add observability-safe 3-year and 5-year targets.
2. Build separate models for:
   - remaining listed/active;
   - meaningful games;
   - games count;
   - scoring conditional on playing;
   - elite threshold probabilities.
3. Add a dedicated draft-time model using pick, drafted position, draft age and draft type, with delayed establishment outcomes.
4. Reconstruct a leakage-safe adapter for the current engine and score it on the identical rows.
5. Simulate correlated multi-season trajectories.
6. Feed both current and challenger trajectories through the existing keeper utility layer.
7. Compare realised discounted value above replacement, captaincy seasons and top-position outcomes.

## Reproducibility

From the `vnext` directory:

```bash
python build_dataset.py \
  --data /path/to/engine/rl_after/rl_model_data.json \
  --out output/historical_rows.csv

pytest -q

python evaluate_v1.py \
  --dataset output/historical_rows.csv \
  --out output/eval_v1

python analyse_results.py
```
