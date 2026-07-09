# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
- Production baseline: frozen unchanged Claude engine under `engine/rl_after/`; no release cutover has been approved.
- Accepted point-forecast evidence: TASK-003Q, TASK-009 zero-history state separation, TASK-012 evidence-weighted demonstrated ceiling and TASK-047 pooled Ridge conditional-average point forecasts.
- Conditional-average defect work is recorded through TASK-047: TASK-044 and TASK-045 diagnosed broad compression, TASK-046 rejected broad-position routing, and TASK-047 accepted pooled Ridge for point forecasts.
- Release constraint: TASK-006 and the TASK-007 TASK-006 export must not be promoted.
- Uncertainty status: TASK-048 rejected acceptance of TASK-047 uncertainty outputs; point quantiles remain blocked after failed calibration, interval-coverage and structural-support gates.
- TASK-049 is the active isolated uncertainty hypothesis: replace the exact non-meaningful zero-mass branch with a three-state zero-game, one-to-five-game and meaningful-season distribution while preserving accepted TASK-047 point forecasts exactly.
- Partial-season exposure remains blocked until origin-safe historical intra-season snapshots exist.
- Forecast, uncertainty, keeper utility and owner policy remain separate layers; no production or keeper-value promotion is implied by TASK-047 or TASK-049.
- Active task: [`TASK-049-THREE-STATE-POINT-DISTRIBUTION.md`](../tasks/TASK-049-THREE-STATE-POINT-DISTRIBUTION.md).
- Accepted decisions recorded: 16.

## Locked evidence
- Authoritative current universe: 804 players; raw Claude export: 805 rows with legacy-only Taylor Adams.
- Historical benchmark: 5,622 player-origin snapshots, 20,094 player-origin-lead rows per model and 25 legal rolling-origin folds, with zero target failures and zero fold failures.
- TASK-047 reduces meaningful-season conditional-average MAE from 14.61 to 11.65 and improves ruck and elite-prior errors materially while preserving every non-average forecast output exactly.
- Using the locked `points` target, TASK-047 improves total-points MAE from 449.43 to 447.15 overall; leads 1-3 improve and leads 4-5 worsen slightly.
- Frozen Claude files are protected by `artifacts/legacy_manifest.json` and `scripts/verify_legacy_manifest.py`.
- TASK-048 evaluated 20,094 rows per model and rejected TASK-047 uncertainty outputs: mean pinball improved from 149.97 to 141.11, but gates 3, 4, 5, 6 and 7 failed (mean absolute quantile calibration error 0.1273; q25-q75 coverage 0.5877; max lead central interval coverage error 0.1663; max subgroup coverage error 0.2540; 1,776 one-to-five-game positive-point rows expose structural zero-mass incompatibility).

## Read first
1. `AGENTS.md`
2. `docs/current/PROJECT_STATE.json`
3. `docs/current/VALIDATION_PROTOCOL.md`
4. `docs/current/ROADMAP_TO_PRODUCTION.md`
5. `docs/current/DECISION_LOG.md`
6. `docs/tasks/TASK-049-THREE-STATE-POINT-DISTRIBUTION.md`

## Immediate sequence
Implement TASK-049 exactly as locked: test one target-compatible three-state point-distribution hypothesis, preserve every accepted TASK-047 point and non-uncertainty output, and accept or reject solely on the predeclared uncertainty gates.

## Decision rule
No component replaces production because selected current players look more plausible. Point-forecast acceptance, uncertainty acceptance, keeper-utility acceptance and production release are separate decisions. Production promotion still requires locked outcome-based evidence and Luke's explicit release approval; TASK-006 remains specifically release-blocked.
