"""Authoritative current-season exposure context for the 2026 partial season."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CurrentSeasonContext:
    season: int
    rounds_elapsed: int
    matches_available_per_player: int

    def __post_init__(self) -> None:
        if self.season <= 0:
            raise ValueError("season must be positive")
        if self.rounds_elapsed <= 0:
            raise ValueError("rounds_elapsed must be positive")
        if self.matches_available_per_player <= 0:
            raise ValueError("matches_available_per_player must be positive")
        if self.matches_available_per_player > self.rounds_elapsed:
            raise ValueError("matches available cannot exceed rounds elapsed")


CURRENT_2026_CONTEXT = CurrentSeasonContext(
    season=2026,
    rounds_elapsed=14,
    matches_available_per_player=13,
)
