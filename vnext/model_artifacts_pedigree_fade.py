"""TASK-011 demonstrated-exposure pedigree-fade candidate."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

import model_artifacts_task003q

FULL_EVIDENCE_GAMES = 50.0
NEUTRAL_PICK = 80.0
ESTABLISHED_DRAFT_TYPE = "ESTABLISHED"


def fade_pedigree_features(rows: pd.DataFrame) -> pd.DataFrame:
    """Fade draft-pick signal smoothly to neutral by 50 observed AFL games.

    Draft pathway remains known until 50 games and then maps to one established
    category. All other origin-safe inputs are unchanged.
    """

    out = rows.copy()
    games = pd.to_numeric(out["total_games"], errors="coerce").fillna(0.0).clip(lower=0.0)
    retained = 1.0 - np.clip(
        games.to_numpy(float) / FULL_EVIDENCE_GAMES,
        0.0,
        1.0,
    )
    pick = pd.to_numeric(out["pick"], errors="coerce").fillna(NEUTRAL_PICK).to_numpy(float)
    pick = np.where(np.isfinite(pick) & (pick > 0), pick, NEUTRAL_PICK)
    out["pick"] = NEUTRAL_PICK + retained * (pick - NEUTRAL_PICK)
    draft_type = out["draft_type"].fillna("UNK").astype(str)
    out["draft_type"] = np.where(
        games.to_numpy(float) >= FULL_EVIDENCE_GAMES,
        ESTABLISHED_DRAFT_TYPE,
        draft_type,
    )
    return out


def train_lead(train: pd.DataFrame, lead: int) -> Any:
    return model_artifacts_task003q.train_lead(fade_pedigree_features(train), lead)


def predict(artifact: Any, rows: pd.DataFrame) -> pd.DataFrame:
    out = model_artifacts_task003q.predict(
        artifact,
        fade_pedigree_features(rows),
    ).copy()
    out["model_id"] = "vnext_task011_pedigree_fade"
    return out
