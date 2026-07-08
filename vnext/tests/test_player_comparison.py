import pytest

from player_comparison import PlayerComparison, compare_players, rank_players


def test_players_rank_by_declared_lens_only():
    veteran = PlayerComparison("veteran", 100, 80, 40)
    prospect = PlayerComparison("prospect", 60, 85, 110)

    assert [p.player_id for p in rank_players([prospect, veteran], lens="contender")] == [
        "veteran",
        "prospect",
    ]
    assert [p.player_id for p in rank_players([prospect, veteran], lens="rebuilder")] == [
        "prospect",
        "veteran",
    ]


def test_direct_comparison_returns_objective_value_gap():
    first = PlayerComparison("a", 90, 80, 70)
    second = PlayerComparison("b", 85, 82, 75)

    assert compare_players(first, second, lens="contender") == 5
    assert compare_players(first, second, lens="balanced") == -2


def test_ranking_is_independent_of_input_order():
    a = PlayerComparison("a", 90, 80, 70)
    b = PlayerComparison("b", 85, 82, 75)

    assert rank_players([a, b], lens="balanced") == rank_players([b, a], lens="balanced")


def test_ties_are_deterministic():
    a = PlayerComparison("a", 90, 80, 70)
    b = PlayerComparison("b", 90, 80, 70)

    assert [p.player_id for p in rank_players([b, a], lens="contender")] == ["a", "b"]


def test_invalid_lens_and_duplicate_players_fail():
    player = PlayerComparison("a", 90, 80, 70)

    with pytest.raises(KeyError):
        rank_players([player], lens="specific_team")
    with pytest.raises(ValueError, match="unique"):
        rank_players([player, player], lens="balanced")
