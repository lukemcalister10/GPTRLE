# TASK-044 — Replacement-aware 804-player board

## Status

Accepted diagnostic board. No production board, forecast or frozen Claude file changed.

## Objective

Build a complete 804-player immediate-lineup board using expected contribution above the best unselected legal replacement after each annual 368-slot league optimisation.

## Outputs

The reproducible runner writes:

- `replacement_aware_player_board_804.csv`;
- `replacement_levels.json`;
- `summary.json`.

For each strategy lens it exposes:

- signed lineup value above replacement;
- startable value, which clips negative annual contributions at zero because a rational manager would not start a below-replacement player;
- deterministic ranks for both views.

## Current result

Balanced values:

| Player | Replacement-aware value | Rank |
|---|---:|---:|
| Tristan Xerri | 169.62 | 151 |
| Logan McDonald | 57.78 | 274 |
| Alex Davies | 48.81 | 284 |

Ratios:

- Xerri / Logan McDonald: 2.94×;
- Xerri / Alex Davies: 3.47×.

This remains based on the flawed forecast that regresses Xerri's 2027 conditional average to 87.6, so correcting the forecast would likely widen the gap further.

## Tail behaviour

Signed negative lineup values:

- contender: 422;
- balanced: 420;
- rebuilder: 415.

These are not negative keeper asset values. They mean the player's expected scoring contribution is below the current replacement benchmark.

Clipping annual negative lineup contribution to zero produces 316 players with zero five-year startable contribution under every lens.

Top-100 membership is almost unchanged between signed and startable views, so the boundary mainly affects the lower-value population.

## Interpretation

Immediate lineup contribution and keeper asset value are not the same thing.

A player can have:

- zero current startable value;
- positive future development probability;
- useful trade optionality;
- future positional flexibility;
- retention value beyond current scoring contribution.

Those must be represented in a separate option-value layer rather than hidden by treating missed games as zero or by awarding broad positional scarcity bonuses.

## Decision

Accept the full replacement-aware board as the authoritative diagnostic for immediate lineup contribution.

Do not promote it as complete keeper value. The next model hypothesis must construct and historically validate a distinct future option component without double-counting expected lineup production.

## Reproduction

```bash
python vnext/run_task044_replacement_board.py \
  --annual-candidate-csv <candidate_board_annual.csv> \
  --output-dir reports/task-044-replacement-aware-board
```