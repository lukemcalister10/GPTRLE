#!/usr/bin/env python3
"""Generate the current repository handover from durable project state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "current" / "HANDOVER.md"
STATE = ROOT / "docs" / "current" / "PROJECT_STATE.json"


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render() -> str:
    active = (ROOT / "docs" / "current" / "ACTIVE_TASK").read_text(encoding="utf-8").strip()
    decisions = (ROOT / "docs" / "current" / "DECISION_LOG.md").read_text(encoding="utf-8").count(
        "## D-"
    )
    state = json.loads(STATE.read_text(encoding="utf-8"))
    required = {"state", "locked_evidence", "immediate_sequence", "decision_rule"}
    missing = sorted(required - set(state))
    if missing:
        raise ValueError(f"PROJECT_STATE.json missing required keys: {missing}")
    return f"""# Current Handover

Generated from repository state. Do not treat chat history as authoritative when this file and chat disagree.

## State
{_bullets(state["state"])}
- Active task: [`{active}`](../tasks/{active}).
- Accepted decisions recorded: {decisions}.

## Locked evidence
{_bullets(state["locked_evidence"])}

## Read first
1. `AGENTS.md`
2. `docs/current/PROJECT_STATE.json`
3. `docs/current/VALIDATION_PROTOCOL.md`
4. `docs/current/ROADMAP_TO_PRODUCTION.md`
5. `docs/current/DECISION_LOG.md`
6. `docs/tasks/{active}`

## Immediate sequence
{state["immediate_sequence"]}

## Decision rule
{state["decision_rule"]}
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
