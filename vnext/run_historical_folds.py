"""Run fold-specific vNext predictions for locked TASK-003 historical cohorts."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark import (
    LOCKED_FOLDS,
    PREDICTION_KEY,
    QUANTILE_COLUMNS,
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
    build_locked_cohorts,
    canonical_players,
)
from historical_eligibility import DraftGuruEligibilityResolver, load_historical_players
from model_artifacts import predict as predict_lead
from model_artifacts import train_lead

DEFAULT_OUT = ROOT / "build" / "task-003b-vnext-folds"
PLAYER_DATA = ROOT / "engine" / "rl_after" / "rl_model_data.json"
SAMPLE_COUNT = 512
MODEL_ID = "vnext_fold_specific"
QUANTILE_LEVELS = np.array([0.10, 0.25, 0.50, 0.75, 0.90, 0.97])


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {
        "rows": int(len(frame)),
        "sha256": sha256_path(path),
        "bytes": path.stat().st_size,
    }


def seed_for(player_key: str, origin_year: int, lead: int) -> int:
    digest = hashlib.sha256(
        f"TASK-003B|{player_key}|{origin_year}|{lead}".encode()
    ).digest()
    return int.from_bytes(digest[:8], "little") & 0xFFFFFFFF


def add_residual_quantiles(
    pred: pd.DataFrame,
    artifact: Any,
    rows: pd.DataFrame,
    sample_count: int = SAMPLE_COUNT,
) -> pd.DataFrame:
    """Add deterministic unconditional point quantiles.

    The zero mass is handled analytically from ``p_meaningful``. Only the
    conditional points distribution is simulated, avoiding Bernoulli sampling
    noise that can otherwise collapse all reported quantiles to zero.
    """

    out = pred.copy()
    qvalues = {column: [] for column in QUANTILE_COLUMNS}
    games_sd = float(getattr(artifact, "games_resid_sd", 3.0))
    avg_sd = float(getattr(artifact, "avg_resid_sd", 12.0))

    for index, row in out.iterrows():
        key_row = rows.loc[index]
        rng = np.random.default_rng(
            seed_for(
                str(key_row.player_key),
                int(key_row.origin_year),
                int(key_row.lead),
            )
        )
        games = np.clip(
            rng.normal(float(row.cond_games), games_sd, sample_count),
            6.0,
            23.0,
        )
        average = np.clip(
            rng.normal(float(row.cond_avg), avg_sd, sample_count),
            1e-6,
            145.0,
        )
        conditional_points = games * average
        probability = float(row.p_meaningful)
        zero_mass = 1.0 - probability
        values = []
        for level in QUANTILE_LEVELS:
            if level <= zero_mass or probability <= 0.0:
                values.append(0.0)
            else:
                conditional_level = np.clip(
                    (level - zero_mass) / probability,
                    0.0,
                    1.0,
                )
                values.append(
                    float(np.quantile(conditional_points, conditional_level))
                )
        values = np.maximum.accumulate(values)

        if (
            np.ptp(values) <= 1e-12
            and float(row.exp_points) > 0.0
            and probability > 1.0 - float(QUANTILE_LEVELS[-1])
        ):
            raise ValueError(
                "non-degenerate forecast produced a collapsed point-quantile vector"
            )
        for column, value in zip(QUANTILE_COLUMNS, values, strict=True):
            qvalues[column].append(float(value))

    for column, values in qvalues.items():
        out[column] = values
    return out


def predict_with_quantiles(artifact: Any, rows: pd.DataFrame) -> pd.DataFrame:
    base = predict_lead(artifact, rows).rename(
        columns={
            f"p{threshold}": f"p_avg_ge_{threshold}"
            for threshold in THRESHOLDS
        }
    )
    return add_residual_quantiles(base, artifact, rows)


def load_or_build_cohorts(cohort_dir: Path) -> dict[str, pd.DataFrame]:
    if not (cohort_dir / "manifest.json").exists():
        build_locked_cohorts(cohort_dir)
    names = [
        "fold_plan",
        "included_snapshots",
        "cohort_membership",
        "targets",
        "excluded",
        "target_failures",
    ]
    cohorts = {
        name: pd.read_csv(cohort_dir / f"{name}.csv")
        for name in names
    }
    if len(cohorts["target_failures"]):
        raise ValueError("target-data failures must remain zero")
    return cohorts


def train_artifacts(
    dataset: pd.DataFrame,
    out_dir: Path,
) -> tuple[dict[tuple[int, int], Any], pd.DataFrame, pd.DataFrame]:
    artifacts: dict[tuple[int, int], Any] = {}
    manifest_rows = []
    count_rows = []
    failures = []
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
            artifact = train_lead(train, lead)
            artifact.artifact_id = f"vnext_lead{lead}_origin{origin}"
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
                    "games_resid_sd": float(artifact.games_resid_sd),
                    "avg_resid_sd": float(artifact.avg_resid_sd),
                }
            )
            count_rows.append(
                {
                    "lead": lead,
                    "origin_year": origin,
                    "train_rows": len(train),
                    "train_min_origin": int(train.origin_year.min()),
                    "train_max_origin": int(train.origin_year.max()),
                    "training_target_max_year": target_max,
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
            f"missing fold artifact(s): {missing[:5]}; failures={failures[:5]}"
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
    if len(targets) != 20094:
        raise ValueError(
            f"locked cohort row count changed: expected 20094 got {len(targets)}"
        )
    if len(cohorts["included_snapshots"]) != 5622:
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
        quantile_method="two_part_exact_mixture_residual_simulation",
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
        "vnext_predictions.csv": write_csv(
            out_dir / "vnext_predictions.csv", predictions
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
            out_dir / "counts_by_origin_lead.csv", counts
        ),
        "training_entry_corrections.csv": write_csv(
            out_dir / "training_entry_corrections.csv",
            entry_corrections.sort_values("player_key").reset_index(drop=True),
        ),
    }
    quantile_method = {
        "method": "two_part_exact_mixture_residual_simulation",
        "sample_count": SAMPLE_COUNT,
        "seed": "sha256(TASK-003B|player_key|origin_year|lead)",
        "components": [
            "p_meaningful exact zero-mass quantile inversion",
            "conditional meaningful games normal residual scale clipped to 6-23",
            "conditional meaningful average normal residual scale clipped positive",
        ],
        "non_negative": True,
        "non_crossing_enforced": True,
        "all_zero_quantiles_allowed_only_when": (
            "p_meaningful <= 0.03 or exp_points == 0"
        ),
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
        "task": "TASK-003B-vNext-fold-predictions",
        "model_id": MODEL_ID,
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
            "python vnext/run_historical_folds.py "
            "--out build/task-003b-vnext-folds"
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
    print(
        json.dumps(
            run(args.out, args.cohort_dir, args.rebuild),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
