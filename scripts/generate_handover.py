#!/usr/bin/env python3
"""Generate a compact handover from repository state rather than chat memory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "current" / "HANDOVER.md"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def render() -> str:
    active = (ROOT / "docs" / "current" / "ACTIVE_TASK").read_text(encoding="utf-8").strip()
    task = ROOT / "docs" / "tasks" / active
    artifact_manifest = ROOT / "artifacts" / "vnext" / "progress_05" / "manifest.json"
    manifest = json.loads(artifact_manifest.read_text(encoding="utf-8"))
    decisions = (ROOT / "docs" / "current" / "DECISION_LOG.md").read_text(encoding="utf-8").count("## D-")
    lead_rows = ", ".join(
        f"L{lead}: {details['rows']:,} rows"
        for lead, details in sorted(manifest["leads"].items(), key=lambda item: int(item[0]))
    )
    return f"""# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
- Production: frozen legacy engine under `engine/rl_after/`.
- Challenger: vNext progress 05 under `vnext/`.
- Active roadmap phase: Phase 0 repository transition.
- Active task: [`{active}`](../tasks/{active}).
- Accepted decisions recorded: {decisions}.

## Current vNext artifact
- Target cutoff: {manifest['target_cutoff']}.
- Training coverage: {lead_rows}.
- Artifact manifest identity: `{file_hash(artifact_manifest)}`.
- Existing integrity suite: 13 tests in `vnext/`.

## Read first
1. `AGENTS.md`
2. `docs/current/OPERATING_MODEL.md`
3. `docs/current/ROADMAP_TO_PRODUCTION.md`
4. `docs/current/VALIDATION_PROTOCOL.md`
5. `docs/current/MODEL_SPEC_VNEXT.md`
6. `docs/tasks/{active}`

## Immediate next milestone
Complete TASK-001 without changing the legacy engine or model outputs. Then activate TASK-002 to reconcile the authoritative player universe, followed by TASK-003 for the fair legacy-vNext benchmark.

## Decision rule
No forecast or utility component replaces production because it looks more plausible. Replacement requires the locked outcome-based evidence in `VALIDATION_PROTOCOL.md` and Luke's explicit release approval.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the tracked handover is stale.")
    args = parser.parse_args()
    content = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
            print("HANDOVER.md is stale. Run: python scripts/generate_handover.py")
            return 1
        print("HANDOVER.md is current.")
        return 0
    OUT.write_text(content, encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
