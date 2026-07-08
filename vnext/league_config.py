"""Authoritative AFL RL keeper-league lineup and scoring configuration."""

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
    all_selected_players_score: bool = True
    captain_multiplier: float = 2.0
    vice_captain_fallback: bool = True
    emergencies_score_only_when_activated: bool = True

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

    @property
    def weekly_scoring_slots(self) -> int:
        return self.listed_lineup_slots if self.all_selected_players_score else self.active_slots


AUTHORITATIVE_LINEUP = LeagueLineup()


def build_authoritative_slots(*, bench_multiplier: float = 1.0) -> tuple[RosterSlot, ...]:
    """Build the league's 18 positional and five free-choice scoring slots.

    All 23 selected players contribute their score.  The five free-choice slots accept
    every position and therefore also represent lineup flexibility.  Emergencies are
    outside this 23-player scoring lineup unless a manager actively promotes one into
    the selected side for that round.
    """

    cfg = AUTHORITATIVE_LINEUP
    specs = (
        ("GDEF", cfg.general_defenders, frozenset({"GDEF"}), 1.0),
        ("KDEF", cfg.key_defenders, frozenset({"KDEF"}), 1.0),
        ("MID", cfg.midfielders, frozenset({"MID"}), 1.0),
        ("RUC", cfg.rucks, frozenset({"RUC"}), 1.0),
        ("GFWD", cfg.general_forwards, frozenset({"GFWD"}), 1.0),
        ("KFWD", cfg.key_forwards, frozenset({"KFWD"}), 1.0),
        ("FREE", cfg.free_choice_bench, ALL_POSITIONS, bench_multiplier),
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
