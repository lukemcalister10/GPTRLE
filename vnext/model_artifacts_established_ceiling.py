"""TASK-012 evidence-weighted demonstrated-ceiling candidate.

Only the conditional-average feature representation changes. The accepted
TASK-009 meaningful-season event layer, conditional games model, elite-threshold
models and hybrid policy remain unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import SGDRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import model_artifacts
import model_artifacts_zero_history
from evaluate_v3_fast import CAT as BASE_CAT
from evaluate_v3_fast import NUM as BASE_NUM

FULL_EVIDENCE_GAMES = 50.0
AVG_MAX_ITER = 800


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
    iterations: int


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

    model = SGDRegressor(
        loss="huber",
        alpha=0.002,
        max_iter=AVG_MAX_ITER,
        tol=1e-3,
        random_state=lead + 20,
    ).fit(
        x_fit[active_fit],
        fit.loc[active_fit, f"l{lead}_avg"].to_numpy(float),
    )
    iterations = int(model.n_iter_)

    if active_calibration.any():
        prediction = np.clip(model.predict(x_cal[active_calibration]), 0.0, 145.0)
        residual = calibration.loc[
            active_calibration,
            f"l{lead}_avg",
        ].to_numpy(float) - prediction
        residual_sd = float(np.std(residual, ddof=1)) if active_calibration.sum() > 2 else 12.0
    else:
        residual_sd = 12.0
    return AvgLayer(preprocessor, model, max(residual_sd, 3.0), iterations)


def train_lead(train: pd.DataFrame, lead: int) -> Task012Artifact:
    base = model_artifacts_zero_history.train_lead(train, lead)
    avg_layer = _fit_avg_layer(train, lead)
    return Task012Artifact(
        lead=lead,
        base=base,
        avg_layer=avg_layer,
        avg_resid_sd=avg_layer.residual_sd,
    )


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
    out["model_id"] = "vnext_task012_established_ceiling"
    return out
