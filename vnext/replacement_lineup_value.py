"""Replacement-aware seasonal lineup value.

Missed games are credited with replacement scoring.  Relative to a replacement-only
baseline, a player's contribution is expected active games multiplied by the gap
between the player's conditional average and the replacement average.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class AnnualReplacementValue:
    expected_active_games: float
    conditional_average: float
    replacement_average: float
    lineup_points_with_player: float
    replacement_only_points: float
    value_above_replacement: float


def annual_replacement_value(
    *,
    expected_active_games: float,
    conditional_average: float,
    replacement_average: float,
    season_games: float = 23.0,
) -> AnnualReplacementValue:
    """Return expected lineup output and value above replacement for one season.

    ``lineup_points_with_player`` credits replacement scoring in games the player is
    unavailable.  ``value_above_replacement`` is therefore the player's marginal
    contribution over using the replacement for every game.
    """

    values = {
        "expected_active_games": expected_active_games,
        "conditional_average": conditional_average,
        "replacement_average": replacement_average,
        "season_games": season_games,
    }
    for name, value in values.items():
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if season_games <= 0:
        raise ValueError("season_games must be positive")
    if not 0 <= expected_active_games <= season_games:
        raise ValueError("expected_active_games must be between zero and season_games")
    if conditional_average < 0 or replacement_average < 0:
        raise ValueError("averages must be non-negative")

    missed_games = season_games - expected_active_games
    lineup_points = (
        expected_active_games * conditional_average
        + missed_games * replacement_average
    )
    replacement_only = season_games * replacement_average
    contribution = expected_active_games * (
        conditional_average - replacement_average
    )
    return AnnualReplacementValue(
        expected_active_games=expected_active_games,
        conditional_average=conditional_average,
        replacement_average=replacement_average,
        lineup_points_with_player=lineup_points,
        replacement_only_points=replacement_only,
        value_above_replacement=contribution,
    )


def best_replacement_average(
    eligible_positions: frozenset[str],
    replacement_by_position: Mapping[str, float],
) -> float:
    """Return the lowest replacement hurdle available through current eligibility.

    A multi-position player can be deployed where the legal replacement is weakest.
    This is an asymmetric eligibility benefit rather than a generic DPP bonus.
    """

    if not eligible_positions:
        raise ValueError("eligible_positions must be non-empty")
    missing = eligible_positions - set(replacement_by_position)
    if missing:
        raise KeyError(f"missing replacement averages for {sorted(missing)}")
    candidates = [float(replacement_by_position[pos]) for pos in eligible_positions]
    if any(not isfinite(value) or value < 0 for value in candidates):
        raise ValueError("replacement averages must be finite and non-negative")
    return min(candidates)


def aggregate_replacement_value(
    annual_values: Sequence[float],
    horizon_weights: Sequence[float],
) -> float:
    """Aggregate annual marginal lineup contributions across forecast horizons."""

    if len(annual_values) != len(horizon_weights):
        raise ValueError("annual values and horizon weights must have equal length")
    if not annual_values:
        raise ValueError("annual values must be non-empty")
    if any(not isfinite(value) for value in annual_values):
        raise ValueError("annual values must be finite")
    if any(not isfinite(weight) or weight < 0 for weight in horizon_weights):
        raise ValueError("horizon weights must be finite and non-negative")
    if abs(sum(horizon_weights) - 1.0) > 1e-9:
        raise ValueError("horizon weights must sum to one")
    return float(sum(value * weight for value, weight in zip(annual_values, horizon_weights, strict=True)))
