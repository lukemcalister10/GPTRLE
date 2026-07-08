import pytest

from current_season_context import CURRENT_2026_CONTEXT
from weekly_scoring import WeeklyPlayer, calculate_weekly_score, expected_captain_bonus


def test_current_2026_exposure_is_uniform_thirteen_matches_from_fourteen_rounds():
    assert CURRENT_2026_CONTEXT.season == 2026
    assert CURRENT_2026_CONTEXT.rounds_elapsed == 14
    assert CURRENT_2026_CONTEXT.matches_available_per_player == 13


def test_all_selected_players_score_and_captain_doubles():
    players = [
        WeeklyPlayer("a", 100, True),
        WeeklyPlayer("b", 90, True),
        WeeklyPlayer("c", 80, True),
    ]
    result = calculate_weekly_score(players, captain_id="a", vice_captain_id="b")

    assert result.base_score == 270
    assert result.captain_bonus == 100
    assert result.total_score == 370
    assert result.captain_used == "a"


def test_vice_captain_replaces_nonplaying_captain():
    players = [
        WeeklyPlayer("captain", 0, False),
        WeeklyPlayer("vice", 95, True),
        WeeklyPlayer("other", 80, True),
    ]
    result = calculate_weekly_score(
        players,
        captain_id="captain",
        vice_captain_id="vice",
    )

    assert result.base_score == 175
    assert result.captain_bonus == 95
    assert result.total_score == 270
    assert result.captain_used == "vice"


def test_no_captain_bonus_when_both_captain_and_vice_miss():
    players = [
        WeeklyPlayer("captain", 0, False),
        WeeklyPlayer("vice", 0, False),
        WeeklyPlayer("other", 80, True),
    ]
    result = calculate_weekly_score(
        players,
        captain_id="captain",
        vice_captain_id="vice",
    )

    assert result.base_score == 80
    assert result.captain_bonus == 0
    assert result.total_score == 80
    assert result.captain_used is None


def test_expected_captain_bonus_includes_vice_fallback():
    result = expected_captain_bonus(
        captain_expected_score=120,
        captain_play_probability=0.8,
        vice_expected_score=110,
        vice_play_probability=0.9,
    )

    assert result == pytest.approx(115.8)


def test_captain_and_vice_must_be_selected_and_distinct():
    players = [WeeklyPlayer("a", 100, True), WeeklyPlayer("b", 90, True)]

    with pytest.raises(ValueError, match="captain must"):
        calculate_weekly_score(players, captain_id="missing", vice_captain_id="b")
    with pytest.raises(ValueError, match="must differ"):
        calculate_weekly_score(players, captain_id="a", vice_captain_id="a")
