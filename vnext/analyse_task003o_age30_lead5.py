"""TASK-003O diagnostic for age-30+ lead-5 candidate regressions.

This script is diagnostic-only: it reads committed current/candidate predictions and
cohort rows, then writes slice metrics and sensitivity summaries. It does not train,
calibrate, tune, or alter model artifacts.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def _mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b)))) if len(a) else float("nan")


def _brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2)) if len(p) else float("nan")


def _metrics(df: pd.DataFrame, prefix: str) -> dict[str, float]:
    p = f"{prefix}p_meaningful"
    g = f"{prefix}exp_games"
    pts = f"{prefix}exp_points"
    return {
        f"{prefix}brier": _brier(df[p], df.actual_meaningful),
        f"{prefix}games_mae": _mae(df[g], df.actual_games),
        f"{prefix}points_mae": _mae(df[pts], df.actual_points),
        f"{prefix}mean_p": float(df[p].mean()) if len(df) else float("nan"),
        f"{prefix}p_bias": float(df[p].mean() - df.actual_meaningful.mean()) if len(df) else float("nan"),
    }


def _pct(cand: float, cur: float) -> float:
    return float((cand - cur) / cur * 100.0) if cur else float("nan")


def _summary(df: pd.DataFrame, label: str) -> dict[str, object]:
    row = {"slice": label, "n": len(df), "unique_players": df.key.nunique(), "prevalence": df.actual_meaningful.mean()}
    row.update(_metrics(df, "current_"))
    row.update(_metrics(df, "candidate_"))
    for m in ["brier", "games_mae", "points_mae"]:
        row[f"{m}_change_pct"] = _pct(row[f"candidate_{m}"], row[f"current_{m}"])
    return row


def _paired_diffs(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["key", "player", "origin_year", "actual_meaningful", "actual_games", "actual_points"]].copy()
    out["current_brier_err"] = (df.current_p_meaningful - df.actual_meaningful) ** 2
    out["candidate_brier_err"] = (df.candidate_p_meaningful - df.actual_meaningful) ** 2
    out["current_games_abs_err"] = (df.current_exp_games - df.actual_games).abs()
    out["candidate_games_abs_err"] = (df.candidate_exp_games - df.actual_games).abs()
    out["current_points_abs_err"] = (df.current_exp_points - df.actual_points).abs()
    out["candidate_points_abs_err"] = (df.candidate_exp_points - df.actual_points).abs()
    for m in ["brier_err", "games_abs_err", "points_abs_err"]:
        out[f"delta_{m}"] = out[f"candidate_{m}"] - out[f"current_{m}"]
    return out


def _bootstrap_by_player(diffs: pd.DataFrame, reps: int, seed: int) -> pd.DataFrame:
    byp = diffs.groupby("key")[["delta_brier_err", "delta_games_abs_err", "delta_points_abs_err"]].mean()
    keys = byp.index.to_numpy()
    rng = np.random.default_rng(seed)
    rows = []
    for col in byp.columns:
        vals = byp[col].to_numpy()
        draws = [float(vals[rng.integers(0, len(vals), len(vals))].mean()) for _ in range(reps)] if len(vals) else [float("nan")]
        rows.append({"metric": col, "mean_delta": float(vals.mean()), "ci025": float(np.quantile(draws, .025)), "ci975": float(np.quantile(draws, .975)), "p_candidate_better": float(np.mean(np.asarray(draws) < 0))})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--current", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--annual", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bootstrap-reps", type=int, default=2000)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    cur = pd.read_csv(args.current)
    cand = pd.read_csv(args.candidate)
    annual = pd.read_csv(args.annual)[["key", "origin_year", "age", "tenure", "total_games", "position"]]
    join_cols = ["key", "origin_year", "lead"]
    keep_actual = ["player", "position", "actual_games", "actual_avg", "actual_points", "actual_meaningful"]
    cur_cols = join_cols + keep_actual + ["p_meaningful", "exp_games", "exp_points"] + [c for c in ["raw_p_meaningful"] if c in cur.columns]
    cand_cols = join_cols + ["p_meaningful", "exp_games", "exp_points"] + [c for c in ["raw_p_meaningful"] if c in cand.columns]
    df = cur[cur_cols].merge(cand[cand_cols], on=join_cols, suffixes=("_current", "_candidate"))
    df = df.rename(columns={"p_meaningful_current":"current_p_meaningful","exp_games_current":"current_exp_games","exp_points_current":"current_exp_points","p_meaningful_candidate":"candidate_p_meaningful","exp_games_candidate":"candidate_exp_games","exp_points_candidate":"candidate_exp_points"})
    df = df.merge(annual, on=["key", "origin_year"], how="left", suffixes=("", "_origin"))
    target = df[(df.age >= 30) & (df.lead == 5)].copy()
    lead4 = df[(df.age >= 30) & (df.lead == 4)].copy()
    pd.DataFrame([_summary(target, "age_30_plus_lead_5"), _summary(lead4, "age_30_plus_lead_4")]).to_csv(out / "summary.csv", index=False)
    pd.DataFrame([_summary(g, f"origin_{k}") for k, g in target.groupby("origin_year")]).to_csv(out / "by_origin.csv", index=False)
    diffs = _paired_diffs(target)
    diffs.to_csv(out / "row_deltas.csv", index=False)
    diffs.groupby(["key", "player"], as_index=False)[["delta_brier_err", "delta_games_abs_err", "delta_points_abs_err"]].sum().sort_values("delta_points_abs_err", ascending=False).to_csv(out / "influential_players.csv", index=False)
    pd.DataFrame([_summary(target[target.origin_year != y], f"drop_origin_{y}") for y in sorted(target.origin_year.dropna().unique())]).to_csv(out / "leave_one_origin_out.csv", index=False)
    _bootstrap_by_player(diffs, args.bootstrap_reps, 30015).to_csv(out / "player_block_bootstrap.csv", index=False)

if __name__ == "__main__":
    main()
