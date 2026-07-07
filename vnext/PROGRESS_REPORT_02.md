# AFL RL vNext — progress 02: multi-horizon trajectory benchmark

## What was added

This iteration moves beyond the original one-season prototype and tests fully observed **one-, three- and five-year** outcomes.

New files:

- `evaluate_v2_linear.py` — fast, reproducible multi-horizon hurdle benchmark.
- `test_horizon_integrity.py` — confirms target mapping and historical cutoff integrity.
- `output/eval_v2_linear/` — predictions, overall metrics and cohort slices.

The model remains separate from the live RL engine. No production value has been changed.

## Evaluation design

The test windows are chosen so the full target horizon is observable in data ending in 2026:

- 1-year: origins 2023–2025;
- 3-year: origins 2021–2023;
- 5-year: origins 2019–2021.

Every training target finishes before the first test origin for that horizon. Historical snapshots use only draft facts and scoring observed by the origin date.

The challenger is deliberately simple:

1. logistic model for the probability of at least one meaningful season;
2. separate conditional models for future games, total SuperCoach points and best meaningful-season average;
3. a draft-time specialist using only pick, draft age, drafted position and draft type.

This is not intended as the final architecture. It is a transparent benchmark for whether separating establishment risk from performance produces useful gains.

## Overall results

### One-year horizon — 7,581 observations

| Model | Establishment Brier | AUC | Games MAE | Total points MAE | Best-average MAE |
|---|---:|---:|---:|---:|---:|
| Naive baseline | 0.0798 | 0.9506 | 3.35 | 249.5 | 36.17 |
| Linear hurdle | 0.0588 | 0.9678 | 1.95 | 140.8 | 7.18 |
| Draft specialist | **0.0582** | **0.9683** | **1.95** | 141.0 | **7.10** |

### Three-year horizon — 6,941 observations

| Model | Establishment Brier | AUC | Games MAE | Total points MAE | Best-average MAE |
|---|---:|---:|---:|---:|---:|
| Naive baseline | 0.0931 | 0.9549 | 10.56 | 825.6 | 32.83 |
| Linear hurdle | **0.0602** | **0.9717** | 6.02 | **456.2** | 8.80 |
| Draft specialist | 0.0603 | 0.9716 | **6.02** | 458.3 | **8.78** |

### Five-year horizon — 6,321 observations

| Model | Establishment Brier | AUC | Games MAE | Total points MAE | Best-average MAE |
|---|---:|---:|---:|---:|---:|
| Naive baseline | 0.1089 | 0.9372 | 19.40 | 1,546.2 | 31.86 |
| Linear hurdle | 0.0666 | 0.9682 | 10.89 | 840.2 | 10.47 |
| Draft specialist | **0.0663** | **0.9683** | **10.84** | **838.7** | **10.43** |

Relative to the naive baseline, the draft-specialist challenger improves:

| Horizon | Establishment Brier | Games MAE | Total-points MAE | Best-average MAE |
|---|---:|---:|---:|---:|
| 1 year | 27.1% | 41.9% | 43.5% | 80.4% |
| 3 years | 35.2% | 43.0% | 44.5% | 73.3% |
| 5 years | 39.1% | 44.1% | 45.8% | 67.3% |

## Young-player findings

The clearest gains occur for early-tenure players.

At five years, for tenure 0–2 players:

- establishment Brier improves from **0.2265 to 0.1613**;
- establishment AUC rises from **0.7141 to 0.8335**;
- games MAE falls from **28.49 to 22.32**;
- total-points MAE falls from **2,094 to 1,566**;
- best-average MAE falls from **30.59 to 23.24**.

This supports the structural decision to model establishment and production separately. It does not yet prove that the final keeper prices are superior.

## Draft-time results

The specialist materially improves ranking at draft time, particularly over five years:

| Horizon | Model | Brier | AUC | Games MAE | Points MAE | Best-average MAE |
|---|---|---:|---:|---:|---:|---:|
| 1 year | Naive | 0.1964 | 0.6658 | 4.54 | 266.8 | 22.15 |
| 1 year | Specialist | **0.1745** | **0.7742** | **4.07** | 238.5 | **19.11** |
| 3 years | Naive | **0.2256** | 0.6657 | 14.96 | 1,035.9 | **26.68** |
| 3 years | Specialist | 0.2302 | **0.6976** | **14.72** | 1,020.5 | 26.92 |
| 5 years | Naive | 0.2125 | 0.6302 | 25.99 | 1,890.7 | 28.07 |
| 5 years | Specialist | **0.1824** | **0.7661** | **23.90** | **1,714.8** | **25.34** |

The three-year draft-time probability result is a warning: better discrimination does not automatically mean better calibration. The specialist overpredicts the chance of establishment over that window. This needs explicit probability calibration rather than another value modifier.

## Important limitations

1. **This is still not a current-engine head-to-head.** The benchmark is against an honest low-complexity baseline.
2. **The model is linear.** This was intentional for speed and interpretability; nonlinear challengers should now be tested against it.
3. **Best-average prediction is unconditional.** A zero outcome is included for players who do not establish; this is appropriate for outcome value, but conditional scoring quality should also be reported separately.
4. **Position history remains limited.** Drafted position is leakage-safe, but annual historical DPP eligibility is not present in the repository.
5. **No keeper utility has yet been applied.** The output predicts football outcomes, not final RL currency.

## Revised next build sequence

1. Add calibrated threshold models for 80/90/100/110/120 and multi-season elite outcomes.
2. Produce annual correlated trajectory simulations rather than aggregate horizon totals.
3. Build an adapter that feeds simulated trajectories through the existing REPL/captaincy/discounting utility.
4. Create genuine +1/+2 asset-value distributions.
5. Run the current RL engine on the same historical snapshots where technically possible; where its stateful architecture prevents an honest replay, document the exact blocker and compare forecast components directly.
6. Test whether the separate young-elite runway multiplier adds value beyond the runway already present in simulated careers.

## Current conclusion

A comparatively simple hurdle model is already a materially stronger objective baseline than the original naive comparator over one, three and five years. The evidence supports continuing with trajectory modelling, but it is not yet sufficient to replace the live RL engine.
