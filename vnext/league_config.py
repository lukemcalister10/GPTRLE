"""Authoritative AFL RL keeper-league lineup configuration."""

from __future__ import annotations

from dataclasses import dataclass

from roster_optimiser import RosterSlot

ALL_POSITIONS = frozenset({"GDEF", "KDEF", "MID", "RUC", "GFWD", "KFWD"})


@dataclass(frozen=True, slots=True)
class LeagueLineup:
    teams: int = 16
    general_defenders: int = 4
    key_defenders: int = 2
    midfielders: int = 5
    rucks: int = 1
    general_forwards: int = 4
    key_forwards: int = 2
    free_choice_bench: int = 5
    in_season_roster_size: int = 42
    offseason_roster_size: int = 37

    @property
    def active_slots(self) -> int:
        return (
            self.general_defenders
            + self.key_defenders
            + self.midfielders
            + self.rucks
            + self.general_forwards
            + self.key_forwards
        )

    @property
    def listed_lineup_slots(self) -> int:
        return self.active_slots + self.free_choice_bench


AUTHORITATIVE_LINEUP = LeagueLineup()


def build_authoritative_slots(*, bench_multiplier: float = 0.0) -> tuple[RosterSlot, ...]:
    """Build the league's 18 active and five free-choice bench slots.

    Bench scoring utility is deliberately configurable.  A zero default means the
    bench supplies eligibility/coverage but is not assumed to contribute weekly
    scoring until the utility model explicitly prices coverage and future use.
    """

    cfg = AUTHORITATIVE_LINEUP
    specs = (
        ("GDEF", cfg.general_defenders, frozenset({"GDEF"}), 1.0),
        ("KDEF", cfg.key_defenders, frozenset({"KDEF"}), 1.0),
        ("MID", cfg.midfielders, frozenset({"MID"}), 1.0),
        ("RUC", cfg.rucks, frozenset({"RUC"}), 1.0),
        ("GFWD", cfg.general_forwards, frozenset({"GFWD"}), 1.0),
        ("KFWD", cfg.key_forwards, frozenset({"KFWD"}), 1.0),
        ("BENCH", cfg.free_choice_bench, ALL_POSITIONS, bench_multiplier),
    )
    slots: list[RosterSlot] = []
    for prefix, count, positions, multiplier in specs:
        for index in range(1, count + 1):
            slots.append(
                RosterSlot(
                    slot_id=f"{prefix}-{index}",
                    accepted_positions=positions,
                    utility_multiplier=multiplier,
                )
            )
    return tuple(slots)
