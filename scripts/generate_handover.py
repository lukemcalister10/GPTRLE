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
- Accepted forecast evidence: TASK-003Q, TASK-009 zero-history state separation and TASK-012 evidence-weighted demonstrated ceiling; no release cutover approved.
- Integration branch: `vnext` includes TASK-008, TASK-009, TASK-010, TASK-012, TASK-013 and TASK-014.
- Rejected experiment: TASK-011 pedigree fade failed predeclared zero-history and 100+ cohort gates and was not merged.
- Release constraint: TASK-006 and the TASK-007 TASK-006 export must not be promoted.
- Partial-season exposure: formally blocked until origin-safe historical intra-season snapshots exist.
- Numerical continuity: TASK-013 removes exact `vP1`/`vP2` zeros in an isolated adapter; it is not wired into production export.
- Current-board composition: TASK-014 validates the accepted TASK-009 + TASK-012 stack across all 804 authoritative players without changing keeper utility or production.
- Active task: [`{active}`](../tasks/{active}).
- Accepted decisions recorded: {decisions}.

## Locked evidence
- Authoritative current universe: 804 players; raw Claude export: 805 rows with legacy-only Taylor Adams.
- Historical benchmark: 5,622 player-origin snapshots, 20,094 player-origin-lead rows per model and 25 legal rolling-origin folds.
- TASK-009 improved zero-history Brier, log loss, games MAE and points MAE while also improving every pooled primary metric.
- TASK-012 improved established low-ceiling conditional-average MAE by 0.33% and points MAE by 0.52%, with event, games and threshold outputs unchanged.
- TASK-010 found 11,243 annual scoring rows but no historical round/date or games-available fields.
- TASK-013 changes seven exact-zero fields across four authoritative players and changes no current value, rank or non-zero forecast.
- TASK-014 preserves every event, games and threshold output exactly; five-year expected-points rank movement averages 1.55 places, peaks at nine and retains 99 of the top 100.
- Frozen Claude files are protected by `artifacts/legacy_manifest.json` and `scripts/verify_legacy_manifest.py`.

## Read first
1. `AGENTS.md`
2. `docs/current/VALIDATION_PROTOCOL.md`
3. `docs/current/ROADMAP_TO_PRODUCTION.md`
4. `docs/current/DECISION_LOG.md`
5. `docs/current/TASK-008-BASELINE-ERROR-AUDIT.md`
6. `docs/tasks/{active}`

## Immediate sequence
The currently testable defect workstream is complete. Further partial-season work requires origin-safe historical intra-season data. Further keeper-utility or release work requires an independent historical keeper-value target or an explicit owner release decision. Preserve TASK-011 as rejected evidence and do not promote TASK-006.

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
