import pandas as pd

from analyse_task003g_components import component_ratios, zero_history_outcome_split


def test_component_ratios_separate_probability_games_and_average():
    rows = pd.DataFrame(
        {
            "meaningful": [1, 0],
            "p_meaningful": [0.4, 0.4],
            "games": [16.0, 0.0],
            "cond_games": [8.0, 8.0],
            "avg": [80.0, 0.0],
            "cond_avg": [40.0, 40.0],
            "points": [1280.0, 0.0],
            "exp_points": [128.0, 128.0],
        }
    )
    result = component_ratios(rows)
    assert result["p_ratio"] == 1.25
    assert result["games_ratio"] == 2.0
    assert result["avg_ratio"] == 2.0
    assert abs(
        result["p_log_share"]
        + result["games_log_share"]
        + result["avg_log_share"]
        - 1.0
    ) < 1e-12


def test_zero_history_split_keeps_eventual_players_separate():
    rows = pd.DataFrame(
        {
            "player_key": ["a", "b"],
            "lead": [1, 1],
            "model_id": ["vnext_fold_specific", "vnext_fold_specific"],
            "total_games": [0, 0],
            "games": [0.0, 5.0],
            "points": [0.0, 250.0],
            "exp_points": [20.0, 40.0],
            "exp_games": [1.0, 2.0],
            "p_meaningful": [0.1, 0.2],
        }
    )
    result = zero_history_outcome_split(rows)
    assert set(result["eventual_played"]) == {False, True}
    assert result.loc[result["eventual_played"], "n"].item() == 1
