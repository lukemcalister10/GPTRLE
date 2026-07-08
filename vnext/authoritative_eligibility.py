"""Adapter from the authoritative 2026 player universe to utility eligibility."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from active_universe import load_authoritative
from position_eligibility import EligibilityRecord

SOURCE_TO_UTILITY = {
    "G-DEF": "GDEF",
    "K-DEF": "KDEF",
    "MID": "MID",
    "RUCK": "RUC",
    "G-FWD": "GFWD",
    "K-FWD": "KFWD",
}


def load_current_eligibility(
    path: Path,
    *,
    effective_date: date,
    source: str = "data/current/Players_2026.csv",
) -> tuple[EligibilityRecord, ...]:
    """Load complete comma-separated eligibility from the authoritative source."""

    df = load_authoritative(path)
    records: list[EligibilityRecord] = []
    seen_names: set[str] = set()

    for _, row in df.iterrows():
        player_name = str(row["Player Name"]).strip()
        if player_name in seen_names:
            raise ValueError(f"duplicate authoritative player name: {player_name}")
        seen_names.add(player_name)

        positions = frozenset(SOURCE_TO_UTILITY[pos] for pos in row["eligibilities"])
        # Stable ids are added by reconciliation.  Until joined, the exact source-row
        # identifier is deterministic and must not be confused with a production id.
        player_id = f"authoritative-row-{int(row['source_row'])}"
        primary = SOURCE_TO_UTILITY[row["eligibilities"][0]]
        records.append(
            EligibilityRecord(
                player_id=player_id,
                positions=positions,
                effective_date=effective_date,
                source=source,
                primary_position=primary,
            )
        )

    if len(records) != 804:
        raise ValueError(f"expected 804 authoritative players, found {len(records)}")
    return tuple(records)
