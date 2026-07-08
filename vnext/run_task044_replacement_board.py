"""Build a complete replacement-aware immediate-lineup diagnostic board."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from league_allocation import build_league_scoring_slots
from replacement_lineup_value import annual_replacement_value, best_replacement_average
from strategy_lenses import DEFAULT_LENSES

EXPECTED_PLAYERS = 804
FORECAST_YEARS = (2027, 2028, 2029, 2030, 2031)
SOURCE_TO_UTILITY = {
    "G-DEF": "GDEF", "K-DEF": "KDEF", "MID": "MID",
    "RUCK": "RUC", "G-FWD": "GFWD", "K-FWD": "KFWD",
}


def _parse_positions(raw: str) -> frozenset[str]:
    return frozenset(SOURCE_TO_UTILITY[item.strip()] for item in raw.split(","))


def _replacement_levels(frame: pd.DataFrame) -> dict[int, dict[str, float]]:
    slots = build_league_scoring_slots()
    output: dict[int, dict[str, float]] = {}
    for year, annual in frame.groupby("forecast_year"):
        annual = annual.reset_index(drop=True)
        positions = [_parse_positions(value) for value in annual["eligibilities"]]
        cost = np.full((len(annual), len(slots)), 1e12, dtype=float)
        for player_index, (average, eligible) in enumerate(zip(annual["cond_avg"], positions, strict=True)):
            for slot_index, slot in enumerate(slots):
                if not eligible.isdisjoint(slot.accepted_positions):
                    cost[player_index, slot_index] = -float(average)
        rows, columns = linear_sum_assignment(cost)
        selected = set(rows)
        if len(columns) != len(slots) or np.any(cost[rows, columns] >= 1e11):
            raise ValueError(f"cannot fill annual league lineup for {year}")
        output[int(year)] = {}
        for position in SOURCE_TO_UTILITY.values():
            candidates = [
                float(annual.iloc[index]["cond_avg"])
                for index in range(len(annual))
                if index not in selected and position in positions[index]
            ]
            if not candidates:
                raise ValueError(f"no unselected replacement for {position} in {year}")
            output[int(year)][position] = max(candidates)
    return output


def run(annual_candidate_csv: Path, output_dir: Path) -> dict[str, object]:
    frame = pd.read_csv(annual_candidate_csv)
    required = {"stable_player_id", "player_name", "affl_team", "eligibilities", "forecast_year", "exp_games", "cond_avg"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if len(frame) != EXPECTED_PLAYERS * len(FORECAST_YEARS):
        raise ValueError("annual candidate file must contain exactly 804 complete five-year vectors")
    if tuple(sorted(frame["forecast_year"].unique())) != FORECAST_YEARS:
        raise ValueError("unexpected forecast horizon")

    replacements = _replacement_levels(frame)
    rows = []
    for player_id, player in frame.groupby("stable_player_id", sort=True):
        player = player.sort_values("forecast_year")
        annual_values = []
        startable_values = []
        for source in player.itertuples(index=False):
            replacement = best_replacement_average(
                _parse_positions(str(source.eligibilities)),
                replacements[int(source.forecast_year)],
            )
            value = annual_replacement_value(
                expected_active_games=float(source.exp_games),
                conditional_average=float(source.cond_avg),
                replacement_average=replacement,
            ).value_above_replacement
            annual_values.append(value)
            startable_values.append(max(0.0, value))
        record = {
            "player_id": str(player_id),
            "player_name": player.iloc[0]["player_name"],
            "positions": player.iloc[0]["eligibilities"],
            "current_owner": player.iloc[0]["affl_team"],
        }
        for lens_name, lens in DEFAULT_LENSES.items():
            record[f"{lens_name}_lineup_value"] = sum(
                value * weight for value, weight in zip(annual_values, lens.horizon_weights, strict=True)
            )
            record[f"{lens_name}_startable_value"] = sum(
                value * weight for value, weight in zip(startable_values, lens.horizon_weights, strict=True)
            )
        rows.append(record)

    output = pd.DataFrame(rows)
    for lens in DEFAULT_LENSES:
        output[f"{lens}_lineup_rank"] = output[f"{lens}_lineup_value"].rank(method="first", ascending=False).astype(int)
        output[f"{lens}_startable_rank"] = output[f"{lens}_startable_value"].rank(method="min", ascending=False).astype(int)
    output = output.sort_values(["balanced_lineup_rank", "player_id"])

    output_dir.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_dir / "replacement_aware_player_board_804.csv", index=False)
    with (output_dir / "replacement_levels.json").open("w", encoding="utf-8") as handle:
        json.dump(replacements, handle, indent=2, sort_keys=True)
        handle.write("\n")

    summary = {
        "status": "diagnostic_only",
        "players": EXPECTED_PLAYERS,
        "replacement_levels": replacements,
        "negative_lineup_values": {
            lens: int((output[f"{lens}_lineup_value"] < 0).sum()) for lens in DEFAULT_LENSES
        },
        "zero_startable_values": {
            lens: int((output[f"{lens}_startable_value"] == 0).sum()) for lens in DEFAULT_LENSES
        },
        "owner_affects_value": False,
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annual-candidate-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.annual_candidate_csv, args.output_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
