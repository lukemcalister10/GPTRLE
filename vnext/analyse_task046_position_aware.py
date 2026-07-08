"""Compare TASK-046 position-aware conditional average with accepted TASK-012."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEY = ["player_key", "origin_year", "lead"]
DEFAULT_BASELINE = ROOT / "build" / "task012-candidate" / "vnext_predictions.csv"
DEFAULT_CANDIDATE = ROOT / "build" / "task046-position-aware-conditional-average" / "vnext_predictions.csv"
DEFAULT_TARGETS = ROOT / "build" / "task-003-cohorts" / "targets.csv"
DEFAULT_FEATURES = ROOT / "build" / "task046-position-aware-conditional-average" / "training_dataset.csv"
DEFAULT_OUT = ROOT / "reports" / "task-046-position-aware-conditional-average"


def _band(series: pd.Series) -> pd.Series:
    return pd.cut(pd.to_numeric(series, errors="coerce"), [0, 60, 75, 90, 105, 120, 200], labels=["<60", "60-75", "75-90", "90-105", "105-120", "120+"], include_lowest=True, right=False).astype("string").fillna("unknown")


def _summarise(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["model"] + groups + ["n", "mae", "bias", "actual_avg", "pred_avg"])
    return frame.groupby(["model"] + groups, dropna=False).agg(
        n=("error", "size"),
        mae=("abs_error", "mean"),
        bias=("error", "mean"),
        actual_avg=("avg", "mean"),
        pred_avg=("cond_avg", "mean"),
    ).reset_index().sort_values(["model"] + groups).reset_index(drop=True)


def _load_one(path: Path, model: str) -> pd.DataFrame:
    out = pd.read_csv(path, usecols=KEY + ["cond_avg", "exp_points"])
    out["model"] = model
    return out


def build_tables(baseline: pd.DataFrame, candidate: pd.DataFrame, targets: pd.DataFrame, features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    preds = pd.concat([baseline, candidate], ignore_index=True)
    target = targets[KEY + ["games", "avg", "meaningful"]].copy()
    feat_cols = ["key", "origin_year", "position", "total_games", "weighted_avg", "last_avg", "career_best"]
    feat = features[[c for c in feat_cols if c in features.columns]].rename(columns={"key": "player_key"})
    joined = preds.merge(target, on=KEY, how="inner", validate="many_to_one").merge(feat, on=["player_key", "origin_year"], how="left", validate="many_to_one")
    if len(joined) != len(preds):
        raise ValueError(f"joined row count changed: predictions={len(preds)} joined={len(joined)}")
    active = joined[joined["meaningful"].astype(bool)].copy()
    if active.empty:
        raise ValueError("no meaningful target rows")
    active["error"] = active["cond_avg"].astype(float) - active["avg"].astype(float)
    active["abs_error"] = active["error"].abs()
    active["broad_position"] = active.get("position", pd.Series("unknown", index=active.index)).fillna("unknown").astype(str)
    active["recent_demonstrated_avg"] = active["weighted_avg"].fillna(active["last_avg"]).fillna(active["career_best"]).fillna(0.0).astype(float)
    active["established"] = np.where(pd.to_numeric(active["total_games"], errors="coerce").fillna(0) >= 50, "established_50_plus", "under_50")
    active["elite_prior"] = np.where(active["recent_demonstrated_avg"] >= 105, "prior_105_plus", "under_105")
    active["predicted_avg_band"] = _band(active["cond_avg"])

    current = active[active["origin_year"].eq(active["origin_year"].max())].copy()
    wide = current.pivot_table(index=KEY, columns="model", values="exp_points", aggfunc="first").reset_index()
    if {"task012", "task046"}.issubset(wide.columns):
        board_delta = wide.assign(delta=wide["task046"] - wide["task012"]).merge(feat, on=["player_key", "origin_year"], how="left")
        rises = board_delta.sort_values("delta", ascending=False).head(50)
        falls = board_delta.sort_values("delta").head(50)
    else:
        rises = pd.DataFrame(); falls = pd.DataFrame()

    tables = {
        "conditional_average_by_lead": _summarise(active, ["lead"]),
        "whole_population": _summarise(active, []),
        "ruck_by_lead": _summarise(active[active["broad_position"].eq("RUC")], ["lead"]),
        "def_mid_fwd_by_lead": _summarise(active[active["broad_position"].isin(["DEF", "MID", "FWD"])], ["lead", "broad_position"]),
        "established_by_lead": _summarise(active[active["established"].eq("established_50_plus")], ["lead"]),
        "elite_prior_by_lead": _summarise(active[active["elite_prior"].eq("prior_105_plus")], ["lead"]),
        "calibration_by_predicted_avg_band": _summarise(active, ["lead", "predicted_avg_band"]),
        "position_by_lead": _summarise(active, ["lead", "broad_position"]),
        "largest_current_board_rises": rises,
        "largest_current_board_falls": falls,
    }
    return active, tables


def write_outputs(active: pd.DataFrame, tables: dict[str, pd.DataFrame], out: Path, inputs: dict[str, Path]) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, table in tables.items():
        path = out / f"{name}.csv"
        table.to_csv(path, index=False, lineterminator="\n")
        artifacts[path.name] = {"rows": int(len(table))}
    failures = {"target_failures": 0, "fold_failures": 0}
    summary_rows = tables["whole_population"]
    summary = {
        "task": "TASK-046-position-aware-conditional-average",
        "state": "candidate",
        "hypothesis": "separate broad-position conditional-average regressors with pooled fallback improve ruck and upper-tail calibration",
        "meaningful_target_rows_per_model": {str(k): int(v) for k, v in active.groupby("model").size().items()},
        "overall": summary_rows.to_dict("records"),
        "failures": failures,
        "inputs": {k: str(v) for k, v in inputs.items()},
        "artifacts": artifacts,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (out / "README.md").write_text("# TASK-046 position-aware conditional average\n\nCandidate benchmark comparison against accepted TASK-012. See summary.json and CSV tables.\n")
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    p.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    p.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    p.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    baseline = _load_one(args.baseline, "task012")
    candidate = _load_one(args.candidate, "task046")
    active, tables = build_tables(baseline, candidate, pd.read_csv(args.targets), pd.read_csv(args.features))
    summary = write_outputs(active, tables, args.out, {"baseline": args.baseline, "candidate": args.candidate, "targets": args.targets, "features": args.features})
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
