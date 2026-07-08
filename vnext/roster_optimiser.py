"""Deterministic roster allocation and marginal-utility primitives.

This module deliberately contains no AFL RL production constants.  A caller supplies
players, current official eligibility, and an explicit slot configuration.  The
optimiser then finds the maximum-utility legal assignment and can re-optimise after
removing a player.

The implementation is a small dependency-free min-cost-flow solver.  It is intended
for 42-player keeper rosters and similarly sized synthetic validation cases, not for
fitting forecast models.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class PlayerUtility:
    player_id: str
    utility: float
    eligible_positions: frozenset[str]
    primary_position: str | None = None

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        if not isfinite(self.utility):
            raise ValueError(f"utility must be finite for {self.player_id}")
        if not self.eligible_positions:
            raise ValueError(f"eligible_positions must be non-empty for {self.player_id}")
        if self.primary_position is not None and self.primary_position not in self.eligible_positions:
            raise ValueError(
                f"primary_position must be eligible for {self.player_id}: "
                f"{self.primary_position!r} not in {sorted(self.eligible_positions)!r}"
            )


@dataclass(frozen=True, slots=True)
class RosterSlot:
    slot_id: str
    accepted_positions: frozenset[str]
    utility_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if not self.slot_id:
            raise ValueError("slot_id must be non-empty")
        if not self.accepted_positions:
            raise ValueError(f"accepted_positions must be non-empty for {self.slot_id}")
        if not isfinite(self.utility_multiplier) or self.utility_multiplier < 0:
            raise ValueError(f"utility_multiplier must be finite and non-negative for {self.slot_id}")


@dataclass(frozen=True, slots=True)
class Assignment:
    slot_id: str
    player_id: str
    utility: float


@dataclass(frozen=True, slots=True)
class OptimisedRoster:
    total_utility: float
    assignments: tuple[Assignment, ...]

    @property
    def players_used(self) -> frozenset[str]:
        return frozenset(item.player_id for item in self.assignments)


@dataclass(slots=True)
class _Edge:
    to: int
    rev: int
    capacity: int
    cost: float
    player_id: str | None = None
    slot_id: str | None = None
    original_capacity: int = 0


def _add_edge(
    graph: list[list[_Edge]],
    source: int,
    target: int,
    capacity: int,
    cost: float,
    *,
    player_id: str | None = None,
    slot_id: str | None = None,
) -> None:
    forward = _Edge(
        to=target,
        rev=len(graph[target]),
        capacity=capacity,
        cost=cost,
        player_id=player_id,
        slot_id=slot_id,
        original_capacity=capacity,
    )
    reverse = _Edge(
        to=source,
        rev=len(graph[source]),
        capacity=0,
        cost=-cost,
        original_capacity=0,
    )
    graph[source].append(forward)
    graph[target].append(reverse)


def optimise_roster(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
) -> OptimisedRoster:
    """Return the maximum-utility legal one-player-per-slot assignment.

    Every supplied slot must be filled.  Callers that want replacement-level or
    empty-roster behaviour should include explicit replacement players rather than
    silently treating an unfilled slot as zero.
    """

    if len({player.player_id for player in players}) != len(players):
        raise ValueError("player_id values must be unique")
    if len({slot.slot_id for slot in slots}) != len(slots):
        raise ValueError("slot_id values must be unique")
    if len(players) < len(slots):
        raise ValueError("not enough players to fill all roster slots")
    if not slots:
        return OptimisedRoster(total_utility=0.0, assignments=())

    ordered_players = sorted(players, key=lambda item: item.player_id)
    ordered_slots = sorted(slots, key=lambda item: item.slot_id)

    source = 0
    player_offset = 1
    slot_offset = player_offset + len(ordered_players)
    sink = slot_offset + len(ordered_slots)
    graph: list[list[_Edge]] = [[] for _ in range(sink + 1)]

    for player_index, player in enumerate(ordered_players):
        player_node = player_offset + player_index
        _add_edge(graph, source, player_node, 1, 0.0)
        for slot_index, slot in enumerate(ordered_slots):
            if player.eligible_positions.isdisjoint(slot.accepted_positions):
                continue
            slot_node = slot_offset + slot_index
            assigned_utility = player.utility * slot.utility_multiplier
            _add_edge(
                graph,
                player_node,
                slot_node,
                1,
                -assigned_utility,
                player_id=player.player_id,
                slot_id=slot.slot_id,
            )

    for slot_index, _slot in enumerate(ordered_slots):
        _add_edge(graph, slot_offset + slot_index, sink, 1, 0.0)

    required_flow = len(ordered_slots)
    flow = 0
    total_cost = 0.0
    node_count = len(graph)

    while flow < required_flow:
        distance = [float("inf")] * node_count
        previous_node = [-1] * node_count
        previous_edge = [-1] * node_count
        distance[source] = 0.0

        # Bellman-Ford is deterministic here and comfortably fast for keeper rosters.
        for _ in range(node_count - 1):
            changed = False
            for node in range(node_count):
                if distance[node] == float("inf"):
                    continue
                for edge_index, edge in enumerate(graph[node]):
                    if edge.capacity <= 0:
                        continue
                    candidate = distance[node] + edge.cost
                    if candidate < distance[edge.to] - 1e-12:
                        distance[edge.to] = candidate
                        previous_node[edge.to] = node
                        previous_edge[edge.to] = edge_index
                        changed = True
            if not changed:
                break

        if previous_node[sink] == -1:
            raise ValueError("roster slots cannot all be filled from current eligibility")

        node = sink
        while node != source:
            parent = previous_node[node]
            edge_index = previous_edge[node]
            edge = graph[parent][edge_index]
            edge.capacity -= 1
            graph[node][edge.rev].capacity += 1
            node = parent
        total_cost += distance[sink]
        flow += 1

    assignments: list[Assignment] = []
    for player_index, _player in enumerate(ordered_players):
        player_node = player_offset + player_index
        for edge in graph[player_node]:
            if edge.player_id is None or edge.slot_id is None:
                continue
            if edge.original_capacity == 1 and edge.capacity == 0:
                assignments.append(
                    Assignment(
                        slot_id=edge.slot_id,
                        player_id=edge.player_id,
                        utility=-edge.cost,
                    )
                )

    assignments.sort(key=lambda item: item.slot_id)
    if len(assignments) != required_flow:
        raise RuntimeError("internal assignment count mismatch")
    return OptimisedRoster(total_utility=-total_cost, assignments=tuple(assignments))


def marginal_roster_utility(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
    player_id: str,
) -> float:
    """Measure roster utility lost after removing one player and re-optimising."""

    if player_id not in {player.player_id for player in players}:
        raise KeyError(player_id)
    with_player = optimise_roster(players, slots)
    without_player = optimise_roster(
        [player for player in players if player.player_id != player_id],
        slots,
    )
    return with_player.total_utility - without_player.total_utility


def flexibility_value(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
    player_id: str,
) -> float:
    """Value of a player's current multi-position eligibility versus primary only."""

    target = next((player for player in players if player.player_id == player_id), None)
    if target is None:
        raise KeyError(player_id)
    if target.primary_position is None:
        raise ValueError(f"primary_position is required to measure flexibility for {player_id}")

    full = optimise_roster(players, slots)
    primary_only = PlayerUtility(
        player_id=target.player_id,
        utility=target.utility,
        eligible_positions=frozenset({target.primary_position}),
        primary_position=target.primary_position,
    )
    restricted_players = [
        primary_only if player.player_id == player_id else player for player in players
    ]
    restricted = optimise_roster(restricted_players, slots)
    return full.total_utility - restricted.total_utility


def build_slots(
    counts: Mapping[str, int],
    accepted_positions: Mapping[str, Iterable[str]],
    *,
    multipliers: Mapping[str, float] | None = None,
) -> tuple[RosterSlot, ...]:
    """Expand a named slot configuration into deterministic slot instances."""

    multipliers = multipliers or {}
    result: list[RosterSlot] = []
    for slot_type in sorted(counts):
        count = counts[slot_type]
        if count < 0:
            raise ValueError(f"slot count must be non-negative for {slot_type}")
        if slot_type not in accepted_positions:
            raise KeyError(f"missing accepted positions for slot type {slot_type}")
        for index in range(1, count + 1):
            result.append(
                RosterSlot(
                    slot_id=f"{slot_type}-{index}",
                    accepted_positions=frozenset(accepted_positions[slot_type]),
                    utility_multiplier=multipliers.get(slot_type, 1.0),
                )
            )
    return tuple(result)
