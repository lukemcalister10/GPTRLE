"""Experimental leakage-safe calibration of conditional games and average.

This module leaves the meaningful-season classifier, probability calibration,
features and rolling-origin protocol unchanged. It calibrates only the two
conditional magnitude regressors on the existing temporally later calibration
rows, restricted to realised meaningful seasons.
"""
from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

if __name__ == "__main__":
    sys.modules["model_artifacts_conditional_calibrated"] = sys.modules[__name__]

from model_artifacts import predict as predict_uncalibrated
from model_artifacts import split_temporal
from model_artifacts import train_lead as train_uncalibrated


@dataclass
class ClippedIdentityCalibrator:
    """Deterministic fallback when a calibration sample is unusable."""

    lower: float
    upper: float

    def predict(self, values: Any) -> np.ndarray:
        return np.clip(np.asarray(values, dtype=float), self.lower, self.upper)


ClippedIdentityCalibrator.__module__ = "model_artifacts_conditional_calibrated"


def fit_conditional_calibrator(
    raw_prediction: Any,
    target: Any,
    *,
    lower: float,
    upper: float,
    minimum_rows: int = 20,
) -> tuple[Any, dict[str, Any]]:
    """Fit a monotonic temporal calibrator or return an explicit identity fallback."""

    raw = np.asarray(raw_prediction, dtype=float)
    actual = np.asarray(target, dtype=float)
    valid = np.isfinite(raw) & np.isfinite(actual)
    raw = raw[valid]
    actual = actual[valid]

    metadata: dict[str, Any] = {
        "rows": int(len(raw)),
        "raw_unique": int(len(np.unique(raw))),
        "target_unique": int(len(np.unique(actual))),
        "lower": float(lower),
        "upper": float(upper),
    }
    if len(raw) < minimum_rows:
        metadata.update(method="clipped_identity", fallback_reason="insufficient_rows")
        return ClippedIdentityCalibrator(lower, upper), metadata
    if len(np.unique(raw)) < 2 or len(np.unique(actual)) < 2:
        metadata.update(method="clipped_identity", fallback_reason="degenerate_sample")
        return ClippedIdentityCalibrator(lower, upper), metadata

    calibrator = IsotonicRegression(
        increasing=True,
        out_of_bounds="clip",
        y_min=float(lower),
        y_max=float(upper),
    ).fit(raw, actual)
    metadata.update(
        method="isotonic_temporal_mean_calibration",
        fallback_reason=None,
        raw_min=float(raw.min()),
        raw_max=float(raw.max()),
        target_min=float(actual.min()),
        target_max=float(actual.max()),
    )
    return calibrator, metadata


def calibrate_conditional_predictions(
    artifact: Any,
    raw_games: Any,
    raw_avg: Any,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply persisted calibrators with coherent conditional bounds."""

    games_calibrator = getattr(
        artifact,
        "games_calibrator",
        ClippedIdentityCalibrator(0.0, 23.0),
    )
    avg_calibrator = getattr(
        artifact,
        "avg_calibrator",
        ClippedIdentityCalibrator(0.0, 145.0),
    )
    games = np.clip(
        games_calibrator.predict(np.asarray(raw_games, dtype=float)),
        0.0,
        23.0,
    )
    average = np.clip(
        avg_calibrator.predict(np.asarray(raw_avg, dtype=float)),
        0.0,
        145.0,
    )
    return games, average


def train_lead(train: pd.DataFrame, lead: int) -> Any:
    """Train the unchanged base model and calibrate only conditional magnitudes."""

    artifact = train_uncalibrated(train, lead)
    _, calibration = split_temporal(train, lead)
    transformed = artifact.preprocessor.transform(calibration)
    active = calibration[f"l{lead}_meaningful"].astype(bool).to_numpy()
    if not active.any():
        raise ValueError(
            f"lead {lead} conditional calibration has no meaningful rows"
        )

    raw_games = np.clip(artifact.games_model.predict(transformed[active]), 0.0, 23.0)
    raw_avg = np.clip(artifact.avg_model.predict(transformed[active]), 0.0, 145.0)
    actual_games = calibration.loc[active, f"l{lead}_games"].to_numpy(float)
    actual_avg = calibration.loc[active, f"l{lead}_avg"].to_numpy(float)

    games_calibrator, games_metadata = fit_conditional_calibrator(
        raw_games,
        actual_games,
        lower=6.0,
        upper=23.0,
    )
    avg_calibrator, avg_metadata = fit_conditional_calibrator(
        raw_avg,
        actual_avg,
        lower=0.0,
        upper=145.0,
    )
    artifact.games_calibrator = games_calibrator
    artifact.avg_calibrator = avg_calibrator
    artifact.games_calibration_metadata = games_metadata
    artifact.avg_calibration_metadata = avg_metadata
    artifact.conditional_calibration_rows = int(active.sum())
    artifact.conditional_calibration_method = (
        "temporally_held_out_isotonic_mean_calibration"
    )

    calibrated_games, calibrated_avg = calibrate_conditional_predictions(
        artifact,
        raw_games,
        raw_avg,
    )
    games_residual = actual_games - calibrated_games
    avg_residual = actual_avg - calibrated_avg
    artifact.games_resid_sd = max(
        float(np.std(games_residual, ddof=1)) if len(games_residual) > 2 else 3.0,
        1.0,
    )
    artifact.avg_resid_sd = max(
        float(np.std(avg_residual, ddof=1)) if len(avg_residual) > 2 else 12.0,
        3.0,
    )
    return artifact


def predict(artifact: Any, rows: pd.DataFrame) -> pd.DataFrame:
    """Predict with unchanged probabilities and calibrated conditional magnitudes."""

    out = predict_uncalibrated(artifact, rows)
    transformed = artifact.preprocessor.transform(rows)
    raw_games = np.clip(artifact.games_model.predict(transformed), 0.0, 23.0)
    raw_avg = np.clip(artifact.avg_model.predict(transformed), 0.0, 145.0)
    games, average = calibrate_conditional_predictions(
        artifact,
        raw_games,
        raw_avg,
    )
    out["cond_games"] = games
    out["cond_avg"] = average
    out["exp_games"] = out["p_meaningful"] * games
    out["exp_avg"] = out["p_meaningful"] * average
    out["exp_points"] = out["p_meaningful"] * games * average
    return out
