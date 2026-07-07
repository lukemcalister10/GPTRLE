"""Deterministic diagnostics for TASK-003 model comparisons."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from benchmark import PINBALL_QUANTILES, PREDICTION_KEY, QUANTILE_COLUMNS, THRESHOLDS

BASELINE_MODEL_ID = "baseline_recent_scoring"
LOSS_COLUMNS = (
    "brier_meaningful",
    "absolute_error_games",
    "absolute_error_total_points",
    "absolute_error_avg_conditional_meaningful",
    *(f"brier_avg_ge_{threshold}" for threshold in THRESHOLDS),
    *(
        f"pinball_points_q{int(level * 100):02d}"
        for level in PINBALL_QUANTILES
    ),
)


def row_losses(predictions: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    joined = predictions.merge(
        targets,
        on=PREDICTION_KEY,
        how="inner",
        validate="many_to_one",
    )
    if len(joined) != len(predictions):
        raise ValueError("prediction/target merge lost comparison rows")

    losses = joined[["model_id", *PREDICTION_KEY]].copy()
    losses["brier_meaningful"] = (
        joined["p_meaningful"] - joined["meaningful"]
    ) ** 2
    losses["absolute_error_games"] = (
        joined["exp_games"] - joined["games"]
    ).abs()
    losses["absolute_error_total_points"] = (
        joined["exp_points"] - joined["points"]
    ).abs()
    losses["absolute_error_avg_conditional_meaningful"] = np.where(
        joined["meaningful"].astype(bool),
        (joined["cond_avg"] - joined["avg"]).abs(),
        np.nan,
    )
    for threshold in THRESHOLDS:
        losses[f"brier_avg_ge_{threshold}"] = (
            joined[f"p_avg_ge_{threshold}"]
            - joined[f"avg_ge_{threshold}"]
        ) ** 2
    for level, column in zip(
        PINBALL_QUANTILES,
        QUANTILE_COLUMNS,
        strict=True,
    ):
        difference = joined["points"] - joined[column]
        losses[f"pinball_points_q{int(level * 100):02d}"] = np.maximum(
            level * difference,
            (level - 1.0) * difference,
        )
    return losses


def metrics_by_origin_lead(losses: pd.DataFrame) -> pd.DataFrame:
    return (
        losses.groupby(["model_id", "origin_year", "lead"], as_index=False)[
            list(LOSS_COLUMNS)
        ]
        .mean()
        .sort_values(["model_id", "origin_year", "lead"])
        .reset_index(drop=True)
    )


def fold_differences(
    fold_metrics: pd.DataFrame,
    baseline_model_id: str = BASELINE_MODEL_ID,
) -> pd.DataFrame:
    baseline = fold_metrics[fold_metrics["model_id"] == baseline_model_id].drop(
        columns=["model_id"]
    )
    challengers = fold_metrics[fold_metrics["model_id"] != baseline_model_id]
    if challengers.empty:
        return pd.DataFrame(
            columns=["model_id", "origin_year", "lead", *LOSS_COLUMNS]
        )
    merged = challengers.merge(
        baseline,
        on=["origin_year", "lead"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_baseline"),
    )
    if merged[[f"{column}_baseline" for column in LOSS_COLUMNS]].isna().all(axis=1).any():
        raise ValueError("baseline fold metrics missing for challenger rows")
    result = merged[["model_id", "origin_year", "lead"]].copy()
    for column in LOSS_COLUMNS:
        result[column] = merged[column] - merged[f"{column}_baseline"]
    return result.sort_values(["model_id", "origin_year", "lead"]).reset_index(drop=True)


def player_block_bootstrap(
    losses: pd.DataFrame,
    *,
    baseline_model_id: str = BASELINE_MODEL_ID,
    repetitions: int = 1000,
    seed: int = 3003,
) -> pd.DataFrame:
    """Bootstrap paired loss differences by player block.

    Differences are challenger minus baseline, so negative values favour the
    challenger. All rows for a sampled player move together.
    """

    baseline = losses[losses["model_id"] == baseline_model_id].drop(
        columns=["model_id"]
    )
    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(seed)

    for model_id, challenger in losses[
        losses["model_id"] != baseline_model_id
    ].groupby("model_id", sort=True):
        paired = challenger.merge(
            baseline,
            on=PREDICTION_KEY,
            how="inner",
            validate="one_to_one",
            suffixes=("", "_baseline"),
        )
        if len(paired) != len(baseline):
            raise ValueError(f"{model_id} is not exactly paired with baseline")
        players = np.array(sorted(paired["player_key"].astype(str).unique()))
        player_index = {player: index for index, player in enumerate(players)}
        row_player = paired["player_key"].astype(str).map(player_index).to_numpy()
        draws = rng.integers(0, len(players), size=(repetitions, len(players)))

        for metric in LOSS_COLUMNS:
            differences = (
                paired[metric] - paired[f"{metric}_baseline"]
            ).to_numpy(float)
            valid = np.isfinite(differences)
            sums = np.bincount(
                row_player[valid],
                weights=differences[valid],
                minlength=len(players),
            )
            counts = np.bincount(
                row_player[valid],
                minlength=len(players),
            ).astype(float)
            sampled_sums = sums[draws].sum(axis=1)
            sampled_counts = counts[draws].sum(axis=1)
            estimates = np.divide(
                sampled_sums,
                sampled_counts,
                out=np.full(repetitions, np.nan),
                where=sampled_counts > 0,
            )
            point = float(np.nanmean(differences))
            rows.append(
                {
                    "model_id": str(model_id),
                    "baseline_model_id": baseline_model_id,
                    "metric": metric,
                    "difference": point,
                    "ci_low": float(np.nanquantile(estimates, 0.025)),
                    "ci_high": float(np.nanquantile(estimates, 0.975)),
                    "probability_challenger_better": float(
                        np.nanmean(estimates < 0.0)
                    ),
                    "bootstrap_repetitions": int(repetitions),
                    "player_blocks": int(len(players)),
                    "seed": int(seed),
                }
            )
    return pd.DataFrame(rows)


def reliability_tables(
    predictions: pd.DataFrame,
    targets: pd.DataFrame,
    bins: int = 10,
) -> pd.DataFrame:
    joined = predictions.merge(
        targets,
        on=PREDICTION_KEY,
        how="inner",
        validate="many_to_one",
    )
    target_pairs = [("meaningful", "p_meaningful")]
    target_pairs.extend(
        (f"avg_ge_{threshold}", f"p_avg_ge_{threshold}")
        for threshold in THRESHOLDS
    )
    rows = []
    for (model_id, lead), group in joined.groupby(
        ["model_id", "lead"], sort=True
    ):
        for actual_column, probability_column in target_pairs:
            ranked = group[[actual_column, probability_column]].copy()
            ranked["bin"] = pd.qcut(
                ranked[probability_column],
                q=bins,
                labels=False,
                duplicates="drop",
            )
            for bin_id, bin_rows in ranked.groupby("bin", dropna=False):
                rows.append(
                    {
                        "model_id": str(model_id),
                        "lead": int(lead),
                        "target": actual_column,
                        "bin": int(bin_id) if pd.notna(bin_id) else 0,
                        "n": int(len(bin_rows)),
                        "predicted": float(bin_rows[probability_column].mean()),
                        "actual": float(bin_rows[actual_column].mean()),
                    }
                )
    return pd.DataFrame(rows).sort_values(
        ["model_id", "lead", "target", "bin"]
    ).reset_index(drop=True)


def _pick_band(value: Any) -> str:
    try:
        pick = float(value)
    except (TypeError, ValueError):
        return "61+ / undrafted"
    if pick <= 5:
        return "1-5"
    if pick <= 10:
        return "6-10"
    if pick <= 20:
        return "11-20"
    if pick <= 40:
        return "21-40"
    if pick <= 60:
        return "41-60"
    return "61+ / undrafted"


def _age_band(value: Any) -> str:
    age = int(value)
    if age <= 20:
        return "18-20"
    if age <= 23:
        return "21-23"
    if age <= 26:
        return "24-26"
    if age <= 29:
        return "27-29"
    return "30+"


def _tenure_band(value: Any) -> str:
    tenure = int(value)
    if tenure <= 3:
        return str(tenure)
    if tenure <= 5:
        return "4-5"
    return "6+"


def slice_metrics(
    predictions: pd.DataFrame,
    targets: pd.DataFrame,
    snapshots: pd.DataFrame,
    *,
    minimum_n: int = 200,
) -> pd.DataFrame:
    joined = predictions.merge(
        targets,
        on=PREDICTION_KEY,
        how="inner",
        validate="many_to_one",
    ).merge(
        snapshots,
        on=["player_key", "origin_year"],
        how="left",
        validate="many_to_one",
    )
    if joined[["position", "draft_type", "age", "tenure", "total_games"]].isna().any(axis=None):
        raise ValueError("slice metadata missing after snapshot join")

    slice_values = {
        "position": joined["position"].astype(str),
        "draft_type": joined["draft_type"].astype(str),
        "pick_band": joined["pick"].map(_pick_band),
        "age_band": joined["age"].map(_age_band),
        "tenure_band": joined["tenure"].map(_tenure_band),
        "prior_games": np.where(
            joined["total_games"].astype(float) <= 0,
            "zero prior games",
            "established history",
        ),
    }
    rows = []
    for slice_type, values in slice_values.items():
        working = joined.assign(slice_value=values)
        for (model_id, lead, slice_value), group in working.groupby(
            ["model_id", "lead", "slice_value"],
            sort=True,
        ):
            if len(group) < minimum_n:
                continue
            rows.append(
                {
                    "model_id": str(model_id),
                    "lead": int(lead),
                    "slice_type": slice_type,
                    "slice_value": str(slice_value),
                    "n": int(len(group)),
                    "brier_meaningful": float(
                        np.mean(
                            (
                                group["p_meaningful"]
                                - group["meaningful"]
                            )
                            ** 2
                        )
                    ),
                    "mae_games": float(
                        np.mean((group["exp_games"] - group["games"]).abs())
                    ),
                    "mae_total_points": float(
                        np.mean((group["exp_points"] - group["points"]).abs())
                    ),
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["slice_type", "slice_value", "model_id", "lead"]
    ).reset_index(drop=True)
