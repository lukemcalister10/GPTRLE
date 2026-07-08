"""Objective player-to-player comparison under three broad strategy lenses.

The primary valuation output is player-specific and league-wide.  Current team
ownership is deliberately excluded from the score so players remain directly
comparable in a live trading market.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


@dataclass(frozen=True, slots=True)
class PlayerComparison:
    player_id: str
    contender_value: float
    balanced_value: float
    rebuilder_value: float

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        for name in ("contender_value", "balanced_value", "rebuilder_value"):
            if not isfinite(getattr(self, name)):
                raise ValueError(f"{name} must be finite")

    def value_for(self, lens: str) -> float:
        if lens == "contender":
            return self.contender_value
        if lens == "balanced":
            return self.balanced_value
        if lens == "rebuilder":
            return self.rebuilder_value
        raise KeyError(lens)


def rank_players(
    players: Iterable[PlayerComparison],
    *,
    lens: str,
) -> tuple[PlayerComparison, ...]:
    """Rank players objectively for one declared strategy lens.

    Team ownership, current ladder position and specific roster composition are not
    accepted inputs.  Ties are broken deterministically by player id.
    """

    rows = tuple(players)
    if len({row.player_id for row in rows}) != len(rows):
        raise ValueError("player_id values must be unique")
    return tuple(sorted(rows, key=lambda row: (-row.value_for(lens), row.player_id)))


def compare_players(
    first: PlayerComparison,
    second: PlayerComparison,
    *,
    lens: str,
) -> float:
    """Return first player's objective advantage over second under one lens."""

    return first.value_for(lens) - second.value_for(lens)
