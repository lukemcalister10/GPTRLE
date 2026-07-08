"""Run TASK-009 with the locked fold and target machinery unchanged."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_historical_folds as locked
from model_artifacts_zero_history import predict as predict_candidate
from model_artifacts_zero_history import train_lead as train_candidate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task009-zero-history-folds"
MODEL_ID = "vnext_task009_zero_history_state"


def run(
    out_dir: Path = DEFAULT_OUT,
    cohort_dir: Path = locked.DEFAULT_COHORT_OUT,
    rebuild: bool = False,
) -> dict[str, Any]:
    locked.train_lead = train_candidate
    locked.predict_lead = predict_candidate
    locked.MODEL_ID = MODEL_ID
    manifest = locked.run(out_dir, cohort_dir, rebuild)
    manifest.update(
        {
            "task": "TASK-009-zero-history-state-separation",
            "state": "experiment",
            "model_id": MODEL_ID,
            "single_change": "meaningful-event zero-history state representation",
            "event_model_families_changed": False,
            "event_calibration_changed": False,
            "conditional_models_changed": False,
            "threshold_models_changed": False,
            "task003q_hybrid_policy_changed": False,
            "validation_protocol_changed": False,
            "production_changed": False,
            "origin_safe_inputs": [
                "total_games_as_of_origin",
                "tenure_as_of_origin",
                "draft_type",
                "draft_pick",
            ],
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
