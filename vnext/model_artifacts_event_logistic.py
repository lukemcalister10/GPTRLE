"""TASK-003K meaningful-season classifier candidate.

Only the meaningful-season event classifier is replaced. The existing
preprocessor, temporal isotonic calibration method, conditional regressors,
threshold models, residual scales and prediction function remain unchanged.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from model_artifacts import make_calibrator
from model_artifacts import predict as predict_current
from model_artifacts import split_temporal
from model_artifacts import train_lead as train_current

EVENT_C = 0.35
EVENT_MAX_ITER = 500
EVENT_SOLVER = "lbfgs"
EVENT_TOL = 1e-4


def make_event_classifier() -> LogisticRegression:
    """Return the single predeclared TASK-003K event-model candidate."""

    return LogisticRegression(
        C=EVENT_C,
        max_iter=EVENT_MAX_ITER,
        solver=EVENT_SOLVER,
        penalty="l2",
        tol=EVENT_TOL,
    )


def replace_event_layer(
    artifact: Any,
    fit: pd.DataFrame,
    calibration: pd.DataFrame,
    lead: int,
) -> Any:
    """Replace only the event classifier and its temporal calibrator."""

    x_fit = artifact.preprocessor.transform(fit)
    x_cal = artifact.preprocessor.transform(calibration)
    y_fit = fit[f"l{lead}_meaningful"].astype(int).to_numpy()
    y_cal = calibration[f"l{lead}_meaningful"].astype(int).to_numpy()
    if len(np.unique(y_fit)) < 2:
        raise ValueError(f"lead {lead} event fit rows contain only one class")

    event_model = make_event_classifier().fit(x_fit, y_fit)
    iterations = int(np.max(event_model.n_iter_))
    if iterations >= EVENT_MAX_ITER:
        raise RuntimeError(
            f"lead {lead} event logistic reached max_iter={EVENT_MAX_ITER}"
        )
    raw_calibration = event_model.predict_proba(x_cal)[:, 1]
    artifact.event_model = event_model
    artifact.event_calibrator = make_calibrator(raw_calibration, y_cal)
    artifact.event_model_family = "LogisticRegression"
    artifact.event_model_spec = {
        "C": EVENT_C,
        "max_iter": EVENT_MAX_ITER,
        "solver": EVENT_SOLVER,
        "penalty": "l2",
        "tol": EVENT_TOL,
        "iterations": iterations,
    }
    artifact.task003k_single_change = "meaningful_season_event_classifier"
    return artifact


def train_lead(train: pd.DataFrame, lead: int) -> Any:
    """Train current vNext, then replace only its event classifier."""

    artifact = train_current(train, lead)
    fit, calibration = split_temporal(train, lead)
    return replace_event_layer(artifact, fit, calibration, lead)


def predict(artifact: Any, rows: pd.DataFrame) -> pd.DataFrame:
    """Use the unchanged current-vNext prediction composition."""

    return predict_current(artifact, rows)
