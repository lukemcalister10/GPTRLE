"""Diagnose conditional-regressor training support for TASK-003J.

Diagnostic only: this script reads fold artifacts, training rows and benchmark
rows, then compares raw and transformed feature support for the conditional
games and conditional-average regressors. It does not fit or mutate models.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

import joblib
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from evaluate_v3_fast import CAT, NUM
from model_artifacts import split_temporal

KEYS = ["player_key", "origin_year", "lead"]
COHORTS: dict[str, Callable[[pd.DataFrame], pd.Series]] = {
    "zero_prior_games": lambda d: d["total_games"].eq(0),
    "ruck": lambda d: d["position"].astype(str).eq("RUC"),
    "age_21_23": lambda d: d["age"].between(21, 23, inclusive="both"),
    "age_24_26": lambda d: d["age"].between(24, 26, inclusive="both"),
    "age_27_29": lambda d: d["age"].between(27, 29, inclusive="both"),
    "tenure_4_5": lambda d: d["tenure"].between(4, 5, inclusive="both"),
    "pick_61_undrafted": lambda d: pd.to_numeric(
        d["pick"], errors="coerce"
    ).fillna(999).gt(60),
}


def _artifact_path(fold_dir: Path, lead: int, origin: int) -> Path:
    manifest = fold_dir / "fold_artifact_manifest.csv"
    if manifest.exists():
        rows = pd.read_csv(manifest)
        row = rows[rows["lead"].eq(lead) & rows["origin_year"].eq(origin)]
        if not row.empty and "artifact_path" in row.columns:
            return fold_dir / str(row.iloc[0]["artifact_path"])
    return fold_dir / "fold_artifacts" / f"lead_{lead}_origin_{origin}.joblib"


def load_benchmark_rows(comparison_dir: Path) -> pd.DataFrame:
    predictions = pd.read_csv(comparison_dir / "predictions.csv")
    predictions = predictions[
        predictions["model_id"].eq("vnext_fold_specific")
    ].copy()
    targets = pd.read_csv(comparison_dir / "cohorts" / "targets.csv")
    snapshots = pd.read_csv(
        comparison_dir / "cohorts" / "included_snapshots.csv"
    )
    return predictions.merge(targets, on=KEYS, validate="one_to_one").merge(
        snapshots,
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )


def raw_feature_summary(
    reference: pd.DataFrame,
    probe: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for column in NUM:
        ref = pd.to_numeric(reference[column], errors="coerce")
        value = pd.to_numeric(probe[column], errors="coerce")
        q01 = float(ref.quantile(0.01)) if ref.notna().any() else np.nan
        q99 = float(ref.quantile(0.99)) if ref.notna().any() else np.nan
        lower = float(ref.min()) if ref.notna().any() else np.nan
        upper = float(ref.max()) if ref.notna().any() else np.nan
        records.append(
            {
                "feature": column,
                "reference_missing_rate": float(ref.isna().mean()),
                "probe_missing_rate": float(value.isna().mean()),
                "reference_min": lower,
                "reference_p01": q01,
                "reference_median": (
                    float(ref.median()) if ref.notna().any() else np.nan
                ),
                "reference_p99": q99,
                "reference_max": upper,
                "probe_min": (
                    float(value.min()) if value.notna().any() else np.nan
                ),
                "probe_median": (
                    float(value.median()) if value.notna().any() else np.nan
                ),
                "probe_max": (
                    float(value.max()) if value.notna().any() else np.nan
                ),
                "probe_below_reference_min": (
                    int((value < lower).sum()) if np.isfinite(lower) else 0
                ),
                "probe_above_reference_max": (
                    int((value > upper).sum()) if np.isfinite(upper) else 0
                ),
                "probe_outside_reference_1_99_pct": (
                    int(((value < q01) | (value > q99)).sum())
                    if np.isfinite(q01) and np.isfinite(q99)
                    else 0
                ),
            }
        )
    for column in CAT:
        seen = set(reference[column].dropna().astype(str))
        values = probe[column].dropna().astype(str)
        unseen = sorted(set(values) - seen)
        records.append(
            {
                "feature": column,
                "reference_missing_rate": float(
                    reference[column].isna().mean()
                ),
                "probe_missing_rate": float(probe[column].isna().mean()),
                "unseen_categories": "|".join(unseen),
                "probe_unseen_category_rows": int(values.isin(unseen).sum()),
            }
        )
    return pd.DataFrame(records)


def _dense(values: Any) -> np.ndarray:
    return (
        values.toarray()
        if hasattr(values, "toarray")
        else np.asarray(values)
    )


def transformed_summary(
    artifact: Any,
    reference: pd.DataFrame,
    probe: pd.DataFrame,
) -> dict[str, float]:
    if reference.empty or probe.empty:
        return {
            "n_reference": int(len(reference)),
            "n_probe": int(len(probe)),
        }
    reference_values = _dense(
        artifact.preprocessor.transform(reference)
    ).astype(float)
    probe_values = _dense(artifact.preprocessor.transform(probe)).astype(float)
    distances = cKDTree(reference_values).query(
        probe_values,
        k=1,
        workers=1,
    )[0]
    reference_norm = np.linalg.norm(reference_values, axis=1)
    probe_norm = np.linalg.norm(probe_values, axis=1)
    reference_norm_p99 = float(np.quantile(reference_norm, 0.99))
    return {
        "n_reference": int(len(reference)),
        "n_probe": int(len(probe)),
        "nearest_train_distance_median": float(np.median(distances)),
        "nearest_train_distance_p90": float(np.quantile(distances, 0.90)),
        "nearest_train_distance_p99": float(np.quantile(distances, 0.99)),
        "reference_transformed_norm_p99": reference_norm_p99,
        "probe_transformed_norm_p99": float(np.quantile(probe_norm, 0.99)),
        "probe_norm_above_reference_p99_rows": int(
            (probe_norm > reference_norm_p99).sum()
        ),
        "probe_norm_above_reference_p99_share": float(
            np.mean(probe_norm > reference_norm_p99)
        ),
    }


def analyse_fold(
    dataset: pd.DataFrame,
    benchmark: pd.DataFrame,
    fold_dir: Path,
    lead: int,
    origin: int,
) -> tuple[list[dict[str, Any]], list[pd.DataFrame]]:
    artifact = joblib.load(_artifact_path(fold_dir, lead, origin))
    train = dataset[
        (dataset.origin_year >= 2008)
        & ((dataset.origin_year + lead) < origin)
    ].copy()
    fit, calibration = split_temporal(train, lead)
    fit_active = fit[fit[f"l{lead}_meaningful"].astype(int).eq(1)].copy()
    calibration_active = calibration[
        calibration[f"l{lead}_meaningful"].astype(int).eq(1)
    ].copy()
    fold_rows = benchmark[
        benchmark["lead"].eq(lead)
        & benchmark["origin_year"].eq(origin)
    ].copy()

    summaries: list[dict[str, Any]] = []
    raw_tables: list[pd.DataFrame] = []
    for cohort, masker in COHORTS.items():
        probe = fold_rows[masker(fold_rows)].copy()
        for reference_name, reference in [
            ("meaningful_fit_rows", fit_active),
            ("temporal_calibration_rows", calibration_active),
        ]:
            row: dict[str, Any] = {
                "lead": lead,
                "origin_year": origin,
                "cohort": cohort,
                "reference": reference_name,
            }
            row.update(transformed_summary(artifact, reference, probe))
            summaries.append(row)
            raw = raw_feature_summary(reference, probe)
            raw.insert(0, "reference", reference_name)
            raw.insert(0, "cohort", cohort)
            raw.insert(0, "origin_year", origin)
            raw.insert(0, "lead", lead)
            raw_tables.append(raw)
    return summaries, raw_tables


def aggregate_support(summary: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "nearest_train_distance_median",
        "nearest_train_distance_p90",
        "nearest_train_distance_p99",
        "probe_norm_above_reference_p99_share",
    ]
    records: list[dict[str, Any]] = []
    for (cohort, reference), group in summary.groupby(
        ["cohort", "reference"], sort=True
    ):
        weights = group["n_probe"].to_numpy(float)
        record: dict[str, Any] = {
            "cohort": cohort,
            "reference": reference,
            "fold_rows": int(len(group)),
            "probe_rows_sum": int(weights.sum()),
        }
        for metric in metrics:
            record[metric] = float(
                np.average(group[metric].to_numpy(float), weights=weights)
            )
        records.append(record)
    return pd.DataFrame(records).sort_values(
        ["reference", "nearest_train_distance_p90"],
        ascending=[True, False],
    )


def write_markdown(
    output: Path,
    aggregate: pd.DataFrame,
) -> None:
    fit = aggregate[
        aggregate["reference"].eq("meaningful_fit_rows")
    ].sort_values("nearest_train_distance_p90", ascending=False)
    lines = [
        "# TASK-003J conditional-regressor support diagnosis",
        "",
        "Diagnostic only. No model, protocol, production, value, keeper utility or UI changes.",
        "",
        "## Aggregate transformed support",
        "",
        fit.to_markdown(index=False),
        "",
        "Nearest-neighbour distance and norm exceedance identify support risk, not causal model improvement. Raw-feature and fold-level tables must be reviewed before proposing a model change.",
        "",
    ]
    output.joinpath("support_diagnosis.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fold-dir", type=Path, required=True)
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    dataset = pd.read_csv(args.fold_dir / "training_dataset.csv")
    benchmark = load_benchmark_rows(args.comparison_dir)
    fold_pairs = (
        benchmark[["lead", "origin_year"]]
        .drop_duplicates()
        .sort_values(["lead", "origin_year"])
    )
    summaries: list[dict[str, Any]] = []
    raw_tables: list[pd.DataFrame] = []
    for lead, origin in fold_pairs.itertuples(index=False, name=None):
        fold_summary, fold_raw = analyse_fold(
            dataset,
            benchmark,
            args.fold_dir,
            int(lead),
            int(origin),
        )
        summaries.extend(fold_summary)
        raw_tables.extend(fold_raw)

    args.out.mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(summaries)
    raw = pd.concat(raw_tables, ignore_index=True)
    aggregate = aggregate_support(summary)
    summary.to_csv(args.out / "transformed_support_summary.csv", index=False)
    raw.to_csv(args.out / "raw_feature_support.csv", index=False)
    aggregate.to_csv(args.out / "support_aggregate.csv", index=False)
    write_markdown(args.out, aggregate)
    manifest = {
        "task": "TASK-003J-CONDITIONAL-SUPPORT-DIAGNOSIS",
        "folds_checked": int(len(fold_pairs)),
        "summary_rows": int(len(summary)),
        "raw_rows": int(len(raw)),
        "cohorts": sorted(COHORTS),
        "model_changed": False,
        "validation_protocol_changed": False,
        "production_changed": False,
    }
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
