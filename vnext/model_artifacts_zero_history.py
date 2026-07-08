"""TASK-009 origin-safe zero-history state-separation candidate.

The accepted TASK-003Q model remains intact except for the feature representation
used by its two meaningful-season event classifiers. Conditional games, conditional
average, elite-threshold models, residual scales and the age/lead hybrid policy are
unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import model_artifacts
import model_artifacts_task003q
from evaluate_v3_fast import CAT as BASE_CAT
from evaluate_v3_fast import NUM as BASE_NUM
from task003q_hybrid import blend_weight

EVENT_C = 0.35
EVENT_MAX_ITER = 500
EVENT_TOL = 1e-4


def _pathway_group(value: Any) -> str:
    code = str(value or "UNK").strip().upper()
    if code == "ND":
        return "national"
    if code == "RD":
        return "rookie"
    if code in {"MSD", "SSP", "PDN", "PDA", "PSD"}:
        return "supplemental"
    if code in {"UNR", "IRE"}:
        return "alternative"
    return "unknown"


def _pick_bucket(value: Any) -> str:
    try:
        pick = float(value)
    except (TypeError, ValueError):
        pick = 100.0
    if not np.isfinite(pick) or pick <= 0:
        pick = 100.0
    if pick <= 10:
        return "1-10"
    if pick <= 30:
        return "11-30"
    if pick <= 60:
        return "31-60"
    return "61+/undrafted"


def _tenure_bucket(value: Any) -> str:
    try:
        tenure = int(float(value))
    except (TypeError, ValueError):
        tenure = 0
    if tenure <= 0:
        return "t0"
    if tenure == 1:
        return "t1"
    if tenure == 2:
        return "t2"
    return "t3+"


def add_zero_history_features(rows: pd.DataFrame) -> pd.DataFrame:
    """Add only origin-safe draft and observed-history interactions."""

    out = rows.copy()
    games = pd.to_numeric(out["total_games"], errors="coerce").fillna(0.0)
    zero = games.eq(0.0)
    tenure = out["tenure"].map(_tenure_bucket)
    pathway = out["draft_type"].map(_pathway_group)
    pick = out["pick"].map(_pick_bucket)

    out["zero_history_flag"] = zero.astype(float)
    out["zero_history_tenure"] = np.where(zero, tenure, "played")
    out["zero_history_state"] = np.where(
        zero,
        "zero|" + tenure.astype(str) + "|" + pathway.astype(str) + "|" + pick.astype(str),
        "played",
    )
    return out


def make_event_preprocessor() -> ColumnTransformer:
    numeric = list(BASE_NUM) + ["zero_history_flag"]
    categorical = list(BASE_CAT) + ["zero_history_tenure", "zero_history_state"]
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
                categorical,
            ),
        ]
    )


@dataclass
class EventLayer:
    preprocessor: Any
    model: Any
    calibrator: Any
    family: str
    iterations: int


@dataclass
class Task009Artifact:
    lead: int
    base: Any
    current_event: EventLayer
    logistic_event: EventLayer

    def __getattr__(self, name: str) -> Any:
        base = object.__getattribute__(self, "__dict__").get("base")
        if base is None:
            raise AttributeError(name)
        return getattr(base, name)


def _fit_event_layer(
    train: pd.DataFrame,
    lead: int,
    family: Literal["sgd", "logistic"],
) -> EventLayer:
    fit, calibration = model_artifacts.split_temporal(train, lead)
    fit_features = add_zero_history_features(fit)
    calibration_features = add_zero_history_features(calibration)
    preprocessor = make_event_preprocessor()
    x_fit = preprocessor.fit_transform(fit_features)
    x_cal = preprocessor.transform(calibration_features)
    y_fit = fit[f"l{lead}_meaningful"].astype(int).to_numpy()
    y_cal = calibration[f"l{lead}_meaningful"].astype(int).to_numpy()
    if len(np.unique(y_fit)) < 2:
        raise ValueError(f"lead {lead} event fit rows contain only one class")

    if family == "sgd":
        model = SGDClassifier(
            loss="log_loss",
            alpha=0.0008,
            max_iter=800,
            tol=1e-3,
            random_state=lead,
        ).fit(x_fit, y_fit)
    else:
        model = LogisticRegression(
            C=EVENT_C,
            max_iter=EVENT_MAX_ITER,
            solver="lbfgs",
            penalty="l2",
            tol=EVENT_TOL,
        ).fit(x_fit, y_fit)

    iterations = int(np.max(model.n_iter_))
    limit = 800 if family == "sgd" else EVENT_MAX_ITER
    if iterations >= limit:
        raise RuntimeError(f"lead {lead} {family} event model reached max_iter={limit}")
    raw_calibration = model.predict_proba(x_cal)[:, 1]
    calibrator = model_artifacts.make_calibrator(raw_calibration, y_cal)
    return EventLayer(preprocessor, model, calibrator, family, iterations)


def _predict_event(layer: EventLayer, rows: pd.DataFrame) -> np.ndarray:
    features = add_zero_history_features(rows)
    x = layer.preprocessor.transform(features)
    raw = layer.model.predict_proba(x)[:, 1]
    return np.clip(layer.calibrator.predict(raw), 0.001, 0.999)


def train_lead(train: pd.DataFrame, lead: int) -> Task009Artifact:
    return Task009Artifact(
        lead=lead,
        base=model_artifacts_task003q.train_lead(train, lead),
        current_event=_fit_event_layer(train, lead, "sgd"),
        logistic_event=_fit_event_layer(train, lead, "logistic"),
    )


def predict(artifact: Task009Artifact, rows: pd.DataFrame) -> pd.DataFrame:
    out = model_artifacts_task003q.predict(artifact.base, rows).copy()
    current_p = _predict_event(artifact.current_event, rows)
    logistic_p = _predict_event(artifact.logistic_event, rows)
    weight = blend_weight(
        rows["age"].to_numpy(float),
        np.full(len(rows), artifact.lead, dtype=int),
    )
    probability = np.clip(current_p + weight * (logistic_p - current_p), 0.001, 0.999)

    out["p_meaningful"] = probability
    out["exp_games"] = probability * out["cond_games"].to_numpy(float)
    out["exp_avg"] = probability * out["cond_avg"].to_numpy(float)
    out["exp_points"] = (
        probability
        * out["cond_games"].to_numpy(float)
        * out["cond_avg"].to_numpy(float)
    )
    out["task003q_weight"] = weight
    out["model_id"] = "vnext_task009_zero_history_state"
    return out
