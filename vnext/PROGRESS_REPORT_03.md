# AFL RL vNext — progress 03: annual trajectories and elite-tail probabilities

## What was built

This stage replaces the single aggregate “future peak” concept with five explicit annual forecast legs. For each historical player state, vNext now predicts separately for years 1–5:

- probability of a meaningful season (at least six games);
- games conditional on establishing;
- SuperCoach average conditional on establishing;
- expected total points;
- probability of averaging at least 80, 90, 100, 110 and 120.

The models are trained and calibrated only on outcomes completed before the held-out test period. The evaluation uses 6,321 player states from the 2019–2021 historical origins, including players who never established.

The live RL engine remains unchanged.

## Annual results

| Future season | Establishment Brier | AUC | Games MAE | Points MAE | 100+ Brier | 110+ Brier |
|---:|---:|---:|---:|---:|---:|---:|
| Year 1 | 0.0695 | 0.959 | 2.22 | 167.6 | 0.0122 | 0.0061 |
| Year 2 | 0.0803 | 0.947 | 2.72 | 204.2 | 0.0135 | 0.0068 |
| Year 3 | 0.0846 | 0.939 | 2.92 | 222.0 | 0.0160 | 0.0070 |
| Year 4 | 0.0852 | 0.932 | 3.00 | 229.4 | 0.0164 | 0.0083 |
| Year 5 | 0.0831 | 0.923 | 2.57 | 197.9 | 0.0164 | 0.0078 |

The expected decline in certainty is visible, but useful discrimination remains through year five. This supports constructing career value from annual outcome distributions rather than inferring an entire career from one peak estimate.

## Calibration

The annual establishment forecasts are mildly conservative:

| Future season | Actual meaningful-season rate | Predicted rate |
|---:|---:|---:|
| Year 1 | 24.76% | 24.10% |
| Year 2 | 24.32% | 22.73% |
| Year 3 | 22.39% | 20.57% |
| Year 4 | 19.90% | 18.39% |
| Year 5 | 16.74% | 15.89% |

That is materially better than applying a generic youth premium, because the model can now distinguish:

- probability of playing at all;
- probability of becoming a useful scorer;
- probability of reaching genuine keeper or captaincy levels.

## Multi-season elite outcomes

The annual probabilities were combined into provisional five-year probabilities of producing at least one elite season.

| Threshold | Actual rate of at least one season | Predicted rate | Brier score |
|---:|---:|---:|---:|
| 90+ | 8.83% | 11.70% | 0.0474 |
| 100+ | 4.52% | 5.49% | 0.0278 |
| 110+ | 2.37% | 2.03% | 0.0157 |

The 90+ and 100+ probabilities are somewhat optimistic; the 110+ probability is slightly conservative. A separate direct five-year classifier was also tested. It did **not** improve Brier score over combining the annual probabilities:

- 90+: direct 0.0499 versus annual-combination 0.0474;
- 100+: direct 0.0384 versus annual-combination 0.0278;
- 110+: direct 0.0166 versus annual-combination 0.0157.

That result supports retaining annual models as the foundation. However, the current combination assumes annual independence, which is not realistic. Strong players tend to have several strong seasons; careers are persistent rather than five independent coin flips.

## Important implementation finding

The first prediction-output assembly exposed a pandas index-alignment defect that created systematic half-empty rows. The defect was detected through output-integrity checks, corrected by resetting both indices before concatenation, and all progress-03 results were rerun.

This is exactly the kind of silent data-pipeline failure the new package tests are intended to prevent.

## What this stage establishes

- A five-year season-by-season forecasting architecture is viable.
- Establishment, games, scoring and elite-tail probabilities can be modelled separately.
- Useful predictive signal remains through year five.
- Annual models outperform a direct five-year elite classifier on probability calibration in this first test.
- The forecast can represent a small genuine superstar chance without raising every young player’s median projection.

## What remains incomplete

- Adjacent future seasons are not yet modelled with realistic correlation.
- Draft-time performance remains materially harder than performance after one or two seasons of evidence.
- Rucks and key-position players still need position-specific establishment timing.
- The exact live REPL/captaincy/runway/currency implementation has not yet been connected through a clean adapter.
- No production current-player board has been generated from vNext.
- The current peak-based engine has not yet been run head-to-head on the same complete historical utility target.

## Next build

1. Estimate annual persistence and survival dependence so simulated careers remain coherent.
2. Build complete-cohort three- and five-year events such as at least one/two 90+, 100+ and 110+ seasons.
3. Add dedicated draft-time and positional development models.
4. Generate Monte Carlo career paths rather than independent annual expectations.
5. Feed each simulated path through the exact existing keeper utility layer.
6. Compare vNext with the current engine using realised discounted value above replacement and captaincy value.
7. Generate genuine future asset-value distributions for the UI.

## Current conclusion

The trajectory approach has passed its first meaningful test. It is not ready to replace the current engine, but it now supplies the missing statistical foundation: explicit probabilities for failure, useful production and elite production in each future season.
