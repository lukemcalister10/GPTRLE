"""Deterministic baseline and comparison harness for TASK-003."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, roc_auc_score

from benchmark import (
    PINBALL_QUANTILES,
    PREDICTION_KEY,
    QUANTILE_COLUMNS,
    THRESHOLDS,
    normalise_predictions,
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {
        "rows": int(len(frame)),
        "bytes": int(path.stat().st_size),
        "sha256": sha256_file(path),
    }


def load_external_predictions(path: Path, model_id: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    if "model_id" in raw.columns:
        observed = sorted(set(raw["model_id"].astype(str)))
        if observed != [model_id]:
            raise ValueError(
                f"{path} model_id values {observed} do not match expected {model_id}"
            )
        raw = raw.drop(columns=["model_id"])
    return normalise_predictions(model_id, raw)


def calibration_intercept_slope_stable(
    y: pd.Series, p: pd.Series
) -> tuple[float, float]:
    """Fit the benchmark calibration model with a stable deterministic solver."""

    yv = y.to_numpy(float)
    pv = np.clip(p.to_numpy(float), 1e-6, 1.0 - 1e-6)
    x = np.log(pv / (1.0 - pv))
    if len(np.unique(yv)) < 2 or np.std(x) < 1e-12:
        return float("nan"), float("nan")

    def objective(beta: np.ndarray) -> float:
        eta = beta[0] + beta[1] * x
        return float(np.sum(np.logaddexp(0.0, eta) - yv * eta))

    def gradient(beta: np.ndarray) -> np.ndarray:
        eta = np.clip(beta[0] + beta[1] * x, -40.0, 40.0)
        fitted = 1.0 / (1.0 + np.exp(-eta))
        residual = fitted - yv
        return np.array([residual.sum(), np.dot(residual, x)], dtype=float)

    result = minimize(
        objective,
        np.array([0.0, 1.0]),
        jac=gradient,
        method="L-BFGS-B",
        options={"ftol": 1e-12, "gtol": 1e-8, "maxiter": 1000},
    )
    if not result.success or not np.isfinite(result.x).all():
        raise ValueError(f"logistic calibration fit failed: {result.message}")
    return float(result.x[0]), float(result.x[1])


def safe_auc(y: pd.Series, p: pd.Series) -> float:
    return float(roc_auc_score(y, p)) if y.nunique() > 1 else float("nan")


def pinball_loss(y: pd.Series, q: pd.Series, tau: float) -> float:
    diff = y.to_numpy(float) - q.to_numpy(float)
    return float(np.mean(np.maximum(tau * diff, (tau - 1.0) * diff)))


def score_predictions_stable(
    predictions: pd.DataFrame, targets: pd.DataFrame
) -> pd.DataFrame:
    """Score predictions using the benchmark metrics with stable calibration fitting."""

    if "model_id" not in predictions.columns:
        raise ValueError("predictions must include model_id")
    validated = []
    for model_id, group in predictions.groupby("model_id", sort=True):
        validated.append(normalise_predictions(str(model_id), group.drop(columns=["model_id"])))
    predictions = pd.concat(validated, ignore_index=True)
    joined = predictions.merge(targets, on=PREDICTION_KEY, how="inner", validate="many_to_one")
    if len(joined) != len(predictions):
        raise ValueError("prediction/target merge did not preserve benchmark prediction rows")

    expected = targets[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    for model_id, group in predictions.groupby("model_id", sort=True):
        got = group[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
        if not got.equals(expected):
            raise ValueError(f"{model_id} predictions do not cover exactly the target rows")

    rows: list[dict[str, Any]] = []
    for (model_id, lead), group in joined.groupby(["model_id", "lead"], sort=True):
        intercept, slope = calibration_intercept_slope_stable(
            group["meaningful"], group["p_meaningful"]
        )
        row: dict[str, Any] = {
            "model_id": model_id,
            "lead": int(lead),
            "n": int(len(group)),
            "brier_meaningful": brier_score_loss(
                group["meaningful"], group["p_meaningful"]
            ),
            "log_loss_meaningful": log_loss(
                group["meaningful"],
                np.clip(group["p_meaningful"], 0.001, 0.999),
                labels=[0, 1],
            ),
            "calibration_intercept_meaningful": intercept,
            "calibration_slope_meaningful": slope,
            "auc_meaningful": safe_auc(group["meaningful"], group["p_meaningful"]),
            "mae_games": mean_absolute_error(group["games"], group["exp_games"]),
            "mae_total_points": mean_absolute_error(
                group["points"], group["exp_points"]
            ),
        }
        meaningful = group[group["meaningful"] == 1]
        row["mae_avg_conditional_meaningful"] = (
            mean_absolute_error(meaningful["avg"], meaningful["cond_avg"])
            if len(meaningful)
            else float("nan")
        )
        for threshold in THRESHOLDS:
            actual = group[f"avg_ge_{threshold}"]
            probability = group[f"p_avg_ge_{threshold}"]
            row[f"brier_avg_ge_{threshold}"] = brier_score_loss(actual, probability)
            row[f"auc_avg_ge_{threshold}"] = safe_auc(actual, probability)
        for tau, column in zip(PINBALL_QUANTILES, QUANTILE_COLUMNS, strict=True):
            row[f"pinball_points_q{int(tau * 100):02d}"] = pinball_loss(
                group["points"], group[column], tau
            )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["model_id", "lead"]).reset_index(drop=True)


def weighted_metric_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    decomposable = [
        column
        for column in metrics.columns
        if column.startswith(("brier_", "log_loss_", "mae_", "pinball_"))
    ]
    rows = []
    for model_id, group in metrics.groupby("model_id", sort=True):
        weights = group["n"].to_numpy(float)
        row: dict[str, Any] = {
            "model_id": str(model_id),
            "n": int(weights.sum()),
            "lead_rows": int(len(group)),
        }
        for column in decomposable:
            values = group[column].to_numpy(float)
            valid = np.isfinite(values)
            row[column] = (
                float(np.average(values[valid], weights=weights[valid]))
                if valid.any()
                else float("nan")
            )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("model_id").reset_index(drop=True)
