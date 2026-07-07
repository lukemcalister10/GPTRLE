"""Leakage-safe historical snapshots derived only from draft facts and scoring observed by an origin year."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date
from typing import Any, Iterable
import math

POSITION_MAP = {
    "MID": "MID", "M": "MID",
    "DEF": "DEF", "D": "DEF",
    "FWD": "FWD", "F": "FWD",
    "RUC": "RUC", "RUCK": "RUC", "R": "RUC",
    "KPD": "KPD", "KPF": "KPF",
}


def canonical_position(value: Any) -> str:
    if value is None:
        return "UNK"
    s = str(value).strip().upper()
    # Preserve explicit key positions first.
    if "KPD" in s or "KEY DEF" in s:
        return "KPD"
    if "KPF" in s or "KEY FWD" in s:
        return "KPF"
    for token in ("RUC", "RUCK", "MID", "DEF", "FWD"):
        if token in s:
            return POSITION_MAP[token]
    return POSITION_MAP.get(s, "UNK")


def birth_year(player: dict[str, Any]) -> int | None:
    by = player.get("_by")
    if isinstance(by, (int, float)) and 1900 <= int(by) <= 2030:
        return int(by)
    bd = player.get("_bd")
    if isinstance(bd, str) and len(bd) >= 4 and bd[:4].isdigit():
        return int(bd[:4])
    return None


def scoring_as_of(player: dict[str, Any], origin_year: int) -> list[dict[str, float]]:
    rows = []
    for row in player.get("scoring") or []:
        try:
            y = int(row["year"])
            avg = float(row.get("avg", 0.0) or 0.0)
            games = int(row.get("games", 0) or 0)
        except (KeyError, TypeError, ValueError):
            continue
        if y <= origin_year:
            rows.append({"year": y, "avg": avg, "games": games})
    return sorted(rows, key=lambda r: r["year"])


def season_at(player: dict[str, Any], year: int) -> dict[str, float]:
    for row in player.get("scoring") or []:
        try:
            if int(row.get("year")) == year:
                return {
                    "year": year,
                    "avg": float(row.get("avg", 0.0) or 0.0),
                    "games": int(row.get("games", 0) or 0),
                }
        except (TypeError, ValueError):
            pass
    return {"year": year, "avg": 0.0, "games": 0}


def weighted_level(rows: Iterable[dict[str, float]], origin_year: int, decay: float = 0.72) -> float:
    num = den = 0.0
    for r in rows:
        w = max(0.0, float(r["games"])) * (decay ** max(0, origin_year - int(r["year"])))
        num += float(r["avg"]) * w
        den += w
    return num / den if den else 0.0


@dataclass(frozen=True)
class PlayerSnapshot:
    key: str
    player: str
    origin_year: int
    draft_year: int
    tenure: int
    age: float
    pick: float
    position: str
    draft_type: str
    total_games: int
    qualifying_seasons: int
    last_avg: float
    last_games: int
    prev_avg: float
    prev_games: int
    weighted_avg: float
    career_best: float
    recent_best: float
    avg_trend: float
    games_last_2: int
    seasons_observed: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_snapshot(player: dict[str, Any], origin_year: int) -> PlayerSnapshot | None:
    try:
        draft_year = int(player.get("year"))
    except (TypeError, ValueError):
        return None
    if draft_year > origin_year:
        return None
    by = birth_year(player)
    age = float(origin_year - by) if by else float(18 + max(0, origin_year - draft_year))
    rows = scoring_as_of(player, origin_year)
    last = next((r for r in reversed(rows) if r["year"] <= origin_year), {"avg": 0.0, "games": 0})
    prev = next((r for r in reversed(rows) if r["year"] <= origin_year - 1), {"avg": 0.0, "games": 0})
    recent_rows = [r for r in rows if r["year"] >= origin_year - 2]
    qualifying = [r for r in rows if r["games"] >= 6]
    try:
        pick = float(player.get("pick"))
        if not math.isfinite(pick) or pick <= 0:
            pick = 80.0
    except (TypeError, ValueError):
        pick = 80.0
    last_avg = float(last["avg"])
    prev_avg = float(prev["avg"])
    return PlayerSnapshot(
        key=str(player.get("key") or player.get("player") or ""),
        player=str(player.get("player") or ""),
        origin_year=origin_year,
        draft_year=draft_year,
        tenure=max(0, origin_year - draft_year),
        age=age,
        pick=min(100.0, pick),
        position=canonical_position(player.get("drafted_position")),
        draft_type=str(player.get("type") or player.get("_draft") or "UNK"),
        total_games=sum(int(r["games"]) for r in rows),
        qualifying_seasons=len(qualifying),
        last_avg=last_avg,
        last_games=int(last["games"]),
        prev_avg=prev_avg,
        prev_games=int(prev["games"]),
        weighted_avg=weighted_level(rows, origin_year),
        career_best=max((float(r["avg"]) for r in qualifying), default=0.0),
        recent_best=max((float(r["avg"]) for r in recent_rows if r["games"] >= 6), default=0.0),
        avg_trend=(last_avg - prev_avg) if last["games"] >= 6 and prev["games"] >= 6 else 0.0,
        games_last_2=sum(int(r["games"]) for r in rows if r["year"] >= origin_year - 1),
        seasons_observed=len(rows),
    )
