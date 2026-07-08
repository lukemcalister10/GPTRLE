"""Combine intrinsic three-lens values with finite budgeted scarcity premiums."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping

from player_comparison import PlayerComparison


@dataclass(frozen=True, slots=True)
class CombinedPlayerValue:
    player_id: str
    contender_intrinsic: float
    contender_scarcity: float
    contender_value: float
    balanced_intrinsic: float
    balanced_scarcity: float
    balanced_value: float
    rebuilder_intrinsic: float
    rebuilder_scarcity: float
    rebuilder_value: float

    def value_for(self, lens: str) -> float:
        if lens == "contender":
            return self.contender_value
        if lens == "balanced":
            return self.balanced_value
        if lens == "rebuilder":
            return self.rebuilder_value
        raise KeyError(lens)


def combine_player_values(
    intrinsic: Iterable[PlayerComparison],
    scarcity_by_lens: Mapping[str, Mapping[str, float]],
) -> tuple[CombinedPlayerValue, ...]:
    """Add owner-independent scarcity components to intrinsic values."""

    expected_lenses = {"contender", "balanced", "rebuilder"}
    if set(scarcity_by_lens) != expected_lenses:
        raise ValueError("scarcity_by_lens must contain contender, balanced and rebuilder")

    rows = tuple(intrinsic)
    if len({row.player_id for row in rows}) != len(rows):
        raise ValueError("player_id values must be unique")
    player_ids = {row.player_id for row in rows}
    for lens, values in scarcity_by_lens.items():
        unknown = set(values) - player_ids
        if unknown:
            raise ValueError(f"unknown scarcity player ids for {lens}: {sorted(unknown)}")
        for player_id, value in values.items():
            if not isfinite(value) or value < 0:
                raise ValueError(f"scarcity must be finite and non-negative for {player_id}")

    output = []
    for row in sorted(rows, key=lambda item: item.player_id):
        contender_scarcity = float(scarcity_by_lens["contender"].get(row.player_id, 0.0))
        balanced_scarcity = float(scarcity_by_lens["balanced"].get(row.player_id, 0.0))
        rebuilder_scarcity = float(scarcity_by_lens["rebuilder"].get(row.player_id, 0.0))
        output.append(
            CombinedPlayerValue(
                player_id=row.player_id,
                contender_intrinsic=row.contender_value,
                contender_scarcity=contender_scarcity,
                contender_value=row.contender_value + contender_scarcity,
                balanced_intrinsic=row.balanced_value,
                balanced_scarcity=balanced_scarcity,
                balanced_value=row.balanced_value + balanced_scarcity,
                rebuilder_intrinsic=row.rebuilder_value,
                rebuilder_scarcity=rebuilder_scarcity,
                rebuilder_value=row.rebuilder_value + rebuilder_scarcity,
            )
        )
    return tuple(output)


def rank_combined_players(
    players: Iterable[CombinedPlayerValue],
    *,
    lens: str,
) -> tuple[CombinedPlayerValue, ...]:
    rows = tuple(players)
    if len({row.player_id for row in rows}) != len(rows):
        raise ValueError("player_id values must be unique")
    return tuple(sorted(rows, key=lambda row: (-row.value_for(lens), row.player_id)))
