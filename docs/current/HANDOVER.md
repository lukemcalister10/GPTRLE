# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
- Production baseline: frozen unchanged Claude engine under `engine/rl_after/`.
- Forecast challenger: accepted TASK-003Q evidence under `vnext/`; no release cutover approved.
- Integration branch: `vnext` at merged TASK-007 state.
- Release constraint: TASK-006 and the TASK-007 TASK-006 export must not be promoted.
- Active workstream: post-TASK-007 baseline defects and bounded one-hypothesis experiments.
- Active task: [`TASK-008-BASELINE-ERROR-AUDIT.md`](../tasks/TASK-008-BASELINE-ERROR-AUDIT.md).
- Accepted decisions recorded: 10.
- Test files discovered under `vnext/`: 26.

## Locked evidence
- Authoritative current universe: 804 players.
- Historical benchmark: 5,622 player-origin snapshots, 20,094 player-origin-lead rows per model and 25 legal rolling-origin folds.
- TASK-003Q production forecast shape: 4,020 rows, exactly five leads per player.
- Frozen Claude files are protected by `artifacts/legacy_manifest.json` and `scripts/verify_legacy_manifest.py`.

## Read first
1. `AGENTS.md`
2. `docs/current/VALIDATION_PROTOCOL.md`
3. `docs/current/ROADMAP_TO_PRODUCTION.md`
4. `docs/current/DECISION_LOG.md`
5. `docs/current/TASK-008-BASELINE-ERROR-AUDIT.md`
6. `docs/tasks/TASK-008-BASELINE-ERROR-AUDIT.md`

## Immediate sequence
Complete the unchanged-Claude baseline audit, then address partial-season exposure, pedigree persistence, zero-history differentiation, established low-ceiling treatment and pathological zero values in separate pull requests. Each modelling PR must preserve the frozen Claude files and show locked historical before/after evidence plus full-population current-board effects.

## Decision rule
No component replaces production because selected current players look more plausible. Promotion requires locked outcome-based evidence and Luke's explicit release approval. TASK-006 is specifically release-blocked.
