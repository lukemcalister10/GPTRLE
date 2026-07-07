"""CLI runner for TASK-003 baseline and model comparison."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from benchmark import (
    BaselineAdapter,
    PREDICTION_KEY,
    REQUIRED_PREDICTION_COLUMNS,
    assert_common_keys_and_targets,
    prediction_keys_from_targets,
    score_predictions,
)
from build_historical_cohorts import build_locked_cohorts
from comparison_harness import (
    load_external_predictions,
    sha256_file,
    weighted_metric_summary,
    write_csv,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task-003-comparison"


def run_comparison(
    out_dir: Path,
    *,
    vnext_predictions: Path | None = None,
    legacy_predictions: Path | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cohort_dir = out_dir / "cohorts"
    cohort_manifest = build_locked_cohorts(cohort_dir)
    snapshots = pd.read_csv(cohort_dir / "included_snapshots.csv")
    targets = pd.read_csv(cohort_dir / "targets.csv")
    prediction_keys = prediction_keys_from_targets(targets)

    baseline = BaselineAdapter().predict(snapshots, prediction_keys)
    predictions: dict[str, pd.DataFrame] = {
        "baseline_recent_scoring": baseline,
    }
    input_files: dict[str, dict[str, str]] = {}

    if vnext_predictions is not None:
        predictions["vnext_artifact"] = load_external_predictions(
            vnext_predictions, "vnext_artifact"
        )
        input_files["vnext_predictions"] = {
            "path": str(vnext_predictions),
            "sha256": sha256_file(vnext_predictions),
        }
    if legacy_predictions is not None:
        predictions["legacy_frozen"] = load_external_predictions(
            legacy_predictions, "legacy_frozen"
        )
        input_files["legacy_predictions"] = {
            "path": str(legacy_predictions),
            "sha256": sha256_file(legacy_predictions),
        }

    assert_common_keys_and_targets(predictions, targets)
    all_predictions = (
        pd.concat(predictions.values(), ignore_index=True)
        .sort_values(["model_id", *PREDICTION_KEY])
        .reset_index(drop=True)
    )
    metrics = score_predictions(all_predictions, targets)
    summary = weighted_metric_summary(metrics)
