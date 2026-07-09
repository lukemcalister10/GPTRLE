# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
- Production baseline: frozen unchanged Claude engine under `engine/rl_after/`; no release cutover has been approved.
- Accepted point-forecast evidence: TASK-003Q, TASK-009 zero-history state separation, TASK-012 evidence-weighted demonstrated ceiling and TASK-047 pooled Ridge conditional-average point forecasts.
- Conditional-average defect work is recorded through TASK-047: TASK-044 and TASK-045 diagnosed broad compression, TASK-046 rejected broad-position routing, and TASK-047 accepted pooled Ridge for point forecasts.
- Uncertainty status: TASK-047 point forecasts are accepted, but its point quantiles and residual-based uncertainty outputs remain blocked pending TASK-048 calibration evidence.
- Release constraint: TASK-006 and the TASK-007 TASK-006 export must not be promoted.
- Partial-season exposure remains blocked until origin-safe historical intra-season snapshots exist.
- Forecast, uncertainty, keeper utility and owner policy remain separate layers; no production or keeper-value promotion is implied by TASK-047.
- Active task: [`TASK-048-RIDGE-UNCERTAINTY-CALIBRATION-AUDIT.md`](../tasks/TASK-048-RIDGE-UNCERTAINTY-CALIBRATION-AUDIT.md).
- Accepted decisions recorded: 15.

## Locked evidence
- Authoritative current universe: 804 players; raw Claude export: 805 rows with legacy-only Taylor Adams.
- Historical benchmark: 5,622 player-origin snapshots, 20,094 player-origin-lead rows per model and 25 legal rolling-origin folds, with zero target failures and zero fold failures.
- TASK-047 reduces meaningful-season conditional-average MAE from 14.61 to 11.65 and improves ruck and elite-prior errors materially while preserving every non-average forecast output exactly.
- Using the locked `points` target, TASK-047 improves total-points MAE from 449.43 to 447.15 overall; leads 1-3 improve and leads 4-5 worsen slightly.
- TASK-047 uncertainty outputs are not accepted because quantile calibration, pinball performance and interval coverage have not yet passed a predeclared audit.
- Frozen Claude files are protected by `artifacts/legacy_manifest.json` and `scripts/verify_legacy_manifest.py`.

## Read first
1. `AGENTS.md`
2. `docs/current/PROJECT_STATE.json`
3. `docs/current/VALIDATION_PROTOCOL.md`
4. `docs/current/ROADMAP_TO_PRODUCTION.md`
5. `docs/current/DECISION_LOG.md`
6. `docs/tasks/TASK-048-RIDGE-UNCERTAINTY-CALIBRATION-AUDIT.md`

## Immediate sequence
Complete TASK-048 as an evaluation-only audit of the accepted TASK-047 point-forecast distribution. Measure pinball loss, empirical quantile calibration, interval coverage and the structural effect of treating all non-meaningful seasons as zero-point mass. Do not alter the accepted Ridge point forecasts or uncertainty generator in the same pull request. If the audit fails, preserve the blocker and formulate one separate repair hypothesis.

## Decision rule
No component replaces production because selected current players look more plausible. Point-forecast acceptance, uncertainty acceptance, keeper-utility acceptance and production release are separate decisions. Production promotion still requires locked outcome-based evidence and Luke's explicit release approval; TASK-006 remains specifically release-blocked.
