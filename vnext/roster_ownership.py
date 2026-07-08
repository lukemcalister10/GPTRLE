"""Roster ownership and free-agent classification for the AFL RL league."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

FREE_AGENT_LABELS = frozenset({"free agents", "free agent"})


@dataclass(frozen=True, slots=True)
class RosterRules:
    teams: int = 16
    total_list_max: int = 46
    offseason_list_max: int = 40

    def __post_init__(self) -> None:
        if self.teams <= 0:
            raise ValueError("teams must be positive")
        if self.total_list_max <= 0:
            raise ValueError("total_list_max must be positive")
        if self.offseason_list_max <= 0:
            raise ValueError("offseason_list_max must be positive")
        if self.offseason_list_max > self.total_list_max:
            raise ValueError("offseason_list_max cannot exceed total_list_max")


AUTHORITATIVE_ROSTER_RULES = RosterRules()


@dataclass(frozen=True, slots=True)
class OwnershipRecord:
    player_id: str
    team: str | None
    is_free_agent: bool


def normalise_team_label(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def is_free_agent_label(value: object) -> bool:
    label = normalise_team_label(value).casefold()
    return label in FREE_AGENT_LABELS


def build_ownership_records(
    rows: Sequence[Mapping[str, object]],
    *,
    id_field: str = "stable_player_id",
    team_field: str = "AFFL Team",
) -> tuple[OwnershipRecord, ...]:
    records: list[OwnershipRecord] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        player_id = str(row.get(id_field) or row.get("key") or "").strip()
        if not player_id:
            raise ValueError(f"row {index} has no player identifier")
        if player_id in seen:
            raise ValueError(f"duplicate player identifier: {player_id}")
        seen.add(player_id)

        raw_team = row.get(team_field)
        free_agent = is_free_agent_label(raw_team)
        team = None if free_agent else normalise_team_label(raw_team)
        if not free_agent and not team:
            raise ValueError(f"missing team assignment for {player_id}")
        records.append(OwnershipRecord(player_id, team, free_agent))
    return tuple(records)


def roster_counts(records: Iterable[OwnershipRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        key = "FREE_AGENTS" if record.is_free_agent else str(record.team)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def validate_roster_universe(
    records: Sequence[OwnershipRecord],
    *,
    rules: RosterRules = AUTHORITATIVE_ROSTER_RULES,
) -> dict[str, int]:
    counts = roster_counts(records)
    teams = {name: count for name, count in counts.items() if name != "FREE_AGENTS"}
    if len(teams) != rules.teams:
        raise ValueError(f"expected {rules.teams} named teams, found {len(teams)}")
    over = {name: count for name, count in teams.items() if count > rules.total_list_max}
    if over:
        raise ValueError(f"teams exceed total list maximum: {over}")
    return counts


def required_offseason_cuts(
    team_size: int,
    *,
    rules: RosterRules = AUTHORITATIVE_ROSTER_RULES,
) -> int:
    """Return the number of players required to reduce a roster to 40 or fewer."""

    if team_size < 0:
        raise ValueError("team_size must be non-negative")
    if team_size > rules.total_list_max:
        raise ValueError("team_size exceeds total list maximum")
    return max(0, team_size - rules.offseason_list_max)
