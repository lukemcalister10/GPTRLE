"""Deterministic baseline and comparison harness for TASK-003."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from benchmark import (
    BaselineAdapter,
    PREDICTION_KEY,
    REQUIRED_PREDICTION_COLUMNS,
    assert_common_keys_and_targets,
    normalise_predictions,
    prediction_keys_from_targets,
    score_predictions,
)
from build_historical_cohorts import build_locked_cohorts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task-003-comparison"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {
        "rows": int(len(frame)),
        "bytes": int(path.stat().st_size),
        "sha256": sha256_file(path),
    }


def load_external_predictions(path: Path, model_id: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    if "model_id" in raw.columns:
        observed = sorted(set(raw["model_id"].astype(str)))
        if observed != [model_id]:
            raise ValueError(
                f"{path} model_id values {observed} do not match expected {model_id}"
            )
        raw = raw.drop(columns=["model_id"])
    return normalise_predictions(model_id, raw)


def weighted_metric_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    decomposable = [
        column
        for column in metrics.columns
        if column.startswith(("brier_", "log_loss_", "mae_", "pinball_"))
    ]
    rows = []
    for model_id, group in metrics.groupby("model_id", sort=True):
        weights = group["n"].to_numpy(float)
        row: dict[str, Any] = {
            "model_id": str(model_id),
            "n": int(weights.sum()),
            "lead_rows": int(len(group)),
        }
        for column in decomposable:
            values = group[column].to_numpy(float)
            valid = np.isfinite(values)
            row[column] = (
                float(np.average(values[valid], weights=weights[valid]))
                if valid.any()
                else float("nan")
            )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("model_id").reset_index(drop=True)
