# TASK-026 — Exact retain-to-40 optimiser

## Status

Accepted as a feasibility baseline only. It is not a complete strategic roster objective and must not be used by itself for contender, balanced or rebuilder recommendations.

## Objective

For each owned roster above 40 players, retain exactly 40 players while:

1. maximising the sum of one scalar player-utility input;
2. preserving the ability to field a legal 23-player scoring lineup;
3. respecting current official multi-position eligibility.

This prevents a simple lowest-value cut list from accidentally removing the only viable ruck, key defender, key forward or other constrained-position cover.

## Implementation

`vnext/roster_cut_optimiser.py` uses an exact mixed-integer optimisation:

- one binary retain variable per player;
- one binary assignment variable for each legal player-slot pairing;
- exactly 40 retained players when the current roster is above 40;
- every one of the 23 scoring slots filled;
- each player assigned to at most one scoring slot;
- only retained players may be assigned.

Teams at 40 or fewer remain unchanged.

## Full current-roster diagnostic

The calculation was run for all 16 current rosters under contender, balanced and rebuilder scalar utility.

Current compulsory cuts per strategy:

- 11 teams at 46 players: 66 cuts;
- 3 teams at 45 players: 15 cuts;
- 2 teams at 44 players: 8 cuts;
- total: 89 cuts across the league.

Strategy overlap:

- contender and balanced agree on 82 of 89 cuts;
- balanced and rebuilder agree on 82 of 89 cuts;
- contender and rebuilder agree on 77 of 89 cuts.

## Effect of positional constraints

Compared with simply cutting the lowest individual utility players, legal-lineup protection changed:

- 2 teams in the contender view;
- 3 teams in the balanced view;
- 4 teams in the rebuilder view.

The binding cases preserved scarce positional cover, principally reserve rucks and key defenders.

## Material limitation identified after acceptance

A strategic roster is not the 40 highest scalar-valued players.

- A contender should concentrate winning production in roughly its best 23–26 players and may prefer low-value positional emergencies beyond that core rather than leave substantial trade value stranded outside the winning lineup.
- A valuable non-core contender asset should often be classified as a trade candidate, not automatically retained because its standalone keeper value is high.
- A rebuilder may deliberately hold elite current production because it preserves trade lines, even when those points do not improve the rebuilding objective directly.
- A rebuilder may also retain development assets whose present production is low.

Therefore TASK-026 answers only: “Can this 40-player set preserve one legal lineup while retaining the largest supplied scalar total?” It does not answer the strategic portfolio question.

## Decision

Retain the optimiser as a deterministic feasibility component and comparison baseline. Do not use its cut identities as final contender, balanced or rebuilder recommendations. TASK-027 defines the required portfolio-role separation.