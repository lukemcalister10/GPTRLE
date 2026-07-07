# TASK-002 — Authoritative current-season player universe

## Type
Data-contract and legacy adapter.

## Status
Implemented as an experiment/data-contract change. No forecast formulas, keeper utility, model calibration, UI, or frozen legacy engine behaviour were changed.

## Goal
Use Luke's 2026 current-season player source as the authoritative current universe, AFFL team, and positional eligibility contract, while preventing those current-season fields from leaking into historical snapshots.

## Authoritative source
- Source file: `data/current/Players_2026.csv.gz.b64`
- Materialised CSV: `data/current/Players_2026.csv`
- Authoritative row count: 804 players
- Authoritative current fields: current-universe inclusion, AFFL team, and positional eligibility only
- Valid exported eligibility values: `K-DEF`, `G-DEF`, `K-FWD`, `G-FWD`, `RUCK`, `MID`

The source contained known eligibility aliases (`RUC`, `SD`, `SF`) that are normalised in the vNext contract to approved codes (`RUCK`, `G-DEF`, `G-FWD`). Legacy eligibility aliases are also normalised (`GEN_DEF` -> `G-DEF`, `GEN_FWD` -> `G-FWD`, `KEY_DEF` -> `K-DEF`, `KEY_FWD` -> `K-FWD`, `RUC`/`RUCK` -> `RUCK`, `MID` -> `MID`). The raw current-source aliases are still reported in `reports/task-002-active-universe/invalid_or_missing_fields.csv` for auditability.

## Implementation
- Reconciliation code: `vnext/active_universe.py`
- Tests: `vnext/test_active_universe.py`
- Report directory: `reports/task-002-active-universe/`

The reconciliation uses normalised names only to find candidate matches. Persisted identifiers are `stable_player_id` values, generated as `afl-player-v1-` plus the first 20 hex characters of a SHA-256 hash over canonical JSON identity evidence. The evidence fields are `legacy_key`, `draft_year`, `draft_type`, `draft_pick`, `birth_year`, and `birth_date`; the legacy slug remains available separately as `legacy_key` for legacy/historical joins. Display name is deliberately excluded from the hash. Missing identity evidence is reported in `missing_identity_evidence.csv`.

## Final reconciliation
| Source / predicate | Count | Notes |
| --- | ---: | --- |
| Legacy board universe | 805 | `data/rl_build/rl_app_data.json` `active` list |
| Authoritative 2026 current source | 804 | `data/current/Players_2026.csv` |
| Previous vNext-derived current predicate | 752 | Predicate in the old current-board generator |
| Authoritative rows matched to stable IDs | 804 | No unmatched or ambiguous authoritative rows |
| Legacy-only rows | 1 | Confirmed as Taylor Adams (`taylor-adams`) |
| Previous-vNext omitted authoritative rows | 53 | All are listed in the wrongly-excluded report |

## Taylor Adams verification
Taylor Adams is confirmed as the exact 805-versus-804 difference:
- Present in the 805-player legacy active list.
- Absent from the 804-row authoritative current-season source.
- No other legacy active row is absent from the authoritative source.
- No authoritative row is absent from the legacy active list.

## Previous 752-player predicate omissions
The previous vNext predicate wrongly excluded 53 authoritative players by conflating current-universe inclusion with current scoring and recent-play signals.

Reason categories:
| Exclusion reason | Players |
| --- | ---: |
| `no_current_or_historical_scoring_games+not_recent_unplayed_draftee` | 38 |
| `no_current_or_historical_scoring_games+no_recent_activity_signal+not_recent_unplayed_draftee` | 12 |
| `no_recent_activity_signal+not_recent_unplayed_draftee` | 3 |

These reasons are diagnostics only. They must not exclude a player from the authoritative current universe.

## Generated reports
- `authoritative_universe.csv`
- `matched_players.csv`
- `unmatched_authoritative_players.csv`
- `legacy_only_players.csv`
- `ambiguous_matches.csv`
- `duplicate_name_cases.csv`
- `affl_ownership_comparison_unavailable.csv`
- `eligibility_disagreements.csv`
- `missing_identity_evidence.csv`
- `invalid_or_missing_fields.csv`
- `players_wrongly_excluded_by_current_scoring_or_recent_play_logic.csv`
- `manifest.json`

## AFFL ownership versus AFL club
`AFFL Team` is fantasy-league ownership. The legacy `club` field is a real AFL club and is retained only as `legacy_afl_club` informational data. Because no earlier AFFL ownership field exists in the checked-in sources, the AFFL ownership comparison report is intentionally empty/unavailable rather than comparing unlike fields.

## Determinism
`vnext/active_universe.py` writes sorted, newline-stable CSV reports plus a SHA-256 manifest. Tests prove repeat exports produce identical hashes and stable player IDs.

## Acceptance criteria
- [x] Exactly 804 authoritative player rows.
- [x] All authoritative rows accounted for.
- [x] No duplicate stable IDs.
- [x] No persisted name-only IDs.
- [x] Display-name-only changes do not alter `stable_player_id`.
- [x] Same-name players with different identity facts receive different IDs.
- [x] Every player has at least one valid eligibility after contract normalisation.
- [x] Eligibility values are limited to the six approved codes.
- [x] Multi-position eligibility is preserved.
- [x] Zero current-season scoring does not exclude a listed player.
- [x] Current-season source fields cannot affect historical snapshots.
- [x] Export output and hashes are deterministic.
- [x] Taylor Adams is the sole 805-versus-804 difference.
