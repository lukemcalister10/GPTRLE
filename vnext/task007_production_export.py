from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

MODEL_ID = "TASK-006"
FORECAST_MODEL_ID = "TASK-003Q"
KEYS = ["stable_player_id", "lead"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def rank_desc(values: pd.Series) -> pd.Series:
    return values.rank(method="min", ascending=False).astype(int)


def serialise_record(row: pd.Series) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if pd.isna(value):
            out[key] = None
        elif isinstance(value, (np.integer,)):
            out[key] = int(value)
        elif isinstance(value, (np.floating,)):
            out[key] = float(value)
        elif isinstance(value, (np.bool_,)):
            out[key] = bool(value)
        else:
            out[key] = value
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude-board", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--task003q-forecast", type=Path, required=True)
    parser.add_argument("--task006-board", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    claude_payload = json.loads(args.claude_board.read_text())
    registry = pd.read_csv(args.registry)
    forecast = pd.read_csv(args.task003q_forecast)
    board = pd.read_csv(args.task006_board)

    required_registry = {"stable_player_id", "legacy_key", "player_name", "affl_team", "eligibilities"}
    required_board = {
        "stable_player_id", "legacy_key", "player_name", "claude_value", "claude_rank",
        "current_vnext_value", "task003q_value", "task003q_increment",
        "task006_value", "task006_rank", "task006_minus_claude_value",
        "task006_minus_claude_rank",
    }
    missing_registry = sorted(required_registry - set(registry.columns))
    missing_board = sorted(required_board - set(board.columns))
    if missing_registry or missing_board:
        raise SystemExit(f"schema failure registry={missing_registry} board={missing_board}")

    if len(registry) != 804 or registry.stable_player_id.nunique() != 804 or registry.legacy_key.nunique() != 804:
        raise SystemExit("authoritative registry coverage failure")
    if len(board) != 804 or board.stable_player_id.nunique() != 804 or board.legacy_key.nunique() != 804:
        raise SystemExit("TASK-006 board coverage failure")
    if board.duplicated("stable_player_id").any() or board.duplicated("legacy_key").any():
        raise SystemExit("duplicate production identity")

    if len(forecast) != 4020 or forecast.stable_player_id.nunique() != 804:
        raise SystemExit("TASK-003Q production forecast coverage failure")
    if forecast.duplicated(KEYS).any() or not forecast.groupby("stable_player_id").lead.nunique().eq(5).all():
        raise SystemExit("TASK-003Q production lead-key failure")
    if set(forecast.lead.astype(int).unique()) != {1, 2, 3, 4, 5}:
        raise SystemExit("unexpected production lead set")

    active_by_key = {str(row["key"]): dict(row) for row in claude_payload["active"]}
    if len(active_by_key) != len(claude_payload["active"]):
        raise SystemExit("duplicate legacy active key")

    production = registry[list(required_registry)].merge(
        board[list(required_board)], on=["stable_player_id", "legacy_key", "player_name"], validate="one_to_one"
    )
    if len(production) != 804:
        raise SystemExit("identity-safe production merge failure")

    numeric_board = [
        "claude_value", "current_vnext_value", "task003q_value", "task003q_increment",
        "task006_value", "task006_minus_claude_value",
    ]
    if not np.isfinite(production[numeric_board].to_numpy(dtype=float)).all():
        raise SystemExit("non-finite production value")
    if (production.task006_value < 0).any():
        raise SystemExit("negative production value")

    claude_total = float(production.claude_value.sum())
    task006_total = float(production.task006_value.sum())
    total_error = abs(task006_total - claude_total)
    if total_error >= 1e-6:
        raise SystemExit(f"capital conservation failure: {total_error}")

    forecast_fields = [
        field for field in [
            "lead", "p_meaningful", "cond_games", "exp_games", "cond_avg", "exp_avg",
            "exp_points", "threshold", "q10", "q50", "q90", "quantile_source",
            "task003q_weight", "model_id",
        ] if field in forecast.columns
    ]
    grouped_forecasts: dict[str, list[dict[str, Any]]] = {}
    for stable_id, group in forecast.sort_values(KEYS).groupby("stable_player_id", sort=False):
        rows = [serialise_record(row[forecast_fields]) for _, row in group.iterrows()]
        if len(rows) != 5:
            raise SystemExit(f"forecast row failure for {stable_id}")
        grouped_forecasts[str(stable_id)] = rows

    final_active: list[dict[str, Any]] = []
    missing_legacy: list[str] = []
    for row in production.sort_values("task006_rank").itertuples(index=False):
        source = active_by_key.get(str(row.legacy_key))
        if source is None:
            missing_legacy.append(str(row.legacy_key))
            continue
        rec = dict(source)
        rec.update({
            "stable_player_id": str(row.stable_player_id),
            "key": str(row.legacy_key),
            "name": str(row.player_name),
            "afflTeam": row.affl_team,
            "eligibilities": row.eligibilities,
            "claudeV": float(row.claude_value),
            "claudeRank": int(row.claude_rank),
            "currentVnextFiveYearV": float(row.current_vnext_value),
            "task003qFiveYearV": float(row.task003q_value),
            "task003qIncrement": float(row.task003q_increment),
            "task006Adjustment": float(row.task006_minus_claude_value),
            "task006RankMove": int(row.task006_minus_claude_rank),
            "v": float(row.task006_value),
            "rank": int(row.task006_rank),
            "forecastModel": FORECAST_MODEL_ID,
            "valueModel": MODEL_ID,
            "forecasts": grouped_forecasts[str(row.stable_player_id)],
        })
        final_active.append(rec)

    if missing_legacy or len(final_active) != 804:
        raise SystemExit(f"legacy bridge failure missing={missing_legacy[:10]} active={len(final_active)}")

    stable_ids = [row["stable_player_id"] for row in final_active]
    legacy_keys = [row["key"] for row in final_active]
    if len(set(stable_ids)) != 804 or len(set(legacy_keys)) != 804:
        raise SystemExit("final active identity uniqueness failure")
    max_rows = [row for row in final_active if row["key"] in {"max-king-stk", "max-king-syd"}]
    if len(max_rows) != 2 or len({row["stable_player_id"] for row in max_rows}) != 2:
        raise SystemExit("Max King / Maxwell King identity collapse")
    if not all(finite(row["v"]) and len(row["forecasts"]) == 5 for row in final_active):
        raise SystemExit("UI payload player validation failure")

    legacy_only = [row for key, row in active_by_key.items() if key not in set(legacy_keys)]
    payload = dict(claude_payload)
    payload["active"] = final_active
    payload["legacyOnlyActive"] = legacy_only
    payload["production"] = {
        "valueModel": MODEL_ID,
        "forecastModel": FORECAST_MODEL_ID,
        "players": 804,
        "forecastRows": 4020,
        "join": "stable_player_id with controlled legacy_key bridge",
        "nameOnlyJoin": False,
        "doubleSurvivalFade": False,
        "year6PlusForecastReplaced": False,
        "capitalTotal": task006_total,
        "capitalError": total_error,
    }

    app_path = args.out / "rl_app_data_task006.json"
    app_path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
    # Prove the emitted app file can be loaded and every active row is renderable.
    loaded = json.loads(app_path.read_text())
    if len(loaded.get("active", [])) != 804:
        raise SystemExit("emitted app payload load failure")
    for rec in loaded["active"]:
        for field in ("name", "key", "stable_player_id", "v", "rank", "forecasts"):
            if field not in rec:
                raise SystemExit(f"emitted app row missing {field}")

    production.sort_values("task006_rank").to_csv(args.out / "task006_production_board.csv", index=False)
    forecast.sort_values(KEYS).to_csv(args.out / "task003q_annual_forecasts.csv", index=False)

    review = production.copy()
    review["abs_rank_move"] = review.task006_minus_claude_rank.abs()
    review.sort_values(["abs_rank_move", "task006_rank"], ascending=[False, True]).head(200).to_csv(
        args.out / "largest_rank_moves.csv", index=False
    )
    review.loc[review.task006_rank <= 100].sort_values("task006_rank").to_csv(args.out / "top_100.csv", index=False)

    meta_cols = [field for field in ["stable_player_id", "age", "zero_history", "position", "position_utility"] if field in forecast.columns]
    meta = forecast.drop_duplicates("stable_player_id")[meta_cols] if meta_cols else pd.DataFrame({"stable_player_id": production.stable_player_id})
    review = review.merge(meta, on="stable_player_id", how="left", validate="one_to_one")
    if "age" in review:
        review.loc[review.age >= 30].sort_values("task006_rank").to_csv(args.out / "age_30_plus.csv", index=False)
        review.loc[review.age <= 21].sort_values("task006_rank").to_csv(args.out / "age_21_and_under.csv", index=False)
    if "zero_history" in review:
        review.loc[review.zero_history.astype(bool)].sort_values("task006_rank").to_csv(args.out / "zero_history.csv", index=False)
    if "position_utility" in review:
        review.sort_values(["position_utility", "task006_rank"]).to_csv(args.out / "position_review.csv", index=False)

    validation = {
        "status": "pass",
        "players": len(final_active),
        "forecast_rows": len(forecast),
        "five_leads_each": True,
        "duplicate_stable_ids": len(stable_ids) - len(set(stable_ids)),
        "duplicate_legacy_keys": len(legacy_keys) - len(set(legacy_keys)),
        "max_identity_separation": True,
        "legacy_only_rows": len(legacy_only),
        "legacy_only_keys": sorted(str(row.get("key")) for row in legacy_only),
        "negative_values": int(sum(float(row["v"]) < 0 for row in final_active)),
        "non_finite_values": int(sum(not finite(row["v"]) for row in final_active)),
        "capital_total_claude": claude_total,
        "capital_total_task006": task006_total,
        "capital_error": total_error,
        "name_only_join": False,
        "double_survival_fade": False,
        "year6_plus_forecast_replaced": False,
        "ui_payload_load": True,
    }
    (args.out / "validation_report.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")

    files = sorted(path for path in args.out.iterdir() if path.is_file())
    manifest = {
        "task": "TASK-007",
        "status": "pass",
        "value_model": MODEL_ID,
        "forecast_model": FORECAST_MODEL_ID,
        "inputs": {
            "claude_board": sha256(args.claude_board),
            "registry": sha256(args.registry),
            "task003q_forecast": sha256(args.task003q_forecast),
            "task006_board": sha256(args.task006_board),
        },
        "outputs": {path.name: sha256(path) for path in files},
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
