"""Generate the first complete objective contender/balanced/rebuilder table.

Usage:
    python vnext/run_task031_player_comparison.py \
        --annual-candidate-csv reports/.../candidate_board_annual.csv \
        --output-dir reports/task-031-player-comparison
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from player_comparison_export import ForecastValueRow, build_export_rows

FORECAST_YEARS = (2027, 2028, 2029, 2030, 2031)
EXPECTED_PLAYERS = 804


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annual-candidate-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def _load_rows(path: Path) -> tuple[ForecastValueRow, ...]:
    frame = pd.read_csv(path)
    required = {
        "stable_player_id",
        "player_name",
        "affl_team",
        "eligibilities",
        "forecast_year",
        "exp_points",
        "p_meaningful",
        "cond_games",
        "cond_avg",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"annual candidate file is missing columns: {missing}")

    conditional_points = frame["cond_games"].astype(float) * frame["cond_avg"].astype(float)
    probability = frame["p_meaningful"].astype(float)
    if ((probability < 0) | (probability > 1)).any():
        raise ValueError("p_meaningful must be between zero and one")
    uncertainty = conditional_points * np.sqrt(probability * (1.0 - probability))

    rows = []
    for index, source in frame.iterrows():
        rows.append(
            ForecastValueRow(
                player_id=str(source["stable_player_id"]),
                forecast_year=int(source["forecast_year"]),
                expected_utility=float(source["exp_points"]),
                uncertainty=float(uncertainty.loc[index]),
                player_name=str(source["player_name"]),
                positions=str(source["eligibilities"]),
                current_owner=str(source["affl_team"]),
            )
        )
    return tuple(rows)


def _rank_set(frame: pd.DataFrame, lens: str, n: int = 100) -> set[str]:
    return set(frame.nsmallest(n, f"{lens}_rank")["player_id"].astype(str))


def run(annual_candidate_csv: Path, output_dir: Path) -> dict[str, object]:
    rows = _load_rows(annual_candidate_csv)
    export_rows = build_export_rows(rows, forecast_years=FORECAST_YEARS)
    output = pd.DataFrame(export_rows)
    if len(output) != EXPECTED_PLAYERS:
        raise ValueError(f"expected {EXPECTED_PLAYERS} players, found {len(output)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "player_comparison_804.csv"
    output.to_csv(output_path, index=False)

    top100 = {lens: _rank_set(output, lens) for lens in ("contender", "balanced", "rebuilder")}
    summary = {
        "status": "diagnostic_only",
        "players": int(len(output)),
        "forecast_years": list(FORECAST_YEARS),
        "owner_affects_value": False,
        "uncertainty_proxy": "conditional_points * sqrt(p_meaningful * (1-p_meaningful))",
        "top100_overlap": {
            "contender_balanced": len(top100["contender"] & top100["balanced"]),
            "balanced_rebuilder": len(top100["balanced"] & top100["rebuilder"]),
            "contender_rebuilder": len(top100["contender"] & top100["rebuilder"]),
        },
        "rank_correlations": {
            "contender_balanced": float(output["contender_rank"].corr(output["balanced_rank"], method="spearman")),
            "balanced_rebuilder": float(output["balanced_rank"].corr(output["rebuilder_rank"], method="spearman")),
            "contender_rebuilder": float(output["contender_rank"].corr(output["rebuilder_rank"], method="spearman")),
        },
        "output": str(output_path),
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
