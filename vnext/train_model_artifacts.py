"""Train persisted per-lead vNext artifacts with a selectable artifact module."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_training_metadata(artifact: Any, rows: int) -> dict[str, Any]:
    return {
        "rows": int(rows),
        "max_origin": int(getattr(artifact, "train_max_origin")),
        "n_fit": int(getattr(artifact, "n_fit")),
        "n_cal": int(getattr(artifact, "n_cal")),
        "event_model_class": type(getattr(artifact, "event_model")).__name__,
        "event_calibrator_class": type(getattr(artifact, "event_calibrator")).__name__,
        "games_model_class": type(getattr(artifact, "games_model")).__name__,
        "avg_model_class": type(getattr(artifact, "avg_model")).__name__,
        "threshold_model_classes": {
            str(k): (None if v is None else type(v).__name__)
            for k, v in sorted(getattr(artifact, "threshold_models").items())
        },
        "games_resid_sd": float(getattr(artifact, "games_resid_sd")),
        "avg_resid_sd": float(getattr(artifact, "avg_resid_sd")),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--module", default="model_artifacts")
    ap.add_argument("--target-cutoff", type=int, default=2025)
    args = ap.parse_args()

    module = importlib.import_module(args.module)
    data_path = Path(args.dataset)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dataset = pd.read_csv(data_path)

    manifest: dict[str, Any] = {
        "module": args.module,
        "target_cutoff": int(args.target_cutoff),
        "dataset_path": str(data_path),
        "dataset_sha256": sha256_file(data_path),
        "leads": {},
    }
    for lead in range(1, 6):
        train = dataset[(dataset.origin_year + lead <= args.target_cutoff) & (dataset.origin_year >= 2008)].copy()
        artifact = module.train_lead(train, lead)
        artifact_path = out / f"lead_{lead}.joblib"
        joblib.dump(artifact, artifact_path, compress=3)
        meta = public_training_metadata(artifact, len(train))
        meta["artifact_sha256"] = sha256_file(artifact_path)
        manifest["leads"][str(lead)] = meta

    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    with (out / "training_summary.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["lead", "rows", "max_origin", "n_fit", "n_cal", "event_model_class", "games_model_class", "avg_model_class", "artifact_sha256"],
        )
        writer.writeheader()
        for lead, meta in manifest["leads"].items():
            writer.writerow({"lead": lead, **{k: meta[k] for k in writer.fieldnames if k != "lead"}})
    print(json.dumps({"out": str(out), "module": args.module, "target_cutoff": args.target_cutoff}, indent=2))


if __name__ == "__main__":
    main()
