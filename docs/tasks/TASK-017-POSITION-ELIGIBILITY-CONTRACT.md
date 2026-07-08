# TASK-017 — Current official position-eligibility contract

## Status

Accepted contract. This task defines how official position updates enter the utility layer. It does not assign or change any player's real eligibility and does not calculate keeper values.

## Audit finding

The frozen Claude model data exposes one `present_position` and one `future_position` per player, and the frozen model explicitly collapses dual-position players to one dominant leg. That is sufficient for reproducing the production board but insufficient for optimisation-derived flexibility value.

The separate authoritative current-universe source, `data/current/Players_2026.csv`, does preserve full current eligibility in its comma-separated `Position/s` field for all 804 players. `vnext/active_universe.py` already parses and reconciles those sets. The earlier statement that the repository lacked a complete multi-position snapshot was incorrect because it inspected only the collapsed legacy model data.

## Contract

- Preferred input is the complete authoritative current eligibility set keyed through the reconciled registry.
- `primary_position` remains separate and is used only to measure the incremental value of additional eligibility.
- The current official eligibility set is reused unchanged at every forecast horizon.
- New preseason or in-season official updates create a new dated snapshot and trigger utility recalculation; they do not retrain the forecast model.
- The single-valued legacy `present_position` field remains a fallback only and must not overwrite authoritative multi-position eligibility.
- Snapshot comparisons fail if the player universe changes unexpectedly.
- Invalid positions, duplicate players and missing eligibility fail explicitly.

## Added implementation

`vnext/position_eligibility.py` provides:

- canonical parsing of single and multi-position fields;
- strict dated eligibility records with source provenance;
- full-snapshot construction;
- unchanged eligibility across forecast horizons;
- exact reporting of official eligibility changes between snapshots.

TASK-018 adds the adapter from the authoritative 804-player source and the exact league lineup configuration.

## Acceptance rule

Accept if the contract preserves multi-position sets, never projects future positions, reports updates exactly and fails on malformed or drifting snapshots. No production or player-level eligibility change is approved by this task.