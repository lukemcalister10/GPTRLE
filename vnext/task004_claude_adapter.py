from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

KEY = ["stable_player_id", "lead"]
LENS_DISCOUNT = 0.15
SOFTPLUS_SCALE = 3.0
KEY_POSITION_MULTIPLIER = 1.05


def soft_positive(value: np.ndarray) -> np.ndarray:
    x = np.asarray(value, dtype=float) / SOFTPLUS_SCALE
    return SOFTPLUS_SCALE * np.log1p(np.exp(np.minimum(x, 40.0)))


def captain_premium(level: np.ndarray, threshold: float, gain: float, exponent: float, cap: float) -> np.ndarray:
    over = np.maximum(0.0, np.asarray(level, dtype=float) - threshold)
    base = gain * np.power(over, exponent)
    return np.where(base > 0, base * cap / (cap + base), 0.0)


def forecast_value(frame: pd.DataFrame, repl: dict[str, float], captain: dict[str, float]) -> pd.DataFrame:
    out = frame.copy()
    replacement = out["claude_group"].map(repl).astype(float).to_numpy()
    conditional_average = out["cond_avg"].astype(float).to_numpy()
    expected_games = out["exp_games"].astype(float).to_numpy()
    premium = captain_premium(conditional_average, **captain)
    annual = soft_positive(conditional_average + premium - replacement) * expected_games
    annual *= np.where(out["claude_group"].isin(["KEY_FWD", "KEY_DEF"]), KEY_POSITION_MULTIPLIER, 1.0)
    annual /= np.power(1.0 + LENS_DISCOUNT, out["lead"].astype(int).to_numpy() - 1)
    out["annual_keeper_value_raw"] = annual
    return out


def rank_desc(values: pd.Series) -> pd.Series:
    return values.rank(method="min", ascending=False).astype(int)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude-board", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--current-forecast", type=Path, required=True)
    parser.add_argument("--task003q-forecast", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    claude_payload = json.loads(args.claude_board.read_text())
    active = pd.DataFrame(claude_payload["active"]).rename(columns={"key": "legacy_key", "name": "claude_name", "v": "claude_value", "grp": "claude_group"})
    registry = pd.read_csv(args.registry)
    current = pd.read_csv(args.current_forecast)
    task003q = pd.read_csv(args.task003q_forecast)

    bridge = registry[["stable_player_id", "legacy_key", "player_name", "affl_team", "eligibilities"]].merge(
        active[["legacy_key", "claude_name", "claude_value", "claude_group", "age", "g"]],
        on="legacy_key",
        how="left",
        validate="one_to_one",
    )
    if bridge["claude_value"].isna().any():
        missing = bridge.loc[bridge["claude_value"].isna(), ["stable_player_id", "legacy_key", "player_name"]]
        missing.to_csv(args.out / "missing_claude_rows.csv", index=False)
        raise SystemExit(f"Claude coverage missing for {len(missing)} authoritative players")

    legacy_only = active.loc[~active["legacy_key"].isin(registry["legacy_key"]), ["legacy_key", "claude_name", "claude_value"]]
    legacy_only.to_csv(args.out / "legacy_only_rows.csv", index=False)

    metadata = bridge[["stable_player_id", "legacy_key", "player_name", "affl_team", "eligibilities", "claude_name", "claude_value", "claude_group"]]
    for label, frame in (("current_vnext", current), ("task003q", task003q)):
        duplicate_rows = int(frame.duplicated(KEY).sum())
        lead_counts = frame.groupby("stable_player_id")["lead"].nunique()
        if duplicate_rows or len(frame) != 4020 or frame["stable_player_id"].nunique() != 804 or not lead_counts.eq(5).all():
            raise SystemExit(f"{label} forecast coverage failure")

    current = current.merge(metadata, on="stable_player_id", validate="many_to_one")
    task003q = task003q.merge(metadata, on="stable_player_id", validate="many_to_one")

    repl = {str(k): float(v) for k, v in claude_payload["REPL"].items()}
    captain = {
        "threshold": float(claude_payload["CAPT_THRESH"]),
        "gain": float(claude_payload["CAPT_GAIN"]),
        "exponent": float(claude_payload["CAPT_EXP"]),
        "cap": float(claude_payload["CAPT_CAP"]),
    }
    current_annual = forecast_value(current, repl, captain)
    task003q_annual = forecast_value(task003q, repl, captain)

    current_roll = current_annual.groupby("stable_player_id", as_index=False)["annual_keeper_value_raw"].sum().rename(columns={"annual_keeper_value_raw": "current_vnext_raw_value"})
    task_roll = task003q_annual.groupby("stable_player_id", as_index=False)["annual_keeper_value_raw"].sum().rename(columns={"annual_keeper_value_raw": "task003q_raw_value"})
    board = metadata.merge(current_roll, on="stable_player_id", validate="one_to_one").merge(task_roll, on="stable_player_id", validate="one_to_one")

    claude_total = float(board["claude_value"].sum())
    board["current_vnext_value"] = board["current_vnext_raw_value"] * claude_total / board["current_vnext_raw_value"].sum()
    board["task003q_value"] = board["task003q_raw_value"] * claude_total / board["task003q_raw_value"].sum()
    board["claude_rank"] = rank_desc(board["claude_value"])
    board["current_vnext_rank"] = rank_desc(board["current_vnext_value"])
    board["task003q_rank"] = rank_desc(board["task003q_value"])
    board["task003q_minus_claude_value"] = board["task003q_value"] - board["claude_value"]
    board["task003q_minus_claude_rank"] = board["claude_rank"] - board["task003q_rank"]
    board["task003q_minus_current_value"] = board["task003q_value"] - board["current_vnext_value"]
    board["task003q_minus_current_rank"] = board["current_vnext_rank"] - board["task003q_rank"]

    player_meta = task003q.drop_duplicates("stable_player_id")[["stable_player_id", "position", "position_utility", "age", "prior_games", "zero_history", "age_band", "tenure_band"]]
    board = board.merge(player_meta, on="stable_player_id", validate="one_to_one")
    board = board.sort_values("task003q_rank").reset_index(drop=True)
    board.to_csv(args.out / "unblinded_three_board_comparison.csv", index=False)

    blinded = board[["stable_player_id", "legacy_key", "player_name", "position", "age", "prior_games", "zero_history"]].copy()
    blinded["board_a_value"] = board["claude_value"]
    blinded["board_a_rank"] = board["claude_rank"]
    blinded["board_b_value"] = board["current_vnext_value"]
    blinded["board_b_rank"] = board["current_vnext_rank"]
    blinded["board_c_value"] = board["task003q_value"]
    blinded["board_c_rank"] = board["task003q_rank"]
    blinded.to_csv(args.out / "blinded_three_board_comparison.csv", index=False)
    (args.out / "board_key.json").write_text(json.dumps({"board_a": "Claude original", "board_b": "Claude pricing with current-vNext forecasts", "board_c": "Claude pricing with TASK-003Q forecasts"}, indent=2) + "\n")

    slices = []
    masks = {
        "all": pd.Series(True, index=board.index),
        "age_30_plus": board["age"] >= 30,
        "age_21_and_under": board["age"] <= 21,
        "zero_history": board["zero_history"].astype(bool),
        "claude_top_100": board["claude_rank"] <= 100,
        "task003q_top_100": board["task003q_rank"] <= 100,
    }
    for position in sorted(board["position_utility"].dropna().unique()):
        masks[f"position_{position}"] = board["position_utility"] == position
    for name, mask in masks.items():
        group = board.loc[mask]
        slices.append({
            "slice": name,
            "n": int(len(group)),
            "mean_task003q_minus_claude_value": float(group["task003q_minus_claude_value"].mean()),
            "median_task003q_minus_claude_value": float(group["task003q_minus_claude_value"].median()),
            "mean_abs_task003q_minus_claude_rank": float(group["task003q_minus_claude_rank"].abs().mean()),
            "mean_task003q_minus_current_value": float(group["task003q_minus_current_value"].mean()),
            "mean_abs_task003q_minus_current_rank": float(group["task003q_minus_current_rank"].abs().mean()),
        })
    pd.DataFrame(slices).to_csv(args.out / "slice_summary.csv", index=False)
    board.reindex(board["task003q_minus_claude_rank"].abs().sort_values(ascending=False).index).head(150).to_csv(args.out / "largest_rank_disagreements.csv", index=False)
    board.reindex(board["task003q_minus_claude_value"].abs().sort_values(ascending=False).index).head(150).to_csv(args.out / "largest_value_disagreements.csv", index=False)

    max_rows = board[board["legacy_key"].isin(["max-king-stk", "max-king-syd"])]
    point_identity_error = np.abs(current["exp_points"] - current["exp_games"] * current["cond_avg"])
    task_point_identity_error = np.abs(task003q["exp_points"] - task003q["exp_games"] * task003q["cond_avg"])
    report = {
        "status": "pass",
        "authoritative_players": int(len(board)),
        "claude_active_rows": int(len(active)),
        "legacy_only_rows": int(len(legacy_only)),
        "legacy_only_names": legacy_only["claude_name"].tolist(),
        "max_king_records": int(len(max_rows)),
        "max_king_distinct_ids": int(max_rows["stable_player_id"].nunique()),
        "current_forecast_rows": int(len(current)),
        "task003q_forecast_rows": int(len(task003q)),
        "current_max_points_identity_error": float(point_identity_error.max()),
        "task003q_max_points_identity_error": float(task_point_identity_error.max()),
        "claude_total_value": claude_total,
        "current_scaled_total_value": float(board["current_vnext_value"].sum()),
        "task003q_scaled_total_value": float(board["task003q_value"].sum()),
        "double_fade_applied": False,
        "adapter_rule": "Claude replacement, convex surplus, captaincy, key-position and balanced discount mechanics applied to conditional average and unconditional expected games; p_meaningful is not multiplied again",
    }
    if not (
        len(board) == 804
        and len(active) == 805
        and len(legacy_only) == 1
        and legacy_only.iloc[0]["legacy_key"] == "taylor-adams"
        and len(max_rows) == 2
        and max_rows["stable_player_id"].nunique() == 2
        and point_identity_error.max() < 1e-8
        and task_point_identity_error.max() < 1e-8
        and np.isfinite(board[["claude_value", "current_vnext_value", "task003q_value"]].to_numpy()).all()
    ):
        report["status"] = "fail"
    (args.out / "validation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    files = sorted(path for path in args.out.iterdir() if path.is_file())
    manifest = {
        "task": "TASK-004",
        "status": report["status"],
        "normalisation": "Each forecast-fed board is rescaled to the matched Claude board total; ranks and relative allocations are unchanged by this scale alignment.",
        "horizon": "Forecast-fed boards use the five validated annual leads. Claude original retains its shipped full-career value and is compared after total-capital alignment.",
        "files": {path.name: sha256(path) for path in files},
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
