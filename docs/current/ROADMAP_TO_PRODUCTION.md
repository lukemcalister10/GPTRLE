# Roadmap to Production

## Definition of finished
The project is finished when the repository can produce a defensible keeper-league board from a clean checkout, the forecast challenger has beaten both simple baselines and the legacy engine under the locked outcome-based protocol, future values are generated from simulated future evidence rather than clock advancement, the UI rebuilds from source, and the legacy board remains available as a rollback.

## Phase 0 — durable repository transition
**Goal:** make GitHub the single source of truth without changing any model output.

Deliverables:
- import the current vNext progress into `vnext/`;
- install concise `AGENTS.md`, current docs, PR template, and CI;
- preserve and hash the legacy engine;
- verify all existing vNext tests from a clean checkout;
- generate a compact repository handover.

Exit gate:
- no legacy file changes;
- vNext tests pass;
- CI and reproduction commands work;
- Luke approves the operating model.

## Phase 1 — common player universe and fair legacy benchmark
**Goal:** compare legacy and vNext on identical players, historical information, and outcome targets.

Deliverables:
- side-effect-free export of the legacy engine's authoritative active-player keys and positions;
- `PlayerSnapshot(as_of_year)` contract covering all time-dependent facts;
- legacy adapter that evaluates historical snapshots without future list status or future position;
- simple baselines and legacy outputs on the locked rolling-origin protocol;
- explicit failed-row report with zero silent omissions.

Exit gate:
- player-universe reconciliation is complete;
- legacy benchmark is reproducible;
- all historical information-boundary tests pass.

## Phase 2 — coherent probability distribution
**Goal:** ensure continuous scoring simulations and threshold probabilities describe the same distribution.

Deliverables:
- calibrated conditional scoring distribution, not pooled Gaussian residuals alone;
- non-crossing quantiles and threshold coherence;
- probability calibration by position, tenure, pick band, and age;
- position/career-stage residual and persistence estimates;
- ablation showing the value of each added complexity.

Exit gate:
- vNext improves the declared distributional metrics over simple baselines;
- no material calibration failure in a sufficiently sized critical subgroup;
- simulations reproduce the model's own 80+/90+/100+/110+/120+ probabilities.

## Phase 3 — full career trajectories
**Goal:** model establishment, availability, scoring, persistence, decline, and delisting beyond five years.

Deliverables:
- season-by-season survival/listed model;
- games and scoring distributions conditional on state;
- position-specific and role-sensitive development/decline where supported;
- correlated career simulation through remaining career;
- proper +1/+2 future asset-value distributions.

Exit gate:
- one-, three-, and five-year forecasts beat the legacy engine on declared primary metrics;
- long-horizon results are stable under sensitivity tests;
- no generic youth boost is required to create plausible upside.

## Phase 4 — keeper-utility validation
**Goal:** test rather than assume the value conversion for this league.

Deliverables:
- formal specification of replacement, lineup, bench, key-position, captaincy, list-size, and acquisition constraints;
- roster optimiser or simulation representing 16 heterogeneous teams;
- comparison of explicit marginal roster utility with the current reduced-form REPL/captaincy formula;
- sensitivity analysis for replacement marks, discounting, gamma compression, and captaincy threshold.

Exit gate:
- retain the current utility formula if it approximates explicit roster utility well;
- otherwise adopt only changes that improve the declared utility objective without sacrificing forecast validity.

## Phase 5 — player/pick currency and board contract
**Goal:** map forecast utility into a stable, interpretable board currency.

Deliverables:
- transparent raw forecast, raw utility, optional policy adjustment, and final currency fields;
- draft-pick valuation from the same outcome model;
- current, +1, +2, downside, median, upside, appreciation, and elite-probability fields;
- exact 805/current authoritative universe or documented successor universe;
- full-population legacy-vNext comparison.

Exit gate:
- no hidden board-only forecast behaviour;
- player and pick values share one documented currency;
- all output components reconcile.

## Phase 6 — UI rebuild
**Goal:** present the model clearly without reproducing calculations in JavaScript.

Deliverables:
- source-controlled UI assets;
- UI consumes authoritative exported values;
- player explanation panel showing forecast, utility, and policy components;
- filters for horizon, position, age, tenure, and risk;
- rebuild and parity tests.

Exit gate:
- clean UI build succeeds;
- displayed values exactly match the authoritative artifact;
- missing source-asset issue is resolved.

## Phase 7 — shadow release and production cutover
**Goal:** earn replacement safely.

Deliverables:
- legacy and vNext boards produced side by side for a defined shadow period;
- frozen release candidate and manifest;
- regression, sensitivity, and cold-start reports;
- rollback procedure;
- release decision.

Production acceptance criteria:
1. vNext beats the legacy engine on both three- and five-year discounted keeper-utility error by at least 3%, or provides a statistically supported equivalent gain on the predeclared composite.
2. vNext beats the strongest simple baseline on every primary horizon.
3. Probability calibration improves or remains within the declared tolerance for meaningful seasons and elite thresholds.
4. No critical subgroup with adequate sample size regresses by more than 5% without an accepted football explanation and compensating overall gain.
5. No leakage, missing-player, silent-row-drop, non-determinism, or UI-parity failure.
6. Luke approves the final production board after reviewing diagnostics, not named-player hard gates.
