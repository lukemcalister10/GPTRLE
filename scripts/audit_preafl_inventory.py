#!/usr/bin/env python3
"""Diagnostic inventory of leakage-safe pre-AFL/pre-debut information already in the repo."""
from __future__ import annotations

import base64, gzip, json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLAYER_DATA = ROOT / "engine/rl_after/rl_model_data.json"
OUT = ROOT / "reports/task-003k-preafl-audit"


def decode_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(pd.io.common.BytesIO(gzip.decompress(base64.b64decode(path.read_bytes()))))


def known(v: Any) -> bool:
    return v is not None and str(v).strip() not in {"", "nan", "None"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    players = json.loads(PLAYER_DATA.read_text())
    rows = []
    for p in players:
        scoring = p.get("scoring") or []
        afl_games_by_origin = {int(r.get("year", 0)): int(r.get("games") or 0) for r in scoring if str(r.get("year", "")).isdigit()}
        first_game_year = min((y for y, g in afl_games_by_origin.items() if g > 0), default=None)
        draft_year = int(p["year"]) if str(p.get("year", "")).isdigit() else None
        first_list_year = draft_year
        rows.append({
            "player_key": p.get("key"),
            "draft_year": draft_year,
            "entry_pick": p.get("pick"),
            "entry_type_code": p.get("type"),
            "entry_type_label": p.get("_draft"),
            "drafted_position": p.get("drafted_position"),
            "present_position": p.get("present_position"),
            "future_position": p.get("future_position"),
            "birth_year": p.get("_by"),
            "birth_date": p.get("_bd"),
            "category": p.get("_cat"),
            "club_current_or_source": p.get("_club"),
            "has_2026_flag": p.get("_has26"),
            "retired_flag": p.get("_retired"),
            "pickless_flag": p.get("_pickless"),
            "last_listed": p.get("_last_listed"),
            "force_active": p.get("_force_active"),
            "pvc_exclude": p.get("_pvc_exclude"),
            "scoring_seasons": len(scoring),
            "first_afl_game_year": first_game_year,
            "zero_prior_games_at_entry": first_game_year is None or (draft_year is not None and first_game_year > draft_year),
            "list_tenure_without_afl_games": None if draft_year is None or first_game_year is None else max(0, first_game_year - draft_year),
        })
    pf = pd.DataFrame(rows)
    field_rows = []
    for col in pf.columns:
        if col == "player_key":
            continue
        s = pf[col]
        field_rows.append({
            "source_file": str(PLAYER_DATA.relative_to(ROOT)),
            "field": col,
            "records": len(pf),
            "non_missing": int(s.map(known).sum()),
            "missing": int((~s.map(known)).sum()),
            "missing_rate": round(float((~s.map(known)).mean()), 4),
            "distinct_values": int(s.dropna().astype(str).nunique()),
            "min_year_or_value": s.dropna().min() if pd.api.types.is_numeric_dtype(s.dropna()) and len(s.dropna()) else "",
            "max_year_or_value": s.dropna().max() if pd.api.types.is_numeric_dtype(s.dropna()) and len(s.dropna()) else "",
            "top_values": "; ".join(f"{k}={v}" for k, v in Counter(s.fillna("<missing>").astype(str)).most_common(8)),
        })
    pd.DataFrame(field_rows).to_csv(OUT / "repository_field_inventory.csv", index=False)

    dg = decode_csv(ROOT / "data/historical/draftguru_player_key_map_final.csv.gz.b64")
    elig = decode_csv(ROOT / "data/historical/historical_eligibility_2018_2024.csv.gz.b64")
    current = pd.read_csv(ROOT / "data/current/Players_2026.csv")
    summary = {
        "repository_players": int(len(pf)),
        "repository_draft_year_min": int(pf["draft_year"].min()),
        "repository_draft_year_max": int(pf["draft_year"].max()),
        "repository_players_with_birth_date": int(pf["birth_date"].map(known).sum()),
        "repository_players_with_birth_year": int(pf["birth_year"].map(known).sum()),
        "repository_players_with_entry_pick": int(pf["entry_pick"].map(known).sum()),
        "repository_players_with_entry_type": int(pf["entry_type_code"].map(known).sum()),
        "repository_players_with_drafted_position": int(pf["drafted_position"].map(known).sum()),
        "draftguru_map_rows": int(len(dg)),
        "draftguru_matched_rows": int((dg["final_status"] == "matched").sum()),
        "draftguru_year_min": int(dg["draft_year"].min()),
        "draftguru_year_max": int(dg["draft_year"].max()),
        "historical_eligibility_rows": int(len(elig)),
        "historical_eligibility_origin_min": int(elig["origin_year"].min()),
        "historical_eligibility_origin_max": int(elig["origin_year"].max()),
        "historical_eligible_positive_rows": int(elig["eligible"].sum()),
        "current_2026_rows": int(len(current)),
        "current_2026_position_non_missing": int(current["Position/s"].map(known).sum()),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
