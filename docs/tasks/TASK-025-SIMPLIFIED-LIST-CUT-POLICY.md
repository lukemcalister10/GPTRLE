# TASK-025 — Simplified total-list cut policy

## Status

Implementation candidate. This task replaces the senior/rookie distinction with one owner-approved total-list rule for keeper-value and offseason-cut diagnostics.

## Rule

- A team may hold up to 46 players.
- At the offseason cut point, a team must reduce to no more than 40 players.
- Rookie status is ignored because its incremental modelling value is not worth the data and maintenance cost.
- Free agents remain outside owned team lists and are eligible to re-enter through the draft process.

## Consequences

Required cuts are now deterministic from total roster size:

- 46 players: cut at least 6;
- 45 players: cut at least 5;
- 44 players: cut at least 4;
- 40 or fewer: no compulsory cut.

There is no longer a blocker from missing rookie identification.

## Implementation

`vnext/roster_ownership.py` now exposes:

- a 46-player total maximum;
- a 40-player offseason maximum;
- `required_offseason_cuts(team_size)` with explicit validation.

The previous 42-senior/4-rookie and 37-senior-cut logic is retired for modelling purposes.

## Next step

Use contender, balanced and rebuilder player utilities to select the lowest-cost cuts while preserving a legal 23-player lineup and sufficient positional depth. This must remain a diagnostic until the cut objective and depth treatment are validated.

## Acceptance rule

Accept if total-list counts alone determine compulsory cuts, teams above 46 fail, and no rookie-status input is required.