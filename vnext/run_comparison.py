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
)
from build_historical_cohorts import build_locked_cohorts
from comparison_harness import (
    load_external_predictions,
    score_predictions_stable,
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
        predictions["vnext_fold_specific"] = load_external_predictions(
            vnext_predictions, "vnext_fold_specific"
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
    metrics = score_predictions_stable(all_predictions, targets)
    summary = weighted_metric_summary(metrics)

    artifacts = {
        "predictions.csv": write_csv(out_dir / "predictions.csv", all_predictions),
        "metrics_by_lead.csv": write_csv(out_dir / "metrics_by_lead.csv", metrics),
        "metrics_summary.csv": write_csv(out_dir / "metrics_summary.csv", summary),
        "baseline_predictions.csv": write_csv(
            out_dir / "baseline_predictions.csv", baseline
        ),
    }
    key_report = {
        "expected_rows_per_model": int(len(targets)),
        "models": {
            model_id: {
                "rows": int(len(frame)),
                "unique_keys": int(len(frame[PREDICTION_KEY].drop_duplicates())),
                "exact_target_key_match": True,
            }
            for model_id, frame in sorted(predictions.items())
        },
    }
    key_path = out_dir / "key_validation.json"
    key_path.write_text(
        json.dumps(key_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifacts["key_validation.json"] = {
        "rows": len(predictions),
        "bytes": int(key_path.stat().st_size),
        "sha256": sha256_file(key_path),
    }

    manifest = {
        "task": "TASK-003D-COMPARISON-HARNESS",
        "models": sorted(predictions),
        "prediction_schema": list(REQUIRED_PREDICTION_COLUMNS),
        "expected_rows_per_model": int(len(targets)),
        "cohort_manifest_sha256": sha256_file(cohort_dir / "manifest.json"),
        "cohort_target_rows": int(cohort_manifest["target_rows"]),
        "calibration_solver": "L-BFGS-B with analytic gradient",
        "input_files": input_files,
        "artifacts": artifacts,
        "reproduction_command": "python vnext/run_comparison.py --out build/task-003-comparison",
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--vnext-predictions", type=Path)
    parser.add_argument("--legacy-predictions", type=Path)
    args = parser.parse_args()
    manifest = run_comparison(
        args.out,
        vnext_predictions=args.vnext_predictions,
        legacy_predictions=args.legacy_predictions,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
