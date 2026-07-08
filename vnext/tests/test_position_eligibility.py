from datetime import date

import pytest

from position_eligibility import (
    EligibilityRecord,
    build_eligibility_snapshot,
    compare_snapshots,
    eligibility_for_horizons,
    parse_positions,
)


def test_parse_positions_accepts_common_delimiters():
    assert parse_positions("MID/FWD".replace("FWD", "GFWD")) == frozenset({"MID", "GFWD"})
    assert parse_positions("MID, GFWD") == frozenset({"MID", "GFWD"})
    assert parse_positions(["MID", "GFWD"]) == frozenset({"MID", "GFWD"})


def test_legacy_single_position_is_explicit_fallback():
    records = build_eligibility_snapshot(
        [{"key": "player-a", "present_position": "MID"}],
        effective_date=date(2026, 7, 8),
        source="legacy-current-data",
    )

    assert records[0].positions == frozenset({"MID"})
    assert records[0].primary_position == "MID"


def test_multi_position_snapshot_preserves_asymmetric_flexibility_input():
    records = build_eligibility_snapshot(
        [
            {
                "stable_player_id": "player-a",
                "eligible_positions": ["MID", "GFWD"],
                "primary_position": "MID",
                "present_position": "MID",
            }
        ],
        effective_date=date(2026, 7, 8),
        source="official-update",
    )

    assert records[0].positions == frozenset({"MID", "GFWD"})
    assert records[0].primary_position == "MID"


def test_current_positions_are_reused_without_future_projection():
    record = EligibilityRecord(
        player_id="player-a",
        positions=frozenset({"MID", "GFWD"}),
        effective_date=date(2026, 7, 8),
        source="official-update",
        primary_position="MID",
    )

    horizons = eligibility_for_horizons(record, [0, 1, 2, 3])
    assert horizons == {
        0: frozenset({"MID", "GFWD"}),
        1: frozenset({"MID", "GFWD"}),
        2: frozenset({"MID", "GFWD"}),
        3: frozenset({"MID", "GFWD"}),
    }


def test_compare_snapshots_reports_only_official_changes():
    previous = [
        EligibilityRecord(
            "player-a", frozenset({"MID"}), date(2026, 3, 1), "preseason", "MID"
        )
    ]
    current = [
        EligibilityRecord(
            "player-a", frozenset({"MID", "GFWD"}), date(2026, 7, 8), "round-update", "MID"
        )
    ]

    assert compare_snapshots(previous, current) == {
        "player-a": (frozenset({"MID"}), frozenset({"MID", "GFWD"}))
    }


def test_snapshot_rejects_duplicates_missing_players_and_invalid_positions():
    with pytest.raises(ValueError, match="duplicate"):
        build_eligibility_snapshot(
            [
                {"key": "player-a", "present_position": "MID"},
                {"key": "player-a", "present_position": "MID"},
            ],
            effective_date=date(2026, 7, 8),
            source="test",
        )

    with pytest.raises(ValueError, match="stable player"):
        build_eligibility_snapshot(
            [{"present_position": "MID"}],
            effective_date=date(2026, 7, 8),
            source="test",
        )

    with pytest.raises(ValueError, match="invalid"):
        parse_positions("MID/UNKNOWN")


def test_snapshot_comparison_refuses_universe_drift():
    previous = [
        EligibilityRecord("player-a", frozenset({"MID"}), date(2026, 3, 1), "old", "MID")
    ]
    current = [
        EligibilityRecord("player-b", frozenset({"MID"}), date(2026, 7, 8), "new", "MID")
    ]

    with pytest.raises(ValueError, match="universe changed"):
        compare_snapshots(previous, current)
