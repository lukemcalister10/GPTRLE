import pytest

from replacement_lineup_value import (
    aggregate_replacement_value,
    annual_replacement_value,
    best_replacement_average,
)


def test_missed_games_receive_replacement_scoring():
    result = annual_replacement_value(
        expected_active_games=16,
        conditional_average=120,
        replacement_average=70,
        season_games=20,
    )

    assert result.lineup_points_with_player == 2200
    assert result.replacement_only_points == 1400
    assert result.value_above_replacement == 800


def test_durable_mediocre_player_can_be_less_valuable_than_elite_partial_player():
    elite = annual_replacement_value(
        expected_active_games=16,
        conditional_average=120,
        replacement_average=70,
        season_games=20,
    )
    durable = annual_replacement_value(
        expected_active_games=20,
        conditional_average=100,
        replacement_average=70,
        season_games=20,
    )

    assert elite.value_above_replacement == 800
    assert durable.value_above_replacement == 600


def test_below_replacement_player_has_negative_lineup_contribution():
    result = annual_replacement_value(
        expected_active_games=10,
        conditional_average=60,
        replacement_average=70,
        season_games=20,
    )

    assert result.value_above_replacement == -100


def test_multi_position_uses_weakest_legal_replacement_hurdle():
    assert best_replacement_average(
        frozenset({"MID", "RUC"}),
        {"MID": 65, "RUC": 55},
    ) == 55


def test_horizon_aggregation_is_weighted():
    assert aggregate_replacement_value([100, 50], [0.75, 0.25]) == 87.5


def test_invalid_inputs_fail():
    with pytest.raises(ValueError, match="between zero"):
        annual_replacement_value(
            expected_active_games=21,
            conditional_average=100,
            replacement_average=70,
            season_games=20,
        )
    with pytest.raises(KeyError, match="missing"):
        best_replacement_average(
            frozenset({"RUC"}),
            {"MID": 65},
        )
    with pytest.raises(ValueError, match="sum to one"):
        aggregate_replacement_value([100, 50], [0.5, 0.4])
