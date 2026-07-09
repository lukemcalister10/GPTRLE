"""TASK-047 pooled Ridge conditional-average candidate.

Only the pooled conditional-average estimator changes relative to accepted
TASK-012. The TASK-012 preprocessing, demonstrated-ceiling feature, temporal
training/calibration split, meaningful-season target filtering and all other
forecast layers remain unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import model_artifacts
import model_artifacts_zero_history
from evaluate_v3_fast import CAT as BASE_CAT
from evaluate_v3_fast import NUM as BASE_NUM

FULL_EVIDENCE_GAMES = 50.0
RIDGE_ALPHA_GRID = (0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0)


def add_ceiling_evidence_feature(rows: pd.DataFrame) -> pd.DataFrame:
    """Add one smooth origin-safe interaction between ceiling and exposure."""

    out = rows.copy()
    games = pd.to_numeric(out["total_games"], errors="coerce").fillna(0.0).clip(lower=0.0)
    career_best = pd.to_numeric(out["career_best"], errors="coerce").fillna(0.0).clip(lower=0.0)
    evidence_weight = np.clip(games.to_numpy(float) / FULL_EVIDENCE_GAMES, 0.0, 1.0)
    out["career_best_x_evidence"] = career_best.to_numpy(float) * evidence_weight
    return out


def make_avg_preprocessor() -> ColumnTransformer:
    numeric = list(BASE_NUM) + ["career_best_x_evidence"]
    return ColumnTransformer(
        [
            (
                "n",
                Pipeline(
                    [
                        ("i", SimpleImputer(strategy="median")),
                        ("s", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "c",
                Pipeline(
                    [
                        ("i", SimpleImputer(strategy="most_frequent")),
                        ("o", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                list(BASE_CAT),
            ),
        ]
    )


@dataclass
class AvgLayer:
    preprocessor: Any
    model: Any
    residual_sd: float
    selected_alpha: float
    alpha_scores: dict[float, float]


@dataclass
class Task012Artifact:
    lead: int
    base: Any
    avg_layer: AvgLayer
    avg_resid_sd: float

    def __getattr__(self, name: str) -> Any:
        base = object.__getattribute__(self, "__dict__").get("base")
        if base is None:
            raise AttributeError(name)
        return getattr(base, name)


def select_ridge_alpha(alpha_scores: dict[float, float]) -> float:
    """Select the lowest-MAE Ridge alpha, breaking exact ties toward smaller alpha."""

    if not alpha_scores:
        raise ValueError("alpha_scores must not be empty")
    return float(min(alpha_scores, key=lambda a: (alpha_scores[a], a)))


def _fit_avg_layer(train: pd.DataFrame, lead: int) -> AvgLayer:
    fit, calibration = model_artifacts.split_temporal(train, lead)
    fit_features = add_ceiling_evidence_feature(fit)
    calibration_features = add_ceiling_evidence_feature(calibration)
    preprocessor = make_avg_preprocessor()
    x_fit = preprocessor.fit_transform(fit_features)
    x_cal = preprocessor.transform(calibration_features)
    active_fit = fit[f"l{lead}_meaningful"].astype(bool).to_numpy()
    active_calibration = calibration[f"l{lead}_meaningful"].astype(bool).to_numpy()
    if not active_fit.any():
        raise ValueError(f"lead {lead} has no meaningful rows for conditional average")

    y_fit = fit.loc[active_fit, f"l{lead}_avg"].to_numpy(float)
    y_cal = calibration.loc[active_calibration, f"l{lead}_avg"].to_numpy(float)

    alpha_scores: dict[float, float] = {}
    if active_calibration.any():
        for alpha in RIDGE_ALPHA_GRID:
            candidate = Ridge(alpha=float(alpha)).fit(x_fit[active_fit], y_fit)
            prediction = np.clip(candidate.predict(x_cal[active_calibration]), 0.0, 145.0)
            alpha_scores[float(alpha)] = float(np.mean(np.abs(prediction - y_cal)))
        selected_alpha = select_ridge_alpha(alpha_scores)
    else:
        selected_alpha = 10.0

    model = Ridge(alpha=float(selected_alpha)).fit(x_fit[active_fit], y_fit)

    if active_calibration.any():
        prediction = np.clip(model.predict(x_cal[active_calibration]), 0.0, 145.0)
        residual = y_cal - prediction
        residual_sd = float(np.std(residual, ddof=1)) if active_calibration.sum() > 2 else 12.0
    else:
        residual_sd = 12.0
    return AvgLayer(preprocessor, model, max(residual_sd, 3.0), float(selected_alpha), alpha_scores)


def train_lead(train: pd.DataFrame, lead: int) -> Task012Artifact:
    base = model_artifacts_zero_history.train_lead(train, lead)
    avg_layer = _fit_avg_layer(train, lead)
    artifact = Task012Artifact(
        lead=lead,
        base=base,
        avg_layer=avg_layer,
        avg_resid_sd=avg_layer.residual_sd,
    )
    artifact.selected_avg_alpha = avg_layer.selected_alpha
    artifact.avg_alpha_scores = avg_layer.alpha_scores
    return artifact


def predict(artifact: Task012Artifact, rows: pd.DataFrame) -> pd.DataFrame:
    out = model_artifacts_zero_history.predict(artifact.base, rows).copy()
    features = add_ceiling_evidence_feature(rows)
    x = artifact.avg_layer.preprocessor.transform(features)
    conditional_average = np.clip(artifact.avg_layer.model.predict(x), 0.0, 145.0)
    probability = out["p_meaningful"].to_numpy(float)
    conditional_games = out["cond_games"].to_numpy(float)
    out["cond_avg"] = conditional_average
    out["exp_avg"] = probability * conditional_average
    out["exp_points"] = probability * conditional_games * conditional_average
    out["model_id"] = "vnext_task047_pooled_ridge_conditional_average"
    return out
