"""Positive monotone risk discount for expected keeper utility.

The transform preserves positive expected value while applying stronger discounts as
uncertainty rises relative to the mean.  It is an isolated diagnostic alternative to
the current linear risk penalty.
"""

from __future__ import annotations

from math import exp, isfinite
from typing import Sequence

from strategy_lenses import StrategyLens


def discount_expected_utility(
    expected_utility: float,
    uncertainty: float,
    *,
    risk_aversion: float,
) -> float:
    """Return ``mean * exp(-risk_aversion * uncertainty / mean)``.

    The transform is always non-negative, equals the mean when uncertainty is zero and
    approaches zero continuously as relative uncertainty grows.  For small relative
    uncertainty it approximates the existing linear penalty through the first-order
    expansion of the exponential.
    """

    for value, name in (
        (expected_utility, "expected_utility"),
        (uncertainty, "uncertainty"),
        (risk_aversion, "risk_aversion"),
    ):
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if expected_utility < 0:
        raise ValueError("expected_utility must be non-negative")
    if uncertainty < 0:
        raise ValueError("uncertainty must be non-negative")
    if risk_aversion < 0:
        raise ValueError("risk_aversion must be non-negative")
    if expected_utility == 0:
        return 0.0
    return expected_utility * exp(-risk_aversion * uncertainty / expected_utility)


def aggregate_positive_risk(
    expected_utility: Sequence[float],
    uncertainty: Sequence[float],
    lens: StrategyLens,
) -> float:
    """Aggregate a complete forecast vector with the positive risk discount."""

    if len(expected_utility) != len(lens.horizon_weights):
        raise ValueError("expected utility length must match lens horizon")
    if len(uncertainty) != len(expected_utility):
        raise ValueError("uncertainty length must match expected utility length")
    return sum(
        weight
        * discount_expected_utility(
            mean,
            spread,
            risk_aversion=lens.risk_aversion,
        )
        for mean, spread, weight in zip(
            expected_utility,
            uncertainty,
            lens.horizon_weights,
            strict=True,
        )
    )
