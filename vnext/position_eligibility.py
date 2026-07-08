"""Current official position-eligibility parsing and validation.

Future eligibility is never projected.  The same current eligibility set is reused for
all forecast horizons until an updated official snapshot is supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping, Sequence

VALID_POSITIONS = frozenset({"MID", "RUC", "GFWD", "KFWD", "GDEF", "KDEF"})
SEPARATORS = ("/", ",", "|", ";")


@dataclass(frozen=True, slots=True)
class EligibilityRecord:
    player_id: str
    positions: frozenset[str]
    effective_date: date
    source: str
    primary_position: str

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        if not self.positions:
            raise ValueError(f"positions must be non-empty for {self.player_id}")
        invalid = self.positions - VALID_POSITIONS
        if invalid:
            raise ValueError(f"invalid positions for {self.player_id}: {sorted(invalid)!r}")
        if self.primary_position not in self.positions:
            raise ValueError(f"primary_position must be eligible for {self.player_id}")
        if not self.source.strip():
            raise ValueError("source must be non-empty")


def parse_positions(value: str | Iterable[str]) -> frozenset[str]:
    """Parse a canonical list or a common delimited official-position field."""

    if isinstance(value, str):
        text = value.strip().upper()
        for separator in SEPARATORS:
            text = text.replace(separator, " ")
        items = text.split()
    else:
        items = [str(item).strip().upper() for item in value]
    positions = frozenset(item for item in items if item)
    invalid = positions - VALID_POSITIONS
    if invalid:
        raise ValueError(f"invalid positions: {sorted(invalid)!r}")
    if not positions:
        raise ValueError("at least one position is required")
    return positions


def build_eligibility_snapshot(
    rows: Sequence[Mapping[str, object]],
    *,
    effective_date: date,
    source: str,
    fallback_field: str = "present_position",
) -> tuple[EligibilityRecord, ...]:
    """Build a strict, complete snapshot from official or legacy-compatible rows.

    Preferred input uses ``eligible_positions``.  The single-valued legacy
    ``present_position`` field is accepted only as a transparent fallback.
    """

    records: list[EligibilityRecord] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        player_id = str(row.get("stable_player_id") or row.get("key") or "").strip()
        if not player_id:
            raise ValueError(f"row {index} has no stable player identifier")
        if player_id in seen:
            raise ValueError(f"duplicate player identifier: {player_id}")
        seen.add(player_id)

        raw_positions = row.get("eligible_positions")
        if raw_positions is None:
            raw_positions = row.get(fallback_field)
        if raw_positions is None:
            raise ValueError(f"missing eligibility for {player_id}")
        positions = parse_positions(raw_positions)  # type: ignore[arg-type]

        raw_primary = row.get("primary_position") or row.get(fallback_field)
        if raw_primary is None:
            primary = sorted(positions)[0]
        else:
            parsed_primary = parse_positions(str(raw_primary))
            if len(parsed_primary) != 1:
                raise ValueError(f"primary position must be single-valued for {player_id}")
            primary = next(iter(parsed_primary))

        records.append(
            EligibilityRecord(
                player_id=player_id,
                positions=positions,
                effective_date=effective_date,
                source=source,
                primary_position=primary,
            )
        )
    return tuple(sorted(records, key=lambda item: item.player_id))


def eligibility_for_horizons(
    record: EligibilityRecord,
    horizons: Iterable[int],
) -> dict[int, frozenset[str]]:
    """Reuse current official eligibility unchanged at every forecast horizon."""

    result: dict[int, frozenset[str]] = {}
    for horizon in horizons:
        if horizon < 0:
            raise ValueError("forecast horizons must be non-negative")
        result[horizon] = record.positions
    return result


def compare_snapshots(
    previous: Sequence[EligibilityRecord],
    current: Sequence[EligibilityRecord],
) -> dict[str, tuple[frozenset[str], frozenset[str]]]:
    """Return only players whose official eligibility changed."""

    old = {record.player_id: record.positions for record in previous}
    new = {record.player_id: record.positions for record in current}
    if old.keys() != new.keys():
        missing = sorted(old.keys() - new.keys())
        added = sorted(new.keys() - old.keys())
        raise ValueError(f"snapshot player universe changed: missing={missing}, added={added}")
    return {
        player_id: (old[player_id], new[player_id])
        for player_id in sorted(old)
        if old[player_id] != new[player_id]
    }
