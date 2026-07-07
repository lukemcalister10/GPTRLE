"""Run TASK-003K by reusing the locked TASK-003B fold machinery unchanged."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_historical_folds as locked
from model_artifacts_event_logistic import predict as predict_candidate
from model_artifacts_event_logistic import train_lead as train_candidate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task-003k-candidate-folds"
MODEL_ID = "vnext_event_logistic"


def run(
    out_dir: Path = DEFAULT_OUT,
    cohort_dir: Path = locked.DEFAULT_COHORT_OUT,
    rebuild: bool = False,
) -> dict[str, Any]:
    """Execute the exact locked runner with only event training substituted."""

    locked.train_lead = train_candidate
    locked.predict_lead = predict_candidate
    locked.MODEL_ID = MODEL_ID
    manifest = locked.run(out_dir, cohort_dir, rebuild)
    manifest.update(
        {
            "task": "TASK-003K-event-logistic-fold-predictions",
            "state": "experiment",
            "model_id": MODEL_ID,
            "single_change": "meaningful-season event classifier",
            "candidate": {
                "family": "LogisticRegression",
                "C": 0.35,
                "max_iter": 500,
                "solver": "lbfgs",
                "penalty": "l2",
                "tol": 0.0001,
            },
            "event_calibration_changed": False,
            "conditional_models_changed": False,
            "threshold_models_changed": False,
            "feature_set_changed": False,
            "validation_protocol_changed": False,
            "production_changed": False,
            "reproduction_command": (
                "python vnext/run_task003k_folds.py "
                "--out build/task-003k-candidate "
                "--cohort-dir build/task-003k-cohorts"
            ),
        }
    )
    (out_dir / "prediction_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cohort-dir", type=Path, default=locked.DEFAULT_COHORT_OUT)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.out, args.cohort_dir, args.rebuild), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
