"""Exact player-level positional eligibility pivotality.

The diagnostic removes a player's ability to fill selected constrained positions while
preserving their ability to occupy unrestricted scoring slots, then re-optimises the
full league.  It measures whether that eligibility is pivotal, not a directly additive
scarcity premium.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment

from league_config import ALL_POSITIONS
from roster_optimiser import PlayerUtility, RosterSlot


@dataclass(frozen=True, slots=True)
class EligibilityPivotality:
    player_id: str
    blocked_positions: frozenset[str]
    league_utility_loss: float


def _cost_matrix(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
    *,
    blocked_player_id: str | None = None,
    blocked_positions: frozenset[str] = frozenset(),
) -> np.ndarray:
    impossible = 1e12
    costs = np.full((len(players), len(slots)), impossible, dtype=float)
    for player_index, player in enumerate(players):
        for slot_index, slot in enumerate(slots):
            is_unrestricted = slot.accepted_positions == ALL_POSITIONS
            if (
                player.player_id == blocked_player_id
                and not is_unrestricted
                and not slot.accepted_positions.isdisjoint(blocked_positions)
            ):
                continue
            if player.eligible_positions.isdisjoint(slot.accepted_positions):
                continue
            costs[player_index, slot_index] = -(player.utility * slot.utility_multiplier)
    return costs


def _optimise(costs: np.ndarray) -> float:
    impossible = 1e12
    row_indices, column_indices = linear_sum_assignment(costs)
    if len(column_indices) != costs.shape[1]:
        raise ValueError("league slots cannot all be filled")
    selected = costs[row_indices, column_indices]
    if np.any(selected >= impossible / 2):
        raise ValueError("league slots cannot all be filled")
    return -float(selected.sum())


def eligibility_pivotality(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
    *,
    player_id: str,
    blocked_positions: frozenset[str],
) -> EligibilityPivotality:
    """Return the optimal league loss after blocking constrained eligibility only."""

    if not blocked_positions:
        raise ValueError("blocked_positions must be non-empty")
    if not blocked_positions.issubset(ALL_POSITIONS):
        raise ValueError("blocked_positions contains an unknown position")
    ordered_players = tuple(sorted(players, key=lambda item: item.player_id))
    ordered_slots = tuple(sorted(slots, key=lambda item: item.slot_id))
    target = next((player for player in ordered_players if player.player_id == player_id), None)
    if target is None:
        raise KeyError(player_id)
    relevant = target.eligible_positions & blocked_positions
    if not relevant:
        return EligibilityPivotality(player_id, blocked_positions, 0.0)

    base = _optimise(_cost_matrix(ordered_players, ordered_slots))
    counterfactual = _optimise(
        _cost_matrix(
            ordered_players,
            ordered_slots,
            blocked_player_id=player_id,
            blocked_positions=blocked_positions,
        )
    )
    loss = base - counterfactual
    if loss < -1e-9:
        raise AssertionError("removing eligibility cannot improve constrained optimum")
    return EligibilityPivotality(player_id, blocked_positions, max(0.0, loss))
