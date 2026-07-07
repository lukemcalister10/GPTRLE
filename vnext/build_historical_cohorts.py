"""Build locked TASK-003 cohorts from reviewed historical eligibility."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from benchmark import LOCKED_FOLDS, PREDICTION_KEY, build_evaluation_cohorts
from historical_eligibility import DraftGuruEligibilityResolver, ROOT, load_historical_players

DEFAULT_OUT = ROOT / "build" / "task-003-cohorts"
PLAYER_DATA = ROOT / "engine" / "rl_after" / "rl_model_data.json"


def canonical_players(players: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for player in players:
        key = str(player.get("key") or "").strip()
        if key:
            grouped.setdefault(key, []).append(player)
    canonical = []
    for _, group in sorted(grouped.items()):
        canonical.append(max(group, key=lambda row: len(row.get("scoring") or [])))
    return canonical
