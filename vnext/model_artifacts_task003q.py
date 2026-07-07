from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

import model_artifacts
import model_artifacts_event_logistic
from task003q_hybrid import blend_predictions


@dataclass
class Task003QArtifact:
    lead: int
    current: Any
    candidate: Any

    def __getattr__(self, name: str) -> Any:
        return getattr(self.current, name)


def train_lead(train: pd.DataFrame, lead: int) -> Task003QArtifact:
    current = model_artifacts.train_lead(train, lead)
    candidate = model_artifacts_event_logistic.train_lead(train, lead)
    return Task003QArtifact(lead=lead, current=current, candidate=candidate)


def predict(artifact: Task003QArtifact, rows: pd.DataFrame) -> pd.DataFrame:
    current = model_artifacts.predict(artifact.current, rows)
    candidate = model_artifacts_event_logistic.predict(artifact.candidate, rows)
    current = current.copy()
    candidate = candidate.copy()
    current["player_key"] = rows["player_key"].to_numpy()
    current["origin_year"] = rows["origin_year"].to_numpy()
    current["lead"] = artifact.lead
    candidate["player_key"] = rows["player_key"].to_numpy()
    candidate["origin_year"] = rows["origin_year"].to_numpy()
    candidate["lead"] = artifact.lead
    return blend_predictions(current, candidate, rows)
