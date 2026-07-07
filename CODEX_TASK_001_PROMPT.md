# Codex prompt — TASK-001 repository bootstrap

Work from the repository's current production branch and create a branch named `feature/task-001-bootstrap`.

Read the supplied transition bundle and `docs/tasks/TASK-001-BOOTSTRAP.md`. Apply the bundle as a non-destructive migration.

Requirements:
- Preserve the legacy production engine exactly.
- Add `vnext/`, `AGENTS.md`, `docs/current/`, `docs/tasks/`, CI, scripts, reports, and persisted progress-05 artifacts from the bundle.
- Run:
  - `python scripts/verify_legacy_manifest.py`
  - `cd vnext && pytest -q`
  - `python scripts/generate_handover.py --check`
- Do not retrain models, regenerate current values, alter validation metrics, archive old files, or edit the UI.
- If the supplied bundle and repository differ, preserve repository production files and report the discrepancy rather than guessing.
- Add a bootstrap report listing every added file group, commands run, results, and any portability problem.
- Open a pull request into the `vnext` integration branch using the repository PR template.

The PR is acceptable only if all existing 13 vNext tests pass and all frozen legacy hashes remain unchanged.
