# TASK-001 — Repository bootstrap and reproducibility

## Type
Engineering infrastructure. No model-formula or player-value changes.

## Goal
Establish the durable GitHub/Codex workflow and import the completed vNext progress-05 work without altering the legacy engine.

## Required work
1. Add the supplied `vnext/`, `docs/current/`, `AGENTS.md`, CI, scripts, reports, and persisted progress-05 artifacts.
2. Ensure `cd vnext && pytest -q` passes from a clean checkout.
3. Ensure `python scripts/verify_legacy_manifest.py` passes.
4. Ensure `python scripts/generate_handover.py` creates a useful compact handover.
5. Document installation and reproduction commands in the root README without deleting historical documentation.
6. Do not retrain models or regenerate player values in this task.

## Explicit exclusions
- No legacy engine edits.
- No new modelling.
- No changed validation metrics.
- No UI work.
- No mass deletion or archival of Claude-era files yet.

## Acceptance criteria
- CI passes on a clean environment.
- Existing 13 vNext tests pass.
- Legacy critical-file hashes are unchanged.
- The PR diff is migration/reproducibility only.
- The report lists every copied artifact and its origin.
