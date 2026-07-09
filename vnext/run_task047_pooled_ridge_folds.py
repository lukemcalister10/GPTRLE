from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

import run_historical_folds as locked
from model_artifacts_pooled_ridge_conditional_average import predict as predict_candidate
from model_artifacts_pooled_ridge_conditional_average import train_lead as train_candidate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task047-pooled-ridge-conditional-average"
MODEL_ID = "vnext_task047_pooled_ridge_conditional_average"


def _append_selected_alphas(out_dir: Path) -> list[dict[str, Any]]:
    manifest_path = out_dir / "fold_artifact_manifest.csv"
    manifest = pd.read_csv(manifest_path)
    alpha_rows: list[dict[str, Any]] = []
    selected = []
    for _, row in manifest.iterrows():
        artifact = joblib.load(out_dir / str(row.artifact_path))
        alpha = float(getattr(artifact, "selected_avg_alpha"))
        scores = getattr(artifact, "avg_alpha_scores", {})
        selected.append(alpha)
        alpha_rows.append(
            {
                "lead": int(row.lead),
                "origin_year": int(row.origin_year),
                "selected_alpha": alpha,
                "alpha_scores_json": json.dumps(
                    {str(k): float(v) for k, v in sorted(scores.items())},
                    sort_keys=True,
                ),
            }
        )
    manifest["selected_avg_alpha"] = selected
    manifest.to_csv(manifest_path, index=False, lineterminator="\n")
    alpha_path = out_dir / "selected_ridge_alpha_by_fold_lead.csv"
    pd.DataFrame(alpha_rows).sort_values(["origin_year", "lead"]).to_csv(
        alpha_path,
        index=False,
        lineterminator="\n",
    )
    return alpha_rows


def run(
    out_dir: Path = DEFAULT_OUT,
    cohort_dir: Path = locked.DEFAULT_COHORT_OUT,
    rebuild: bool = False,
) -> dict[str, Any]:
    locked.train_lead = train_candidate
    locked.predict_lead = predict_candidate
    locked.MODEL_ID = MODEL_ID
    manifest = locked.run(out_dir, cohort_dir, rebuild)
    alpha_rows = _append_selected_alphas(out_dir)
    manifest.update(
        {
            "task": "TASK-047-pooled-ridge-conditional-average",
            "model_id": MODEL_ID,
            "state": "candidate",
            "single_change": "replace TASK-012 pooled conditional-average SGDRegressor with pooled Ridge tuned on the fold-local temporal calibration split",
            "accepted_baseline": "TASK-012-established-ceiling",
            "ridge_alpha_grid": [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0],
            "selected_ridge_alpha_by_fold_lead": alpha_rows,
            "validation_protocol_changed": False,
            "production_changed": False,
            "frozen_claude_changed": False,
        }
    )
    manifest["artifacts"]["selected_ridge_alpha_by_fold_lead.csv"] = {
        "rows": len(alpha_rows),
        "sha256": locked.sha256_path(out_dir / "selected_ridge_alpha_by_fold_lead.csv"),
        "bytes": (out_dir / "selected_ridge_alpha_by_fold_lead.csv").stat().st_size,
    }
    fold_manifest_path = out_dir / "fold_artifact_manifest.csv"
    alpha_path = out_dir / "selected_ridge_alpha_by_fold_lead.csv"
    manifest["artifacts"]["fold_artifact_manifest.csv"] = {
        "rows": int(len(alpha_rows)),
        "sha256": locked.sha256_path(fold_manifest_path),
        "bytes": fold_manifest_path.stat().st_size,
    }
    manifest["output_hashes"]["fold_artifact_manifest.csv"] = locked.sha256_path(fold_manifest_path)
    manifest["output_hashes"]["selected_ridge_alpha_by_fold_lead.csv"] = locked.sha256_path(alpha_path)
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
    print(json.dumps(run(args.out, args.cohort_dir, args.rebuild), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
