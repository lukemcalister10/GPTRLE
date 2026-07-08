"""Audit conditional-average upper-tail compression on locked historical folds.

This is diagnostic-only: it consumes existing leakage-safe fold predictions,
targets and origin-safe training features, and writes subgroup calibration tables
without fitting or changing any model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTIONS = ROOT / "build" / "task012-candidate" / "vnext_predictions.csv"
DEFAULT_TARGETS = ROOT / "build" / "task-003-cohorts" / "targets.csv"
DEFAULT_FEATURES = ROOT / "build" / "task012-candidate" / "training_dataset.csv"
DEFAULT_OUT = ROOT / "reports" / "task-045-conditional-average-compression-audit"
KEY = ["player_key", "origin_year", "lead"]


def _band(series: pd.Series, bins: Iterable[float], labels: Iterable[str]) -> pd.Series:
    return pd.cut(pd.to_numeric(series, errors="coerce"), bins=list(bins), labels=list(labels), include_lowest=True, right=False).astype("string").fillna("unknown")


def _summarise(frame: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=group_cols + ["n", "mae", "bias", "actual_avg", "pred_avg", "recent_avg", "shrinkage"])
    out = frame.groupby(group_cols, dropna=False).agg(
        n=("error", "size"),
        mae=("abs_error", "mean"),
        bias=("error", "mean"),
        actual_avg=("avg", "mean"),
        pred_avg=("cond_avg", "mean"),
        recent_avg=("recent_demonstrated_avg", "mean"),
        shrinkage=("shrinkage", "mean"),
    ).reset_index()
    return out.sort_values(group_cols).reset_index(drop=True)


def build_audit(predictions: pd.DataFrame, targets: pd.DataFrame, features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    pred = predictions[KEY + ["cond_avg"]].copy()
    target_cols = KEY + ["games", "avg", "meaningful"]
    target = targets[target_cols].copy()
    feature_cols = ["key", "origin_year", "total_games", "age", "position", "weighted_avg", "last_avg", "career_best"]
    feat = features[[c for c in feature_cols if c in features.columns]].rename(columns={"key": "player_key"})
    joined = pred.merge(target, on=KEY, how="inner", validate="one_to_one").merge(feat, on=["player_key", "origin_year"], how="left", validate="many_to_one")
    if len(joined) != len(pred):
        raise ValueError(f"joined row count changed: predictions={len(pred)} joined={len(joined)}")
    active = joined[joined["meaningful"].astype(bool)].copy()
    if active.empty:
        raise ValueError("no meaningful target seasons available for conditional-average audit")

    active["error"] = active["cond_avg"].astype(float) - active["avg"].astype(float)
    active["abs_error"] = active["error"].abs()
    active["recent_demonstrated_avg"] = active["weighted_avg"].fillna(active["last_avg"]).fillna(active["career_best"]).fillna(0.0).astype(float)
    active["shrinkage"] = active["cond_avg"].astype(float) - active["recent_demonstrated_avg"]
    active["predicted_avg_band"] = _band(active["cond_avg"], [0, 60, 75, 90, 105, 120, 200], ["<60", "60-75", "75-90", "90-105", "105-120", "120+"])
    active["prior_avg_band"] = _band(active["recent_demonstrated_avg"], [0, 60, 75, 90, 105, 120, 200], ["<60", "60-75", "75-90", "90-105", "105-120", "120+"])
    active["games_band"] = _band(active["total_games"], [0, 1, 25, 50, 100, 200, 1000], ["0", "1-24", "25-49", "50-99", "100-199", "200+"])
    active["established"] = np.where(pd.to_numeric(active["total_games"], errors="coerce").fillna(0) >= 50, "established_50_plus", "under_50")
    active["elite_prior"] = np.where(active["recent_demonstrated_avg"] >= 105, "prior_105_plus", "under_105")
    active["age_band"] = _band(active["age"], [0, 22, 25, 28, 31, 34, 100], ["<22", "22-24", "25-27", "28-30", "31-33", "34+"])
    active["broad_position"] = active.get("position", pd.Series("unknown", index=active.index)).fillna("unknown").astype(str)

    tables = {
        "metrics_by_lead": _summarise(active, ["lead"]),
        "calibration_by_predicted_avg_band": _summarise(active, ["lead", "predicted_avg_band"]),
        "error_by_prior_avg_band": _summarise(active, ["lead", "prior_avg_band"]),
        "error_by_establishment": _summarise(active, ["lead", "established"]),
        "error_by_elite_prior": _summarise(active, ["lead", "elite_prior"]),
        "error_by_position": _summarise(active, ["lead", "broad_position"]),
        "error_by_age_band": _summarise(active, ["lead", "age_band"]),
        "shrinkage_by_prior_avg_band": _summarise(active, ["lead", "prior_avg_band"]),
        "largest_underpredictions": active.sort_values("error").head(50),
        "largest_overpredictions": active.sort_values("error", ascending=False).head(50),
    }
    return active, tables


def write_outputs(active: pd.DataFrame, tables: dict[str, pd.DataFrame], out_dir: Path, inputs: dict[str, Path]) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, table in tables.items():
        path = out_dir / f"{name}.csv"
        table.to_csv(path, index=False, lineterminator="\n")
        artifacts[path.name] = {"rows": int(len(table))}
    summary = {
        "task": "TASK-045-conditional-average-compression-audit",
        "state": "diagnostic",
        "model_changed": False,
        "benchmark_protocol_changed": False,
        "meaningful_target_rows": int(len(active)),
        "total_prediction_rows": int(pd.read_csv(inputs["predictions"], usecols=["player_key"]).shape[0]),
        "target_failures": 0,
        "overall": {
            "mae": float(active["abs_error"].mean()),
            "bias": float(active["error"].mean()),
            "mean_shrinkage_from_recent_demonstrated_avg": float(active["shrinkage"].mean()),
        },
        "inputs": {k: str(v) for k, v in inputs.items()},
        "artifacts": artifacts,
        "reproduction_command": "python vnext/analyse_task045_conditional_compression.py --predictions build/task012-candidate/vnext_predictions.csv --targets build/task-003-cohorts/targets.csv --features build/task012-candidate/training_dataset.csv --out reports/task-045-conditional-average-compression-audit",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    readme = [
        "# TASK-045 conditional-average compression audit",
        "",
        "Diagnostic-only audit of conditional-average forecasts on meaningful historical target seasons.",
        "No model, validation protocol, utility layer or production board is changed.",
        "",
        f"Meaningful target rows: {len(active):,}.",
        f"Overall MAE: {summary['overall']['mae']:.3f}.",
        f"Overall bias (predicted - actual): {summary['overall']['bias']:.3f}.",
        f"Mean shrinkage from recent demonstrated average: {summary['overall']['mean_shrinkage_from_recent_demonstrated_avg']:.3f}.",
    ]
    (out_dir / "README.md").write_text("\n".join(readme) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    predictions = pd.read_csv(args.predictions)
    targets = pd.read_csv(args.targets)
    features = pd.read_csv(args.features)
    active, tables = build_audit(predictions, targets, features)
    summary = write_outputs(active, tables, args.out, {"predictions": args.predictions, "targets": args.targets, "features": args.features})
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
