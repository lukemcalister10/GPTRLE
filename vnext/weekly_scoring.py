"""Weekly scoring rules for selected lineups.

All 23 selected players score.  A captain receives double points.  The vice captain
receives the double-score bonus only when the captain does not play.  Emergencies are
not part of the selected scoring lineup unless explicitly activated by the manager.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class WeeklyPlayer:
    player_id: str
    score: float
    played: bool

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        if not isfinite(self.score):
            raise ValueError(f"score must be finite for {self.player_id}")


@dataclass(frozen=True, slots=True)
class WeeklyTeamScore:
    base_score: float
    captain_bonus: float
    total_score: float
    captain_used: str | None


def calculate_weekly_score(
    selected_players: Sequence[WeeklyPlayer],
    *,
    captain_id: str,
    vice_captain_id: str,
) -> WeeklyTeamScore:
    """Calculate the team score for the 23-player selected lineup."""

    if len({player.player_id for player in selected_players}) != len(selected_players):
        raise ValueError("selected player ids must be unique")
    by_id: Mapping[str, WeeklyPlayer] = {
        player.player_id: player for player in selected_players
    }
    if captain_id not in by_id:
        raise ValueError("captain must be in the selected lineup")
    if vice_captain_id not in by_id:
        raise ValueError("vice captain must be in the selected lineup")
    if captain_id == vice_captain_id:
        raise ValueError("captain and vice captain must differ")

    base_score = sum(player.score for player in selected_players if player.played)
    captain = by_id[captain_id]
    vice_captain = by_id[vice_captain_id]

    if captain.played:
        captain_bonus = captain.score
        captain_used = captain.player_id
    elif vice_captain.played:
        captain_bonus = vice_captain.score
        captain_used = vice_captain.player_id
    else:
        captain_bonus = 0.0
        captain_used = None

    return WeeklyTeamScore(
        base_score=base_score,
        captain_bonus=captain_bonus,
        total_score=base_score + captain_bonus,
        captain_used=captain_used,
    )


def expected_captain_bonus(
    *,
    captain_expected_score: float,
    captain_play_probability: float,
    vice_expected_score: float,
    vice_play_probability: float,
) -> float:
    """Expected bonus from captaincy with vice-captain fallback.

    The vice captain contributes the extra score only when the captain misses and the
    vice captain plays. Independence is an explicit approximation for this diagnostic
    expectation and can later be replaced by joint availability simulation.
    """

    for value, name in (
        (captain_expected_score, "captain_expected_score"),
        (vice_expected_score, "vice_expected_score"),
        (captain_play_probability, "captain_play_probability"),
        (vice_play_probability, "vice_play_probability"),
    ):
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if not 0 <= captain_play_probability <= 1:
        raise ValueError("captain_play_probability must be between zero and one")
    if not 0 <= vice_play_probability <= 1:
        raise ValueError("vice_play_probability must be between zero and one")

    captain_bonus = captain_play_probability * captain_expected_score
    fallback_bonus = (
        (1.0 - captain_play_probability)
        * vice_play_probability
        * vice_expected_score
    )
    return captain_bonus + fallback_bonus
