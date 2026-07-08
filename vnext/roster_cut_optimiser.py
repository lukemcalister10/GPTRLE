"""Exact offseason retain-to-40 optimisation with legal-lineup protection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from roster_optimiser import PlayerUtility, RosterSlot


@dataclass(frozen=True, slots=True)
class RosterCutResult:
    retained_player_ids: frozenset[str]
    cut_player_ids: frozenset[str]
    retained_utility: float
    lineup_player_ids: frozenset[str]


def optimise_retained_roster(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
    *,
    retain_limit: int = 40,
) -> RosterCutResult:
    """Maximise retained player utility while preserving one legal scoring lineup."""

    if len({player.player_id for player in players}) != len(players):
        raise ValueError("player_id values must be unique")
    if len({slot.slot_id for slot in slots}) != len(slots):
        raise ValueError("slot_id values must be unique")
    if retain_limit < len(slots):
        raise ValueError("retain_limit cannot be smaller than the scoring lineup")
    if retain_limit <= 0:
        raise ValueError("retain_limit must be positive")
    if len(players) <= retain_limit:
        retained = frozenset(player.player_id for player in players)
        return RosterCutResult(retained, frozenset(), sum(p.utility for p in players), frozenset())

    ordered_players = tuple(sorted(players, key=lambda item: item.player_id))
    ordered_slots = tuple(sorted(slots, key=lambda item: item.slot_id))
    player_count = len(ordered_players)

    eligible_edges: list[tuple[int, int]] = []
    for player_index, player in enumerate(ordered_players):
        for slot_index, slot in enumerate(ordered_slots):
            if not player.eligible_positions.isdisjoint(slot.accepted_positions):
                eligible_edges.append((player_index, slot_index))

    variable_count = player_count + len(eligible_edges)
    objective = np.zeros(variable_count, dtype=float)
    objective[:player_count] = -np.array([player.utility for player in ordered_players])

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    lower: list[float] = []
    upper: list[float] = []
    constraint_index = 0

    # Retain exactly the allowed number.
    for player_index in range(player_count):
        rows.append(constraint_index); cols.append(player_index); data.append(1.0)
    lower.append(float(retain_limit)); upper.append(float(retain_limit)); constraint_index += 1

    # Every lineup slot is filled exactly once.
    for slot_index in range(len(ordered_slots)):
        for edge_index, (_player_index, edge_slot_index) in enumerate(eligible_edges):
            if edge_slot_index == slot_index:
                rows.append(constraint_index); cols.append(player_count + edge_index); data.append(1.0)
        lower.append(1.0); upper.append(1.0); constraint_index += 1

    # A player can occupy at most one lineup slot, and only when retained.
    for player_index in range(player_count):
        rows.append(constraint_index); cols.append(player_index); data.append(-1.0)
        for edge_index, (edge_player_index, _slot_index) in enumerate(eligible_edges):
            if edge_player_index == player_index:
                rows.append(constraint_index); cols.append(player_count + edge_index); data.append(1.0)
        lower.append(-np.inf); upper.append(0.0); constraint_index += 1

    matrix = coo_matrix((data, (rows, cols)), shape=(constraint_index, variable_count)).tocsr()
    result = milp(
        c=objective,
        integrality=np.ones(variable_count, dtype=int),
        bounds=Bounds(np.zeros(variable_count), np.ones(variable_count)),
        constraints=LinearConstraint(matrix, np.array(lower), np.array(upper)),
        options={"presolve": True},
    )
    if not result.success or result.x is None:
        raise ValueError(f"no feasible retain-to-{retain_limit} roster: {result.message}")

    retained = frozenset(
        ordered_players[index].player_id
        for index, value in enumerate(result.x[:player_count])
        if value > 0.5
    )
    lineup = frozenset(
        ordered_players[player_index].player_id
        for edge_index, (player_index, _slot_index) in enumerate(eligible_edges)
        if result.x[player_count + edge_index] > 0.5
    )
    all_ids = frozenset(player.player_id for player in ordered_players)
    return RosterCutResult(
        retained_player_ids=retained,
        cut_player_ids=all_ids - retained,
        retained_utility=sum(player.utility for player in ordered_players if player.player_id in retained),
        lineup_player_ids=lineup,
    )
