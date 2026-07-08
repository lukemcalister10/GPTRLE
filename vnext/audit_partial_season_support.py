from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PLAYER_DATA = ROOT / "engine" / "rl_after" / "rl_model_data.json"
INTRASEASON_FIELDS = {
    "round",
    "round_number",
    "match_date",
    "date",
    "as_of_date",
    "as_of_round",
    "games_available",
    "scheduled_games_to_date",
    "team_games_played",
}


def audit_players(players: list[dict[str, Any]]) -> dict[str, Any]:
    scoring_rows: list[dict[str, Any]] = []
    duplicate_player_years: list[dict[str, Any]] = []
    for player in players:
        key = str(player.get("key") or player.get("player") or "")
        seen: set[int] = set()
        for row in player.get("scoring") or []:
            if not isinstance(row, dict):
                continue
            record = dict(row)
            record["player_key"] = key
            scoring_rows.append(record)
            try:
                year = int(row.get("year"))
            except (TypeError, ValueError):
                continue
            if year in seen:
                duplicate_player_years.append({"player_key": key, "year": year})
            seen.add(year)

    scoring_keys = sorted(
        {field for row in scoring_rows for field in row if field != "player_key"}
    )
    present_intraseason = sorted(INTRASEASON_FIELDS.intersection(scoring_keys))
    years = pd.to_numeric(
        pd.Series([row.get("year") for row in scoring_rows]),
        errors="coerce",
    )
    current_rows = [row for row in scoring_rows if str(row.get("year")) == "2026"]
    current_with_games = 0
    for row in current_rows:
        try:
            current_with_games += int(float(row.get("games", 0) or 0) > 0)
        except (TypeError, ValueError):
            pass

    blockers = []
    if not present_intraseason:
        blockers.append("no_round_date_or_games_available_field")
    if scoring_keys and set(scoring_keys).issubset({"year", "avg", "games"}):
        blockers.append("scoring_history_is_annual_aggregate_only")
    if not current_rows:
        blockers.append("no_current_partial_season_rows")

    return {
        "status": (
            "blocked_by_missing_origin_safe_intraseason_data"
            if blockers
            else "intraseason_fields_present"
        ),
        "players": len(players),
        "scoring_rows": len(scoring_rows),
        "min_year": int(years.min()) if years.notna().any() else None,
        "max_year": int(years.max()) if years.notna().any() else None,
        "scoring_row_fields": scoring_keys,
        "intraseason_fields_present": present_intraseason,
        "current_2026_scoring_rows": len(current_rows),
        "current_2026_rows_with_games": current_with_games,
        "duplicate_player_year_rows": len(duplicate_player_years),
        "blockers": blockers,
        "minimum_required_evidence": [
            "player and club identity",
            "as-of date or round",
            "games played by player as of origin",
            "team games available as of origin",
            "scoring average or points through origin",
            "future season-end outcomes kept strictly post-origin",
        ],
        "decision": (
            "Do not fit or validate a partial-season exposure correction from annual "
            "season-end aggregates. Acquire or reconstruct historical round/date snapshots first."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=PLAYER_DATA)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    from historical_eligibility import load_historical_players

    players = load_historical_players(args.data)
    report = audit_players(players)
    (args.out / "partial_season_support.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
