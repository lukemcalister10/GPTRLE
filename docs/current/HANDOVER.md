# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
- Production: frozen legacy engine under `engine/rl_after/`.
- Challenger: vNext progress 05 under `vnext/`.
- Active roadmap phase: Phase 0 repository transition.
- Active task: [`TASK-003-LEGACY-BENCHMARK.md`](../tasks/TASK-003-LEGACY-BENCHMARK.md).
- Accepted decisions recorded: 9.

## Current vNext artifact
- Target cutoff: 2025.
- Training coverage: L1: 28,112 rows, L2: 25,580 rows, L3: 23,165 rows, L4: 20,848 rows, L5: 18,639 rows.
- Artifact manifest identity: `b61da298819f`.
- Existing integrity suite: 13 tests in `vnext/`.

## Read first
1. `AGENTS.md`
2. `docs/current/OPERATING_MODEL.md`
3. `docs/current/ROADMAP_TO_PRODUCTION.md`
4. `docs/current/VALIDATION_PROTOCOL.md`
5. `docs/current/MODEL_SPEC_VNEXT.md`
6. `docs/tasks/TASK-003-LEGACY-BENCHMARK.md`

## Immediate next milestone
Complete TASK-001 without changing the legacy engine or model outputs. Then activate TASK-002 to reconcile the authoritative player universe, followed by TASK-003 for the fair legacy-vNext benchmark.

## Decision rule
No forecast or utility component replaces production because it looks more plausible. Replacement requires the locked outcome-based evidence in `VALIDATION_PROTOCOL.md` and Luke's explicit release approval.
