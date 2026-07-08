"""Build reproducible contender, balanced and rebuilder comparison exports.

The input is a long-form player forecast table.  The output is one row per player with
three objective values and three deterministic ranks.  Team ownership is metadata only
and is never accepted as a valuation input.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping, Sequence

from player_comparison import PlayerComparison, rank_players
from strategy_lenses import DEFAULT_LENSES, strategy_values


@dataclass(frozen=True, slots=True)
class ForecastValueRow:
    player_id: str
    forecast_year: int
    expected_utility: float
    uncertainty: float
    player_name: str | None = None
    positions: str | None = None
    current_owner: str | None = None

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        if self.forecast_year <= 0:
            raise ValueError("forecast_year must be positive")
        if not isfinite(self.expected_utility):
            raise ValueError("expected_utility must be finite")
        if not isfinite(self.uncertainty) or self.uncertainty < 0:
            raise ValueError("uncertainty must be finite and non-negative")


def build_player_comparisons(
    rows: Iterable[ForecastValueRow],
    *,
    forecast_years: Sequence[int],
) -> tuple[PlayerComparison, ...]:
    """Aggregate one complete forecast vector into three objective player values."""

    years = tuple(forecast_years)
    if len(years) != len(next(iter(DEFAULT_LENSES.values())).horizon_weights):
        raise ValueError("forecast_years must match the declared strategy horizon")
    if len(set(years)) != len(years) or tuple(sorted(years)) != years:
        raise ValueError("forecast_years must be unique and ascending")

    grouped: dict[str, list[ForecastValueRow]] = defaultdict(list)
    for row in rows:
        grouped[row.player_id].append(row)
    if not grouped:
        raise ValueError("no forecast rows supplied")

    comparisons: list[PlayerComparison] = []
    for player_id, player_rows in sorted(grouped.items()):
        by_year = {row.forecast_year: row for row in player_rows}
        if len(by_year) != len(player_rows):
            raise ValueError(f"duplicate forecast year for {player_id}")
        if tuple(sorted(by_year)) != years:
            raise ValueError(
                f"incomplete forecast horizon for {player_id}: "
                f"expected {years}, found {tuple(sorted(by_year))}"
            )
        values = strategy_values(
            [by_year[year].expected_utility for year in years],
            [by_year[year].uncertainty for year in years],
        )
        comparisons.append(
            PlayerComparison(
                player_id=player_id,
                contender_value=values["contender"],
                balanced_value=values["balanced"],
                rebuilder_value=values["rebuilder"],
            )
        )
    return tuple(comparisons)


def build_export_rows(
    forecast_rows: Iterable[ForecastValueRow],
    *,
    forecast_years: Sequence[int],
) -> tuple[dict[str, object], ...]:
    """Return one deterministic export row per player.

    Name, position and owner are copied as display metadata only.  Conflicting metadata
    for the same player fails explicitly rather than selecting an arbitrary row.
    """

    rows = tuple(forecast_rows)
    comparisons = build_player_comparisons(rows, forecast_years=forecast_years)
    metadata: dict[str, dict[str, str | None]] = {}
    for row in rows:
        candidate = {
            "player_name": row.player_name,
            "positions": row.positions,
            "current_owner": row.current_owner,
        }
        existing = metadata.setdefault(row.player_id, candidate)
        if existing != candidate:
            raise ValueError(f"conflicting display metadata for {row.player_id}")

    ranks: dict[str, dict[str, int]] = {lens: {} for lens in DEFAULT_LENSES}
    for lens in DEFAULT_LENSES:
        for rank, comparison in enumerate(rank_players(comparisons, lens=lens), start=1):
            ranks[lens][comparison.player_id] = rank

    output = []
    for comparison in rank_players(comparisons, lens="balanced"):
        meta = metadata[comparison.player_id]
        output.append(
            {
                "player_id": comparison.player_id,
                "player_name": meta["player_name"],
                "positions": meta["positions"],
                "current_owner": meta["current_owner"],
                "contender_value": comparison.contender_value,
                "contender_rank": ranks["contender"][comparison.player_id],
                "balanced_value": comparison.balanced_value,
                "balanced_rank": ranks["balanced"][comparison.player_id],
                "rebuilder_value": comparison.rebuilder_value,
                "rebuilder_rank": ranks["rebuilder"][comparison.player_id],
            }
        )
    return tuple(output)
