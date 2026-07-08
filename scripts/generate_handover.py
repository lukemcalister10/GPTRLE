#!/usr/bin/env python3
"""Generate the current repository handover from durable project state."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "current" / "HANDOVER.md"


def render() -> str:
    active = (ROOT / "docs" / "current" / "ACTIVE_TASK").read_text(encoding="utf-8").strip()
    decisions = (ROOT / "docs" / "current" / "DECISION_LOG.md").read_text(encoding="utf-8").count(
        "## D-"
    )
    return f"""# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
- Production baseline: frozen unchanged Claude engine under `engine/rl_after/`.
- Accepted forecast evidence: TASK-003Q plus TASK-009 zero-history state separation; no release cutover approved.
- Integration branch: `vnext` includes TASK-008, TASK-009 and TASK-010.
- Release constraint: TASK-006 and the TASK-007 TASK-006 export must not be promoted.
- Partial-season exposure: formally blocked until origin-safe historical intra-season snapshots exist.
- Active experiments: TASK-011 pedigree fade and TASK-012 established-ceiling conditional average.
- Numerical candidate: TASK-013 exact forward-zero continuity; not wired into production export.
- Active task: [`{active}`](../tasks/{active}).
- Accepted decisions recorded: {decisions}.

## Locked evidence
- Authoritative current universe: 804 players; raw Claude export: 805 rows with legacy-only Taylor Adams.
- Historical benchmark: 5,622 player-origin snapshots, 20,094 player-origin-lead rows per model and 25 legal rolling-origin folds.
- TASK-009 improved zero-history Brier, log loss, games MAE and points MAE while also improving pooled metrics.
- TASK-010 found 11,243 annual scoring rows but no historical round/date or games-available fields.
- TASK-013 continuity evidence changes seven exact-zero fields across four authoritative players and no current value or rank.
- Frozen Claude files are protected by `artifacts/legacy_manifest.json` and `scripts/verify_legacy_manifest.py`.

## Read first
1. `AGENTS.md`
2. `docs/current/VALIDATION_PROTOCOL.md`
3. `docs/current/ROADMAP_TO_PRODUCTION.md`
4. `docs/current/DECISION_LOG.md`
5. `docs/current/TASK-008-BASELINE-ERROR-AUDIT.md`
6. `docs/tasks/{active}`

## Immediate sequence
Resolve TASK-011 and TASK-012 strictly from their locked gates. Preserve rejected evidence without weakening thresholds. Then validate any accepted forecast components together, report full-population current-board effects, and keep utility-layer promotion blocked until an independent keeper-value target or explicit release decision exists.

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
