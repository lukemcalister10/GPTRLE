# TASK-024 — Roster ownership and team-specific utility

## Status

Completed ownership-contract and team-specific diagnostic. No production board or forecast changed.

## Resolved roster structure

Each of the 16 fantasy teams may hold:

- up to 42 senior-list players;
- up to four additional rookie-list players;
- up to 46 total players.

The observed 44–46 player counts are therefore valid and do not indicate ownership corruption.

Players labelled `Free Agents` or `Free agents` are deliberately outside the 16 owned rosters. The AFL has 18 clubs while the fantasy league has 16 teams, so surplus players remain available for later drafting.

## Ownership contract

`vnext/roster_ownership.py` now:

- normalises free-agent label spelling and case;
- separates owned players from free agents;
- validates exactly 16 named teams;
- permits up to 46 total players per team;
- records the 42 senior plus four rookie limit;
- prevents an exact 42-to-37 senior-list cut calculation unless rookie status is identified.

## Team-specific lineup diagnostic

For each team and each contender, balanced and rebuilder strategy:

1. all currently owned players were considered;
2. the optimiser selected the best legal 23-player scoring lineup;
3. all constrained and five free-choice slots were filled;
4. captain and vice-captain candidates were selected from the legal 23.

This produced 48 valid team-strategy lineups: 16 teams × three strategies.

Captaincy uses an explicit diagnostic proxy based on lead-one expected points plus vice-captain fallback when the captain misses. It is not yet a full weekly joint-availability simulation.

## Remaining limitation

The authoritative player source does not currently identify which owned players are rookies. This does not block team lineups, captaincy, vice-captain selection or roster-level marginal production because all owned players may be selected.

It does block an exact senior-list reduction from 42 to 37. A team with 46 total players could contain 42 seniors and four rookies, but total ownership alone cannot identify which five senior players must be cut while preserving rookie exemptions.

## Decision

Accept team ownership and free-agent treatment as valid. Proceed with team-specific utility using the full owned list. Keep offseason senior-list cut recommendations blocked until rookie status is supplied or added to the authoritative source.