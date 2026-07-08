from __future__ import annotations

from audit_partial_season_support import audit_players


def test_annual_only_rows_are_formally_blocked() -> None:
    report = audit_players(
        [
            {
                "key": "a",
                "scoring": [
                    {"year": 2025, "avg": 80, "games": 20},
                    {"year": 2026, "avg": 85, "games": 10},
                ],
            }
        ]
    )
    assert report["status"] == "blocked_by_missing_origin_safe_intraseason_data"
    assert "scoring_history_is_annual_aggregate_only" in report["blockers"]
    assert report["current_2026_rows_with_games"] == 1


def test_round_aware_rows_are_detected() -> None:
    report = audit_players(
        [
            {
                "key": "a",
                "scoring": [
                    {"year": 2025, "round": 8, "avg": 80, "games": 7},
                ],
            }
        ]
    )
    assert report["intraseason_fields_present"] == ["round"]
    assert "no_round_date_or_games_available_field" not in report["blockers"]
