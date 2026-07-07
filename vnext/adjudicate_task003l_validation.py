"""Adjudicate TASK-003L using functional invariants and committed evidence names."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from validate_task003l_independent import (
    KEY,
    EXPECTED_TARGET_ROWS,
    legal_fold_table,
    raw_event_probs,
    score,
)

MODEL_MAP = {"current": "vnext_fold_specific", "candidate": "vnext_event_logistic"}


def weighted_pooled(by_fold: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metrics = [c for c in by_fold.columns if c not in {"model_id", "origin_year", "lead", "n"}]
    for model_id, group in by_fold.groupby("model_id"):
        row = {"model_id": MODEL_MAP[model_id]}
        row.update({c: float(np.average(group[c], weights=group["n"])) for c in metrics})
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cohort-dir", type=Path, required=True)
    p.add_argument("--current-run-dir", type=Path, required=True)
    p.add_argument("--current-predictions", type=Path, required=True)
    p.add_argument("--candidate-run-dir", type=Path, required=True)
    p.add_argument("--candidate-predictions", type=Path, required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--tolerance", type=float, default=1e-9)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    targets = pd.read_csv(args.cohort_dir / "targets.csv")
    snapshots = pd.read_csv(args.cohort_dir / "included_snapshots.csv")
    cur = pd.read_csv(args.current_predictions)
    cand = pd.read_csv(args.candidate_predictions)
    cur_manifest = pd.read_csv(args.current_run_dir / "fold_artifact_manifest.csv")
    cand_manifest = pd.read_csv(args.candidate_run_dir / "fold_artifact_manifest.csv")

    checks = []
    checks.append(("target_rows", len(targets) == EXPECTED_TARGET_ROWS, f"rows={len(targets)}"))
    checks.append(("prediction_keys", not cur.duplicated(KEY).any() and not cand.duplicated(KEY).any(), "duplicate-free"))
    expected_folds = legal_fold_table()
    got_cur = cur_manifest[["lead", "origin_year", "training_target_max_year"]].sort_values(["lead", "origin_year"]).reset_index(drop=True)
    got_cand = cand_manifest[["lead", "origin_year", "training_target_max_year"]].sort_values(["lead", "origin_year"]).reset_index(drop=True)
    checks.append(("legal_folds", got_cur.equals(expected_folds) and got_cand.equals(expected_folds), "25 current + 25 candidate"))

    transformed_mismatch = 0
    conditional_mismatch = 0
    event_model_changed = 0
    event_calibrator_changed = 0
    for row in cur_manifest.itertuples(index=False):
        lead, origin = int(row.lead), int(row.origin_year)
        crow = cand_manifest[(cand_manifest.lead == lead) & (cand_manifest.origin_year == origin)].iloc[0]
        a = joblib.load(args.current_run_dir / str(row.artifact_path))
        b = joblib.load(args.candidate_run_dir / str(crow.artifact_path))
        keys = cand[(cand.lead == lead) & (cand.origin_year == origin)][KEY].head(100)
        sample = keys.merge(snapshots, on=["player_key", "origin_year"], validate="one_to_one")
        za, zb = a.preprocessor.transform(sample), b.preprocessor.transform(sample)
        transformed_mismatch += int(za.shape != zb.shape or not np.allclose(za, zb, atol=1e-12))
        conditional_mismatch += int(not np.allclose(a.games_model.predict(za), b.games_model.predict(zb), atol=1e-10))
        conditional_mismatch += int(not np.allclose(a.avg_model.predict(za), b.avg_model.predict(zb), atol=1e-10))
        event_model_changed += int(type(a.event_model).__name__ != type(b.event_model).__name__ or not np.allclose(a.event_model.predict_proba(za), b.event_model.predict_proba(zb), atol=1e-12))
        event_calibrator_changed += int(type(a.event_calibrator).__name__ != type(b.event_calibrator).__name__ or not np.allclose(a.event_calibrator.predict(a.event_model.predict_proba(za)[:, 1]), b.event_calibrator.predict(b.event_model.predict_proba(zb)[:, 1]), atol=1e-12))
    checks.append(("functional_invariants", transformed_mismatch == 0 and conditional_mismatch == 0, f"transformed={transformed_mismatch} conditional={conditional_mismatch}"))
    checks.append(("declared_event_change", event_model_changed == 25 and event_calibrator_changed == 25, f"model={event_model_changed} calibrator={event_calibrator_changed}"))

    fold_frames = []
    for label, pred, run_dir, manifest in (("current", cur, args.current_run_dir, cur_manifest), ("candidate", cand, args.candidate_run_dir, cand_manifest)):
        raw = raw_event_probs(run_dir, manifest, pred, snapshots)
        by_fold, _ = score(pred, targets, label, raw)
        fold_frames.append(by_fold)
    pooled = weighted_pooled(pd.concat(fold_frames, ignore_index=True)).rename(columns={
        "calibrated_brier_meaningful": "brier_meaningful",
        "calibrated_log_loss_meaningful": "log_loss_meaningful",
        "raw_brier_meaningful": "raw_event_brier",
        "raw_log_loss_meaningful": "raw_event_log_loss",
        "probability_bias": "calibrated_event_bias",
    })
    expected = pd.read_csv(args.evidence_dir / "metrics_summary.csv")
    # AUC is intentionally excluded here because averaging fold AUC is not the same
    # estimand as the committed pooled-row AUC. The decomposable pooled metrics below
    # reproduce the committed evidence exactly and are the acceptance check.
    cols = ["brier_meaningful", "log_loss_meaningful", "mae_games", "mae_total_points", "raw_event_brier", "raw_event_log_loss", "calibrated_event_bias"]
    merged = pooled[["model_id", *cols]].merge(expected[["model_id", *cols]], on="model_id", suffixes=("_got", "_expected"), validate="one_to_one")
    max_diff = max(float((merged[f"{c}_got"] - merged[f"{c}_expected"]).abs().max()) for c in cols)
    checks.append(("committed_pooled_metrics", len(merged) == 2 and max_diff <= args.tolerance, f"max_diff={max_diff}"))

    report = {"status": "pass" if all(ok for _, ok, _ in checks) else "fail", "checks": [{"name": n, "ok": ok, "details": d} for n, ok, d in checks]}
    (args.out / "task003l_adjudication.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
