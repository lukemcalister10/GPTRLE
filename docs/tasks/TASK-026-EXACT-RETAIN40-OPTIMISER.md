# TASK-026 — Exact retain-to-40 optimiser

## Status

Implementation and diagnostic candidate. No production board, forecast or frozen Claude file changed.

## Objective

For each owned roster above 40 players, retain exactly 40 players while:

1. maximising the sum of the selected strategy's multi-year player utility;
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

The calculation was run for all 16 current rosters under contender, balanced and rebuilder utility.

Current compulsory cuts per strategy:

- 11 teams at 46 players: 66 cuts;
- 3 teams at 45 players: 15 cuts;
- 2 teams at 44 players: 8 cuts;
- total: 89 cuts across the league.

Strategy overlap:

- contender and balanced agree on 82 of 89 cuts;
- balanced and rebuilder agree on 82 of 89 cuts;
- contender and rebuilder agree on 77 of 89 cuts.

This shows that the strategy lenses alter a meaningful minority of marginal retention decisions without generating unrelated lists.

## Effect of positional constraints

Compared with simply cutting the lowest individual utility players, legal-lineup protection changed:

- 2 teams in the contender view;
- 3 teams in the balanced view;
- 4 teams in the rebuilder view.

The binding cases preserved scarce positional cover, principally reserve rucks and key defenders. In most cases the utility cost of protecting lineup feasibility was small, but the rule prevented an invalid post-cut roster.

One rebuilder tie involved equivalent key-forward/general-forward utility; the deterministic optimiser selected one of the equal-value alternatives. Equal-utility cut identities should be presented as interchangeable rather than falsely ordered.

## Interpretation

The optimiser answers: “Which 40 currently owned players maximise this strategy's retained forecast utility while preserving one legal scoring lineup?”

It does not yet price:

- trade return available before cutting;
- probability of redrafting a cut player;
- free-agent replacement quality after the draft;
- more than one layer of positional emergency depth;
- manager-specific preferences.

Therefore these remain diagnostic cut candidates rather than final instructions to delist players.

## Acceptance rule

Accept if the retained roster contains exactly 40 players, can field a legal 23, maximises declared player utility, and exposes when positional feasibility changes the naive cut order.