# AFL RL vNext — progress 05: persisted models and current five-year career simulation

## What was built

This stage converts the research prototype into a deterministic inference pipeline.

- Five annual lead models are now trained once and saved as versioned `joblib` artifacts.
- The artifacts include preprocessing, establishment models, conditional games and scoring models, temporal isotonic calibrators, threshold models and residual scales.
- Current-player inference loads those artifacts; it does **not** refit models during export.
- A coherent Monte Carlo career simulator now generates correlated five-year paths for establishment, games and scoring.
- Every simulated season is passed through the existing keeper-utility concepts: position-specific cheap replacement, nonlinear surplus, captaincy value and 15% discounting.
- Genuine year-one and year-two future-value distributions are produced rather than advancing an empty valuation clock.

## Artifact training population

The persisted leads use every fully observable historical row through the 2025 target cutoff:

| Lead | Training rows | Latest origin whose target is complete | Conditional games residual SD | Conditional average residual SD |
|---:|---:|---:|---:|---:|
| 1 | 28,112 | 2024 | 5.28 | 15.02 |
| 2 | 25,580 | 2023 | 5.66 | 16.44 |
| 3 | 23,165 | 2022 | 5.87 | 17.39 |
| 4 | 20,848 | 2021 | 6.13 | 18.63 |
| 5 | 18,639 | 2020 | 6.30 | 19.61 |

## Independent 2021-origin check of the artifact estimator

The persisted implementation was separately checked on the 2021 historical origin. No 2021-or-later origin was used to train the corresponding lead model.

| Lead | Establishment Brier | Establishment AUC | Games MAE | Total-points MAE |
|---:|---:|---:|---:|---:|
| 1 | 0.0646 | 0.965 | 2.14 | 161.5 |
| 2 | 0.0727 | 0.956 | 2.54 | 187.0 |
| 3 | 0.0791 | 0.944 | 2.75 | 207.2 |
| 4 | 0.0812 | 0.935 | 2.74 | 209.9 |
| 5 | 0.0808 | 0.918 | 1.67 | 126.1 |

The threshold classifiers also retain strong discrimination. For example, 100+ AUC ranges from 0.938 to 0.983 across the five leads. These are not final model-selection claims, but they confirm that the faster persisted estimator has retained meaningful signal.

## Current simulation output

The current flattened source yielded 752 current/recent players under the reproducible eligibility rule available from the JSON. Historical and retired records are no longer included in the current board output.

For each player the output now includes:

- five-year mean, median, p10 and p90 keeper utility;
- expected games and total SuperCoach points;
- probability of no meaningful season;
- probability of at least one 90+, 100+ or 110+ season;
- expected number of 90+, 100+ and 110+ seasons;
- genuine simulated year-one and year-two utility means and ranges.

The current inference and 100-simulation board build takes about 7 seconds once artifacts exist. Increasing simulations changes Monte Carlo precision, not model fitting.

## Important interpretation

The current ranking is a **forecast/utility prototype**, not a replacement live board.

Some young players rank very aggressively. That is useful diagnostic evidence, but it is not yet proof that the ranking is correct. The current continuous simulator draws conditional averages around modelled means using pooled residual scales. It does not yet force its simulated 90+/100+/110+ frequencies to exactly match the separately calibrated threshold probabilities. This can create tension between the continuous scoring draw and the threshold classifiers.

The next stage must reconcile those two representations before comparing final keeper values.

## Confirmed engineering improvement

The earlier prototype repeatedly fitted preprocessing and all annual models during current-player generation. The new pipeline separates:

```text
training data -> persisted lead artifacts -> deterministic inference -> Monte Carlo careers -> keeper utility
```

This removes training side effects from production export and makes outputs reproducible from an explicit artifact set and random seed.

## Newly identified issue

The flattened `rl_model_data.json` produces 752 current/recent candidates under fields directly available in that file, whereas the live engine documentation refers to an 805-player board. The difference likely comes from transformations and force-active/position mappings created inside `rl_model.py` rather than represented directly in the flattened JSON.

Before any live comparison, vNext should consume an authoritative exported current-player key list from the existing engine, rather than independently approximating current eligibility.

## Next build

1. Export the exact active player universe and historical position state from the current engine in a stable, side-effect-free format.
2. Reconcile continuous simulated averages with calibrated threshold probabilities using a calibrated conditional distribution rather than pooled Gaussian residuals.
3. Estimate position- and career-stage-specific persistence, especially for rucks and key-position players.
4. Create realised historical keeper-utility targets and run the current engine and vNext against identical historical snapshots.
5. Extend simulated value beyond five years with explicit survival and decline rather than a generic peak runway.
6. Map raw simulated utility into the current RL player/pick currency only after the head-to-head validation is complete.

## Current conclusion

vNext now has a workable production spine: frozen model artifacts, fast deterministic current inference and coherent correlated career simulation. The next modelling priority is distributional coherence and a fair current-engine comparison, not more ad hoc youth adjustments.
