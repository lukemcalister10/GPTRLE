"""Generate diagnostic-only analysis for TASK-003E material slice regressions."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

BASELINE = "baseline_recent_scoring"
VNEXT = "vnext_fold_specific"
KEYS = ["player_key", "origin_year", "lead"]
SLICE_KEYS = ["lead", "slice_type", "slice_value"]


def material_regressions(
    slices: pd.DataFrame, threshold_pct: float = 3.0
) -> pd.DataFrame:
    """Return slice/lead rows where vNext points MAE exceeds baseline materially."""
    required = {"model_id", *SLICE_KEYS, "n", "mae_total_points"}
    missing = required - set(slices.columns)
    if missing:
        raise ValueError(f"slice_metrics.csv missing columns: {sorted(missing)}")

    vnext = slices[slices["model_id"].eq(VNEXT)].copy()
    baseline = slices[slices["model_id"].eq(BASELINE)].copy()
    merged = vnext.merge(
        baseline,
        on=SLICE_KEYS,
        suffixes=("_vnext", "_baseline"),
        validate="one_to_one",
    )
    merged["points_mae_change_pct"] = 100.0 * (
        merged["mae_total_points_vnext"]
        - merged["mae_total_points_baseline"]
    ) / merged["mae_total_points_baseline"]
    merged["excess_mae"] = (
        merged["mae_total_points_vnext"]
        - merged["mae_total_points_baseline"]
    )
    merged["practical_burden"] = merged["excess_mae"] * merged["n_vnext"]

    result = merged[merged["points_mae_change_pct"].gt(threshold_pct)].copy()
    result["severity_rank"] = result["points_mae_change_pct"].rank(
        method="first", ascending=False
    ).astype(int)
    result["burden_rank"] = result["practical_burden"].rank(
        method="first", ascending=False
    ).astype(int)
    return result.sort_values(["severity_rank", "burden_rank"])


def add_slice_columns(rows: pd.DataFrame) -> pd.DataFrame:
    """Recreate the locked comparison slice labels from as-of snapshots."""
    result = rows.copy()
    result["age_band"] = pd.cut(
        result["age"],
        [-float("inf"), 20, 23, 26, 29, float("inf")],
        labels=["18-20", "21-23", "24-26", "27-29", "30+"],
    )
    result["tenure_band"] = pd.cut(
        result["tenure"],
        [-float("inf"), 1, 3, 5, float("inf")],
        labels=["0-1", "2-3", "4-5", "6+"],
    )
    result["pick_band"] = pd.cut(
        result["pick"].fillna(999),
        [-float("inf"), 20, 40, 60, float("inf")],
        labels=["1-20", "21-40", "41-60", "61+ / undrafted"],
    )
    result["prior_games_band"] = result["total_games"].map(
        lambda value: "zero prior games"
        if value == 0
        else "one or more prior games"
    )
    return result


def _joined_rows(comparison_dir: Path) -> pd.DataFrame:
    predictions = pd.read_csv(comparison_dir / "predictions.csv")
    targets = pd.read_csv(comparison_dir / "cohorts" / "targets.csv")
    snapshots = pd.read_csv(
        comparison_dir / "cohorts" / "included_snapshots.csv"
    )
    rows = predictions.merge(targets, on=KEYS, validate="many_to_one").merge(
        snapshots,
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )
    return add_slice_columns(rows)


def _slice_column(slice_type: str) -> str | None:
    return {
        "age_band": "age_band",
        "tenure_band": "tenure_band",
        "position": "position",
        "pick_band": "pick_band",
        "prior_games": "prior_games_band",
    }.get(slice_type)


def component_diagnostics(
    comparison_dir: Path, regressions: pd.DataFrame
) -> pd.DataFrame:
    """Decompose regressing rows into opportunity and scoring components."""
    rows = _joined_rows(comparison_dir)
    records: list[dict[str, object]] = []

    for regression in regressions.itertuples(index=False):
        column = _slice_column(regression.slice_type)
        if column is None:
            continue
        subset = rows[
            rows["lead"].eq(regression.lead)
            & rows[column].astype(str).eq(str(regression.slice_value))
        ]
        for model_id, model_rows in subset.groupby("model_id"):
            records.append(
                {
                    "lead": regression.lead,
                    "slice_type": regression.slice_type,
                    "slice_value": regression.slice_value,
                    "model_id": model_id,
                    "n": len(model_rows),
                    "actual_games_mean": model_rows["games"].mean(),
                    "predicted_games_mean": model_rows["exp_games"].mean(),
                    "games_bias": (
                        model_rows["exp_games"] - model_rows["games"]
                    ).mean(),
                    "actual_points_mean": model_rows["points"].mean(),
                    "predicted_points_mean": model_rows["exp_points"].mean(),
                    "points_bias": (
                        model_rows["exp_points"] - model_rows["points"]
                    ).mean(),
                    "p_meaningful_mean": model_rows["p_meaningful"].mean(),
                    "actual_meaningful_rate": model_rows["meaningful"].mean(),
                    "cond_games_mean": model_rows["cond_games"].mean(),
                    "cond_avg_mean": model_rows["cond_avg"].mean(),
                }
            )

    return pd.DataFrame.from_records(records).sort_values(
        SLICE_KEYS + ["model_id"]
    )


def fold_stability(
    comparison_dir: Path, regressions: pd.DataFrame
) -> pd.DataFrame:
    """Measure whether each pooled regression repeats across legal origins."""
    rows = _joined_rows(comparison_dir)
    records: list[dict[str, object]] = []

    for regression in regressions.itertuples(index=False):
        column = _slice_column(regression.slice_type)
        if column is None:
            continue
        subset = rows[
            rows["lead"].eq(regression.lead)
            & rows[column].astype(str).eq(str(regression.slice_value))
        ].copy()
        subset["abs_points_error"] = (
            subset["exp_points"] - subset["points"]
        ).abs()
        grouped = (
            subset.groupby(["origin_year", "model_id"])
            .agg(
                n=("player_key", "size"),
                mae_total_points=("abs_points_error", "mean"),
            )
            .reset_index()
        )
        pivot = grouped.pivot(
            index="origin_year",
            columns="model_id",
            values=["n", "mae_total_points"],
        )
        for origin_year, row in pivot.iterrows():
            baseline = row[("mae_total_points", BASELINE)]
            vnext = row[("mae_total_points", VNEXT)]
            records.append(
                {
                    "lead": regression.lead,
                    "slice_type": regression.slice_type,
                    "slice_value": regression.slice_value,
                    "origin_year": origin_year,
                    "n": int(row[("n", VNEXT)]),
                    "baseline_mae_total_points": baseline,
                    "vnext_mae_total_points": vnext,
                    "points_mae_change_pct": 100.0
                    * (vnext - baseline)
                    / baseline,
                    "vnext_worse": bool(vnext > baseline),
                }
            )

    return pd.DataFrame.from_records(records).sort_values(
        SLICE_KEYS + ["origin_year"]
    )


def write_outputs(
    out_dir: Path,
    regressions: pd.DataFrame,
    components: pd.DataFrame,
    stability: pd.DataFrame,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    regressions.to_csv(out_dir / "material_regressions.csv", index=False)
    components.to_csv(out_dir / "component_diagnostics.csv", index=False)
    stability.to_csv(out_dir / "fold_stability.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--threshold-pct", type=float, default=3.0)
    args = parser.parse_args()

    slices = pd.read_csv(args.comparison_dir / "slice_metrics.csv")
    regressions = material_regressions(slices, args.threshold_pct)
    components = component_diagnostics(args.comparison_dir, regressions)
    stability = fold_stability(args.comparison_dir, regressions)
    write_outputs(args.out, regressions, components, stability)
    print(f"wrote {len(regressions)} material regressions to {args.out}")


if __name__ == "__main__":
    main()
