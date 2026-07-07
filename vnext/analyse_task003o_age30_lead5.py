"""TASK-003O diagnostic for age-30+ lead-5 candidate regressions.

Diagnostic only: reads current/candidate fold predictions plus locked annual rows
and writes subgroup metrics/sensitivity summaries. It does not train, calibrate,
tune, alter folds, or write model artifacts.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

METRICS = ("brier", "games_mae", "points_mae")
OPTIONAL_RAW_NAMES = ("p_meaningful_raw", "raw_p_meaningful", "event_raw", "raw_event_probability")


def _mae(a: Iterable[float], b: Iterable[float]) -> float:
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    return float(np.mean(np.abs(aa - bb))) if len(aa) else float("nan")


def _brier(p: Iterable[float], y: Iterable[float]) -> float:
    pp = np.asarray(p, dtype=float)
    yy = np.asarray(y, dtype=float)
    return float(np.mean((pp - yy) ** 2)) if len(pp) else float("nan")


def _pct(candidate: float, current: float) -> float:
    return float((candidate - current) / current * 100.0) if current else float("nan")


def _raw_column(frame: pd.DataFrame) -> str | None:
    return next((name for name in OPTIONAL_RAW_NAMES if name in frame.columns), None)


def _model_metrics(df: pd.DataFrame, prefix: str) -> dict[str, float]:
    out = {
        f"{prefix}brier": _brier(df[f"{prefix}p_meaningful"], df.actual_meaningful),
        f"{prefix}games_mae": _mae(df[f"{prefix}exp_games"], df.actual_games),
        f"{prefix}points_mae": _mae(df[f"{prefix}exp_points"], df.actual_points),
        f"{prefix}mean_calibrated_p": float(df[f"{prefix}p_meaningful"].mean()) if len(df) else float("nan"),
        f"{prefix}calibrated_p_bias": float(df[f"{prefix}p_meaningful"].mean() - df.actual_meaningful.mean()) if len(df) else float("nan"),
    }
    raw = f"{prefix}raw_p_meaningful"
    if raw in df.columns:
        out.update(
            {
                f"{prefix}raw_brier": _brier(df[raw], df.actual_meaningful),
                f"{prefix}mean_raw_p": float(df[raw].mean()) if len(df) else float("nan"),
                f"{prefix}raw_p_bias": float(df[raw].mean() - df.actual_meaningful.mean()) if len(df) else float("nan"),
                f"{prefix}calibration_shift": float((df[f"{prefix}p_meaningful"] - df[raw]).mean()) if len(df) else float("nan"),
            }
        )
    return out


def _summary(df: pd.DataFrame, label: str) -> dict[str, object]:
    row: dict[str, object] = {
        "slice": label,
        "n": int(len(df)),
        "unique_players": int(df.key.nunique()) if "key" in df else 0,
        "prevalence": float(df.actual_meaningful.mean()) if len(df) else float("nan"),
    }
    row.update(_model_metrics(df, "current_"))
    row.update(_model_metrics(df, "candidate_"))
    for metric in METRICS:
        row[f"{metric}_change_pct"] = _pct(float(row[f"candidate_{metric}"]), float(row[f"current_{metric}"]))
    if "candidate_raw_brier" in row and "current_raw_brier" in row:
        row["raw_brier_change_pct"] = _pct(float(row["candidate_raw_brier"]), float(row["current_raw_brier"]))
    return row


def _paired_diffs(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "key", "player", "origin_year", "lead", "age", "tenure", "total_games", "position",
        "prior_games_band", "tenure_band", "support_risk_categories", "actual_meaningful",
        "actual_games", "actual_points",
    ]
    out = df[[c for c in cols if c in df.columns]].copy()
    out["current_brier_err"] = (df.current_p_meaningful - df.actual_meaningful) ** 2
    out["candidate_brier_err"] = (df.candidate_p_meaningful - df.actual_meaningful) ** 2
    out["current_games_abs_err"] = (df.current_exp_games - df.actual_games).abs()
    out["candidate_games_abs_err"] = (df.candidate_exp_games - df.actual_games).abs()
    out["current_points_abs_err"] = (df.current_exp_points - df.actual_points).abs()
    out["candidate_points_abs_err"] = (df.candidate_exp_points - df.actual_points).abs()
    for metric in ("brier_err", "games_abs_err", "points_abs_err"):
        out[f"delta_{metric}"] = out[f"candidate_{metric}"] - out[f"current_{metric}"]
    return out


def _bootstrap_by_player(diffs: pd.DataFrame, reps: int, seed: int) -> pd.DataFrame:
    by_player = diffs.groupby("key")[["delta_brier_err", "delta_games_abs_err", "delta_points_abs_err"]].mean()
    rng = np.random.default_rng(seed)
    rows = []
    for column in by_player.columns:
        vals = by_player[column].to_numpy(dtype=float)
        draws = (
            np.array([vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(reps)])
            if len(vals)
            else np.array([np.nan])
        )
        rows.append(
            {
                "metric": column,
                "mean_delta_candidate_minus_current": float(np.mean(vals)) if len(vals) else float("nan"),
                "ci025": float(np.quantile(draws, 0.025)),
                "ci975": float(np.quantile(draws, 0.975)),
                "p_candidate_better": float(np.mean(draws < 0.0)),
                "repetitions": int(reps),
                "player_blocks": int(len(vals)),
                "seed": int(seed),
            }
        )
    return pd.DataFrame(rows)


def _add_bands(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["prior_games_band"] = np.select(
        [out.total_games.eq(0), out.total_games.between(1, 25), out.total_games.between(26, 75), out.total_games.gt(75)],
        ["zero_prior_games", "1-25", "26-75", "76+"],
        default="unknown",
    )
    out["tenure_band"] = np.select(
        [out.tenure.between(0, 1), out.tenure.between(2, 3), out.tenure.between(4, 5), out.tenure.between(6, 9), out.tenure.ge(10)],
        ["0-1", "2-3", "4-5", "6-9", "10+"],
        default="unknown",
    )
    late_pick = pd.to_numeric(out.get("pick", pd.Series(np.nan, index=out.index)), errors="coerce").fillna(999).gt(60)
    categories: list[str] = []
    for _, row in out.iterrows():
        flags = []
        if row.get("prior_games_band") == "zero_prior_games":
            flags.append("zero_prior_games")
        if str(row.get("position")) == "RUC":
            flags.append("ruck")
        if 27 <= float(row.get("age", np.nan)) <= 29:
            flags.append("age_27_29")
        if row.get("tenure_band") == "4-5":
            flags.append("tenure_4_5")
        categories.append("|".join(flags) if flags else "none")
    out["support_risk_categories"] = categories
    out.loc[late_pick, "support_risk_categories"] = out.loc[late_pick, "support_risk_categories"].map(
        lambda value: "pick_61_undrafted" if value == "none" else f"{value}|pick_61_undrafted"
    )
    return out


def _overlap_tables(target: pd.DataFrame) -> dict[str, pd.DataFrame]:
    tables = {
        "overlap_by_position.csv": pd.DataFrame([_summary(g, f"position={k}") for k, g in target.groupby("position", dropna=False)]),
        "overlap_by_tenure_band.csv": pd.DataFrame([_summary(g, f"tenure_band={k}") for k, g in target.groupby("tenure_band", dropna=False)]),
        "overlap_by_prior_games_band.csv": pd.DataFrame([_summary(g, f"prior_games_band={k}") for k, g in target.groupby("prior_games_band", dropna=False)]),
    }
    support_rows = []
    for category in ["zero_prior_games", "ruck", "age_27_29", "tenure_4_5", "pick_61_undrafted", "none"]:
        mask = target.support_risk_categories.str.split("|").map(lambda xs: category in xs)
        support_rows.append(_summary(target[mask], f"support_risk={category}"))
    tables["overlap_by_task003j_support_risk.csv"] = pd.DataFrame(support_rows)
    return tables


def _normalise_key(frame: pd.DataFrame) -> pd.DataFrame:
    if "key" not in frame.columns and "player_key" in frame.columns:
        return frame.rename(columns={"player_key": "key"})
    return frame


def _add_actuals_from_annual(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "actual_games" in out.columns:
        return out
    for metric, suffix in [
        ("actual_games", "games"),
        ("actual_avg", "avg"),
        ("actual_points", "points"),
        ("actual_meaningful", "meaningful"),
    ]:
        values = []
        for row in out.itertuples(index=False):
            col = f"l{int(row.lead)}_{suffix}"
            if col not in out.columns:
                raise ValueError(f"annual rows are missing required target column {col}")
            values.append(getattr(row, col))
        out[metric] = values
    return out


def _load_inputs(current_path: Path, candidate_path: Path, annual_path: Path) -> pd.DataFrame:
    current = _normalise_key(pd.read_csv(current_path))
    candidate = _normalise_key(pd.read_csv(candidate_path))
    annual = _normalise_key(pd.read_csv(annual_path))
    required_annual = ["key", "origin_year", "age", "tenure", "total_games", "position", "pick"]
    missing = [col for col in required_annual if col not in annual.columns]
    if missing:
        raise ValueError(f"annual rows are missing required columns: {missing}")
    lead_target_cols = [c for c in annual.columns if c.startswith("l") and c.split("_", 1)[0][1:].isdigit()]
    annual_cols = required_annual + [c for c in lead_target_cols if c not in required_annual]
    annual = annual[annual_cols]
    join_cols = ["key", "origin_year", "lead"]
    actual_cols = ["player", "position", "pick", "actual_games", "actual_avg", "actual_points", "actual_meaningful"]
    current_raw = _raw_column(current)
    candidate_raw = _raw_column(candidate)
    current_cols = join_cols + [c for c in actual_cols if c in current.columns] + ["p_meaningful", "exp_games", "exp_points"]
    candidate_cols = join_cols + ["p_meaningful", "exp_games", "exp_points"]
    if current_raw:
        current_cols.append(current_raw)
    if candidate_raw:
        candidate_cols.append(candidate_raw)
    merged = current[current_cols].merge(candidate[candidate_cols], on=join_cols, suffixes=("_current", "_candidate"), validate="one_to_one")
    rename = {
        "p_meaningful_current": "current_p_meaningful",
        "exp_games_current": "current_exp_games",
        "exp_points_current": "current_exp_points",
        "p_meaningful_candidate": "candidate_p_meaningful",
        "exp_games_candidate": "candidate_exp_games",
        "exp_points_candidate": "candidate_exp_points",
    }
    if current_raw:
        rename[f"{current_raw}_current"] = "current_raw_p_meaningful"
    if candidate_raw:
        rename[f"{candidate_raw}_candidate"] = "candidate_raw_p_meaningful"
    merged = merged.rename(columns=rename)
    if "player" not in merged.columns:
        merged["player"] = merged["key"]
    merged = merged.merge(annual, on=["key", "origin_year"], how="left", suffixes=("", "_origin"), validate="many_to_one")
    if "position_origin" in merged.columns:
        if "position" not in merged.columns:
            merged["position"] = merged["position_origin"]
        else:
            merged["position"] = merged["position"].fillna(merged["position_origin"])
    if "pick_origin" in merged.columns:
        if "pick" not in merged.columns:
            merged["pick"] = merged["pick_origin"]
        else:
            merged["pick"] = merged["pick"].fillna(merged["pick_origin"])
    merged = _add_actuals_from_annual(merged)
    return _add_bands(merged)



def _recommendation(
    summary: pd.DataFrame,
    leave_one_origin_out: pd.DataFrame,
    bootstrap: pd.DataFrame,
    influential: pd.DataFrame,
) -> tuple[str, pd.DataFrame]:
    lead5 = summary[summary["slice"].eq("age_30_plus_lead_5")].iloc[0]
    primary_worse = all(float(lead5[f"{metric}_change_pct"]) > 0.0 for metric in METRICS)
    loo_worse = all(
        float(row[f"{metric}_change_pct"]) > 0.0
        for _, row in leave_one_origin_out.iterrows()
        for metric in METRICS
    )
    bootstrap_worse = all(float(row["ci025"]) > 0.0 for _, row in bootstrap.iterrows())
    bootstrap_not_worse = any(float(row["ci975"]) <= 0.0 for _, row in bootstrap.iterrows())
    positive_points = influential["delta_points_abs_err"].clip(lower=0.0)
    total_positive_points = float(positive_points.sum())
    largest_player_share = (
        float(positive_points.max() / total_positive_points)
        if total_positive_points > 0.0
        else 0.0
    )
    dominated_by_one_player = largest_player_share >= 0.50

    diagnostics = pd.DataFrame(
        [
            {
                "primary_metrics_all_worse": primary_worse,
                "leave_one_origin_out_all_worse": loo_worse,
                "player_block_bootstrap_ci_all_worse": bootstrap_worse,
                "player_block_bootstrap_any_not_worse": bootstrap_not_worse,
                "largest_player_positive_points_share": largest_player_share,
                "dominated_by_one_player": dominated_by_one_player,
            }
        ]
    )
    if primary_worse and loo_worse and bootstrap_worse and not dominated_by_one_player:
        return "block TASK-003K", diagnostics
    if (not primary_worse) or bootstrap_not_worse:
        return "do not block TASK-003K", diagnostics
    return "insufficient evidence", diagnostics

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--annual", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expected-age30-lead5-n", type=int, default=278)
    parser.add_argument("--bootstrap-reps", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=30015)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    df = _load_inputs(args.current, args.candidate, args.annual)
    target = df[(df.age >= 30) & (df.lead == 5)].copy()
    if len(target) != args.expected_age30_lead5_n:
        raise ValueError(f"age-30+ lead-5 population changed: expected {args.expected_age30_lead5_n} got {len(target)}")
    lead4 = df[(df.age >= 30) & (df.lead == 4)].copy()

    summary = pd.DataFrame([_summary(target, "age_30_plus_lead_5"), _summary(lead4, "age_30_plus_lead_4")])
    by_origin = pd.DataFrame([_summary(g, f"origin={k}") for k, g in target.groupby("origin_year")])
    leave_one_origin_out = pd.DataFrame([_summary(target[target.origin_year != y], f"drop_origin={y}") for y in sorted(target.origin_year.unique())])

    summary.to_csv(args.out / "summary.csv", index=False)
    by_origin.to_csv(args.out / "by_origin.csv", index=False)
    leave_one_origin_out.to_csv(args.out / "leave_one_origin_out.csv", index=False)

    diffs = _paired_diffs(target)
    diffs.to_csv(args.out / "row_deltas.csv", index=False)
    influential = diffs.groupby(["key", "player"], as_index=False)[["delta_brier_err", "delta_games_abs_err", "delta_points_abs_err"]].sum().sort_values("delta_points_abs_err", ascending=False)
    influential.to_csv(args.out / "influential_players.csv", index=False)
    bootstrap = _bootstrap_by_player(diffs, args.bootstrap_reps, args.seed)
    bootstrap.to_csv(args.out / "player_block_bootstrap.csv", index=False)
    for name, table in _overlap_tables(target).items():
        table.to_csv(args.out / name, index=False)
    recommendation, recommendation_diagnostics = _recommendation(summary, leave_one_origin_out, bootstrap, influential)
    recommendation_diagnostics.to_csv(args.out / "recommendation_diagnostics.csv", index=False)
    (args.out / "recommendation.txt").write_text(f"{recommendation}\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
