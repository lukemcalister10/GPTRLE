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
- Existing integrity suite: 20 tests in `vnext/`, including TASK-002 active-universe contract tests.

## Read first
1. `AGENTS.md`
2. `docs/current/OPERATING_MODEL.md`
3. `docs/current/ROADMAP_TO_PRODUCTION.md`
4. `docs/current/VALIDATION_PROTOCOL.md`
5. `docs/current/MODEL_SPEC_VNEXT.md`
6. `docs/tasks/TASK-003-LEGACY-BENCHMARK.md`
7. `docs/tasks/TASK-002-ACTIVE-UNIVERSE.md`

## Immediate next milestone
TASK-002 is implemented: the 804-row authoritative 2026 universe is reconciled to the 805-player legacy board, Taylor Adams is confirmed as the sole legacy-only row, and 53 players wrongly omitted by the previous 752-player vNext predicate are reported. Next, complete TASK-003 for the fair legacy-vNext benchmark.

## Decision rule
No forecast or utility component replaces production because it looks more plausible. Replacement requires the locked outcome-based evidence in `VALIDATION_PROTOCOL.md` and Luke's explicit release approval.
