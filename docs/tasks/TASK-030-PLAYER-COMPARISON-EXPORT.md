# TASK-030 — Objective player comparison export

## Status

Implementation candidate. This task converts complete five-season forecast vectors into one objective contender, balanced and rebuilder comparison row per player.

## Objective

Produce the practical output required by the project:

- one row per player;
- contender value and rank;
- balanced value and rank;
- rebuilder value and rank;
- deterministic player-to-player comparability across the complete universe.

## Input contract

The builder accepts long-form annual forecast rows containing:

- stable player identifier;
- forecast year;
- expected utility;
- uncertainty in the same units;
- optional display metadata such as name, current positions and current owner.

Every player must have exactly one row for every declared forecast year. Missing years, duplicate years, non-finite values or conflicting metadata fail explicitly.

## Ownership guardrail

Current owner is copied to the export only as display metadata. It is not passed into strategy aggregation, ranking or tie-breaking.

Changing the owner labels while holding forecast vectors constant must leave every value and rank unchanged.

## Calculation

The same expected-utility and uncertainty vector is passed through the accepted contender, balanced and rebuilder horizon lenses. The resulting values are stored in `PlayerComparison` records and ranked independently under each lens.

The final export is ordered by balanced rank and contains the three values and three ranks.

## Deliberate exclusions

- No named-team adjustment.
- No current ladder adjustment.
- No roster-role or trade recommendation.
- No arbitrary rescaling to match the legacy board.
- No production promotion.

## Next step

Connect the successful TASK-012 current-board annual prediction artifact to this strict adapter, derive the declared uncertainty field, and persist the first complete 804-player comparison table with validation summaries.

## Acceptance rule

Accept if complete forecast vectors yield deterministic three-lens values and ranks, owner metadata cannot alter them, and malformed horizons fail rather than silently dropping or imputing rows.