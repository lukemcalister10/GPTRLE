"""Build the complete positive-risk plus budgeted-scarcity comparison export.

Usage:
    python vnext/run_task041_combined_export.py \
      --annual-candidate-csv reports/.../candidate_board_annual.csv \
      --output-dir reports/task-041-combined-export
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from budgeted_scarcity import allocate_scarcity_budgets
from combined_player_values import combine_player_values, rank_combined_players
from counterfactual_scarcity import relaxation_curve
from league_allocation import build_league_scoring_slots
from player_comparison import PlayerComparison
from player_eligibility_pivotality import eligibility_pivotality
from positive_risk_discount import aggregate_positive_risk
from roster_optimiser import PlayerUtility
from strategy_lenses import DEFAULT_LENSES

FORECAST_YEARS = (2027, 2028, 2029, 2030, 2031)
EXPECTED_PLAYERS = 804
BINDING_POSITIONS = ("KDEF", "RUC")
SOURCE_TO_UTILITY = {
    "G-DEF": "GDEF",
    "K-DEF": "KDEF",
    "MID": "MID",
    "RUCK": "RUC",
    "G-FWD": "GFWD",
    "K-FWD": "KFWD",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annual-candidate-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_positions(raw: str) -> frozenset[str]:
    positions = frozenset(SOURCE_TO_UTILITY[item.strip()] for item in raw.split(","))
    if not positions:
        raise ValueError("eligibility must be non-empty")
    return positions


def _load(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = pd.read_csv(path)
    required = {
        "stable_player_id", "player_name", "affl_team", "eligibilities",
        "forecast_year", "exp_points", "p_meaningful", "cond_games", "cond_avg",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"annual candidate file is missing columns: {missing}")
    if len(frame) != EXPECTED_PLAYERS * len(FORECAST_YEARS):
        raise ValueError(f"expected {EXPECTED_PLAYERS * len(FORECAST_YEARS)} annual rows")
    if tuple(sorted(frame["forecast_year"].unique())) != FORECAST_YEARS:
        raise ValueError("forecast years do not match the declared horizon")

    metadata_columns = ["stable_player_id", "player_name", "affl_team", "eligibilities"]
    metadata = frame[metadata_columns].drop_duplicates()
    if metadata["stable_player_id"].nunique() != EXPECTED_PLAYERS or len(metadata) != EXPECTED_PLAYERS:
        raise ValueError("player metadata must be constant and complete")

    probability = frame["p_meaningful"].astype(float)
    if ((probability < 0) | (probability > 1)).any():
        raise ValueError("p_meaningful must be between zero and one")
    conditional_points = frame["cond_games"].astype(float) * frame["cond_avg"].astype(float)
    frame = frame.copy()
    frame["uncertainty_proxy"] = conditional_points * np.sqrt(probability * (1 - probability))
    return frame, metadata


def _intrinsic_values(frame: pd.DataFrame) -> tuple[PlayerComparison, ...]:
    output = []
    for player_id, rows in frame.groupby("stable_player_id", sort=True):
        rows = rows.sort_values("forecast_year")
        expected = rows["exp_points"].astype(float).tolist()
        uncertainty = rows["uncertainty_proxy"].astype(float).tolist()
        values = {
            lens_name: aggregate_positive_risk(expected, uncertainty, lens)
            for lens_name, lens in DEFAULT_LENSES.items()
        }
        output.append(
            PlayerComparison(
                player_id=str(player_id),
                contender_value=values["contender"],
                balanced_value=values["balanced"],
                rebuilder_value=values["rebuilder"],
            )
        )
    return tuple(output)


def _scarcity_for_lens(
    comparisons: tuple[PlayerComparison, ...],
    metadata: pd.DataFrame,
    lens: str,
) -> tuple[dict[str, float], dict[str, float], dict[str, dict[str, float]]]:
    comparison_by_id = {row.player_id: row for row in comparisons}
    players = []
    for row in metadata.itertuples(index=False):
        value = getattr(comparison_by_id[str(row.stable_player_id)], f"{lens}_value")
        positions = _parse_positions(str(row.eligibilities))
        players.append(
            PlayerUtility(
                player_id=str(row.stable_player_id),
                utility=float(value),
                eligible_positions=positions,
                primary_position=sorted(positions)[0],
            )
        )

    slots = build_league_scoring_slots()
    budgets = {
        position: relaxation_curve(
            players,
            slots,
            position=position,
            max_relaxations=sum(
                1 for slot in slots if slot.accepted_positions == frozenset({position})
            ),
        )[-1].cumulative_cost
        for position in BINDING_POSITIONS
    }
    pivotality = {
        position: {
            player.player_id: eligibility_pivotality(
                players,
                slots,
                player_id=player.player_id,
                blocked_positions=frozenset({position}),
            ).league_utility_loss
            for player in players
            if position in player.eligible_positions
        }
        for position in BINDING_POSITIONS
    }
    allocations = allocate_scarcity_budgets(pivotality, budgets)
    premium = {row.player_id: row.total_premium for row in allocations}
    return premium, budgets, pivotality


def run(annual_candidate_csv: Path, output_dir: Path) -> dict[str, object]:
    frame, metadata = _load(annual_candidate_csv)
    comparisons = _intrinsic_values(frame)

    premiums: dict[str, dict[str, float]] = {}
    budgets: dict[str, dict[str, float]] = {}
    pivotality_counts: dict[str, dict[str, int]] = {}
    for lens in DEFAULT_LENSES:
        premium, lens_budgets, pivotality = _scarcity_for_lens(comparisons, metadata, lens)
        premiums[lens] = premium
        budgets[lens] = lens_budgets
        pivotality_counts[lens] = {
            position: sum(value > 0 for value in values.values())
            for position, values in pivotality.items()
        }

    combined = combine_player_values(comparisons, premiums)
    metadata_by_id = metadata.set_index("stable_player_id").to_dict("index")
    ranks = {
        lens: {
            row.player_id: rank
            for rank, row in enumerate(rank_combined_players(combined, lens=lens), start=1)
        }
        for lens in DEFAULT_LENSES
    }

    output_rows = []
    for row in rank_combined_players(combined, lens="balanced"):
        meta = metadata_by_id[row.player_id]
        output_rows.append({
            "player_id": row.player_id,
            "player_name": meta["player_name"],
            "positions": meta["eligibilities"],
            "current_owner": meta["affl_team"],
            "contender_intrinsic": row.contender_intrinsic,
            "contender_scarcity": row.contender_scarcity,
            "contender_value": row.contender_value,
            "contender_rank": ranks["contender"][row.player_id],
            "balanced_intrinsic": row.balanced_intrinsic,
            "balanced_scarcity": row.balanced_scarcity,
            "balanced_value": row.balanced_value,
            "balanced_rank": ranks["balanced"][row.player_id],
            "rebuilder_intrinsic": row.rebuilder_intrinsic,
            "rebuilder_scarcity": row.rebuilder_scarcity,
            "rebuilder_value": row.rebuilder_value,
            "rebuilder_rank": ranks["rebuilder"][row.player_id],
        })
    output = pd.DataFrame(output_rows)
    if len(output) != EXPECTED_PLAYERS:
        raise ValueError(f"expected {EXPECTED_PLAYERS} output rows")

    output_dir.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_dir / "combined_player_comparison_804.csv", index=False)
    metadata.sort_values("stable_player_id").to_csv(
        output_dir / "eligibility_snapshot_804.csv", index=False
    )

    summary = {
        "status": "diagnostic_only",
        "players": EXPECTED_PLAYERS,
        "forecast_years": list(FORECAST_YEARS),
        "input_sha256": _sha256(annual_candidate_csv),
        "risk_transform": "expected * exp(-risk_aversion * uncertainty / expected)",
        "uncertainty_proxy": "conditional_points * sqrt(p_meaningful * (1-p_meaningful))",
        "scarcity_budgets": budgets,
        "positive_pivotality_counts": pivotality_counts,
        "negative_values": {
            lens: int((output[f"{lens}_value"] < 0).sum()) for lens in DEFAULT_LENSES
        },
        "exact_zero_values": {
            lens: int((output[f"{lens}_value"] == 0).sum()) for lens in DEFAULT_LENSES
        },
        "owner_affects_value": False,
        "outputs": ["combined_player_comparison_804.csv", "eligibility_snapshot_804.csv"],
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return summary


def main() -> None:
    args = _parse_args()
    print(json.dumps(run(args.annual_candidate_csv, args.output_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
