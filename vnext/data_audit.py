"""Initial audit of the repository's authoritative player dataset.

This script deliberately performs no modelling. It establishes coverage and
flags fields that cannot safely be used in historical snapshots without an
as-of reconstruction.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "engine" / "rl_after" / "rl_model_data.json"


def main() -> None:
    players: list[dict[str, Any]] = json.loads(DATA.read_text())
    scoring_years = [
        int(row["year"])
        for p in players
        for row in (p.get("scoring") or [])
        if row.get("year") is not None
    ]
    draft_years = [int(p["year"]) for p in players if p.get("year") is not None]

    risky_fields = [
        "present_position",
        "future_position",
        "_retired",
        "_club",
        "_has26",
    ]

    report = {
        "players": len(players),
        "draft_year_min": min(draft_years),
        "draft_year_max": max(draft_years),
        "scoring_year_min": min(scoring_years),
        "scoring_year_max": max(scoring_years),
        "players_with_scoring": sum(bool(p.get("scoring")) for p in players),
        "players_without_scoring": sum(not bool(p.get("scoring")) for p in players),
        "draft_types": Counter(p.get("type") for p in players),
        "drafted_positions": Counter(p.get("drafted_position") for p in players),
        "future_positions": Counter(str(p.get("future_position")) for p in players),
        "historically_unsafe_without_reconstruction": {
            field: sum(field in p and p.get(field) is not None for p in players)
            for field in risky_fields
        },
    }

    def serialise(obj: Any) -> Any:
        if isinstance(obj, Counter):
            return dict(obj)
        raise TypeError(type(obj).__name__)

    out = Path(__file__).with_name("data_audit.json")
    out.write_text(json.dumps(report, indent=2, default=serialise) + "\n")
    print(out)


if __name__ == "__main__":
    main()
