"""Compare TASK-003H conditional calibration against current fold-specific vNext."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from analyse_task003g_components import add_slice_columns, zero_history_outcome_split
from benchmark import PREDICTION_KEY, THRESHOLDS, assert_common_keys_and_targets
from comparison_diagnostics import (
    fold_differences,
    metrics_by_origin_lead,
    player_block_bootstrap,
    reliability_tables,
    row_losses,
    slice_metrics,
)
from comparison_harness import (
    load_external_predictions,
    score_predictions_stable,
    sha256_file,
    weighted_metric_summary,
    write_csv,
)

CURRENT_MODEL_ID = "vnext_fold_specific"
CANDIDATE_MODEL_ID = "vnext_conditional_calibrated"


def conditional_metrics(
    predictions: pd.DataFrame,
    targets: pd.DataFrame,
) -> pd.DataFrame:
    joined = predictions.merge(
        targets,
        on=PREDICTION_KEY,
        validate="many_to_one",
    )
    active = joined[joined["meaningful"].eq(1)].copy()
    active["absolute_error_cond_games"] = (
        active["cond_games"] - active["games"]
    ).abs()
    active["bias_cond_games"] = active["cond_games"] - active["games"]
    active["absolute_error_cond_avg"] = (
        active["cond_avg"] - active["avg"]
    ).abs()
    active["bias_cond_avg"] = active["cond_avg"] - active["avg"]
    return (
        active.groupby(["model_id", "lead"], as_index=False)
        .agg(
            n=("player_key", "size"),
            mae_cond_games=("absolute_error_cond_games", "mean"),
            bias_cond_games=("bias_cond_games", "mean"),
            mae_cond_avg=("absolute_error_cond_avg", "mean"),
            bias_cond_avg=("bias_cond_avg", "mean"),
            predicted_cond_games=("cond_games", "mean"),
            actual_games=("games", "mean"),
            predicted_cond_avg=("cond_avg", "mean"),
            actual_avg=("avg", "mean"),
        )
        .sort_values(["model_id", "lead"])
        .reset_index(drop=True)
    )


def conditional_reliability(
    predictions: pd.DataFrame,
    targets: pd.DataFrame,
    bins: int = 10,
) -> pd.DataFrame:
    joined = predictions.merge(
        targets,
        on=PREDICTION_KEY,
        validate="many_to_one",
    )
    joined = joined[joined["meaningful"].eq(1)]
    rows: list[dict[str, Any]] = []
    for (model_id, lead), group in joined.groupby(["model_id", "lead"], sort=True):
        for target, prediction in [("games", "cond_games"), ("avg", "cond_avg")]:
            ranked = group[[target, prediction]].copy()
            ranked["bin"] = pd.qcut(
                ranked[prediction],
                q=bins,
                labels=False,
                duplicates="drop",
            )
            for bin_id, bin_rows in ranked.groupby("bin", dropna=False):
                rows.append(
                    {
                        "model_id": str(model_id),
                        "lead": int(lead),
                        "target": target,
                        "bin": int(bin_id) if pd.notna(bin_id) else 0,
                        "n": int(len(bin_rows)),
                        "predicted": float(bin_rows[prediction].mean()),
                        "actual": float(bin_rows[target].mean()),
                    }
                )
    return pd.DataFrame(rows).sort_values(
        ["model_id", "lead", "target", "bin"]
    ).reset_index(drop=True)


def slice_differences(slices: pd.DataFrame) -> pd.DataFrame:
    keys = ["lead", "slice_type", "slice_value"]
    current = slices[slices["model_id"].eq(CURRENT_MODEL_ID)].drop(
        columns=["model_id"]
    )
    candidate = slices[slices["model_id"].eq(CANDIDATE_MODEL_ID)].drop(
        columns=["model_id"]
    )
    merged = candidate.merge(
        current,
        on=keys,
        suffixes=("_candidate", "_current"),
        validate="one_to_one",
    )
    for metric in ["brier_meaningful", "mae_games", "mae_total_points"]:
        merged[f"{metric}_change"] = (
            merged[f"{metric}_candidate"] - merged[f"{metric}_current"]
        )
        merged[f"{metric}_change_pct"] = 100.0 * merged[
            f"{metric}_change"
        ] / merged[f"{metric}_current"]
    return merged.sort_values(
        ["mae_total_points_change_pct", "lead", "slice_type", "slice_value"]
    ).reset_index(drop=True)


def probability_invariance(predictions: pd.DataFrame) -> dict[str, float]:
    current = predictions[predictions["model_id"].eq(CURRENT_MODEL_ID)].drop(
        columns=["model_id"]
    )
    candidate = predictions[predictions["model_id"].eq(CANDIDATE_MODEL_ID)].drop(
        columns=["model_id"]
    )
    paired = candidate.merge(
        current,
        on=PREDICTION_KEY,
        suffixes=("_candidate", "_current"),
        validate="one_to_one",
    )
    columns = ["p_meaningful", *(f"p_avg_ge_{t}" for t in THRESHOLDS)]
    result = {
        column: float(
            np.max(
                np.abs(
                    paired[f"{column}_candidate"]
                    - paired[f"{column}_current"]
                )
            )
        )
        for column in columns
    }
    if any(value > 1e-12 for value in result.values()):
        raise ValueError(f"TASK-003H changed probability outputs: {result}")
    return result


def run(
    out_dir: Path,
    *,
    current_predictions: Path,
    candidate_predictions: Path,
    cohort_dir: Path,
    bootstrap_repetitions: int = 1000,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = pd.read_csv(cohort_dir / "targets.csv")
    snapshots = pd.read_csv(cohort_dir / "included_snapshots.csv")

    current = load_external_predictions(current_predictions, CURRENT_MODEL_ID)
    candidate = load_external_predictions(candidate_predictions, CANDIDATE_MODEL_ID)
    prediction_map = {
        CURRENT_MODEL_ID: current,
        CANDIDATE_MODEL_ID: candidate,
    }
    assert_common_keys_and_targets(prediction_map, targets)
    predictions = (
        pd.concat(prediction_map.values(), ignore_index=True)
        .sort_values(["model_id", *PREDICTION_KEY])
        .reset_index(drop=True)
    )
    invariant = probability_invariance(predictions)

    metrics = score_predictions_stable(predictions, targets)
    summary = weighted_metric_summary(metrics)
    losses = row_losses(predictions, targets)
    origin_lead = metrics_by_origin_lead(losses)
    fold_delta = fold_differences(
        origin_lead,
        baseline_model_id=CURRENT_MODEL_ID,
    )
    bootstrap = player_block_bootstrap(
        losses,
        baseline_model_id=CURRENT_MODEL_ID,
        repetitions=bootstrap_repetitions,
        seed=3008,
    )
    reliability = reliability_tables(predictions, targets)
    slices = slice_metrics(predictions, targets, snapshots, minimum_n=200)
    slice_delta = slice_differences(slices)
    conditional = conditional_metrics(predictions, targets)
    conditional_rel = conditional_reliability(predictions, targets)

    joined = predictions.merge(
        targets,
        on=PREDICTION_KEY,
        validate="many_to_one",
    ).merge(
        snapshots,
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )
    zero_split = zero_history_outcome_split(add_slice_columns(joined))

    artifacts = {
        "predictions.csv": write_csv(out_dir / "predictions.csv", predictions),
        "metrics_by_lead.csv": write_csv(out_dir / "metrics_by_lead.csv", metrics),
        "metrics_summary.csv": write_csv(out_dir / "metrics_summary.csv", summary),
        "metrics_by_origin_lead.csv": write_csv(
            out_dir / "metrics_by_origin_lead.csv", origin_lead
        ),
        "fold_differences_vs_current.csv": write_csv(
            out_dir / "fold_differences_vs_current.csv", fold_delta
        ),
        "player_block_bootstrap.csv": write_csv(
            out_dir / "player_block_bootstrap.csv", bootstrap
        ),
        "reliability.csv": write_csv(out_dir / "reliability.csv", reliability),
        "slice_metrics.csv": write_csv(out_dir / "slice_metrics.csv", slices),
        "slice_differences_vs_current.csv": write_csv(
            out_dir / "slice_differences_vs_current.csv", slice_delta
        ),
        "conditional_metrics.csv": write_csv(
            out_dir / "conditional_metrics.csv", conditional
        ),
        "conditional_reliability.csv": write_csv(
            out_dir / "conditional_reliability.csv", conditional_rel
        ),
        "zero_history_outcome_split.csv": write_csv(
            out_dir / "zero_history_outcome_split.csv", zero_split
        ),
    }

    summary_indexed = summary.set_index("model_id")
    primary = {}
    for metric in ["brier_meaningful", "mae_games", "mae_total_points"]:
        current_value = float(summary_indexed.loc[CURRENT_MODEL_ID, metric])
        candidate_value = float(summary_indexed.loc[CANDIDATE_MODEL_ID, metric])
        primary[metric] = {
            "current": current_value,
            "candidate": candidate_value,
            "change": candidate_value - current_value,
            "change_pct": 100.0 * (candidate_value - current_value) / current_value,
        }
    decision = {
        "task": "TASK-003H-conditional-calibration-comparison",
        "state": "experiment",
        "hypothesis": (
            "conditional temporal calibration reduces magnitude underprediction"
        ),
        "current_model_id": CURRENT_MODEL_ID,
        "candidate_model_id": CANDIDATE_MODEL_ID,
        "rows_per_model": int(len(targets)),
        "probability_outputs_unchanged": True,
        "maximum_probability_differences": invariant,
        "primary_metrics": primary,
        "material_slice_regressions_vs_current": int(
            slice_delta["mae_total_points_change_pct"].gt(3.0).sum()
        ),
        "material_slice_improvements_vs_current": int(
            slice_delta["mae_total_points_change_pct"].lt(-3.0).sum()
        ),
        "bootstrap_repetitions": int(bootstrap_repetitions),
        "production_changed": False,
        "validation_protocol_changed": False,
    }
    decision_path = out_dir / "decision_summary.json"
    decision_path.write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    artifacts["decision_summary.json"] = {
        "rows": 1,
        "bytes": int(decision_path.stat().st_size),
        "sha256": sha256_file(decision_path),
    }

    report_lines = [
        "# TASK-003H conditional magnitude calibration",
        "",
        f"- Rows per model: **{len(targets):,}**",
        "- Meaningful-season and threshold probabilities unchanged: **yes**",
        f"- Material slice regressions versus current: **{decision['material_slice_regressions_vs_current']}**",
        f"- Material slice improvements versus current: **{decision['material_slice_improvements_vs_current']}**",
        "",
        "Full metrics, fold differences, bootstrap intervals, conditional calibration tables and zero-history splits are included in this artifact.",
    ]
    report_path = out_dir / "comparison_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    artifacts["comparison_report.md"] = {
        "rows": len(report_lines),
        "bytes": int(report_path.stat().st_size),
        "sha256": sha256_file(report_path),
    }

    manifest = {
        **decision,
        "input_files": {
            "current_predictions": {
                "path": str(current_predictions),
                "sha256": sha256_file(current_predictions),
            },
            "candidate_predictions": {
                "path": str(candidate_predictions),
                "sha256": sha256_file(candidate_predictions),
            },
            "cohort_manifest": {
                "path": str(cohort_dir / "manifest.json"),
                "sha256": sha256_file(cohort_dir / "manifest.json"),
            },
        },
        "artifacts": artifacts,
        "reproduction_command": (
            "python vnext/run_task003h_comparison.py "
            "--current-predictions build/task-003h-current/vnext_predictions.csv "
            "--candidate-predictions build/task-003h-candidate/candidate_predictions.csv "
            "--cohort-dir build/task-003h-cohorts "
            "--out build/task-003h-comparison"
        ),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--current-predictions", type=Path, required=True)
    parser.add_argument("--candidate-predictions", type=Path, required=True)
    parser.add_argument("--cohort-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=1000)
    args = parser.parse_args()
    manifest = run(
        args.out,
        current_predictions=args.current_predictions,
        candidate_predictions=args.candidate_predictions,
        cohort_dir=args.cohort_dir,
        bootstrap_repetitions=args.bootstrap_repetitions,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
