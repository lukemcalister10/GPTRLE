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


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {
        "rows": int(len(frame)),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def build_locked_cohorts(out_dir: Path = DEFAULT_OUT) -> dict[str, Any]:
    resolver = DraftGuruEligibilityResolver()
    players = canonical_players(load_historical_players(PLAYER_DATA))
    player_keys = {str(player["key"]) for player in players}
    evidence_keys = set(resolver.database_keys["player_key"])
    if player_keys != evidence_keys:
        raise ValueError(
            "benchmark player universe differs from eligibility matrix: "
            f"missing={sorted(evidence_keys - player_keys)[:5]} "
            f"extra={sorted(player_keys - evidence_keys)[:5]}"
        )

    cohorts = build_evaluation_cohorts(players, eligibility_resolver=resolver)
    evidence = resolver.evidence_frame()

    included = cohorts["included"].merge(
        evidence,
        on=["player_key", "origin_year"],
        how="left",
        validate="one_to_one",
        suffixes=("", "_eligibility"),
    )
    if included["eligible"].isna().any() or not included["eligible"].all():
        raise ValueError("included snapshots are missing verified positive eligibility")

    membership = cohorts["targets"][PREDICTION_KEY].merge(
        evidence,
        on=["player_key", "origin_year"],
        how="left",
        validate="many_to_one",
    )
    if membership["eligible"].isna().any() or not membership["eligible"].all():
        raise ValueError("target cohort contains rows without verified positive eligibility")

    excluded = cohorts["excluded"].merge(
        evidence,
        on=["player_key", "origin_year"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_eligibility"),
    )

    counts = (
        membership.groupby(["origin_year", "lead"], as_index=False)
        .agg(players=("player_key", "nunique"), target_rows=("player_key", "size"))
        .sort_values(["origin_year", "lead"])
        .reset_index(drop=True)
    )
    exclusion_counts = (
        excluded.groupby(["origin_year", "lead", "reason"], dropna=False, as_index=False)
        .size()
        .rename(columns={"size": "rows"})
        .sort_values(["origin_year", "lead", "reason"])
        .reset_index(drop=True)
    )
