from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_historical_folds as locked
from model_artifacts_pedigree_fade import predict as predict_candidate
from model_artifacts_pedigree_fade import train_lead as train_candidate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task011-candidate"
MODEL_ID = "vnext_task011_pedigree_fade"


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
            "task": "TASK-011-pedigree-fade",
            "model_id": MODEL_ID,
            "state": "experiment",
            "single_change": "fade draft pick to neutral by 50 observed games and collapse draft type at 50 games",
            "validation_protocol_changed": False,
            "production_changed": False,
            "frozen_claude_changed": False,
        }
    )
    (out_dir / "prediction_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
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
