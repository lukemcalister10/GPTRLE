"""League-wide lineup allocation and marginal utility diagnostics.

This module uses the current official eligibility set and an externally supplied
utility vector. It does not forecast positions or define keeper utility itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment

from league_config import ALL_POSITIONS, AUTHORITATIVE_LINEUP
from roster_optimiser import Assignment, PlayerUtility, RosterSlot


@dataclass(frozen=True, slots=True)
class LeagueAllocation:
    total_utility: float
    assignments: tuple[Assignment, ...]

    @property
    def selected_players(self) -> frozenset[str]:
        return frozenset(item.player_id for item in self.assignments)


def build_league_active_slots() -> tuple[RosterSlot, ...]:
    """Return 16 copies of the league's 18 position-constrained slots."""

    cfg = AUTHORITATIVE_LINEUP
    templates = (
        ("GDEF", cfg.general_defenders, frozenset({"GDEF"})),
        ("KDEF", cfg.key_defenders, frozenset({"KDEF"})),
        ("MID", cfg.midfielders, frozenset({"MID"})),
        ("RUC", cfg.rucks, frozenset({"RUC"})),
        ("GFWD", cfg.general_forwards, frozenset({"GFWD"})),
        ("KFWD", cfg.key_forwards, frozenset({"KFWD"})),
    )
    slots: list[RosterSlot] = []
    for team_index in range(1, cfg.teams + 1):
        for prefix, count, accepted in templates:
            for slot_index in range(1, count + 1):
                slots.append(
                    RosterSlot(
                        slot_id=f"T{team_index:02d}-{prefix}-{slot_index}",
                        accepted_positions=accepted,
                    )
                )
    return tuple(slots)


def build_league_scoring_slots() -> tuple[RosterSlot, ...]:
    """Return all 368 weekly scoring slots: 288 constrained and 80 free choice."""

    slots = list(build_league_active_slots())
    cfg = AUTHORITATIVE_LINEUP
    for team_index in range(1, cfg.teams + 1):
        for slot_index in range(1, cfg.free_choice_bench + 1):
            slots.append(
                RosterSlot(
                    slot_id=f"T{team_index:02d}-FREE-{slot_index}",
                    accepted_positions=ALL_POSITIONS,
                )
            )
    return tuple(slots)


def optimise_league_active_lineups(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot] | None = None,
) -> LeagueAllocation:
    """Maximise utility across supplied slots; defaults to 288 constrained slots."""

    slots = tuple(slots or build_league_active_slots())
    if len({player.player_id for player in players}) != len(players):
        raise ValueError("player_id values must be unique")
    if len({slot.slot_id for slot in slots}) != len(slots):
        raise ValueError("slot_id values must be unique")
    if len(players) < len(slots):
        raise ValueError("not enough players to fill all league slots")

    ordered_players = tuple(sorted(players, key=lambda item: item.player_id))
    ordered_slots = tuple(sorted(slots, key=lambda item: item.slot_id))
    impossible = 1e12
    costs = np.full((len(ordered_players), len(ordered_slots)), impossible, dtype=float)

    for player_index, player in enumerate(ordered_players):
        for slot_index, slot in enumerate(ordered_slots):
            if player.eligible_positions.isdisjoint(slot.accepted_positions):
                continue
            costs[player_index, slot_index] = -(player.utility * slot.utility_multiplier)

    row_indices, column_indices = linear_sum_assignment(costs)
    if len(column_indices) != len(ordered_slots):
        raise ValueError("league slots cannot all be filled")
    selected_costs = costs[row_indices, column_indices]
    if np.any(selected_costs >= impossible / 2):
        raise ValueError("league slots cannot all be filled from current eligibility")

    assignments = [
        Assignment(
            slot_id=ordered_slots[column_index].slot_id,
            player_id=ordered_players[row_index].player_id,
            utility=-float(costs[row_index, column_index]),
        )
        for row_index, column_index in zip(row_indices, column_indices, strict=True)
    ]
    assignments.sort(key=lambda item: item.slot_id)
    return LeagueAllocation(
        total_utility=sum(item.utility for item in assignments),
        assignments=tuple(assignments),
    )


def optimise_league_scoring_lineups(players: Sequence[PlayerUtility]) -> LeagueAllocation:
    """Maximise weekly utility across all 368 scoring slots."""

    return optimise_league_active_lineups(players, build_league_scoring_slots())


def marginal_league_utility(
    players: Sequence[PlayerUtility],
    player_id: str,
    slots: Sequence[RosterSlot] | None = None,
) -> float:
    """Return utility lost after removing and re-optimising."""

    if player_id not in {player.player_id for player in players}:
        raise KeyError(player_id)
    with_player = optimise_league_active_lineups(players, slots)
    without_player = optimise_league_active_lineups(
        [player for player in players if player.player_id != player_id],
        slots,
    )
    return with_player.total_utility - without_player.total_utility


def league_flexibility_value(
    players: Sequence[PlayerUtility],
    player_id: str,
    slots: Sequence[RosterSlot] | None = None,
) -> float:
    """Value of current additional eligibility versus primary eligibility only."""

    target = next((player for player in players if player.player_id == player_id), None)
    if target is None:
        raise KeyError(player_id)
    if target.primary_position is None:
        raise ValueError(f"primary_position is required for {player_id}")

    full = optimise_league_active_lineups(players, slots)
    restricted_target = PlayerUtility(
        player_id=target.player_id,
        utility=target.utility,
        eligible_positions=frozenset({target.primary_position}),
        primary_position=target.primary_position,
    )
    restricted_players = [
        restricted_target if player.player_id == player_id else player
        for player in players
    ]
    restricted = optimise_league_active_lineups(restricted_players, slots)
    return full.total_utility - restricted.total_utility


def assigned_position_summary(allocation: LeagueAllocation) -> dict[str, dict[str, float]]:
    """Summarise assigned utility by slot family."""

    grouped: dict[str, list[float]] = {}
    for assignment in allocation.assignments:
        position = assignment.slot_id.split("-")[1]
        grouped.setdefault(position, []).append(assignment.utility)

    return {
        position: {
            "count": float(len(values)),
            "minimum": float(min(values)),
            "median": float(np.median(values)),
            "maximum": float(max(values)),
        }
        for position, values in sorted(grouped.items())
    }
