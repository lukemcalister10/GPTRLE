# TASK-029 — Objective player comparison contract

## Status

Accepted design candidate. This task restores the primary purpose of the engine: compare one player with another objectively under three broad strategic lenses.

## Primary output

Every player receives three league-wide values:

- contender;
- balanced;
- rebuilder.

These values must support direct player-to-player comparison and deterministic ranking across the full player universe.

## Explicit non-goal

The primary player value must not depend on:

- the player's current fantasy owner;
- one named team's current roster construction;
- current ladder position;
- a specific team's temporary injury list;
- whether one particular contender or rebuilder happens to need that player's position today.

The league is a live trading market. Players move, contenders consolidate as finals approach, eliminated contenders sell current production, and rebuilding sides may hold production assets to create trade lines. A value tied too tightly to today's owner would cease to be an objective comparison tool.

## Role of current team assignments

The current `AFFL Team` assignments remain useful only to:

- show the ordinary distribution of scoring, age and future assets across 16 teams;
- test whether the resulting global values produce plausible market distributions;
- calibrate broad assumptions about scarcity, concentration and trading behaviour;
- identify structural anomalies in the valuation system.

They are not truth labels and do not alter an individual player's primary contender, balanced or rebuilder value.

## Relationship to TASK-027 and TASK-028

TASK-027's portfolio roles and TASK-028's market-envelope logic remain optional secondary decision-support tools. They can explain why a team might trade, retain or cut a player, but they do not replace the global player ranking.

The output hierarchy is:

1. objective player forecasts;
2. objective contender, balanced and rebuilder player values;
3. league-wide player rankings and direct comparison gaps;
4. optional roster or trade interpretation.

The optional interpretation must never feed back into the primary value and create circular team-specific pricing.

## Implementation

`vnext/player_comparison.py` provides:

- a strict three-value player record;
- deterministic ranking under one selected lens;
- direct value-gap comparison between two players;
- no team-specific input surface.

## Acceptance rule

Accept if two players can be compared under each lens without knowing who currently owns either player, while current ownership data remains available only as market context and validation evidence.