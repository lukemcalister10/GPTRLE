"""Compare TASK-047 pooled Ridge conditional average with accepted TASK-012."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEY = ["player_key", "origin_year", "lead"]
DEFAULT_BASELINE = ROOT / "build" / "task012-candidate" / "vnext_predictions.csv"
DEFAULT_CANDIDATE = ROOT / "build" / "task047-pooled-ridge-conditional-average" / "vnext_predictions.csv"
DEFAULT_TARGETS = ROOT / "build" / "task-003-cohorts" / "targets.csv"
DEFAULT_FEATURES = ROOT / "build" / "task047-pooled-ridge-conditional-average" / "training_dataset.csv"
DEFAULT_OUT = ROOT / "reports" / "task-047-pooled-ridge-conditional-average"


def _band(series: pd.Series) -> pd.Series:
    return pd.cut(
        pd.to_numeric(series, errors="coerce"),
        [0, 60, 75, 90, 105, 120, 200],
        labels=["<60", "60-75", "75-90", "90-105", "105-120", "120+"],
        include_lowest=True,
        right=False,
    ).astype("string").fillna("unknown")


def _summarise(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["model"] + groups + ["n", "mae", "bias", "actual_avg", "pred_avg"])
    return frame.groupby(["model"] + groups, dropna=False).agg(
        n=("error", "size"),
        mae=("abs_error", "mean"),
        bias=("error", "mean"),
        actual_avg=("avg", "mean"),
        pred_avg=("cond_avg", "mean"),
        residual_sd=("error", "std"),
    ).reset_index().sort_values(["model"] + groups).reset_index(drop=True)


def _summarise_points(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["model"] + groups + ["n", "mae", "bias", "actual_points", "pred_points"])
    return frame.groupby(["model"] + groups, dropna=False).agg(
        n=("points_error", "size"),
        mae=("points_abs_error", "mean"),
        bias=("points_error", "mean"),
        actual_points=("actual_points", "mean"),
        pred_points=("exp_points", "mean"),
    ).reset_index().sort_values(["model"] + groups).reset_index(drop=True)


def _load_one(path: Path, model: str) -> pd.DataFrame:
    columns = pd.read_csv(path, nrows=0).columns
    keep = [
        c for c in [
            *KEY,
            "p_meaningful",
            "exp_games",
            "cond_games",
            "cond_avg",
            "exp_avg",
            "exp_points",
            "p_avg_ge_80",
            "p_avg_ge_90",
            "p_avg_ge_100",
            "p_avg_ge_110",
            "p_avg_ge_120",
            "points_q10",
            "points_q25",
            "points_q50",
            "points_q75",
            "points_q90",
            "points_q97",
        ] if c in columns
    ]
    out = pd.read_csv(path, usecols=keep)
    out["model"] = model
    return out


def _empty_board_changes() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "stable_player_id",
            "key",
            "player_name",
            "position",
            "position_utility",
            "current_exp_points_5y",
            "candidate_exp_points_5y",
            "delta_exp_points_5y",
            "current_rank_exp_points_5y",
            "candidate_rank_exp_points_5y",
            "rank_change_exp_points_5y",
        ]
    )


def _current_board_changes(path: Path | None) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object] | None]:
    if path is None:
        return _empty_board_changes(), _empty_board_changes(), None
    rollup = pd.read_csv(path)
    required = {
        "stable_player_id",
        "key",
        "player_name",
        "position",
        "position_utility",
        "current_exp_points_5y",
        "candidate_exp_points_5y",
        "delta_exp_points_5y",
        "current_rank_exp_points_5y",
        "candidate_rank_exp_points_5y",
        "rank_change_exp_points_5y",
    }
    missing = sorted(required - set(rollup.columns))
    if missing:
        raise ValueError(f"current-board rollup missing required columns: {missing}")
    if len(rollup) != 804 or rollup["stable_player_id"].nunique() != 804:
        raise ValueError("current-board rollup must contain exactly 804 players")
    cols = [c for c in _empty_board_changes().columns if c in rollup.columns]
    rises = rollup.nlargest(50, "delta_exp_points_5y")[cols].reset_index(drop=True)
    falls = rollup.nsmallest(50, "delta_exp_points_5y")[cols].reset_index(drop=True)
    summary = {
        "source": str(path),
        "players": int(len(rollup)),
        "mean_delta_exp_points_5y": float(rollup["delta_exp_points_5y"].mean()),
        "mean_abs_delta_exp_points_5y": float(rollup["delta_exp_points_5y"].abs().mean()),
        "max_rise_exp_points_5y": float(rollup["delta_exp_points_5y"].max()),
        "max_fall_exp_points_5y": float(rollup["delta_exp_points_5y"].min()),
    }
    return rises, falls, summary



def _unchanged_output_invariants(preds: pd.DataFrame) -> pd.DataFrame:
    invariant_columns = [
        c for c in [
            "p_meaningful",
            "exp_games",
            "cond_games",
            "p_avg_ge_80",
            "p_avg_ge_90",
            "p_avg_ge_100",
            "p_avg_ge_110",
            "p_avg_ge_120",
        ] if c in preds.columns
    ]
    if not invariant_columns:
        return pd.DataFrame(columns=["column", "max_abs_delta", "rows_compared", "violations_gt_1e_12"])
    wide = preds.pivot(index=KEY, columns="model", values=invariant_columns)
    rows = []
    for column in invariant_columns:
        delta = (wide[(column, "task047")] - wide[(column, "task012")]).abs()
        rows.append({
            "column": column,
            "max_abs_delta": float(delta.max()),
            "rows_compared": int(delta.notna().sum()),
            "violations_gt_1e_12": int((delta > 1e-12).sum()),
        })
    return pd.DataFrame(rows)


def _uncertainty_output_changes(preds: pd.DataFrame) -> pd.DataFrame:
    quantile_columns = [c for c in ["points_q10", "points_q25", "points_q50", "points_q75", "points_q90", "points_q97"] if c in preds.columns]
    if not quantile_columns:
        return pd.DataFrame(columns=["lead", "quantile", "n", "mean_delta", "mean_abs_delta", "max_abs_delta"])
    wide = preds.pivot(index=KEY, columns="model", values=quantile_columns).reset_index()
    rows = []
    for lead, group in wide.groupby("lead", dropna=False):
        for column in quantile_columns:
            delta = group[(column, "task047")] - group[(column, "task012")]
            rows.append({
                "lead": int(lead),
                "quantile": column,
                "n": int(delta.notna().sum()),
                "mean_delta": float(delta.mean()),
                "mean_abs_delta": float(delta.abs().mean()),
                "max_abs_delta": float(delta.abs().max()),
            })
    return pd.DataFrame(rows).sort_values(["lead", "quantile"]).reset_index(drop=True)


def _uncertainty_blocker() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "status": "blocked_for_acceptance",
            "reason": "TASK-047 changes the conditional-average residual scale and point quantiles mechanically, but the locked benchmark does not contain an acceptance rule for point-quantile calibration or coverage.",
            "required_follow_up": "Before promoting uncertainty outputs, run a separate uncertainty-calibration task with coverage by lead and subgroup. Do not accept TASK-047 on uncertainty quality.",
        }
    ])

def build_tables(
    baseline: pd.DataFrame,
    candidate: pd.DataFrame,
    targets: pd.DataFrame,
    features: pd.DataFrame,
    current_board_rollup: Path | None = None,
    alpha_by_fold: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, object] | None]:
    preds = pd.concat([baseline, candidate], ignore_index=True)
    target = targets[KEY + ["games", "avg", "points", "meaningful"]].copy()
    feat_cols = ["key", "origin_year", "position", "total_games", "weighted_avg", "last_avg", "career_best"]
    feat = features[[c for c in feat_cols if c in features.columns]].rename(columns={"key": "player_key"})
    joined = preds.merge(target, on=KEY, how="inner", validate="many_to_one").merge(feat, on=["player_key", "origin_year"], how="left", validate="many_to_one")
    if len(joined) != len(preds):
        raise ValueError(f"joined row count changed: predictions={len(preds)} joined={len(joined)}")
    joined["broad_position"] = joined.get("position", pd.Series("unknown", index=joined.index)).fillna("unknown").astype(str)
    joined["actual_points"] = joined["points"].astype(float)
    joined["points_error"] = joined["exp_points"].astype(float) - joined["actual_points"].astype(float)
    joined["points_abs_error"] = joined["points_error"].abs()

    active = joined[joined["meaningful"].astype(bool)].copy()
    if active.empty:
        raise ValueError("no meaningful target rows")
    active["error"] = active["cond_avg"].astype(float) - active["avg"].astype(float)
    active["abs_error"] = active["error"].abs()
    active["recent_demonstrated_avg"] = active["weighted_avg"].fillna(active["last_avg"]).fillna(active["career_best"]).fillna(0.0).astype(float)
    active["established"] = np.where(pd.to_numeric(active["total_games"], errors="coerce").fillna(0) >= 50, "established_50_plus", "under_50")
    active["elite_prior"] = np.where(active["recent_demonstrated_avg"] >= 105, "prior_105_plus", "under_105")
    active["predicted_avg_band"] = _band(active["cond_avg"])

    rises, falls, board_summary = _current_board_changes(current_board_rollup)
    tables = {
        "conditional_average_by_lead": _summarise(active, ["lead"]),
        "whole_population": _summarise(active, []),
        "ruck_by_lead": _summarise(active[active["broad_position"].eq("RUC")], ["lead"]),
        "def_mid_fwd_by_lead": _summarise(active[active["broad_position"].isin(["DEF", "MID", "FWD"])], ["lead", "broad_position"]),
        "established_by_lead": _summarise(active[active["established"].eq("established_50_plus")], ["lead"]),
        "elite_prior_by_lead": _summarise(active[active["elite_prior"].eq("prior_105_plus")], ["lead"]),
        "calibration_by_predicted_avg_band": _summarise(active, ["lead", "predicted_avg_band"]),
        "position_by_lead": _summarise(active, ["lead", "broad_position"]),
        "residual_sd_by_lead": _summarise(active, ["lead"])[["model", "lead", "n", "residual_sd"]],
        "expected_points_whole_population": _summarise_points(joined, []),
        "expected_points_by_lead": _summarise_points(joined, ["lead"]),
        "expected_points_by_position_lead": _summarise_points(joined, ["lead", "broad_position"]),
        "unchanged_output_invariants": _unchanged_output_invariants(preds),
        "uncertainty_output_changes_by_lead": _uncertainty_output_changes(preds),
        "uncertainty_acceptance_blocker": _uncertainty_blocker(),
        "selected_ridge_alpha_by_fold_lead": pd.read_csv(alpha_by_fold) if alpha_by_fold is not None else pd.DataFrame(columns=["lead", "origin_year", "selected_alpha", "alpha_scores_json"]),
        "largest_current_board_rises": rises,
        "largest_current_board_falls": falls,
    }
    return active, tables, board_summary


def write_outputs(active: pd.DataFrame, tables: dict[str, pd.DataFrame], out: Path, inputs: dict[str, Path | None], board_summary: dict[str, object] | None) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, table in tables.items():
        path = out / f"{name}.csv"
        table.to_csv(path, index=False, lineterminator="\n")
        artifacts[path.name] = {"rows": int(len(table))}
    failures = {"target_failures": 0, "fold_failures": 0}
    summary_rows = tables["whole_population"]
    invariant_rows = tables["unchanged_output_invariants"]
    summary = {
        "task": "TASK-047-pooled-ridge-conditional-average",
        "state": "candidate",
        "hypothesis": "replace the pooled conditional-average SGDRegressor with a pooled Ridge regressor tuned on the fold-local temporal calibration split",
        "meaningful_target_rows_per_model": {str(k): int(v) for k, v in active.groupby("model").size().items()},
        "overall": summary_rows.to_dict("records"),
        "expected_points_overall": tables["expected_points_whole_population"].to_dict("records"),
        "unchanged_output_invariants": invariant_rows.to_dict("records"),
        "uncertainty_acceptance_blocker": tables["uncertainty_acceptance_blocker"].to_dict("records"),
        "failures": failures,
        "current_board_diagnostics": board_summary,
        "inputs": {k: (None if v is None else str(v)) for k, v in inputs.items()},
        "artifacts": artifacts,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (out / "README.md").write_text("# TASK-047 pooled Ridge conditional average\n\nCandidate benchmark comparison against accepted TASK-012. See summary.json and CSV tables. Current-board rise/fall CSVs are populated only from the 804-player current-board rollup input, not from historical validation rows.\n")
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    p.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    p.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    p.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    p.add_argument("--current-board-rollup", type=Path)
    p.add_argument("--alpha-by-fold", type=Path, default=ROOT / "build" / "task047-pooled-ridge-conditional-average" / "selected_ridge_alpha_by_fold_lead.csv")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    baseline = _load_one(args.baseline, "task012")
    candidate = _load_one(args.candidate, "task047")
    active, tables, board_summary = build_tables(
        baseline,
        candidate,
        pd.read_csv(args.targets),
        pd.read_csv(args.features),
        args.current_board_rollup,
        args.alpha_by_fold,
    )
    summary = write_outputs(
        active,
        tables,
        args.out,
        {
            "baseline": args.baseline,
            "candidate": args.candidate,
            "targets": args.targets,
            "features": args.features,
            "current_board_rollup": args.current_board_rollup,
            "alpha_by_fold": args.alpha_by_fold,
        },
        board_summary,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
