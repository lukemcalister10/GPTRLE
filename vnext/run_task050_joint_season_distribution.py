from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

import run_historical_folds as locked
from benchmark import PREDICTION_KEY, prediction_keys_from_targets
from model_artifacts_joint_season_distribution import (
    ALL_POOL,
    SAMPLE_COUNT,
    SEED_PREFIX,
    predict as predict_candidate,
    predict_with_diagnostics,
    train_lead as train_candidate,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "task050-joint-season-outcome-distribution"
MODEL_ID = "vnext_task050_joint_season_distribution"


def _artifact_details(out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    manifest_path = out_dir / "fold_artifact_manifest.csv"
    manifest = pd.read_csv(manifest_path)
    details: list[dict[str, Any]] = []
    for index, row in manifest.iterrows():
        artifact = joblib.load(out_dir / str(row.artifact_path))
        short_pool_rows = len(artifact.short_pools[ALL_POOL].games)
        meaningful_pool_rows = len(
            artifact.meaningful_pools[ALL_POOL].games_residuals
        )
        manifest.loc[index, "selected_state_c"] = float(artifact.selected_state_c)
        manifest.loc[index, "selected_short_alpha"] = float(
            artifact.selected_short_alpha
        )
        manifest.loc[index, "selected_meaningful_avg_alpha"] = float(
            artifact.task047_artifact.selected_avg_alpha
        )
        manifest.loc[index, "short_residual_rows"] = int(short_pool_rows)
        manifest.loc[index, "meaningful_residual_rows"] = int(
            meaningful_pool_rows
        )
        details.append(
            {
                "origin_year": int(row.origin_year),
                "lead": int(row.lead),
                "selected_state_c": float(artifact.selected_state_c),
                "state_c_scores_json": json.dumps(
                    {
                        str(key): float(value)
                        for key, value in sorted(artifact.state_c_scores.items())
                    },
                    sort_keys=True,
                ),
                "selected_short_alpha": float(artifact.selected_short_alpha),
                "short_alpha_scores_json": json.dumps(
                    {
                        str(key): float(value)
                        for key, value in sorted(
                            artifact.short_alpha_scores.items()
                        )
                    },
                    sort_keys=True,
                ),
                "selected_meaningful_avg_alpha": float(
                    artifact.task047_artifact.selected_avg_alpha
                ),
                "short_residual_rows": int(short_pool_rows),
                "meaningful_residual_rows": int(meaningful_pool_rows),
                "short_position_pools": "|".join(
                    sorted(key for key in artifact.short_pools if key != ALL_POOL)
                ),
                "meaningful_position_pools": "|".join(
                    sorted(
                        key
                        for key in artifact.meaningful_pools
                        if key != ALL_POOL
                    )
                ),
            }
        )
    manifest.to_csv(manifest_path, index=False, lineterminator="\n")
    detail_frame = pd.DataFrame(details).sort_values(["origin_year", "lead"])
    detail_frame.to_csv(
        out_dir / "fold_model_selection.csv", index=False, lineterminator="\n"
    )
    return manifest, detail_frame


def _write_diagnostics(out_dir: Path, cohort_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    cohorts = locked.load_or_build_cohorts(cohort_dir)
    targets = cohorts["targets"].sort_values(PREDICTION_KEY).reset_index(drop=True)
    keys = prediction_keys_from_targets(targets)
    snapshots = cohorts["included_snapshots"]
    fold_manifest = pd.read_csv(out_dir / "fold_artifact_manifest.csv")
    artifact_paths = {
        (int(row.lead), int(row.origin_year)): out_dir / str(row.artifact_path)
        for row in fold_manifest.itertuples(index=False)
    }

    pieces: list[pd.DataFrame] = []
    for (lead, origin), key_rows in keys.groupby(
        ["lead", "origin_year"], sort=True
    ):
        path = artifact_paths[(int(lead), int(origin))]
        artifact = joblib.load(path)
        joined = key_rows.merge(
            snapshots,
            on=["player_key", "origin_year"],
            how="left",
            validate="many_to_one",
        )
        if joined.isna().any(axis=None):
            bad = joined[joined.isna().any(axis=1)][PREDICTION_KEY].head(5)
            raise ValueError(
                f"TASK-050 diagnostic snapshot join failed: {bad.to_dict('records')}"
            )
        _, diagnostics = predict_with_diagnostics(artifact, joined)
        pieces.append(diagnostics)

    diagnostic_frame = pd.concat(pieces, ignore_index=True).sort_values(
        PREDICTION_KEY
    )
    if len(diagnostic_frame) != 20094:
        raise ValueError(
            f"TASK-050 diagnostic row count changed: {len(diagnostic_frame)}"
        )
    diagnostic_path = out_dir / "branch_diagnostics.csv"
    diagnostic_frame.to_csv(diagnostic_path, index=False, lineterminator="\n")

    aggregate = (
        diagnostic_frame.groupby(["origin_year", "lead"], as_index=False)
        .agg(
            rows=("player_key", "size"),
            state_model_p_zero=("state_model_p_zero", "mean"),
            state_model_p_short=("state_model_p_short", "mean"),
            state_model_p_meaningful=("state_model_p_meaningful", "mean"),
            draw_p_zero=("draw_p_zero", "mean"),
            draw_p_short=("draw_p_short", "mean"),
            draw_p_meaningful=("draw_p_meaningful", "mean"),
            zero_draw_count=("zero_draw_count", "sum"),
            short_draw_count=("short_draw_count", "sum"),
            meaningful_draw_count=("meaningful_draw_count", "sum"),
            min_short_games=("short_games_min", "min"),
            max_short_games=("short_games_max", "max"),
            min_short_points=("short_points_min", "min"),
            min_meaningful_games=("meaningful_games_min", "min"),
            max_meaningful_games=("meaningful_games_max", "max"),
            threshold_monotonic_rows=("threshold_monotonic", "sum"),
        )
        .sort_values(["origin_year", "lead"])
    )
    aggregate.to_csv(
        out_dir / "branch_diagnostics_by_fold_lead.csv",
        index=False,
        lineterminator="\n",
    )
    return diagnostic_frame, aggregate


def run(
    out_dir: Path = DEFAULT_OUT,
    cohort_dir: Path = locked.DEFAULT_COHORT_OUT,
    rebuild: bool = False,
) -> dict[str, Any]:
    if rebuild and out_dir.exists():
        shutil.rmtree(out_dir)

    locked.train_lead = train_candidate
    locked.predict_lead = predict_candidate
    locked.predict_with_quantiles = predict_candidate
    locked.MODEL_ID = MODEL_ID
    locked.SAMPLE_COUNT = SAMPLE_COUNT

    manifest = locked.run(out_dir, cohort_dir, rebuild=False)
    fold_manifest, selection = _artifact_details(out_dir)
    diagnostics, diagnostic_aggregate = _write_diagnostics(out_dir, cohort_dir)

    quantile_method = {
        "method": "joint_three_state_paired_residual_distribution",
        "sample_count": SAMPLE_COUNT,
        "seed": f"sha256({SEED_PREFIX}|player_key|origin_year|lead)",
        "states": [
            "zero games and zero points",
            "one-to-five games with positive points",
            "six-plus games",
        ],
        "components": [
            "fold-local multinomial logistic state probabilities",
            "short-season Ridge log scoring-rate mean with paired empirical games/rate residual draws",
            "TASK-047 conditional games and average means with paired empirical meaningful residual draws",
            "all expected values, quantiles and scoring thresholds derived from the same draws",
        ],
        "row_level_moment_forcing": False,
        "post_hoc_quantile_calibration": False,
        "non_negative": True,
        "non_crossing": True,
    }
    quantile_path = out_dir / "quantile_method.json"
    quantile_path.write_text(
        json.dumps(quantile_method, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    generated = {
        "fold_artifact_manifest.csv": fold_manifest,
        "fold_model_selection.csv": selection,
        "branch_diagnostics.csv": diagnostics,
        "branch_diagnostics_by_fold_lead.csv": diagnostic_aggregate,
    }
    for name, frame in generated.items():
        path = out_dir / name
        manifest["artifacts"][name] = {
            "rows": int(len(frame)),
            "sha256": locked.sha256_path(path),
            "bytes": path.stat().st_size,
        }
        manifest["output_hashes"][name] = locked.sha256_path(path)
    manifest["artifacts"]["quantile_method.json"] = {
        "rows": 1,
        "sha256": locked.sha256_path(quantile_path),
        "bytes": quantile_path.stat().st_size,
    }
    manifest["output_hashes"]["quantile_method.json"] = locked.sha256_path(
        quantile_path
    )
    manifest.update(
        {
            "task": "TASK-050-joint-season-outcome-distribution",
            "model_id": MODEL_ID,
            "state": "experiment",
            "single_hypothesis": "derive all annual forecast outputs from one coherent zero/short/meaningful joint distribution without row-level moment forcing",
            "accepted_baseline": "TASK-047-pooled-ridge-conditional-average",
            "sample_count": SAMPLE_COUNT,
            "seed_contract": f"sha256({SEED_PREFIX}|player_key|origin_year|lead)",
            "quantile_method": quantile_method,
            "validation_protocol_changed": False,
            "partial_season_data_used": False,
            "keeper_utility_changed": False,
            "production_changed": False,
            "frozen_claude_changed": False,
            "reproduction_command": "python vnext/run_task050_joint_season_distribution.py --out build/task050-joint-season-outcome-distribution --rebuild",
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
