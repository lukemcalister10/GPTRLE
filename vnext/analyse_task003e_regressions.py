"""Diagnostic-only TASK-003E subgroup regression analysis."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

BASELINE = "baseline_recent_scoring"
VNEXT = "vnext_fold_specific"
SLICE_KEYS = ["lead", "slice_type", "slice_value"]


def material_regressions(slices: pd.DataFrame, threshold_pct: float = 3.0) -> pd.DataFrame:
    required = {"model_id", *SLICE_KEYS, "n", "mae_total_points"}
    missing = required - set(slices.columns)
    if missing:
        raise ValueError(f"slice metrics missing columns: {sorted(missing)}")
    vnext = slices[slices.model_id.eq(VNEXT)]
    baseline = slices[slices.model_id.eq(BASELINE)]
    result = vnext.merge(
        baseline,
        on=SLICE_KEYS,
        suffixes=("_vnext", "_baseline"),
        validate="one_to_one",
    )
    result["points_mae_change_pct"] = 100.0 * (
        result.mae_total_points_vnext - result.mae_total_points_baseline
    ) / result.mae_total_points_baseline
    result["excess_mae"] = (
        result.mae_total_points_vnext - result.mae_total_points_baseline
    )
    result["practical_burden"] = result.excess_mae * result.n_vnext
    result = result[result.points_mae_change_pct.gt(threshold_pct)].copy()
    result["severity_rank"] = result.points_mae_change_pct.rank(
        method="first", ascending=False
    ).astype(int)
    result["burden_rank"] = result.practical_burden.rank(
        method="first", ascending=False
    ).astype(int)
    return result.sort_values(["severity_rank", "burden_rank"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--threshold-pct", type=float, default=3.0)
    args = parser.parse_args()
    slices = pd.read_csv(args.comparison_dir / "slice_metrics.csv")
    result = material_regressions(slices, args.threshold_pct)
    args.out.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out / "material_regressions.csv", index=False)
    print(f"wrote {len(result)} material regressions")


if __name__ == "__main__":
    main()
