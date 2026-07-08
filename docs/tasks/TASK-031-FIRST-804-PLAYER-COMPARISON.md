# TASK-031 — First complete 804-player comparison run

## Status

Completed diagnostic run from the accepted TASK-009 + TASK-012 annual candidate forecasts. No production board or frozen Claude file changed.

## Input

- 804 authoritative players;
- five forecast seasons: 2027–2031;
- expected season points from the accepted candidate board;
- meaningful-season mixture uncertainty proxy;
- accepted contender, balanced and rebuilder horizon lenses.

## Uncertainty proxy

The current annual candidate artifact does not contain conditional scoring quantiles. This run therefore uses:

`conditional season points × sqrt(p_meaningful × (1 − p_meaningful))`

This captures establishment/availability mixture uncertainty. It is not a complete forecast standard deviation and must remain labelled as a proxy.

## Output contract

The reproducible runner writes `player_comparison_804.csv` containing:

- stable player identifier;
- player name;
- current positions;
- current owner as display metadata only;
- contender value and rank;
- balanced value and rank;
- rebuilder value and rank.

Changing ownership labels cannot alter values or ranks.

## Diagnostic results

All 804 players received complete values and deterministic ranks.

Top-100 overlap:

- contender versus balanced: 96;
- balanced versus rebuilder: 95;
- contender versus rebuilder: 91.

Spearman rank correlation:

- contender versus balanced: 0.9972;
- balanced versus rebuilder: 0.9971;
- contender versus rebuilder: 0.9892.

The three views therefore remain recognisably one player market while changing a meaningful minority of decisions near ranking boundaries.

## Interpretation

These are intrinsic, risk-adjusted forecast values under three horizon profiles. League-wide scarcity and roster-allocation effects remain separate diagnostics and are not yet folded into the displayed values.

This separation is deliberate. A final combined keeper score must demonstrate that adding scarcity improves objective usefulness without double-counting production or creating a large tied zero-value tail for players outside the optimal 368 scoring allocation.

## Reproducibility

Run:

```bash
python vnext/run_task031_player_comparison.py \
  --annual-candidate-csv <candidate_board_annual.csv> \
  --output-dir reports/task-031-player-comparison
```

The runner fails unless exactly 804 complete five-year player vectors are produced.

## Decision

Accept this as the first complete objective comparison table and reproducible baseline. Do not promote it as the final keeper ranking until the scarcity-combination hypothesis is separately tested.