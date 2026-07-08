# TASK-023 — First full 804-player utility diagnostic

## Status

Completed diagnostic-only calculation from the accepted TASK-009 + TASK-012 current-board artifact. No forecast, production export, TASK-006 output or frozen Claude file changed.

## Inputs

- 804 authoritative players;
- forecast years 2027–2031;
- current official comma-separated eligibility;
- 16 teams;
- 288 position-constrained scoring slots;
- 80 free-choice scoring slots;
- 368 total scoring slots;
- contender, balanced and rebuilder horizon lenses from TASK-020.

The successful TASK-012 current-board artifact was recovered from GitHub Actions artifact `8157996496` with digest `sha256:5534660164853f730631db02dce9c5a9ec0322dac8ea90fa0159b8b6cde3e47a`.

## Utility construction

For each player and strategy:

1. Aggregate the five annual expected-points forecasts using the declared horizon weights.
2. Apply the declared risk coefficient to a meaningful-season mixture uncertainty proxy:
   `conditional season points × sqrt(p × (1 − p))`.
3. Optimise all 368 scoring slots using current eligibility.
4. Remove each selected player and re-optimise to obtain exact marginal production utility.
5. Restrict each selected dual-position player to the first authoritative eligibility and re-optimise to measure exact flexibility value.

The uncertainty proxy captures establishment/availability uncertainty only because the current-board export does not contain conditional scoring quantiles. It must not be represented as a complete forecast standard deviation.

## Results

All three strategies selected exactly 368 players and every selected player had positive exact marginal production utility.

| Metric | Contender | Balanced | Rebuilder |
|---|---:|---:|---:|
| Total selected risk-adjusted utility | 288,198.27 | 286,713.14 | 283,098.83 |
| Median selected marginal utility | 407.18 | 422.75 | 401.78 |
| Maximum marginal utility | 1,799.02 | 1,778.40 | 1,755.84 |
| Selected players with positive flexibility value | 32 | 31 | 31 |
| Maximum flexibility value | 67.74 | 62.60 | 91.66 |

Selection overlap:

- contender versus balanced: 360 of 368;
- balanced versus rebuilder: 361 of 368;
- contender versus rebuilder: 353 of 368.

Top-100 marginal-value overlap:

- contender versus balanced: 96;
- balanced versus rebuilder: 94;
- contender versus rebuilder: 90.

This demonstrates that the strategy views are meaningfully different without producing three unrelated boards.

## Scarcity behaviour

The optimiser does not use fixed replacement marks. The minimum selected utility differs by slot family and strategy. For the balanced view:

- GDEF: 328.89;
- KDEF: 254.91;
- MID: 363.91;
- RUC: 294.16;
- GFWD: 330.06;
- KFWD: 363.00;
- free choice: 310.36.

These are realised assignment cut lines, not permanent replacement constants. They will change when forecasts or official eligibility change.

Dual-position value is asymmetric and often exactly zero. Only 31 balanced selections gained positive total league utility from their additional eligibility. The largest positive flexibility effects were concentrated in players who could fill key-defender constraints. A forward adding midfield eligibility generally produced no marginal benefit, as expected.

## Captaincy

The exact weekly captain and vice-captain rules are implemented, but captaincy is not included in the diagnostic ranking.

A league-optimal top-16 captain potential was calculated separately. The balanced replacement-captain utility was 1,579.26. This is not roster-specific captain value and is not added to keeper rankings.

## Ownership audit blocker

The authoritative `AFFL Team` field contains 16 named teams plus free agents, confirming that current ownership data is present. However, the named teams currently contain 44–46 players each rather than the declared in-season roster size of 42:

- 12 teams contain 46 players;
- 3 teams contain 45 players;
- 2 teams contain 44 players;
- 75 players are labelled free agents across the two spellings `Free Agents` and `Free agents`.

The 16 named-team counts total more than 16 × 42. Until this discrepancy is explained or reconciled, roster-specific lineup, captain, vice-captain, emergency and five-player cut decisions cannot be treated as authoritative.

## Partial 2026 handling

TASK-021 is not overlaid on these forecasts. The accepted current-board snapshot already contains the 2026 row, so applying the adapter after prediction would double-count current evidence. The next forecast experiment must apply asymmetric shrinkage while constructing the 2026 snapshot, before prediction.

## Decision

Accept the aggregate league-allocation mechanism as a successful diagnostic. Do not promote the resulting values to production.

Roster-specific utility and captaincy are blocked on ownership reconciliation. Partial-season integration remains a separate forecast hypothesis at snapshot construction.