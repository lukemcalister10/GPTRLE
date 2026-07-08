"""Asymmetric current-season evidence update.

This module is an isolated diagnostic adapter. It does not retrain the accepted
forecast model and is not wired into production. Performance and availability are
updated separately so a short scoring sample can add information without treating
missed games as equally strong negative evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class PartialSeasonUpdate:
    prior_scoring_rate: float
    observed_scoring_rate: float | None
    updated_scoring_rate: float
    scoring_credibility: float
    prior_availability_rate: float
    observed_availability_rate: float
    updated_availability_rate: float
    availability_credibility: float
    games_played: int
    rounds_observed: int


@dataclass(frozen=True, slots=True)
class PartialSeasonPolicy:
    scoring_prior_games: float = 8.0
    positive_availability_prior_rounds: float = 8.0
    negative_availability_prior_deficit: float = 22.0

    def __post_init__(self) -> None:
        values = (
            self.scoring_prior_games,
            self.positive_availability_prior_rounds,
            self.negative_availability_prior_deficit,
        )
        if any((not isfinite(value)) or value <= 0 for value in values):
            raise ValueError("policy strengths must be finite and positive")


DEFAULT_POLICY = PartialSeasonPolicy()


def _validate_rate(value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")


def update_partial_season(
    *,
    prior_scoring_rate: float,
    observed_scoring_rate: float | None,
    prior_availability_rate: float,
    games_played: int,
    rounds_observed: int,
    policy: PartialSeasonPolicy = DEFAULT_POLICY,
) -> PartialSeasonUpdate:
    """Blend recent scoring and availability with deliberately asymmetric evidence.

    Scoring credibility is ``games / (games + prior_games)``.

    Availability compares observed selection rate with the prior expectation. Positive
    evidence uses rounds observed. Negative evidence uses only the expected-game
    deficit and a much larger prior strength, so missed games do not receive a direct
    proportional penalty.
    """

    _validate_rate(prior_scoring_rate, "prior_scoring_rate")
    _validate_rate(prior_availability_rate, "prior_availability_rate")
    if observed_scoring_rate is not None:
        _validate_rate(observed_scoring_rate, "observed_scoring_rate")
    if not 0 <= prior_availability_rate <= 1:
        raise ValueError("prior_availability_rate must be between zero and one")
    if rounds_observed <= 0:
        raise ValueError("rounds_observed must be positive")
    if games_played < 0 or games_played > rounds_observed:
        raise ValueError("games_played must be between zero and rounds_observed")
    if games_played > 0 and observed_scoring_rate is None:
        raise ValueError("observed_scoring_rate is required when games_played is positive")

    if games_played == 0:
        scoring_credibility = 0.0
        updated_scoring_rate = prior_scoring_rate
    else:
        scoring_credibility = games_played / (games_played + policy.scoring_prior_games)
        updated_scoring_rate = (
            scoring_credibility * float(observed_scoring_rate)
            + (1.0 - scoring_credibility) * prior_scoring_rate
        )

    observed_availability_rate = games_played / rounds_observed
    difference = observed_availability_rate - prior_availability_rate

    if difference >= 0:
        availability_credibility = rounds_observed / (
            rounds_observed + policy.positive_availability_prior_rounds
        )
    else:
        expected_games = prior_availability_rate * rounds_observed
        deficit = max(0.0, expected_games - games_played)
        availability_credibility = deficit / (
            deficit + policy.negative_availability_prior_deficit
        )

    updated_availability_rate = prior_availability_rate + availability_credibility * difference
    updated_availability_rate = max(0.0, min(1.0, updated_availability_rate))

    return PartialSeasonUpdate(
        prior_scoring_rate=prior_scoring_rate,
        observed_scoring_rate=observed_scoring_rate,
        updated_scoring_rate=updated_scoring_rate,
        scoring_credibility=scoring_credibility,
        prior_availability_rate=prior_availability_rate,
        observed_availability_rate=observed_availability_rate,
        updated_availability_rate=updated_availability_rate,
        availability_credibility=availability_credibility,
        games_played=games_played,
        rounds_observed=rounds_observed,
    )
