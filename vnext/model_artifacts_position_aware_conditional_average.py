"""TASK-046 position-aware conditional-average candidate.

Only the conditional-average regressors change relative to accepted TASK-012.
A pooled conditional-average regressor is fitted in every rolling-origin fold, then
separate broad-position regressors are fitted from the same fold training data
when the meaningful target sample for that position is sufficient. Prediction
uses the matching position regressor or the pooled fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDRegressor

import model_artifacts
import model_artifacts_established_ceiling as task012
import model_artifacts_zero_history

MIN_POSITION_MEANINGFUL_ROWS = 75
MODEL_ID = "vnext_task046_position_aware_conditional_average"


@dataclass
class PositionAwareAvgLayer:
    preprocessor: Any
    pooled_model: Any
    position_models: dict[str, Any]
    residual_sd: float
    iterations: int
    position_training_rows: dict[str, int]
    fallback_positions: dict[str, str]


@dataclass
class Task046Artifact:
    lead: int
    base: Any
    avg_layer: PositionAwareAvgLayer
    avg_resid_sd: float

    def __getattr__(self, name: str) -> Any:
        base = object.__getattribute__(self, "__dict__").get("base")
        if base is None:
            raise AttributeError(name)
        return getattr(base, name)


def broad_position_values(rows: pd.DataFrame) -> pd.Series:
    """Return leakage-safe broad origin position labels used for model routing."""
    if "position" not in rows.columns:
        return pd.Series("UNK", index=rows.index, dtype="string")
    pos = rows["position"].fillna("UNK").astype(str).str.upper().str.strip()
    return pos.mask(pos.eq("") | pos.eq("NAN"), "UNK").astype("string")


def _new_avg_model(lead: int) -> SGDRegressor:
    """Return the unchanged TASK-012 conditional-average estimator."""

    return SGDRegressor(
        loss="huber",
        alpha=0.002,
        max_iter=task012.AVG_MAX_ITER,
        tol=1e-3,
        random_state=lead + 20,
    )


def _fit_avg_layer(train: pd.DataFrame, lead: int) -> PositionAwareAvgLayer:
    fit, calibration = model_artifacts.split_temporal(train, lead)
    fit_features = task012.add_ceiling_evidence_feature(fit)
    calibration_features = task012.add_ceiling_evidence_feature(calibration)
    preprocessor = task012.make_avg_preprocessor()
    x_fit = preprocessor.fit_transform(fit_features)
    x_cal = preprocessor.transform(calibration_features)
    active_fit = fit[f"l{lead}_meaningful"].astype(bool).to_numpy()
    active_calibration = calibration[f"l{lead}_meaningful"].astype(bool).to_numpy()
    if not active_fit.any():
        raise ValueError(f"lead {lead} has no meaningful rows for conditional average")

    y_fit = fit.loc[active_fit, f"l{lead}_avg"].to_numpy(float)
    pooled_model = _new_avg_model(lead).fit(x_fit[active_fit], y_fit)

    fit_pos = broad_position_values(fit).to_numpy()
    position_training_rows: dict[str, int] = {}
    position_models: dict[str, Any] = {}
    fallback_positions: dict[str, str] = {}
    for offset, position in enumerate(sorted(pd.unique(fit_pos))):
        mask = active_fit & (fit_pos == position)
        count = int(mask.sum())
        position_training_rows[str(position)] = count
        if count >= MIN_POSITION_MEANINGFUL_ROWS:
            position_models[str(position)] = _new_avg_model(lead).fit(
                x_fit[mask],
                fit.loc[mask, f"l{lead}_avg"].to_numpy(float),
            )
        else:
            fallback_positions[str(position)] = "pooled_insufficient_position_rows"

    if active_calibration.any():
        prediction = _predict_avg(
            PositionAwareAvgLayer(
                preprocessor=preprocessor,
                pooled_model=pooled_model,
                position_models=position_models,
                residual_sd=12.0,
                iterations=int(pooled_model.n_iter_),
                position_training_rows=position_training_rows,
                fallback_positions=fallback_positions,
            ),
            calibration_features,
            positions=broad_position_values(calibration_features),
        )[active_calibration]
        residual = calibration.loc[active_calibration, f"l{lead}_avg"].to_numpy(float) - prediction
        residual_sd = float(np.std(residual, ddof=1)) if active_calibration.sum() > 2 else 12.0
    else:
        residual_sd = 12.0

    iterations = int(pooled_model.n_iter_) + sum(int(m.n_iter_) for m in position_models.values())
    return PositionAwareAvgLayer(
        preprocessor=preprocessor,
        pooled_model=pooled_model,
        position_models=position_models,
        residual_sd=max(residual_sd, 3.0),
        iterations=iterations,
        position_training_rows=position_training_rows,
        fallback_positions=fallback_positions,
    )


def _predict_avg(layer: PositionAwareAvgLayer, features: pd.DataFrame, positions: pd.Series | None = None) -> np.ndarray:
    x = layer.preprocessor.transform(features)
    pred = layer.pooled_model.predict(x)
    pos = broad_position_values(features) if positions is None else positions.astype("string")
    for position, model in layer.position_models.items():
        mask = (pos == position).to_numpy()
        if mask.any():
            pred[mask] = model.predict(x[mask])
    return np.clip(pred, 0.0, 145.0)


def train_lead(train: pd.DataFrame, lead: int) -> Task046Artifact:
    base = model_artifacts_zero_history.train_lead(train, lead)
    avg_layer = _fit_avg_layer(train, lead)
    return Task046Artifact(
        lead=lead,
        base=base,
        avg_layer=avg_layer,
        avg_resid_sd=avg_layer.residual_sd,
    )


def predict(artifact: Task046Artifact, rows: pd.DataFrame) -> pd.DataFrame:
    out = model_artifacts_zero_history.predict(artifact.base, rows).copy()
    features = task012.add_ceiling_evidence_feature(rows)
    conditional_average = _predict_avg(artifact.avg_layer, features)
    probability = out["p_meaningful"].to_numpy(float)
    conditional_games = out["cond_games"].to_numpy(float)
    out["cond_avg"] = conditional_average
    out["exp_avg"] = probability * conditional_average
    out["exp_points"] = probability * conditional_games * conditional_average
    out["model_id"] = MODEL_ID
    return out
