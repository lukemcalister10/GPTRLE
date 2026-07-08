from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

INVARIANT_DELTA_COLUMNS = [
    "delta_p_meaningful",
    "delta_cond_games",
    "delta_exp_games",
    "delta_p80",
    "delta_p90",
    "delta_p100",
    "delta_p110",
    "delta_p120",
]
CHANGED_DELTA_COLUMNS = ["delta_cond_avg", "delta_exp_avg", "delta_exp_points"]


def _cohort_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    return {
        "rows": int(len(frame)),
        "players": int(frame["stable_player_id"].nunique()),
        "mean_cond_avg_delta": float(frame["delta_cond_avg"].mean()),
        "mean_abs_cond_avg_delta": float(frame["delta_cond_avg"].abs().mean()),
        "mean_exp_points_delta": float(frame["delta_exp_points"].mean()),
        "mean_abs_exp_points_delta": float(frame["delta_exp_points"].abs().mean()),
        "positive_exp_points_rows": int((frame["delta_exp_points"] > 1e-12).sum()),
        "negative_exp_points_rows": int((frame["delta_exp_points"] < -1e-12).sum()),
        "unchanged_exp_points_rows": int((frame["delta_exp_points"].abs() <= 1e-12).sum()),
    }


def summarize(
    deltas: pd.DataFrame,
    rollup: pd.DataFrame,
    snapshots: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    required_delta = {
        "stable_player_id",
        "key",
        "lead",
        "prior_games",
        *INVARIANT_DELTA_COLUMNS,
        *CHANGED_DELTA_COLUMNS,
    }
    missing = sorted(required_delta - set(deltas.columns))
    if missing:
        raise ValueError(f"annual deltas missing required columns: {missing}")
    if deltas.duplicated(["stable_player_id", "lead"]).any():
        raise ValueError("annual deltas contain duplicate player-lead keys")
    if len(deltas) != 804 * 5 or deltas["stable_player_id"].nunique() != 804:
        raise ValueError("annual deltas must cover exactly 804 players and five leads")

    required_snapshots = {"stable_player_id", "career_best"}
    missing_snapshots = sorted(required_snapshots - set(snapshots.columns))
    if missing_snapshots:
        raise ValueError(f"snapshots missing required columns: {missing_snapshots}")
    snapshot_features = snapshots[["stable_player_id", "career_best"]].copy()
    if snapshot_features["stable_player_id"].duplicated().any():
        raise ValueError("snapshots contain duplicate stable player ids")
    frame = deltas.merge(snapshot_features, on="stable_player_id", validate="many_to_one")
    prior_games = pd.to_numeric(frame["prior_games"], errors="coerce").fillna(0.0)
    career_best = pd.to_numeric(frame["career_best"], errors="coerce").fillna(0.0)
    cohorts = {
        "all": pd.Series(True, index=frame.index),
        "zero_history": prior_games.eq(0),
        "under_50_games": prior_games.lt(50),
        "established_50_plus": prior_games.ge(50),
        "established_low_ceiling": prior_games.ge(50) & career_best.lt(65),
        "established_other": prior_games.ge(50) & career_best.ge(65),
    }
    cohort_rows = []
    cohort_report: dict[str, Any] = {}
    for name, mask in cohorts.items():
        metrics = _cohort_metrics(frame.loc[mask])
        cohort_report[name] = metrics
        cohort_rows.append({"cohort": name, **metrics})

    invariant_max = {
        column: float(frame[column].abs().max()) for column in INVARIANT_DELTA_COLUMNS
    }
    changed_rows = {
        column: int((frame[column].abs() > 1e-12).sum()) for column in CHANGED_DELTA_COLUMNS
    }

    required_rollup = {
        "stable_player_id",
        "delta_exp_points_5y",
        "current_rank_exp_points_5y",
        "candidate_rank_exp_points_5y",
        "rank_change_exp_points_5y",
    }
    missing_rollup = sorted(required_rollup - set(rollup.columns))
    if missing_rollup:
        raise ValueError(f"player rollup missing required columns: {missing_rollup}")
    if len(rollup) != 804 or rollup["stable_player_id"].nunique() != 804:
        raise ValueError("player rollup must contain exactly 804 unique players")
    current_top100 = set(
        rollup.nsmallest(100, "current_rank_exp_points_5y")["stable_player_id"]
    )
    candidate_top100 = set(
        rollup.nsmallest(100, "candidate_rank_exp_points_5y")["stable_player_id"]
    )
    player_delta = pd.to_numeric(rollup["delta_exp_points_5y"], errors="coerce")
    rank_change = pd.to_numeric(rollup["rank_change_exp_points_5y"], errors="coerce")
    report = {
        "status": "current_board_composition_validated",
        "diagnostic_only": True,
        "production_changed": False,
        "task006_used": False,
        "baseline": "TASK-009",
        "candidate": "TASK-009 + TASK-012",
        "players": 804,
        "rows_per_model": 4020,
        "forecast_leads": 5,
        "invariant_max_absolute_differences": invariant_max,
        "all_required_invariants_exact": all(value <= 1e-12 for value in invariant_max.values()),
        "changed_rows": changed_rows,
        "player_five_year_points": {
            "mean_delta": float(player_delta.mean()),
            "median_delta": float(player_delta.median()),
            "mean_absolute_delta": float(player_delta.abs().mean()),
            "min_delta": float(player_delta.min()),
            "max_delta": float(player_delta.max()),
            "positive_players": int((player_delta > 1e-12).sum()),
            "negative_players": int((player_delta < -1e-12).sum()),
            "unchanged_players": int((player_delta.abs() <= 1e-12).sum()),
        },
        "exp_points_rank_effects": {
            "mean_absolute_rank_change": float(rank_change.abs().mean()),
            "maximum_absolute_rank_change": int(rank_change.abs().max()),
            "top100_overlap": int(len(current_top100 & candidate_top100)),
        },
        "cohorts": cohort_report,
        "notes": {
            "career_best_threshold": "65 is the predeclared TASK-008 reporting cohort only; it is not supplied to TASK-012",
            "utility": "No keeper utility, board value or capital allocation is calculated in this diagnostic",
            "production": "Persisted candidate artifacts are reviewed after training; no tuning occurs from current-player outputs",
        },
    }
    return pd.DataFrame(cohort_rows), report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--authoritative", type=Path)
    parser.add_argument("--legacy", type=Path)
    parser.add_argument("--previous-vnext", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from review_task003n_current_board import ROOT, universe

    authoritative = args.authoritative or ROOT / "data/current/Players_2026.csv"
    legacy = args.legacy or ROOT / "data/rl_build/rl_app_data.json"
    previous = args.previous_vnext or ROOT / "engine/rl_after/rl_model_data.json"
    _, snapshots = universe(authoritative, legacy, previous)
    deltas = pd.read_csv(args.review_dir / "annual_deltas.csv")
    rollup = pd.read_csv(args.review_dir / "player_rollup_rank_changes.csv")
    cohort_summary, report = summarize(deltas, rollup, snapshots)
    cohort_summary.to_csv(args.out / "cohort_summary.csv", index=False)
    (args.out / "final_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
