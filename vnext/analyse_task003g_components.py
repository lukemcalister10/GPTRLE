"""Attribute TASK-003E subgroup regressions to forecast components."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from analyse_task003e_regressions import material_regressions

KEYS = ["player_key", "origin_year", "lead"]
VNEXT = "vnext_fold_specific"


def add_slice_columns(rows: pd.DataFrame) -> pd.DataFrame:
    result = rows.copy()
    result["age_band"] = pd.cut(
        result["age"],
        [-np.inf, 20, 23, 26, 29, np.inf],
        labels=["18-20", "21-23", "24-26", "27-29", "30+"],
    )
    result["tenure_band"] = pd.cut(
        result["tenure"],
        [-np.inf, 1, 3, 5, np.inf],
        labels=["0-1", "2-3", "4-5", "6+"],
    )
    result["pick_band"] = pd.cut(
        result["pick"].fillna(999),
        [-np.inf, 20, 40, 60, np.inf],
        labels=["1-20", "21-40", "41-60", "61+ / undrafted"],
    )
    result["prior_games"] = np.where(
        result["total_games"].eq(0),
        "zero prior games",
        "one or more prior games",
    )
    return result


def joined_rows(comparison_dir: Path) -> pd.DataFrame:
    predictions = pd.read_csv(comparison_dir / "predictions.csv")
    targets = pd.read_csv(comparison_dir / "cohorts" / "targets.csv")
    snapshots = pd.read_csv(comparison_dir / "cohorts" / "included_snapshots.csv")
    rows = predictions.merge(targets, on=KEYS, validate="many_to_one").merge(
        snapshots,
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )
    return add_slice_columns(rows)


def component_ratios(group: pd.DataFrame) -> dict[str, float]:
    active = group[group["meaningful"].eq(1)]
    if active.empty:
        raise ValueError("component attribution requires meaningful outcomes")
    p_ratio = group["meaningful"].mean() / group["p_meaningful"].mean()
    games_ratio = active["games"].mean() / active["cond_games"].mean()
    avg_ratio = active["avg"].mean() / active["cond_avg"].mean()
    logs = np.log([p_ratio, games_ratio, avg_ratio])
    total = logs.sum()
    shares = logs / total if total else np.full(3, np.nan)
    return {
        "actual_meaningful_rate": group["meaningful"].mean(),
        "pred_meaningful_prob": group["p_meaningful"].mean(),
        "actual_games_active": active["games"].mean(),
        "pred_cond_games_active": active["cond_games"].mean(),
        "actual_avg_active": active["avg"].mean(),
        "pred_cond_avg_active": active["cond_avg"].mean(),
        "p_ratio": p_ratio,
        "games_ratio": games_ratio,
        "avg_ratio": avg_ratio,
        "p_log_share": shares[0],
        "games_log_share": shares[1],
        "avg_log_share": shares[2],
        "actual_points_mean": group["points"].mean(),
        "pred_points_mean": group["exp_points"].mean(),
        "points_bias": (group["exp_points"] - group["points"]).mean(),
    }


def component_attribution(
    rows: pd.DataFrame, regressions: pd.DataFrame
) -> pd.DataFrame:
    slice_columns = {
        "age_band": "age_band",
        "tenure_band": "tenure_band",
        "position": "position",
        "pick_band": "pick_band",
        "prior_games": "prior_games",
    }
    vnext = rows[rows["model_id"].eq(VNEXT)]
    records = []
    for regression in regressions.itertuples(index=False):
        column = slice_columns[regression.slice_type]
        group = vnext[
            vnext["lead"].eq(regression.lead)
            & vnext[column].astype(str).eq(str(regression.slice_value))
        ]
        records.append(
            {
                "lead": regression.lead,
                "slice_type": regression.slice_type,
                "slice_value": regression.slice_value,
                "n": len(group),
                **component_ratios(group),
            }
        )
    return pd.DataFrame(records)


def zero_history_outcome_split(rows: pd.DataFrame) -> pd.DataFrame:
    zero = rows[rows["total_games"].eq(0)].copy()
    zero["eventual_played"] = zero["games"].gt(0)
    zero["absolute_error_points"] = (
        zero["exp_points"] - zero["points"]
    ).abs()
    zero["points_bias"] = zero["exp_points"] - zero["points"]
    return (
        zero.groupby(["lead", "model_id", "eventual_played"], as_index=False)
        .agg(
            n=("player_key", "size"),
            actual_points=("points", "mean"),
            predicted_points=("exp_points", "mean"),
            mae_points=("absolute_error_points", "mean"),
            points_bias=("points_bias", "mean"),
            actual_games=("games", "mean"),
            predicted_games=("exp_games", "mean"),
            predicted_meaningful_probability=("p_meaningful", "mean"),
        )
        .sort_values(["lead", "model_id", "eventual_played"])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = joined_rows(args.comparison_dir)
    slices = pd.read_csv(args.comparison_dir / "slice_metrics.csv")
    regressions = material_regressions(slices)
    attribution = component_attribution(rows, regressions)
    zero_split = zero_history_outcome_split(rows)

    args.out.mkdir(parents=True, exist_ok=True)
    attribution.to_csv(args.out / "component_attribution.csv", index=False)
    zero_split.to_csv(args.out / "zero_history_outcome_split.csv", index=False)
    print(f"wrote component attribution for {len(attribution)} regressions")


if __name__ == "__main__":
    main()
