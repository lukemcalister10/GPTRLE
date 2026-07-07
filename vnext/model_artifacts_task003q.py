from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

import model_artifacts
import model_artifacts_event_logistic
from task003q_hybrid import blend_weight


@dataclass
class Task003QArtifact:
    lead: int
    current: Any
    candidate: Any

    def __getattr__(self, name):
        current = object.__getattribute__(self, "__dict__").get("current")
        if current is None:
            raise AttributeError(name)
        return getattr(current, name)


def train_lead(train: pd.DataFrame, lead: int) -> Task003QArtifact:
    return Task003QArtifact(
        lead=lead,
        current=model_artifacts.train_lead(train, lead),
        candidate=model_artifacts_event_logistic.train_lead(train, lead),
    )


def predict(artifact: Task003QArtifact, rows: pd.DataFrame) -> pd.DataFrame:
    current = model_artifacts.predict(artifact.current, rows).copy()
    candidate = model_artifacts_event_logistic.predict(artifact.candidate, rows)
    weight = blend_weight(rows["age"].to_numpy(float), np.full(len(rows), artifact.lead, dtype=int))
    for column in ("p_meaningful", "exp_games", "exp_points"):
        current[column] = current[column].to_numpy(float) + weight * (
            candidate[column].to_numpy(float) - current[column].to_numpy(float)
        )
    current["task003q_weight"] = weight
    current["model_id"] = "vnext_task003q_hybrid"
    return current
