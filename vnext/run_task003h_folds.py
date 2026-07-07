"""Run the TASK-003H conditional-calibration candidate on locked folds."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from benchmark import (
    LOCKED_FOLDS,
    PREDICTION_KEY,
    THRESHOLDS,
    VNextAdapter,
    assert_common_keys_and_targets,
    normalise_predictions,
    prediction_keys_from_targets,
)
from build_annual_dataset import build_rows
from build_historical_cohorts import (
    DEFAULT_OUT as DEFAULT_COHORT_OUT,
    align_entries_to_verified_history,
    canonical_players,
)
from historical_eligibility import DraftGuruEligibilityResolver, load_historical_players
from model_artifacts_conditional_calibrated import predict as predict_candidate
from model_artifacts_conditional_calibrated import train_lead as train_candidate
from run_historical_folds import (
    PLAYER_DATA,
    SAMPLE_COUNT,
    add_residual_quantiles,
    load_or_build_cohorts,
    sha256_path,
    write_csv,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task-003h-candidate-folds"
MODEL_ID = "vnext_conditional_calibrated"


def predict_with_quantiles(artifact: Any, rows: pd.DataFrame) -> pd.DataFrame:
    base = predict_candidate(artifact, rows).rename(
        columns={
            f"p{threshold}": f"p_avg_ge_{threshold}"
            for threshold in THRESHOLDS
        }
    )
    return add_residual_quantiles(base, artifact, rows)


def train_artifacts(
    dataset: pd.DataFrame,
    out_dir: Path,
) -> tuple[dict[tuple[int, int], Any], pd.DataFrame, pd.DataFrame]:
    artifacts: dict[tuple[int, int], Any] = {}
    manifest_rows: list[dict[str, Any]] = []
    count_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    artifact_dir = out_dir / "fold_artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    for lead, origins in LOCKED_FOLDS.items():
        for origin in origins:
            train = dataset[
                (dataset.origin_year >= 2008)
                & ((dataset.origin_year + lead) < origin)
            ].copy()
            if train.empty:
                failures.append(
                    {
                        "lead": lead,
                        "origin_year": origin,
                        "reason": "no_legal_training_rows",
                    }
                )
                continue
            if int((train.origin_year + lead).max()) >= origin:
                raise ValueError(
                    f"illegal training cutoffs for lead {lead} origin {origin}"
                )

            artifact = train_candidate(train, lead)
            artifact.artifact_id = f"task003h_lead{lead}_origin{origin}"
            path = artifact_dir / f"lead_{lead}_origin_{origin}.joblib"
            joblib.dump(artifact, path, compress=3)
            artifacts[(lead, origin)] = artifact
            target_max = int(train.origin_year.max() + lead)
            manifest_rows.append(
                {
                    "lead": lead,
                    "origin_year": origin,
                    "artifact_path": str(path.relative_to(out_dir)),
                    "artifact_sha256": sha256_path(path),
                    "train_max_origin": int(train.origin_year.max()),
                    "training_target_max_year": target_max,
                    "allowed_training_origins": "|".join(
                        map(str, sorted(map(int, train.origin_year.unique())))
                    ),
                    "n_fit": int(artifact.n_fit),
                    "n_cal": int(artifact.n_cal),
                    "conditional_calibration_rows": int(
                        artifact.conditional_calibration_rows
                    ),
                    "games_calibration_method": artifact.games_calibration_metadata[
                        "method"
                    ],
                    "avg_calibration_method": artifact.avg_calibration_metadata[
                        "method"
                    ],
                    "games_resid_sd": float(artifact.games_resid_sd),
                    "avg_resid_sd": float(artifact.avg_resid_sd),
                }
            )
            count_rows.append(
                {
                    "lead": lead,
                    "origin_year": origin,
                    "train_rows": int(len(train)),
                    "train_min_origin": int(train.origin_year.min()),
                    "train_max_origin": int(train.origin_year.max()),
                    "training_target_max_year": target_max,
                    "conditional_calibration_rows": int(
                        artifact.conditional_calibration_rows
                    ),
                }
            )

    expected = {
        (lead, origin)
        for lead, origins in LOCKED_FOLDS.items()
        for origin in origins
    }
    missing = sorted(expected - set(artifacts))
    if missing:
        raise ValueError(
            f"missing candidate fold artifact(s): {missing[:5]}; "
            f"failures={failures[:5]}"
        )
    return artifacts, pd.DataFrame(manifest_rows), pd.DataFrame(count_rows)


def run(
    out_dir: Path = DEFAULT_OUT,
    cohort_dir: Path = DEFAULT_COHORT_OUT,
    rebuild: bool = False,
) -> dict[str, Any]:
    if rebuild and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cohorts = load_or_build_cohorts(cohort_dir)
    targets = cohorts["targets"].sort_values(PREDICTION_KEY).reset_index(drop=True)
    if len(targets) != 20_094:
        raise ValueError(
            f"locked cohort row count changed: expected 20094 got {len(targets)}"
        )
    if len(cohorts["included_snapshots"]) != 5_622:
        raise ValueError(
            "included snapshot count changed: "
            f"expected 5622 got {len(cohorts['included_snapshots'])}"
        )

    resolver = DraftGuruEligibilityResolver()
    players = canonical_players(load_historical_players(PLAYER_DATA))
    players, entry_corrections = align_entries_to_verified_history(
        players,
        resolver.evidence_frame(),
    )
    dataset = build_rows(players, min_origin=2008, max_origin=2024)
    if dataset.duplicated(["key", "origin_year"]).any():
        sample = dataset.loc[
            dataset.duplicated(["key", "origin_year"], keep=False),
            ["key", "origin_year"],
        ].head(10).to_dict("records")
        raise ValueError(f"duplicate training key/origin rows: {sample}")

    dataset_path = out_dir / "training_dataset.csv"
    write_csv(dataset_path, dataset)
    artifacts, fold_manifest, fold_counts = train_artifacts(dataset, out_dir)
    adapter = VNextAdapter(
        artifacts=artifacts,
        prediction_function=predict_with_quantiles,
        model_id=MODEL_ID,
        quantile_method=(
            "two_part_exact_mixture_calibrated_conditional_residual_simulation"
        ),
    )
    predictions = adapter.predict(
        cohorts["included_snapshots"],
        prediction_keys_from_targets(targets),
    )
    predictions = normalise_predictions(
        MODEL_ID,
        predictions.drop(columns=["model_id"]),
    )
    assert_common_keys_and_targets({MODEL_ID: predictions}, targets)
    counts = (
        predictions.groupby(["origin_year", "lead"], as_index=False)
        .size()
        .rename(columns={"size": "prediction_rows"})
    )

    artifacts_meta = {
        "candidate_predictions.csv": write_csv(
            out_dir / "candidate_predictions.csv",
            predictions,
        ),
        "fold_artifact_manifest.csv": write_csv(
            out_dir / "fold_artifact_manifest.csv",
            fold_manifest.sort_values(["origin_year", "lead"]),
        ),
        "fold_training_counts.csv": write_csv(
            out_dir / "fold_training_counts.csv",
            fold_counts.sort_values(["origin_year", "lead"]),
        ),
        "fold_failures.csv": write_csv(
            out_dir / "fold_failures.csv",
            pd.DataFrame(columns=["lead", "origin_year", "reason"]),
        ),
        "counts_by_origin_lead.csv": write_csv(
            out_dir / "counts_by_origin_lead.csv",
            counts,
        ),
        "training_entry_corrections.csv": write_csv(
            out_dir / "training_entry_corrections.csv",
            entry_corrections.sort_values("player_key").reset_index(drop=True),
        ),
    }
    quantile_method = {
        "method": (
            "two_part_exact_mixture_calibrated_conditional_residual_simulation"
        ),
        "sample_count": SAMPLE_COUNT,
        "seed": "sha256(TASK-003B|player_key|origin_year|lead)",
        "conditional_means": (
            "temporally held-out isotonic calibration among meaningful rows"
        ),
        "non_negative": True,
        "non_crossing_enforced": True,
    }
    quantile_path = out_dir / "quantile_method.json"
    quantile_path.write_text(
        json.dumps(quantile_method, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    artifacts_meta["quantile_method.json"] = {
        "rows": 1,
        "sha256": sha256_path(quantile_path),
        "bytes": quantile_path.stat().st_size,
    }

    manifest = {
        "task": "TASK-003H-conditional-calibration-fold-predictions",
        "model_id": MODEL_ID,
        "hypothesis": (
            "temporally calibrated conditional games and average reduce "
            "systematic magnitude underprediction"
        ),
        "event_model_changed": False,
        "feature_set_changed": False,
        "validation_protocol_changed": False,
        "prediction_rows": int(len(predictions)),
        "included_snapshot_rows": int(len(cohorts["included_snapshots"])),
        "training_rows": int(len(dataset)),
        "training_unique_keys": int(dataset["key"].nunique()),
        "training_key_origin_unique": True,
        "training_entry_correction_rows": int(len(entry_corrections)),
        "folds": LOCKED_FOLDS,
        "target_failure_rows": 0,
        "quantile_method": quantile_method,
        "input_hashes": {
            "player_data_sha256": sha256_path(PLAYER_DATA),
            "cohort_manifest_sha256": sha256_path(cohort_dir / "manifest.json"),
            "training_dataset_sha256": sha256_path(dataset_path),
        },
        "output_hashes": {
            name: details["sha256"]
            for name, details in artifacts_meta.items()
        },
        "artifacts": artifacts_meta,
        "reproduction_command": (
            "python vnext/run_task003h_folds.py "
            "--out build/task-003h-candidate-folds "
            "--cohort-dir build/task-003-cohorts"
        ),
    }
    (out_dir / "prediction_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cohort-dir", type=Path, default=DEFAULT_COHORT_OUT)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.out, args.cohort_dir, args.rebuild), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
