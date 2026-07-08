from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def rank_desc(values: pd.Series) -> pd.Series:
    return values.rank(method="min", ascending=False).astype(int)


def concentration(values: pd.Series) -> dict[str, float]:
    ranks = rank_desc(values)
    n = len(values)
    total = float(values.sum())
    return {
        "top100_share": float(values[ranks <= 100].sum() / total),
        "bottom_half_share": float(values[ranks > n / 2].sum() / total),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task004-board", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    board = pd.read_csv(args.task004_board)
    required = {
        "stable_player_id", "legacy_key", "player_name", "claude_value",
        "current_vnext_value", "task003q_value", "claude_rank",
        "current_vnext_rank", "task003q_rank",
    }
    missing = sorted(required - set(board.columns))
    if missing:
        raise SystemExit(f"missing columns: {missing}")
    if len(board) != 804 or board.stable_player_id.nunique() != 804:
        raise SystemExit("authoritative coverage failure")
    if board.duplicated("stable_player_id").any():
        raise SystemExit("duplicate stable_player_id")

    # Transfer only the incremental TASK-003Q forecast effect into Claude's
    # existing keeper-utility spine. This preserves Claude's option/scarcity/
    # career allocation and tail, while avoiding a second survival fade.
    board["task003q_increment"] = board["task003q_value"] - board["current_vnext_value"]
    raw = board["claude_value"] + board["task003q_increment"]
    if (raw < 0).any():
        raise SystemExit("negative value created by incremental overlay")
    board["task006_value"] = raw * board["claude_value"].sum() / raw.sum()
    board["task006_rank"] = rank_desc(board["task006_value"])
    board["task006_minus_claude_value"] = board["task006_value"] - board["claude_value"]
    board["task006_minus_claude_rank"] = board["claude_rank"] - board["task006_rank"]
    board["task006_minus_task003q_rank"] = board["task003q_rank"] - board["task006_rank"]
    board.to_csv(args.out / "task006_overlay_board.csv", index=False)

    c = concentration(board.claude_value)
    q = concentration(board.task003q_value)
    o = concentration(board.task006_value)
    top100_overlap = int(len(set(board.loc[board.claude_rank <= 100, "stable_player_id"]) & set(board.loc[board.task006_rank <= 100, "stable_player_id"])))
    sign_match = np.sign(board.task006_minus_claude_value) == np.sign(board.task003q_increment)
    nonzero = np.abs(board.task003q_increment) > 1e-10
    sign_preservation = float(sign_match[nonzero].mean()) if nonzero.any() else 1.0
    report = {
        "status": "pass",
        "players": int(len(board)),
        "total_value_error": float(abs(board.task006_value.sum() - board.claude_value.sum())),
        "claude_concentration": c,
        "direct_task003q_concentration": q,
        "task006_concentration": o,
        "top100_overlap_with_claude": top100_overlap,
        "mean_abs_rank_move_from_claude": float(board.task006_minus_claude_rank.abs().mean()),
        "max_abs_rank_move_from_claude": int(board.task006_minus_claude_rank.abs().max()),
        "forecast_delta_sign_preservation": sign_preservation,
        "mean_abs_value_delta": float(board.task006_minus_claude_value.abs().mean()),
        "max_abs_value_delta": float(board.task006_minus_claude_value.abs().max()),
        "double_survival_fade_applied": False,
        "year6_plus_forecast_replaced": False,
        "rule": "Claude value plus the normalized marginal difference between TASK-003Q-fed and current-vNext-fed five-year utility boards",
    }
    gate = (
        report["total_value_error"] < 1e-6
        and o["top100_share"] <= c["top100_share"] + 0.02
        and o["bottom_half_share"] >= c["bottom_half_share"] * 0.80
        and top100_overlap >= 95
        and report["mean_abs_rank_move_from_claude"] <= 10
        and sign_preservation >= 0.99
    )
    report["status"] = "pass" if gate else "fail"
    report["decision_rule"] = "preserve Claude capital shape, >=95 top-100 overlap, <=10 mean rank move, >=99% marginal direction preservation"
    (args.out / "task006_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    board.reindex(board.task006_minus_claude_rank.abs().sort_values(ascending=False).index).head(150).to_csv(args.out / "largest_rank_moves.csv", index=False)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
