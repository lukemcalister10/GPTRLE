"""Independent validation scaffold for TASK-003K event-classifier candidates.

This script is diagnostic-only. It compares an already-built current vNext fold run
against an already-built TASK-003K candidate fold run and, when comparison outputs
are supplied, reproduces locked-cohort scoring summaries for both on identical
TASK-003 targets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "vnext"
if str(VNEXT) not in sys.path:
    sys.path.insert(0, str(VNEXT))

from benchmark import LOCKED_FOLDS, PREDICTION_KEY, REQUIRED_PREDICTION_COLUMNS
from build_historical_cohorts import build_locked_cohorts
from comparison_harness import calibration_intercept_slope_stable, weighted_metric_summary

EXPECTED_TARGET_ROWS = 20094
ARTIFACT_COMPONENTS = (
    "preprocessor",
    "event_model",
    "event_calibrator",
    "games_model",
    "avg_model",
    "threshold_models",
    "threshold_calibrators",
    "games_resid_sd",
    "avg_resid_sd",
    "n_fit",
    "n_cal",
)


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    details: str


def sha256_value(value: Any) -> str:
    return hashlib.sha256(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)).hexdigest()


def read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


def check(statuses: list[Check], name: str, ok: bool, details: str) -> None:
    statuses.append(Check(name, "pass" if ok else "fail", details))


def pending(statuses: list[Check], name: str, details: str) -> None:
    statuses.append(Check(name, "pending", details))


def load_fold_manifest(run_dir: Path) -> pd.DataFrame | None:
    return read_csv_if_exists(run_dir / "fold_artifact_manifest.csv")


def legal_fold_table() -> pd.DataFrame:
    rows = []
    for lead, origins in LOCKED_FOLDS.items():
        for origin in origins:
            allowed = [y for y in range(2008, origin) if y + lead < origin]
            rows.append(
                {
                    "lead": lead,
                    "origin_year": origin,
                    "training_target_max_year": origin - 1,
                    "allowed_training_origins": "|".join(map(str, allowed)),
                }
            )
    return pd.DataFrame(rows).sort_values(["lead", "origin_year"]).reset_index(drop=True)


def validate_fold_cutoffs(statuses: list[Check], label: str, run_dir: Path) -> None:
    manifest = load_fold_manifest(run_dir)
    if manifest is None:
        pending(statuses, f"{label}: fold cutoff legality", f"{run_dir}/fold_artifact_manifest.csv not found")
        return
    expected_pairs = legal_fold_table()[["lead", "origin_year", "training_target_max_year"]]
    got = manifest[["lead", "origin_year", "training_target_max_year"]].sort_values(["lead", "origin_year"]).reset_index(drop=True)
    ok = len(got) == 25 and got.equals(expected_pairs)
    check(statuses, f"{label}: 25 legal rolling-origin cutoffs", ok, f"observed {len(got)} fold rows")


def validate_prediction_keys(statuses: list[Check], label: str, prediction_path: Path, targets: pd.DataFrame) -> pd.DataFrame | None:
    if not prediction_path.exists():
        pending(statuses, f"{label}: prediction keys", f"{prediction_path} not found")
        return None
    pred = pd.read_csv(prediction_path)
    missing_cols = sorted(set(REQUIRED_PREDICTION_COLUMNS) - set(pred.columns))
    check(statuses, f"{label}: prediction schema", not missing_cols, f"missing columns: {missing_cols}")
    target_keys = targets[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    pred_keys = pred[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    ok = len(pred) == EXPECTED_TARGET_ROWS and pred_keys.equals(target_keys)
    check(statuses, f"{label}: locked 20,094-row key match", ok, f"rows={len(pred)}, unique_keys={len(pred_keys.drop_duplicates())}")
    return pred


def score(pred: pd.DataFrame, targets: pd.DataFrame, model_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    joined = pred.merge(targets, on=PREDICTION_KEY, how="inner", validate="one_to_one")
    rows: list[dict[str, Any]] = []
    for lead, group in joined.groupby("lead", sort=True):
        intercept, slope = calibration_intercept_slope_stable(group["meaningful"], group["p_meaningful"])
        row: dict[str, Any] = {
            "model_id": model_id,
            "lead": int(lead),
            "n": int(len(group)),
            "brier_meaningful": brier_score_loss(group["meaningful"], group["p_meaningful"]),
            "log_loss_meaningful": log_loss(group["meaningful"], np.clip(group["p_meaningful"], 0.001, 0.999), labels=[0, 1]),
            "auc_meaningful": float(roc_auc_score(group["meaningful"], group["p_meaningful"])) if group["meaningful"].nunique() > 1 else float("nan"),
            "calibration_intercept_meaningful": intercept,
            "calibration_slope_meaningful": slope,
            "mae_games": mean_absolute_error(group["games"], group["exp_games"]),
            "mae_total_points": mean_absolute_error(group["points"], group["exp_points"]),
        }
        rows.append(row)
    by_lead = pd.DataFrame(rows).sort_values(["model_id", "lead"]).reset_index(drop=True)
    return by_lead, weighted_metric_summary(by_lead)


def compare_artifacts(statuses: list[Check], current_dir: Path, candidate_dir: Path) -> None:
    current_manifest = load_fold_manifest(current_dir)
    candidate_manifest = load_fold_manifest(candidate_dir)
    if current_manifest is None or candidate_manifest is None:
        pending(statuses, "component fingerprint comparison", "one or both fold manifests are missing")
        return
    changed: dict[str, int] = {component: 0 for component in ARTIFACT_COMPONENTS}
    total = 0
    for _, row in current_manifest.iterrows():
        lead, origin = int(row.lead), int(row.origin_year)
        cand_rows = candidate_manifest[(candidate_manifest.lead == lead) & (candidate_manifest.origin_year == origin)]
        if len(cand_rows) != 1:
            check(statuses, "component fingerprint comparison", False, f"missing candidate artifact for lead={lead} origin={origin}")
            return
        current_art = joblib.load(current_dir / str(row.artifact_path))
        candidate_art = joblib.load(candidate_dir / str(cand_rows.iloc[0].artifact_path))
        total += 1
        for component in ARTIFACT_COMPONENTS:
            if sha256_value(getattr(current_art, component)) != sha256_value(getattr(candidate_art, component)):
                changed[component] += 1
    allowed = {"event_model"}
    illegal = {k: v for k, v in changed.items() if v and k not in allowed}
    ok = not illegal and changed["event_model"] > 0
    check(statuses, "only meaningful-season event classifier changed", ok, json.dumps({"folds": total, "changed_components": changed}, sort_keys=True))


def run(args: argparse.Namespace) -> int:
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    statuses: list[Check] = []

    cohort_dir = args.cohort_dir
    if not (cohort_dir / "targets.csv").exists():
        build_locked_cohorts(cohort_dir)
    targets = pd.read_csv(cohort_dir / "targets.csv")
    check(statuses, "locked target cohort row count", len(targets) == EXPECTED_TARGET_ROWS, f"rows={len(targets)}")

    current_pred = validate_prediction_keys(statuses, "current", args.current_predictions, targets)
    validate_fold_cutoffs(statuses, "current", args.current_run_dir)

    candidate_pred = None
    if args.candidate_predictions:
        candidate_pred = validate_prediction_keys(statuses, "candidate", args.candidate_predictions, targets)
        validate_fold_cutoffs(statuses, "candidate", args.candidate_run_dir)
        compare_artifacts(statuses, args.current_run_dir, args.candidate_run_dir)
    else:
        pending(statuses, "candidate-dependent checks", "TASK-003K candidate predictions/artifacts were not supplied")

    metric_outputs: dict[str, Any] = {}
    frames = []
    for label, pred in (("current", current_pred), ("candidate", candidate_pred)):
        if pred is None:
            continue
        by_lead, summary = score(pred, targets, label)
        by_lead.to_csv(out / f"{label}_metrics_by_lead.csv", index=False, lineterminator="\n")
        summary.to_csv(out / f"{label}_metrics_summary.csv", index=False, lineterminator="\n")
        metric_outputs[label] = {"metrics_by_lead": f"{label}_metrics_by_lead.csv", "metrics_summary": f"{label}_metrics_summary.csv"}
        frames.append(by_lead)
    if len(frames) == 2:
        combined = pd.concat(frames, ignore_index=True)
        combined.to_csv(out / "independent_metrics_by_lead.csv", index=False, lineterminator="\n")
        check(statuses, "current and candidate scored on identical targets", True, f"targets_sha_rows={len(targets)}")
    else:
        pending(statuses, "current and candidate scored on identical targets", "candidate metrics pending")

    pending(statuses, "raw event probability reproduction", "requires candidate artifact convention or exported raw event scores")
    pending(statuses, "player-block bootstrap reproduction", "requires candidate comparison output or candidate predictions to run bootstrap externally")
    pending(statuses, "zero-history eventual-player versus eventual-zero trade-off", "requires included snapshot history fields plus candidate predictions")
    pending(statuses, "material subgroup regression audit", "requires candidate predictions; run comparison diagnostics once available")
    pending(statuses, "current-board tuning guard", "manual review pending candidate PR/artifact provenance")

    report = {
        "task": "TASK-003K independent validation scaffold",
        "status_counts": {s: sum(1 for c in statuses if c.status == s) for s in ("pass", "fail", "pending")},
        "checks": [c.__dict__ for c in statuses],
        "metric_outputs": metric_outputs,
    }
    (out / "task003k_validation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pd.DataFrame([c.__dict__ for c in statuses]).to_csv(out / "task003k_validation_checks.csv", index=False, lineterminator="\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if any(c.status == "fail" for c in statuses) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build" / "task-003k-validation")
    parser.add_argument("--cohort-dir", type=Path, default=ROOT / "build" / "task-003b-cohorts")
    parser.add_argument("--current-run-dir", type=Path, default=ROOT / "build" / "task-003b-vnext-folds")
    parser.add_argument("--current-predictions", type=Path, default=ROOT / "build" / "task-003b-vnext-folds" / "vnext_predictions.csv")
    parser.add_argument("--candidate-run-dir", type=Path, default=ROOT / "build" / "task-003k-candidate-folds")
    parser.add_argument("--candidate-predictions", type=Path)
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
