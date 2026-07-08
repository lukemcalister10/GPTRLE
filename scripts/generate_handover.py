#!/usr/bin/env python3
"""Generate the current repository handover from durable project state."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "current" / "HANDOVER.md"


def test_file_count() -> int:
    return len(list((ROOT / "vnext").glob("test_*.py"))) + len(
        list((ROOT / "vnext" / "tests").glob("test_*.py"))
    )


def render() -> str:
    active = (ROOT / "docs" / "current" / "ACTIVE_TASK").read_text(encoding="utf-8").strip()
    decisions = (ROOT / "docs" / "current" / "DECISION_LOG.md").read_text(encoding="utf-8").count(
        "## D-"
    )
    tests = test_file_count()
    return f"""# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
- Production baseline: frozen unchanged Claude engine under `engine/rl_after/`.
- Forecast challenger: accepted TASK-003Q evidence under `vnext/`; no release cutover approved.
- Integration branch: `vnext` at merged TASK-007 state.
- Release constraint: TASK-006 and the TASK-007 TASK-006 export must not be promoted.
- Active workstream: post-TASK-007 baseline defects and bounded one-hypothesis experiments.
- Active task: [`{active}`](../tasks/{active}).
- Accepted decisions recorded: {decisions}.
- Test files discovered under `vnext/`: {tests}.

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
6. `docs/tasks/{active}`

## Immediate sequence
Complete the unchanged-Claude baseline audit, then address partial-season exposure, pedigree persistence, zero-history differentiation, established low-ceiling treatment and pathological zero values in separate pull requests. Each modelling PR must preserve the frozen Claude files and show locked historical before/after evidence plus full-population current-board effects.

## Decision rule
No component replaces production because selected current players look more plausible. Promotion requires locked outcome-based evidence and Luke's explicit release approval. TASK-006 is specifically release-blocked.
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
