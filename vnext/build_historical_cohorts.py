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
ENTRY_FIELDS = ("year", "pick", "type", "_draft", "drafted_position")


def draft_year(player: dict[str, Any]) -> int:
    try:
        return int(player.get("year"))
    except (TypeError, ValueError):
        return 9999


def canonical_players(players: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse duplicate records while preserving the earliest repository entry."""

    grouped: dict[str, list[dict[str, Any]]] = {}
    for player in players:
        key = str(player.get("key") or "").strip()
        if key:
            grouped.setdefault(key, []).append(player)

    canonical = []
    for _, group in sorted(grouped.items()):
        richest = max(group, key=lambda row: len(row.get("scoring") or []))
        earliest = min(group, key=lambda row: (draft_year(row), str(row.get("type") or "")))
        merged = dict(richest)
        for field in ENTRY_FIELDS:
            value = earliest.get(field)
            if value not in (None, ""):
                merged[field] = value
        merged["_source_record_count"] = len(group)
        canonical.append(merged)
    return canonical


def align_entries_to_verified_history(
    players: list[dict[str, Any]], evidence: pd.DataFrame
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    """Neutralise later-entry draft facts when verified list history starts earlier."""

    first_listed = (
        evidence[evidence["eligible"]]
        .groupby("player_key", as_index=True)["origin_year"]
        .min()
        .astype(int)
        .to_dict()
    )
    aligned = []
    corrections = []
    for player in players:
        key = str(player["key"])
        first_year = first_listed.get(key)
        repository_year = draft_year(player)
        if first_year is not None and repository_year > first_year:
            corrected = dict(player)
            corrected["year"] = int(first_year)
            corrected["pick"] = 80
            corrected["type"] = "UNK"
            corrected["_draft"] = "UNK"
            corrected["drafted_position"] = "UNK"
            aligned.append(corrected)
            corrections.append(
                {
                    "player_key": key,
                    "player": str(player.get("player") or ""),
                    "repository_draft_year": repository_year,
                    "verified_first_list_year": int(first_year),
                    "corrected_draft_year": int(first_year),
                    "corrected_pick": 80,
                    "corrected_draft_type": "UNK",
                    "reason": "verified_list_presence_precedes_repository_entry",
                }
            )
        else:
            aligned.append(player)
    return aligned, pd.DataFrame(corrections)


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {
        "rows": int(len(frame)),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def build_locked_cohorts(out_dir: Path = DEFAULT_OUT) -> dict[str, Any]:
    resolver = DraftGuruEligibilityResolver()
    evidence = resolver.evidence_frame()
    players = canonical_players(load_historical_players(PLAYER_DATA))
    players, entry_corrections = align_entries_to_verified_history(players, evidence)
    player_keys = {str(player["key"]) for player in players}
    evidence_keys = set(resolver.database_keys["player_key"])
    if player_keys != evidence_keys:
        raise ValueError(
            "benchmark player universe differs from eligibility matrix: "
            f"missing={sorted(evidence_keys - player_keys)[:5]} "
            f"extra={sorted(player_keys - evidence_keys)[:5]}"
        )

    cohorts = build_evaluation_cohorts(players, eligibility_resolver=resolver)

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
    unexpected = excluded[excluded["reason"] != "draftguru_verified_absence"]
    if len(unexpected):
        sample = unexpected[["player_key", "origin_year", "lead", "reason"]].head(10).to_dict("records")
        raise ValueError(f"verified eligible rows failed cohort construction: {sample}")

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

    frames = {
        "fold_plan": cohorts["fold_plan"].sort_values(["origin_year", "lead"]).reset_index(drop=True),
        "included_snapshots": included.sort_values(["origin_year", "player_key"]).reset_index(drop=True),
        "cohort_membership": membership.sort_values(PREDICTION_KEY).reset_index(drop=True),
        "targets": cohorts["targets"].sort_values(PREDICTION_KEY).reset_index(drop=True),
        "excluded": excluded.sort_values(["origin_year", "lead", "player_key"]).reset_index(drop=True),
        "target_failures": cohorts["target_failures"].sort_values(["origin_year", "lead", "player_key"]).reset_index(drop=True),
        "cohort_counts": counts,
        "exclusion_counts": exclusion_counts,
        "identity_exclusions": resolver.identity_exclusions.sort_values(["season", "player_name"]).reset_index(drop=True),
        "entry_corrections": entry_corrections.sort_values(["player_key"]).reset_index(drop=True),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, frame in frames.items():
        artifacts[f"{name}.csv"] = write_csv(out_dir / f"{name}.csv", frame)

    manifest = {
        "task": "TASK-003A-HISTORICAL-ELIGIBILITY-COHORTS",
        "folds": LOCKED_FOLDS,
        "eligibility_source": "DraftGuru reviewed annual AFL club lists",
        "eligibility_matrix_sha256": resolver.matrix_sha256,
        "player_data_sha256": hashlib.sha256(PLAYER_DATA.read_bytes()).hexdigest(),
        "database_unique_keys": int(len(player_keys)),
        "included_snapshot_rows": int(len(included)),
        "target_rows": int(len(cohorts["targets"])),
        "excluded_rows": int(len(excluded)),
        "target_failure_rows": int(len(cohorts["target_failures"])),
        "identity_exclusion_rows": int(len(resolver.identity_exclusions)),
        "entry_correction_rows": int(len(entry_corrections)),
        "reproduction_command": "python vnext/build_historical_cohorts.py --out build/task-003-cohorts",
        "artifacts": artifacts,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    manifest = build_locked_cohorts(args.out)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
