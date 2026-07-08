# TASK-018 — League lineup and authoritative eligibility

## Status

Implementation candidate. This task supplies the exact league lineup and connects the existing 804-player comma-separated eligibility source to the utility layer. It does not yet calculate or promote keeper values.

## Authoritative league structure

There are 16 teams. Each team fields:

- 4 general defenders;
- 2 key defenders;
- 5 midfielders;
- 1 ruck;
- 4 general forwards;
- 2 key forwards;
- 5 free-choice bench players.

That is 18 active positional slots and 23 listed lineup slots per team. In-season rosters contain 42 players and are reduced to 37 in the offseason.

## Eligibility source

`data/current/Players_2026.csv` is authoritative for the current 804-player universe and current eligibility. Its `Position/s` column stores one or more positions separated by commas. `vnext/active_universe.py` already parses these values into eligibility tuples.

This task adds a utility-layer adapter that maps:

- `G-DEF` to `GDEF`;
- `K-DEF` to `KDEF`;
- `MID` to `MID`;
- `RUCK` to `RUC`;
- `G-FWD` to `GFWD`;
- `K-FWD` to `KFWD`.

The adapter requires exactly 804 rows and preserves multi-position sets.

## Bench treatment

The five bench slots accept every position. Their scoring multiplier defaults to zero because the league rules supplied identify them as free-choice bench slots but do not yet establish that their weekly points contribute directly. Later utility work may price injury coverage, optionality and future use explicitly rather than counting full bench production by assumption.

## Correction to TASK-017

TASK-017 incorrectly stated that the repository lacked a complete authoritative multi-position snapshot. That conclusion came from inspecting the collapsed legacy model data. The authoritative current-universe CSV does contain the required comma-separated eligibility and is now wired through this task.

## Acceptance rule

Accept if the lineup counts are exact, the authoritative source yields 804 complete eligibility records, at least one multi-position player is preserved, and no forecast, production or frozen Claude file changes.