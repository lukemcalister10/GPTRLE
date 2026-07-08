# TASK-017 — Current official position-eligibility contract

## Status

Implementation candidate. This task defines how official position updates enter the utility layer. It does not assign or change any player's real eligibility and does not calculate keeper values.

## Audit finding

The frozen Claude data currently exposes one `present_position` and one `future_position` per player. The frozen model explicitly collapses dual-position players to one dominant leg. That is sufficient for reproducing the production board but insufficient for optimisation-derived flexibility value.

## Contract

- Preferred input is a complete `eligible_positions` set keyed by `stable_player_id` or the reconciled legacy key.
- `primary_position` remains separate and is used only to measure the incremental value of additional eligibility.
- The current official eligibility set is reused unchanged at every forecast horizon.
- New preseason or in-season official updates create a new dated snapshot and trigger utility recalculation; they do not retrain the forecast model.
- The current single-valued `present_position` field remains an explicit fallback only. It must not be represented as proof that a player has no additional eligibility.
- Snapshot comparisons fail if the player universe changes unexpectedly.
- Invalid positions, duplicate players and missing eligibility fail explicitly.

## Added implementation

`vnext/position_eligibility.py` provides:

- canonical parsing of single and multi-position fields;
- strict dated eligibility records with source provenance;
- full-snapshot construction;
- unchanged eligibility across forecast horizons;
- exact reporting of official eligibility changes between snapshots.

## Current limitation

The repository does not yet contain a complete authoritative multi-position eligibility snapshot for the 804-player universe. Real-board dual-position valuation therefore remains blocked until that data is supplied or generated from an authoritative source. Single-position optimisation can proceed using the legacy fallback, but its flexibility output must be labelled incomplete.

## Acceptance rule

Accept if the contract preserves multi-position sets, never projects future positions, reports updates exactly and fails on malformed or drifting snapshots. No production or player-level eligibility change is approved by this task.