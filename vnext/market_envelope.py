"""League market envelope for strategy-dependent player values.

A player's trade opportunity is based on the value available to plausible buyers,
not only the value the player creates on the current roster.  This module deliberately
keeps market value, current-roster fit and realised trade opportunity separate.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class StrategyValues:
    contender: float
    balanced: float
    rebuilder: float

    def __post_init__(self) -> None:
        for name in ("contender", "balanced", "rebuilder"):
            if not isfinite(getattr(self, name)):
                raise ValueError(f"{name} value must be finite")

    def ordered(self) -> tuple[float, float, float]:
        return tuple(sorted((self.contender, self.balanced, self.rebuilder), reverse=True))


@dataclass(frozen=True, slots=True)
class MarketEnvelopePolicy:
    best_use_weight: float = 0.70
    second_best_use_weight: float = 0.30
    liquidity: float = 0.75

    def __post_init__(self) -> None:
        for name in ("best_use_weight", "second_best_use_weight", "liquidity"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if abs(self.best_use_weight + self.second_best_use_weight - 1.0) > 1e-12:
            raise ValueError("best and second-best weights must sum to one")
        if self.liquidity > 1:
            raise ValueError("liquidity cannot exceed one")


DEFAULT_MARKET_POLICY = MarketEnvelopePolicy()


@dataclass(frozen=True, slots=True)
class MarketOpportunity:
    market_value: float
    current_roster_value: float
    gross_surplus: float
    realisable_trade_opportunity: float


def market_value(
    values: StrategyValues,
    policy: MarketEnvelopePolicy = DEFAULT_MARKET_POLICY,
) -> float:
    """Estimate league value from the player's two strongest plausible uses.

    The best-use value is not accepted at 100 cents on the dollar because a single
    ideal buyer may not exist.  The second-best strategy provides a simple breadth-of-
    demand adjustment without requiring historical fantasy trades as truth labels.
    """

    best, second, _third = values.ordered()
    return policy.best_use_weight * best + policy.second_best_use_weight * second


def trade_opportunity(
    values: StrategyValues,
    *,
    current_roster_value: float,
    policy: MarketEnvelopePolicy = DEFAULT_MARKET_POLICY,
) -> MarketOpportunity:
    """Return the potentially realisable value stranded on the current roster."""

    if not isfinite(current_roster_value):
        raise ValueError("current_roster_value must be finite")
    market = market_value(values, policy)
    gross = max(0.0, market - current_roster_value)
    return MarketOpportunity(
        market_value=market,
        current_roster_value=current_roster_value,
        gross_surplus=gross,
        realisable_trade_opportunity=policy.liquidity * gross,
    )
