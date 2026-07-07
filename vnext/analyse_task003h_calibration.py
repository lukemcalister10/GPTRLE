"""Diagnostic-only audit of meaningful-season classifier calibration.

Separates the raw event classifier probability from the fold-specific temporal
isotonic calibrated probability for locked TASK-003 folds. The script reads
already-trained fold artifacts and locked comparison outputs; it does not alter
model fitting, validation, production inference, values, keeper utility or UI.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
VNEXT_DIR = Path(__file__).resolve().parent
for path in (ROOT, VNEXT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from analyse_task003e_regressions import material_regressions
from analyse_task003g_components import add_slice_columns

KEYS = ["player_key", "origin_year", "lead"]
VNEXT = "vnext_fold_specific"
SLICE_COLUMNS = {
    "age_band": "age_band",
    "tenure_band": "tenure_band",
    "position": "position",
    "pick_band": "pick_band",
    "prior_games": "prior_games",
}


def safe_auc(y: pd.Series, p: pd.Series) -> float:
    if y.nunique() < 2:
        return float("nan")
    return float(roc_auc_score(y, p))


def probability_metrics(group: pd.DataFrame, probability_column: str) -> dict[str, float]:
    y = group["meaningful"].astype(int)
    p = group[probability_column].astype(float).clip(0.001, 0.999)
    return {
        f"{probability_column}_mean": float(p.mean()),
        f"{probability_column}_bias": float(p.mean() - y.mean()),
        f"{probability_column}_brier": float(brier_score_loss(y, p)),
        f"{probability_column}_log_loss": float(log_loss(y, p, labels=[0, 1])),
        f"{probability_column}_auc": safe_auc(y, p),
    }


def classify_origin(actual: float, raw: float, calibrated: float, tolerance: float) -> str:
    raw_bias = raw - actual
    cal_bias = calibrated - actual
    if raw_bias < -tolerance:
        return "raw_classifier_underpredicts"
    if abs(raw_bias) <= tolerance and cal_bias < -tolerance:
        return "isotonic_introduces_underprediction"
    if raw_bias > tolerance and cal_bias < -tolerance:
        return "isotonic_overcorrects_to_underprediction"
    if cal_bias < raw_bias - tolerance:
        return "isotonic_moves_down"
    if cal_bias > raw_bias + tolerance:
        return "isotonic_moves_up"
    return "no_material_probability_underprediction"


def load_diagnostic_rows(comparison_dir: Path, folds_dir: Path) -> pd.DataFrame:
    predictions = pd.read_csv(comparison_dir / "predictions.csv")
    predictions = predictions[predictions["model_id"].eq(VNEXT)].copy()
    targets = pd.read_csv(comparison_dir / "cohorts" / "targets.csv")
    snapshots = pd.read_csv(comparison_dir / "cohorts" / "included_snapshots.csv")
    rows = predictions.merge(targets, on=KEYS, validate="one_to_one").merge(
        snapshots,
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )
    rows = add_slice_columns(rows)
    raw_parts: list[pd.DataFrame] = []
    for (lead, origin), group in rows.groupby(["lead", "origin_year"], sort=True):
        artifact_path = folds_dir / "fold_artifacts" / f"lead_{int(lead)}_origin_{int(origin)}.joblib"
        if not artifact_path.exists():
            raise FileNotFoundError(f"missing fold artifact: {artifact_path}")
        artifact: Any = joblib.load(artifact_path)
        transformed = artifact.preprocessor.transform(group)
        raw = artifact.event_model.predict_proba(transformed)[:, 1]
        calibrated = artifact.event_calibrator.predict(raw)
        part = group[[*KEYS]].copy()
        part["p_meaningful_raw"] = np.clip(raw, 0.001, 0.999)
        part["p_meaningful_calibrated_recomputed"] = np.clip(calibrated, 0.001, 0.999)
        raw_parts.append(part)
    raw_rows = pd.concat(raw_parts, ignore_index=True)
    out = rows.merge(raw_rows, on=KEYS, validate="one_to_one")
    max_delta = (out["p_meaningful"] - out["p_meaningful_calibrated_recomputed"]).abs().max()
    if max_delta > 1e-9:
        raise ValueError(f"recomputed calibrated probabilities do not match predictions; max delta={max_delta}")
    return out


def summarize_groups(rows: pd.DataFrame, group_columns: list[str], tolerance: float) -> pd.DataFrame:
    records = []
    for keys, group in rows.groupby(group_columns, observed=True, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        actual = float(group["meaningful"].mean())
        raw = float(group["p_meaningful_raw"].mean())
        calibrated = float(group["p_meaningful"].mean())
        record = dict(zip(group_columns, keys, strict=True))
        record.update(
            n=int(len(group)),
            actual_meaningful_rate=actual,
            isotonic_delta_mean=calibrated - raw,
            origin=classify_origin(actual, raw, calibrated, tolerance),
            **probability_metrics(group, "p_meaningful_raw"),
            **probability_metrics(group, "p_meaningful"),
        )
        records.append(record)
    return pd.DataFrame(records)


def locked_slice_rows(rows: pd.DataFrame, regressions: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for regression in regressions.itertuples(index=False):
        column = SLICE_COLUMNS[regression.slice_type]
        part = rows[
            rows["lead"].eq(regression.lead)
            & rows[column].astype(str).eq(str(regression.slice_value))
        ].copy()
        part["slice_type"] = regression.slice_type
        part["slice_value"] = regression.slice_value
        parts.append(part)
    return pd.concat(parts, ignore_index=True) if parts else rows.iloc[0:0].copy()


def audit(comparison_dir: Path, folds_dir: Path, tolerance: float = 0.01) -> dict[str, pd.DataFrame]:
    rows = load_diagnostic_rows(comparison_dir, folds_dir)
    slices = pd.read_csv(comparison_dir / "slice_metrics.csv")
    regressions = material_regressions(slices)
    locked = locked_slice_rows(rows, regressions)
    return {
        "raw_vs_calibrated_predictions": rows[
            [
                *KEYS,
                "model_id",
                "meaningful",
                "p_meaningful_raw",
                "p_meaningful",
                "age_band",
                "tenure_band",
                "position",
                "pick_band",
                "prior_games",
            ]
        ],
        "fold_lead_summary": summarize_groups(rows, ["origin_year", "lead"], tolerance),
        "locked_slice_summary": summarize_groups(locked, ["lead", "slice_type", "slice_value"], tolerance),
        "locked_slice_fold_summary": summarize_groups(locked, ["lead", "origin_year", "slice_type", "slice_value"], tolerance),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--folds-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=0.01)
    args = parser.parse_args()
    outputs = audit(args.comparison_dir, args.folds_dir, args.tolerance)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(args.out / f"{name}.csv", index=False)
    print(f"wrote TASK-003H calibration audit to {args.out}")


if __name__ == "__main__":
    main()
