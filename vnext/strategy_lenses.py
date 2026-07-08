"""Transparent contender, balanced and rebuilder horizon aggregation.

The profiles in this module are diagnostic presets, not production policy. They all
retain greatest weight on the immediate/near future and operate on the same forecast
vector so strategy differences remain auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class StrategyLens:
    name: str
    horizon_weights: tuple[float, ...]
    risk_aversion: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("strategy name must be non-empty")
        if not self.horizon_weights:
            raise ValueError(f"horizon weights must be non-empty for {self.name}")
        if any((not isfinite(weight)) or weight < 0 for weight in self.horizon_weights):
            raise ValueError(f"horizon weights must be finite and non-negative for {self.name}")
        if not isclose(sum(self.horizon_weights), 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"horizon weights must sum to one for {self.name}")
        if not isfinite(self.risk_aversion) or self.risk_aversion < 0:
            raise ValueError(f"risk_aversion must be finite and non-negative for {self.name}")


# Five-season diagnostic presets. These are intentionally explicit and replaceable.
# Every profile remains anchored to observable near-term production; the rebuilder
# profile shifts weight later without awarding an independent youth bonus.
CONTENDER = StrategyLens(
    name="contender",
    horizon_weights=(0.50, 0.27, 0.13, 0.07, 0.03),
    risk_aversion=0.35,
)
BALANCED = StrategyLens(
    name="balanced",
    horizon_weights=(0.36, 0.25, 0.18, 0.13, 0.08),
    risk_aversion=0.25,
)
REBUILDER = StrategyLens(
    name="rebuilder",
    horizon_weights=(0.24, 0.24, 0.21, 0.17, 0.14),
    risk_aversion=0.18,
)

DEFAULT_LENSES: Mapping[str, StrategyLens] = {
    lens.name: lens for lens in (CONTENDER, BALANCED, REBUILDER)
}


def aggregate_forecast(
    expected_utility: Sequence[float],
    uncertainty: Sequence[float],
    lens: StrategyLens,
) -> float:
    """Aggregate one forecast vector with an explicit downside-risk penalty.

    ``uncertainty`` must be expressed in the same utility units as the expected
    vector. The penalty is linear and deliberately visible rather than hidden in the
    forecast model.
    """

    if len(expected_utility) != len(lens.horizon_weights):
        raise ValueError(
            f"expected utility length {len(expected_utility)} does not match "
            f"{lens.name} horizon length {len(lens.horizon_weights)}"
        )
    if len(uncertainty) != len(expected_utility):
        raise ValueError("uncertainty length must match expected utility length")
    if any(not isfinite(value) for value in expected_utility):
        raise ValueError("expected utility values must be finite")
    if any((not isfinite(value)) or value < 0 for value in uncertainty):
        raise ValueError("uncertainty values must be finite and non-negative")

    return sum(
        weight * (mean - lens.risk_aversion * spread)
        for mean, spread, weight in zip(
            expected_utility,
            uncertainty,
            lens.horizon_weights,
            strict=True,
        )
    )


def strategy_values(
    expected_utility: Sequence[float],
    uncertainty: Sequence[float],
    lenses: Mapping[str, StrategyLens] = DEFAULT_LENSES,
) -> dict[str, float]:
    """Return all declared strategy views from the same forecast distribution."""

    return {
        name: aggregate_forecast(expected_utility, uncertainty, lens)
        for name, lens in sorted(lenses.items())
    }


def contribution_breakdown(
    expected_utility: Sequence[float],
    uncertainty: Sequence[float],
    lens: StrategyLens,
) -> tuple[dict[str, float], ...]:
    """Expose annual mean, risk penalty, weight and final contribution."""

    if len(expected_utility) != len(lens.horizon_weights) or len(uncertainty) != len(expected_utility):
        raise ValueError("forecast, uncertainty and horizon lengths must match")
    rows = []
    for horizon, (mean, spread, weight) in enumerate(
        zip(expected_utility, uncertainty, lens.horizon_weights, strict=True),
        start=1,
    ):
        risk_penalty = lens.risk_aversion * spread
        rows.append(
            {
                "horizon": float(horizon),
                "expected_utility": float(mean),
                "uncertainty": float(spread),
                "risk_penalty": float(risk_penalty),
                "weight": float(weight),
                "contribution": float(weight * (mean - risk_penalty)),
            }
        )
    return tuple(rows)
