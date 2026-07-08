"""Roster ownership and free-agent classification for the AFL RL league."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

FREE_AGENT_LABELS = frozenset({"free agents", "free agent"})


@dataclass(frozen=True, slots=True)
class RosterRules:
    teams: int = 16
    senior_list_max: int = 42
    rookie_list_max: int = 4
    offseason_senior_list: int = 37

    @property
    def total_list_max(self) -> int:
        return self.senior_list_max + self.rookie_list_max


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
        raise ValueError(f"teams exceed senior-plus-rookie maximum: {over}")
    return counts


def senior_cut_status(
    team_size: int,
    *,
    known_rookies: int | None,
    rules: RosterRules = AUTHORITATIVE_ROSTER_RULES,
) -> tuple[bool, str]:
    """Return whether an exact 42-to-37 senior cut can be calculated.

    Total team size alone is insufficient when rookie status is not identified.
    """

    if team_size < 0:
        raise ValueError("team_size must be non-negative")
    if team_size > rules.total_list_max:
        raise ValueError("team_size exceeds senior-plus-rookie maximum")
    if known_rookies is None:
        return False, "rookie status is required to isolate the senior list"
    if known_rookies < 0 or known_rookies > rules.rookie_list_max:
        raise ValueError("known_rookies is outside the allowed range")
    senior_size = team_size - known_rookies
    if senior_size > rules.senior_list_max:
        raise ValueError("derived senior list exceeds maximum")
    return True, f"senior list contains {senior_size}; target is {rules.offseason_senior_list}"
