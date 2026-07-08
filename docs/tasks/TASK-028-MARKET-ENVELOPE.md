# TASK-028 — Strategy-market envelope

## Status

Implementation candidate. This task defines a diagnostic trade-opportunity layer without using historical fantasy trades as truth labels.

## Objective

Separate three quantities:

1. **League market value:** what the player may be worth to plausible buyers with different competitive windows.
2. **Current-roster value:** what the player contributes in their actual role on the present team.
3. **Realisable trade opportunity:** the portion of market value above current-roster value that may plausibly be converted through trade.

This allows:

- an elite producer on a rebuilding roster to create a trade line;
- a future-heavy asset on a contender to be valuable without belonging in the contender core;
- a valuable non-core contender player to be classified as trade inventory rather than expensive emergency depth;
- a player whose current roster is already their best use to have no forced trade surplus.

## Market envelope

The initial diagnostic market value is:

`70% × best strategy value + 30% × second-best strategy value`

across the contender, balanced and rebuilder views.

The best-use value is not accepted at 100 cents on the dollar because one ideal buyer may not exist. Including the second-best use provides a simple breadth-of-demand adjustment.

Realisable trade opportunity is:

`75% × max(0, market value − current-roster value)`

The 75% liquidity factor represents transaction friction and uncertain buyer availability. It is explicit and replaceable.

## Important limitation

These weights are sensitivity parameters, not learned coefficients. The current 16-team ownership distribution provides market-calibration evidence, but there are no authoritative historical trade outcomes or declared team-window labels suitable for fitting the values directly.

The envelope estimates opportunity, not the exact return in a negotiated trade.

## Acceptance rule

Accept as diagnostic infrastructure if it can:

- identify surplus value for a contender asset stranded outside the core;
- identify trade value in an older elite producer held by a rebuilder;
- identify market value in a future-heavy asset held by a contender;
- return zero surplus when the current roster is already the player's strongest use;
- expose all demand and liquidity assumptions.