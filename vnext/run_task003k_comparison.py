"""Compare TASK-003K event logistic with unchanged fold-specific vNext."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

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

ROOT = Path(__file__).resolve().parents[1]
CURRENT = "vnext_fold_specific"
CANDIDATE = "vnext_event_logistic"
KEYS = ["player_key", "origin_year", "lead"]
LOCKED_REGRESSIONS = (
    ROOT
    / "reports"
    / "task-003h-conditional-calibration"
    / "original_15_slice_results.csv"
)


def safe_auc(y: pd.Series, p: pd.Series) -> float:
    return float(roc_auc_score(y, p)) if y.nunique() > 1 else float("nan")


def event_metrics(group: pd.DataFrame, column: str) -> dict[str, float]:
    y = group["meaningful"].astype(int)
    p = group[column].astype(float).clip(0.001, 0.999)
    return {
        f"{column}_mean": float(p.mean()),
        f"{column}_bias": float(p.mean() - y.mean()),
        f"{column}_brier": float(brier_score_loss(y, p)),
        f"{column}_log_loss": float(log_loss(y, p, labels=[0, 1])),
        f"{column}_auc": safe_auc(y, p),
    }


def raw_event_rows(
    predictions: pd.DataFrame,
    targets: pd.DataFrame,
    snapshots: pd.DataFrame,
    fold_dirs: dict[str, Path],
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for model_id, fold_dir in fold_dirs.items():
        joined = predictions[predictions["model_id"].eq(model_id)].merge(
            targets,
            on=KEYS,
            validate="one_to_one",
        ).merge(
            snapshots,
            on=["player_key", "origin_year"],
            validate="many_to_one",
        )
        for (lead, origin), group in joined.groupby(
            ["lead", "origin_year"], sort=True
        ):
            path = (
                fold_dir
                / "fold_artifacts"
                / f"lead_{int(lead)}_origin_{int(origin)}.joblib"
            )
            if not path.exists():
                raise FileNotFoundError(f"missing fold artifact: {path}")
            artifact: Any = joblib.load(path)
            transformed = artifact.preprocessor.transform(group)
            raw = artifact.event_model.predict_proba(transformed)[:, 1]
            calibrated = artifact.event_calibrator.predict(raw)
            delta = np.max(
                np.abs(
                    np.clip(calibrated, 0.001, 0.999)
                    - group["p_meaningful"].to_numpy(float)
                )
            )
            if delta > 1e-9:
                raise ValueError(
                    f"{model_id} recomputed probability mismatch at "
                    f"lead {lead} origin {origin}: {delta}"
                )
            part = group.copy()
            part["p_meaningful_raw"] = np.clip(raw, 0.001, 0.999)
            parts.append(part)
    return add_slice_columns(pd.concat(parts, ignore_index=True))


def summarize_event(rows: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for keys, group in rows.groupby(groups, observed=True, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        record = dict(zip(groups, keys, strict=True))
        record.update(
            n=int(len(group)),
            actual_meaningful_rate=float(group["meaningful"].mean()),
            **event_metrics(group, "p_meaningful_raw"),
            **event_metrics(group, "p_meaningful"),
        )
        records.append(record)
    return pd.DataFrame(records)


def raw_reliability(rows: pd.DataFrame, bins: int = 10) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for (model_id, lead), group in rows.groupby(["model_id", "lead"], sort=True):
        for stage, column in [
            ("raw", "p_meaningful_raw"),
            ("calibrated", "p_meaningful"),
        ]:
            ranked = group[[column, "meaningful"]].copy()
            ranked["bin"] = pd.qcut(
                ranked[column], bins, labels=False, duplicates="drop"
            )
            for bin_id, part in ranked.groupby("bin", dropna=False):
                records.append(
                    {
                        "model_id": model_id,
                        "lead": int(lead),
                        "stage": stage,
                        "bin": int(bin_id) if pd.notna(bin_id) else 0,
                        "n": int(len(part)),
                        "predicted": float(part[column].mean()),
                        "actual": float(part["meaningful"].mean()),
                    }
                )
    return pd.DataFrame(records)


def invariant_components(predictions: pd.DataFrame) -> dict[str, float]:
    current = predictions[predictions["model_id"].eq(CURRENT)].drop(
        columns=["model_id"]
    )
    candidate = predictions[predictions["model_id"].eq(CANDIDATE)].drop(
        columns=["model_id"]
    )
    paired = candidate.merge(
        current,
        on=KEYS,
        suffixes=("_candidate", "_current"),
        validate="one_to_one",
    )
    columns = [
        "cond_games",
        "cond_avg",
        *(f"p_avg_ge_{threshold}" for threshold in THRESHOLDS),
    ]
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
        raise ValueError(f"TASK-003K changed an undeclared component: {result}")
    return result


def slice_differences(slices: pd.DataFrame) -> pd.DataFrame:
    keys = ["lead", "slice_type", "slice_value"]
    current = slices[slices["model_id"].eq(CURRENT)].drop(columns=["model_id"])
    candidate = slices[slices["model_id"].eq(CANDIDATE)].drop(
        columns=["model_id"]
    )
    paired = candidate.merge(
        current,
        on=keys,
        suffixes=("_candidate", "_current"),
        validate="one_to_one",
    )
    for metric in ["brier_meaningful", "mae_games", "mae_total_points"]:
        paired[f"{metric}_change"] = (
            paired[f"{metric}_candidate"] - paired[f"{metric}_current"]
        )
        paired[f"{metric}_change_pct"] = (
            100.0
            * paired[f"{metric}_change"]
            / paired[f"{metric}_current"]
        )
    return paired.sort_values(
        ["mae_total_points_change_pct", *keys]
    ).reset_index(drop=True)


def locked_slice_results(slice_delta: pd.DataFrame) -> pd.DataFrame:
    locked = pd.read_csv(LOCKED_REGRESSIONS)[
        ["lead", "slice_type", "slice_value"]
    ].drop_duplicates()
    return locked.merge(
        slice_delta,
        on=["lead", "slice_type", "slice_value"],
        how="left",
        validate="one_to_one",
    )


def run(
    out_dir: Path,
    *,
    current_predictions: Path,
    candidate_predictions: Path,
    current_folds: Path,
    candidate_folds: Path,
    cohort_dir: Path,
    bootstrap_repetitions: int = 1000,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = pd.read_csv(cohort_dir / "targets.csv")
    snapshots = pd.read_csv(cohort_dir / "included_snapshots.csv")
    current = load_external_predictions(current_predictions, CURRENT)
    candidate = load_external_predictions(candidate_predictions, CANDIDATE)
    prediction_map = {CURRENT: current, CANDIDATE: candidate}
    assert_common_keys_and_targets(prediction_map, targets)
    predictions = pd.concat(prediction_map.values(), ignore_index=True)
    invariants = invariant_components(predictions)

    metrics = score_predictions_stable(predictions, targets)
    summary = weighted_metric_summary(metrics)
    losses = row_losses(predictions, targets)
    origin_lead = metrics_by_origin_lead(losses)
    fold_delta = fold_differences(origin_lead, baseline_model_id=CURRENT)
    bootstrap = player_block_bootstrap(
        losses,
        baseline_model_id=CURRENT,
        repetitions=bootstrap_repetitions,
        seed=3011,
    )
    reliability = reliability_tables(predictions, targets)
    slices = slice_metrics(predictions, targets, snapshots, minimum_n=200)
    slice_delta = slice_differences(slices)
    locked_slices = locked_slice_results(slice_delta)
    joined = predictions.merge(targets, on=KEYS, validate="many_to_one").merge(
        snapshots,
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )
    zero_split = zero_history_outcome_split(add_slice_columns(joined))

    raw_rows = raw_event_rows(
        predictions,
        targets,
        snapshots,
        {CURRENT: current_folds, CANDIDATE: candidate_folds},
    )
    event_summary = summarize_event(raw_rows, ["model_id"])
    event_by_lead = summarize_event(raw_rows, ["model_id", "lead"])
    event_by_fold = summarize_event(
        raw_rows, ["model_id", "origin_year", "lead"]
    )
    event_rel = raw_reliability(raw_rows)

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
        "locked_15_slice_results.csv": write_csv(
            out_dir / "locked_15_slice_results.csv", locked_slices
        ),
        "zero_history_outcome_split.csv": write_csv(
            out_dir / "zero_history_outcome_split.csv", zero_split
        ),
        "event_summary.csv": write_csv(
            out_dir / "event_summary.csv", event_summary
        ),
        "event_by_lead.csv": write_csv(
            out_dir / "event_by_lead.csv", event_by_lead
        ),
        "event_by_fold.csv": write_csv(
            out_dir / "event_by_fold.csv", event_by_fold
        ),
        "event_raw_calibrated_reliability.csv": write_csv(
            out_dir / "event_raw_calibrated_reliability.csv", event_rel
        ),
    }

    indexed = summary.set_index("model_id")
    event_indexed = event_summary.set_index("model_id")
    primary: dict[str, Any] = {}
    for metric in ["brier_meaningful", "mae_games", "mae_total_points"]:
        old = float(indexed.loc[CURRENT, metric])
        new = float(indexed.loc[CANDIDATE, metric])
        primary[metric] = {
            "current": old,
            "candidate": new,
            "change": new - old,
            "change_pct": 100.0 * (new - old) / old,
        }
    raw_log_old = float(event_indexed.loc[CURRENT, "p_meaningful_raw_log_loss"])
    raw_log_new = float(event_indexed.loc[CANDIDATE, "p_meaningful_raw_log_loss"])
    cal_log_old = float(event_indexed.loc[CURRENT, "p_meaningful_log_loss"])
    cal_log_new = float(event_indexed.loc[CANDIDATE, "p_meaningful_log_loss"])
    decision = {
        "task": "TASK-003K-event-logistic-comparison",
        "state": "experiment",
        "rows_per_model": int(len(targets)),
        "folds": 25,
        "single_change_verified": True,
        "maximum_undeclared_component_differences": invariants,
        "primary_metrics": primary,
        "raw_event_log_loss_change": raw_log_new - raw_log_old,
        "calibrated_event_log_loss_change": cal_log_new - cal_log_old,
        "material_slice_regressions_vs_current": int(
            slice_delta["mae_total_points_change_pct"].gt(3.0).sum()
        ),
        "material_slice_improvements_vs_current": int(
            slice_delta["mae_total_points_change_pct"].lt(-3.0).sum()
        ),
        "historical_rule_checks": {
            "brier_improves": primary["brier_meaningful"]["change"] < 0,
            "calibrated_log_loss_improves": cal_log_new < cal_log_old,
            "games_mae_not_worse_by_more_than_1pct": (
                primary["mae_games"]["change_pct"] <= 1.0
            ),
            "points_mae_not_worse_by_more_than_1pct": (
                primary["mae_total_points"]["change_pct"] <= 1.0
            ),
        },
        "current_board_review": "pending",
        "production_changed": False,
        "validation_protocol_changed": False,
        "bootstrap_repetitions": int(bootstrap_repetitions),
    }
    decision_path = out_dir / "decision_summary.json"
    decision_path.write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    artifacts["decision_summary.json"] = {
        "rows": 1,
        "bytes": decision_path.stat().st_size,
        "sha256": sha256_file(decision_path),
    }
    manifest = {
        **decision,
        "inputs": {
            "current_predictions_sha256": sha256_file(current_predictions),
            "candidate_predictions_sha256": sha256_file(candidate_predictions),
            "cohort_manifest_sha256": sha256_file(cohort_dir / "manifest.json"),
        },
        "artifacts": artifacts,
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
    parser.add_argument("--current-folds", type=Path, required=True)
    parser.add_argument("--candidate-folds", type=Path, required=True)
    parser.add_argument("--cohort-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=1000)
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.out,
                current_predictions=args.current_predictions,
                candidate_predictions=args.candidate_predictions,
                current_folds=args.current_folds,
                candidate_folds=args.candidate_folds,
                cohort_dir=args.cohort_dir,
                bootstrap_repetitions=args.bootstrap_repetitions,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
