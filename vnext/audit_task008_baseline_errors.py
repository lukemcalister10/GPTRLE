from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

CURRENT_YEAR = 2026
LOW_CEILING_LEVEL = 65.0
ESTABLISHED_GAMES = 50
VALUE_FLOOR = 1.0


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _current_average(track: Any) -> float:
    if not isinstance(track, list):
        return math.nan
    for row in track:
        if isinstance(row, dict) and row.get("s") == 1:
            try:
                value = float(row.get("a"))
            except (TypeError, ValueError):
                return math.nan
            return value if math.isfinite(value) else math.nan
    return math.nan


def _track_seasons(track: Any) -> int:
    return len(track) if isinstance(track, list) else 0


def _pick_band(value: float) -> str:
    if value <= 5:
        return "1-5"
    if value <= 10:
        return "6-10"
    if value <= 20:
        return "11-20"
    if value <= 40:
        return "21-40"
    if value <= 60:
        return "41-60"
    return "61+/undrafted"


def _games_band(value: float) -> str:
    if value <= 0:
        return "0"
    if value <= 9:
        return "1-9"
    if value <= 24:
        return "10-24"
    if value <= 49:
        return "25-49"
    if value <= 99:
        return "50-99"
    if value <= 199:
        return "100-199"
    return "200+"


def _safe_float_series(frame: pd.DataFrame, field: str, default: float = math.nan) -> pd.Series:
    if field not in frame:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[field], errors="coerce")


def build_audit(payload: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    active = payload.get("active")
    if not isinstance(active, list) or not active:
        raise ValueError("board payload must contain a non-empty active list")
    frame = pd.DataFrame(active).copy()
    required = {"name", "key", "g", "pn", "pedDecay", "vP1", "vP2", "vM1", "vM2"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"missing required board fields: {missing}")
    if frame["key"].isna().any() or frame["key"].duplicated().any():
        raise ValueError("legacy player keys must be non-null and unique")

    value_field = "claudeV" if "claudeV" in frame else "v"
    frame["claude_value"] = _safe_float_series(frame, value_field)
    frame["current_avg"] = frame.get("track", pd.Series([None] * len(frame))).map(_current_average)
    frame["track_seasons"] = frame.get("track", pd.Series([None] * len(frame))).map(_track_seasons).astype(int)
    frame["games"] = _safe_float_series(frame, "g", 0.0).fillna(0.0)
    frame["pick_effective"] = _safe_float_series(frame, "ep")
    if "pk" in frame:
        frame["pick_effective"] = frame["pick_effective"].fillna(_safe_float_series(frame, "pk"))
    frame["pick_effective"] = frame["pick_effective"].fillna(99.0)
    frame["pick_band"] = frame["pick_effective"].map(_pick_band)
    frame["games_band"] = frame["games"].map(_games_band)
    frame["zero_history"] = frame["games"].eq(0)
    h26 = frame["h26"] if "h26" in frame else pd.Series(False, index=frame.index)
    frame["partial_season_observed"] = h26.fillna(False).astype(bool) & frame["current_avg"].notna()
    frame["pn_error_vs_current"] = _safe_float_series(frame, "pn") - frame["current_avg"]
    frame["ps_error_vs_current"] = _safe_float_series(frame, "ps") - frame["current_avg"]
    frame["ln_error_vs_current"] = _safe_float_series(frame, "ln") - frame["current_avg"]
    frame["pedigree_persistence"] = (_safe_float_series(frame, "pedDecay", 0.0).fillna(0.0) > 0) & (
        frame["games"] >= ESTABLISHED_GAMES
    )
    frame["established_low_ceiling"] = (frame["games"] >= ESTABLISHED_GAMES) & (
        _safe_float_series(frame, "pn") < LOW_CEILING_LEVEL
    )
    component_fields = ["vM2", "vM1", "vP1", "vP2"]
    component = frame[component_fields].apply(pd.to_numeric, errors="coerce")
    frame["pathological_zero_value"] = component[["vP1", "vP2"]].eq(0).any(axis=1)
    frame["non_finite_component"] = ~pd.Series(
        np.isfinite(component.to_numpy(dtype=float)).all(axis=1), index=frame.index
    )
    frame["value_floor"] = frame["claude_value"] <= VALUE_FLOOR
    frame["non_finite_value"] = ~frame["claude_value"].map(_finite)

    zero_values = frame.loc[frame["zero_history"], "claude_value"]
    zero_median = float(zero_values.median()) if len(zero_values) else math.nan
    frame["established_below_zero_history_median"] = (frame["games"] >= ESTABLISHED_GAMES) & (
        frame["claude_value"] < zero_median
    )

    ordered = [
        "key", "stable_player_id", "name", "club", "age", "yr", "draft", "pk", "ep",
        "pick_effective", "pick_band", "games", "games_band", "track_seasons", "current_avg",
        "pn", "ps", "ln", "lns", "pedDecay", "claude_value", "claudeRank", "rank",
        "vM2", "vM1", "vP1", "vP2", "zero_history", "partial_season_observed",
        "pn_error_vs_current", "ps_error_vs_current", "ln_error_vs_current",
        "pedigree_persistence", "established_low_ceiling",
        "established_below_zero_history_median", "pathological_zero_value",
        "non_finite_component", "value_floor", "non_finite_value",
    ]
    audit = frame[[field for field in ordered if field in frame.columns]].copy()

    cohort_defs = {
        "all": pd.Series(True, index=frame.index),
        "partial_season_observed": frame["partial_season_observed"],
        "zero_history": frame["zero_history"],
        "pedigree_persistence_50_plus_games": frame["pedigree_persistence"],
        "established_low_ceiling": frame["established_low_ceiling"],
        "established_below_zero_history_median": frame["established_below_zero_history_median"],
        "pathological_zero_value": frame["pathological_zero_value"],
        "value_floor": frame["value_floor"],
    }
    rows: list[dict[str, Any]] = []
    for cohort, mask in cohort_defs.items():
        part = frame.loc[mask].copy()
        row: dict[str, Any] = {
            "cohort": cohort,
            "players": int(len(part)),
            "mean_value": float(part["claude_value"].mean()) if len(part) else math.nan,
            "median_value": float(part["claude_value"].median()) if len(part) else math.nan,
            "min_value": float(part["claude_value"].min()) if len(part) else math.nan,
            "max_value": float(part["claude_value"].max()) if len(part) else math.nan,
            "mean_games": float(part["games"].mean()) if len(part) else math.nan,
            "mean_ped_decay": float(pd.to_numeric(part.get("pedDecay"), errors="coerce").mean()) if len(part) else math.nan,
        }
        observed = part["current_avg"].notna()
        row["current_avg_rows"] = int(observed.sum())
        row["pn_mae_vs_current"] = (
            float(part.loc[observed, "pn_error_vs_current"].abs().mean()) if observed.any() else math.nan
        )
        row["pn_bias_vs_current"] = (
            float(part.loc[observed, "pn_error_vs_current"].mean()) if observed.any() else math.nan
        )
        rows.append(row)
    cohorts = pd.DataFrame(rows)

    rank_field = "claudeRank" if "claudeRank" in frame else ("rank" if "rank" in frame else None)
    tied_rank_rows = 0
    duplicate_rank_values = 0
    if rank_field:
        rank_counts = frame[rank_field].value_counts(dropna=True)
        tied_rank_rows = int(rank_counts[rank_counts > 1].sum())
        duplicate_rank_values = int((rank_counts > 1).sum())

    summary = {
        "status": "diagnostic_complete",
        "players": int(len(frame)),
        "unique_keys": int(frame["key"].nunique()),
        "value_field": value_field,
        "zero_history_players": int(frame["zero_history"].sum()),
        "partial_season_observed_players": int(frame["partial_season_observed"].sum()),
        "pedigree_persistence_50_plus_games": int(frame["pedigree_persistence"].sum()),
        "pedigree_persistence_100_plus_games": int(
            ((frame["games"] >= 100) & (_safe_float_series(frame, "pedDecay", 0.0).fillna(0.0) > 0)).sum()
        ),
        "established_low_ceiling_players": int(frame["established_low_ceiling"].sum()),
        "established_below_zero_history_median": int(frame["established_below_zero_history_median"].sum()),
        "zero_history_median_value": zero_median,
        "pathological_forward_zero_players": int(frame["pathological_zero_value"].sum()),
        "value_floor_players": int(frame["value_floor"].sum()),
        "non_finite_component_players": int(frame["non_finite_component"].sum()),
        "non_finite_value_players": int(frame["non_finite_value"].sum()),
        "duplicate_rank_values": duplicate_rank_values,
        "tied_rank_rows": tied_rank_rows,
        "partial_season_pn_mae_vs_current": float(
            frame.loc[frame["partial_season_observed"], "pn_error_vs_current"].abs().mean()
        ),
        "partial_season_pn_bias_vs_current": float(
            frame.loc[frame["partial_season_observed"], "pn_error_vs_current"].mean()
        ),
        "notes": {
            "current_average": "track entry s=1; diagnostic only because the 2026 season is incomplete",
            "established": f"at least {ESTABLISHED_GAMES} career games",
            "low_ceiling": f"pn below {LOW_CEILING_LEVEL}",
            "pathological_zero": "vP1 or vP2 equals exactly zero",
            "task006": "not evaluated or promoted; claudeV is used when present",
        },
    }
    return audit, cohorts, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude-board", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    payload = json.loads(args.claude_board.read_text())
    audit, cohorts, summary = build_audit(payload)
    audit.to_csv(args.out / "player_audit.csv", index=False)
    cohorts.to_csv(args.out / "cohort_summary.csv", index=False)

    slices = {
        "partial_season.csv": audit["partial_season_observed"],
        "pedigree_persistence.csv": audit["pedigree_persistence"],
        "zero_history.csv": audit["zero_history"],
        "established_low_ceiling.csv": audit["established_low_ceiling"],
        "established_below_zero_history_median.csv": audit["established_below_zero_history_median"],
        "pathological_zero_values.csv": audit["pathological_zero_value"] | audit["value_floor"],
    }
    for filename, mask in slices.items():
        audit.loc[mask].sort_values(
            [field for field in ["claude_value", "games"] if field in audit.columns],
            ascending=[False, False],
        ).to_csv(args.out / filename, index=False)

    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
