# TASK-027 — Strategic roster portfolio objective

## Status

Decision and infrastructure candidate. This task corrects the assumption that a contender, balanced team or rebuilder should simply retain the 40 highest scalar-valued players.

## Core principle

Player value and roster-slot value are different.

A player can be highly valuable in the league while being a poor use of a particular team's roster portfolio. The correct action may be to trade the player rather than retain or cut them.

## Contender portfolio

A contender should generally:

- concentrate as much winning production as possible in approximately its best 23–26 players;
- carry enough low-cost positional emergency depth to survive ordinary injuries;
- avoid leaving substantial asset value stranded in players ranked roughly 25–45 who do not materially improve the best side;
- convert valuable non-core players into upgrades, future assets or better positional fits where possible;
- distinguish trade candidates from cut candidates.

A high-value player outside the contender core is therefore not automatically a keeper. The model must compare the player's emergency contribution with the value that could be realised through trade.

## Rebuilder portfolio

A rebuilder should generally:

- retain development and longer-horizon assets;
- retain some elite current-production players where they preserve strong trade lines;
- avoid treating current points as worthless merely because the team is rebuilding;
- distinguish production held for trade inventory from production held to win immediately;
- avoid forcing every valuable veteran into the cut pool.

## Balanced portfolio

A balanced team sits between those objectives and may retain a broader productive core while preserving both trade flexibility and development value.

## Required player components

The strategic portfolio layer must keep at least four values separate:

1. **Lineup utility:** contribution to the best legal 23 and captaincy.
2. **Emergency utility:** likely value when covering injuries or role changes.
3. **Future asset utility:** longer-horizon retained value and development.
4. **Trade utility:** value that could plausibly be converted into other assets.

No single weighted sum should erase these distinctions before the roster role is assigned.

## Roster roles

TASK-027 introduces five explicit roles:

- core;
- emergency depth;
- development;
- trade candidate;
- cut candidate.

The role is strategy-dependent. The same player may be contender trade inventory, balanced core, and rebuilder trade inventory or development value.

## Initial diagnostic profiles

The code includes replaceable profile defaults:

- contender core target: 26 players;
- balanced core target: 27 players;
- rebuilder immediate core target: 23 players;
- strategy-specific weights for future and trade value;
- a contender stranded-asset penalty that pushes valuable non-core players toward the trade-candidate role rather than falsely treating them as ordinary depth.

These are structural sensitivity parameters, not accepted production calibration.

## Consequence for TASK-026

The exact retain-to-40 optimiser remains useful for legal-lineup feasibility and as a scalar baseline. Its cut identities are not final strategic recommendations because it cannot distinguish a tradeable non-core asset from a cheap emergency.

## Next implementation

1. Derive lineup and emergency utility from exact team optimisation.
2. Define an auditable trade-utility proxy without using historical fantasy trades as truth labels.
3. Produce team-level role classifications rather than one cut ranking.
4. Test whether contender portfolios concentrate production in the top 23–26 while retaining sufficient positional cover.
5. Test whether rebuilder portfolios preserve development assets and selected production trade inventory.

## Acceptance rule

Accept if the system can classify a valuable non-core contender player as a trade candidate, retain low-value required emergency cover, and allow a rebuilder to hold elite production for trade value without treating that production as immediate winning utility.