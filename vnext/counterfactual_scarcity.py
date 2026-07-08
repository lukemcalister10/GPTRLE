"""Optimisation-invariant positional scarcity diagnostics.

Scarcity is measured by relaxing constrained scoring slots to unrestricted eligibility
and re-optimising the full league. The result depends on the constraint itself, not on
which equivalent player an optimiser happens to label as positional or free-choice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from league_allocation import optimise_league_active_lineups
from league_config import ALL_POSITIONS
from roster_optimiser import PlayerUtility, RosterSlot


@dataclass(frozen=True, slots=True)
class RelaxationPoint:
    position: str
    relaxed_slots: int
    cumulative_cost: float
    marginal_cost: float


def relax_slots(
    slots: Sequence[RosterSlot],
    *,
    position: str,
    count: int,
) -> tuple[RosterSlot, ...]:
    """Replace exactly ``count`` single-position constraints with unrestricted slots."""

    if position not in ALL_POSITIONS:
        raise ValueError(f"unknown position: {position}")
    if count <= 0:
        raise ValueError("count must be positive")

    relaxed = []
    remaining = count
    for slot in slots:
        if remaining and slot.accepted_positions == frozenset({position}):
            relaxed.append(
                RosterSlot(
                    slot_id=slot.slot_id,
                    accepted_positions=ALL_POSITIONS,
                    utility_multiplier=slot.utility_multiplier,
                )
            )
            remaining -= 1
        else:
            relaxed.append(slot)
    if remaining:
        raise ValueError(f"cannot relax {count} {position} slots")
    return tuple(relaxed)


def relaxation_curve(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
    *,
    position: str,
    max_relaxations: int,
) -> tuple[RelaxationPoint, ...]:
    """Return cumulative and marginal league cost of positional constraints."""

    if max_relaxations <= 0:
        raise ValueError("max_relaxations must be positive")
    base = optimise_league_active_lineups(players, slots).total_utility
    points = []
    previous = 0.0
    for count in range(1, max_relaxations + 1):
        relaxed_slots = relax_slots(slots, position=position, count=count)
        relaxed_total = optimise_league_active_lineups(players, relaxed_slots).total_utility
        cumulative = relaxed_total - base
        if cumulative < -1e-9:
            raise AssertionError("relaxing a constraint cannot reduce optimal utility")
        marginal = cumulative - previous
        points.append(
            RelaxationPoint(
                position=position,
                relaxed_slots=count,
                cumulative_cost=max(0.0, cumulative),
                marginal_cost=max(0.0, marginal),
            )
        )
        previous = cumulative
    return tuple(points)


def first_slot_scarcity_cost(
    players: Sequence[PlayerUtility],
    slots: Sequence[RosterSlot],
    *,
    position: str,
) -> float:
    """Return the value gained by relaxing one slot of the named position."""

    return relaxation_curve(
        players,
        slots,
        position=position,
        max_relaxations=1,
    )[0].cumulative_cost
