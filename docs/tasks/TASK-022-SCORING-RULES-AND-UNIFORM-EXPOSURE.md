# TASK-022 — Scoring rules and uniform 2026 exposure

## Status

Implementation candidate. This task records the authoritative weekly scoring rules and the uniform current-season exposure context. It does not calculate or promote real-player keeper values.

## Current-season exposure

- 14 AFL rounds have elapsed.
- Every player has had one bye.
- Therefore every player has had 13 possible matches.
- The partial-season availability denominator is uniformly 13 for the current source.

No individual round mapping is required for this snapshot.

## Weekly scoring rules

Each team selects 23 scoring players:

- 4 general defenders;
- 2 key defenders;
- 5 midfielders;
- 1 ruck;
- 4 general forwards;
- 2 key forwards;
- 5 free-choice players.

All 23 selected players contribute their score. The five free-choice players are not non-scoring bench cover.

A designated captain scores double points. A designated vice captain receives the double-score bonus when the captain does not play. If neither plays, no captain bonus is awarded.

Emergencies are outside the 23-player scoring lineup. Their scores do not count automatically. A manager may actively promote an emergency into the selected 23 to cover an injury, in which case the promoted player scores and the unavailable selected player does not.

## Implementation

- `vnext/current_season_context.py` stores the uniform 14-round/13-match context.
- `vnext/league_config.py` now gives all 23 selected slots full scoring weight.
- The five unrestricted slots accept every position.
- `vnext/weekly_scoring.py` calculates exact captain and vice-captain fallback scoring.
- An expected captain-bonus helper supports later forecast utility diagnostics with an explicit independence approximation.

## Consequences for utility modelling

- League-wide production allocation must include 368 scoring slots, not only the 288 position-constrained slots.
- The 80 unrestricted scoring slots create genuine value for surplus high-scoring players, especially midfielders, but do not erase position scarcity because 288 slots remain constrained.
- Captaincy is an additional marginal utility component concentrated among the highest projected scorers.
- Vice-captain availability reduces the downside of captain non-selection.
- Emergency value is depth/optionality utility, not automatic weekly scoring.

## Acceptance rule

Accept if all 23 selected players score, captain and vice-captain fallback reconcile exactly, current availability uses 13 possible matches for every player, and emergencies remain non-scoring unless explicitly activated.