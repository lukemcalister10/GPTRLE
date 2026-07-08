"""Allocate finite league scarcity budgets across pivotal players.

Each position's total scarcity budget is measured externally through full constraint
relaxation.  Player-level pivotality scores are normalized within that position so the
allocated premiums sum exactly to the measured budget and cannot multiply the same
league constraint cost across many players.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Mapping


@dataclass(frozen=True, slots=True)
class PlayerScarcityAllocation:
    player_id: str
    position_premiums: Mapping[str, float]

    @property
    def total_premium(self) -> float:
        return float(sum(self.position_premiums.values()))


def allocate_position_budget(
    pivotality: Mapping[str, float],
    *,
    budget: float,
) -> dict[str, float]:
    """Allocate one position's finite budget in proportion to positive pivotality."""

    if not isfinite(budget) or budget < 0:
        raise ValueError("budget must be finite and non-negative")
    cleaned: dict[str, float] = {}
    for player_id, value in pivotality.items():
        if not player_id:
            raise ValueError("player_id must be non-empty")
        if not isfinite(value) or value < 0:
            raise ValueError(f"pivotality must be finite and non-negative for {player_id}")
        cleaned[player_id] = float(value)

    total_weight = sum(cleaned.values())
    if budget == 0:
        return {player_id: 0.0 for player_id in cleaned}
    if total_weight <= 0:
        raise ValueError("positive budget requires positive pivotality weight")

    allocations = {
        player_id: budget * weight / total_weight
        for player_id, weight in cleaned.items()
    }
    if not isclose(sum(allocations.values()), budget, rel_tol=0.0, abs_tol=1e-9):
        raise AssertionError("allocated premium does not conserve the scarcity budget")
    return allocations


def allocate_scarcity_budgets(
    pivotality_by_position: Mapping[str, Mapping[str, float]],
    budgets: Mapping[str, float],
) -> tuple[PlayerScarcityAllocation, ...]:
    """Allocate all declared position budgets and combine them by player."""

    if set(pivotality_by_position) != set(budgets):
        raise ValueError("pivotality positions must exactly match budget positions")

    by_player: dict[str, dict[str, float]] = {}
    for position in sorted(budgets):
        allocations = allocate_position_budget(
            pivotality_by_position[position],
            budget=float(budgets[position]),
        )
        for player_id, premium in allocations.items():
            by_player.setdefault(player_id, {})[position] = premium

    return tuple(
        PlayerScarcityAllocation(
            player_id=player_id,
            position_premiums=dict(sorted(position_values.items())),
        )
        for player_id, position_values in sorted(by_player.items())
    )
