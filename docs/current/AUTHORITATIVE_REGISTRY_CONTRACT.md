# Authoritative Player Registry Contract

## Scope

The vNext authoritative registry is the canonical 2026 player-universe and identity spine. It is allowed to define:

- the current 2026 player universe;
- `stable_player_id`;
- `legacy_key` linkage;
- current AFFL team ownership;
- current eligibility labels;
- identity evidence needed to prevent player-history collapse.

It must not alter frozen legacy production files or use current-season ownership/eligibility fields to construct historical snapshots.

## Canonical fields

`reports/task-002-active-universe/authoritative_universe.csv` is generated from `vnext/active_universe.py` and should contain one row per authoritative player:

- `source_row`: row number in `data/current/Players_2026.csv`.
- `stable_player_id`: non-name player identifier derived from identity evidence.
- `legacy_key`: historical/legacy player key used to join scoring history.
- `player_name`: current display name.
- `affl_team`: current AFFL team or free-agent state.
- `eligibilities`: current AFFL eligibility labels.
- `match_status`: authoritative-to-legacy reconciliation status.
- `legacy_name`, `legacy_afl_club`, `legacy_eligibilities`: legacy context, not current AFFL ownership.
- `identity_evidence_json`: sorted JSON used to derive `stable_player_id`.
- `missing_identity_evidence`: fields missing from the identity-evidence payload.
- `previous_vnext_included`, `previous_vnext_exclusion_reason`: audit of the old vNext inclusion predicate.

## Join rules

1. New vNext outputs must join by `stable_player_id` when both sides have it.
2. Historical backfills may use `legacy_key` only as a bridge into legacy scoring data.
3. Display names are labels only. They are never valid primary join keys.
4. Duplicate display names are permitted only when `stable_player_id` and `legacy_key` remain distinct and validation documents the alias.
5. Current AFFL team and current eligibility must not leak into historical snapshot feature construction.

## Known identity exception now locked

The Max King / Maxwell King pair is a permanent duplicate-name hazard:

- `max-king-stk` is St Kilda Max King: born `2000-07-07`, pick 4, 2018 national draft.
- `max-king-syd` is the younger Max/Maxwell King: born `2007-01-09`, pick 49, 2025 national draft.

The registry must keep these records separate. A zero/low-history young player must never inherit St Kilda Max King's established history, and St Kilda Max King must never carry the younger player's 2007 birth evidence.

## Validation gates

A registry release candidate is blocked if any critical identity issue is present:

- duplicate `stable_player_id`;
- duplicate `legacy_key` within matched players;
- impossible or implausible ND/RD/MSD draft age;
- unmatched authoritative player;
- ambiguous authoritative-to-legacy match;
- a known duplicate-name hazard collapsing into one identity;
- current-board row count drifting away from the authoritative registry without an explicit, reviewed derivation.

The generated `identity_health_issues.csv` is the machine-readable release gate. Rows with severity `critical` block finalisation. Rows with severity `review` can be accepted only when the disposition states why they are safe.

## Reproduction command

```bash
PYTHONPATH=vnext python vnext/active_universe.py --out reports/task-002-active-universe
cd vnext && pytest -q test_active_universe.py
```

## Downstream contract

Current-board, forecast, benchmark, and Claude-comparison tooling should consume the registry or a documented immutable snapshot derived from it. Any shadow player list, name-only join, or duplicated identity logic must be removed or explicitly documented as transitional technical debt.
