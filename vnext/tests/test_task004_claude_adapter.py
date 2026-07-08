import numpy as np
import pandas as pd

from task004_claude_adapter import captain_premium, forecast_value, soft_positive


def test_soft_positive_matches_legacy_shape():
    values = soft_positive(np.array([-10.0, 0.0, 10.0]))
    assert np.all(values > 0)
    assert values[0] < values[1] < values[2]


def test_captain_premium_is_zero_below_threshold_and_capped():
    premium = captain_premium(
        np.array([90.0, 108.0, 150.0]),
        threshold=107.4,
        gain=0.35,
        exponent=1.25,
        cap=18.0,
    )
    assert premium[0] == 0.0
    assert premium[1] > 0.0
    assert premium[2] < 18.0


def test_forecast_value_uses_expected_games_without_second_probability_fade():
    frame = pd.DataFrame(
        {
            "stable_player_id": ["p", "p"],
            "lead": [1, 1],
            "claude_group": ["MID", "MID"],
            "cond_avg": [100.0, 100.0],
            "exp_games": [10.0, 5.0],
            "p_meaningful": [0.2, 0.9],
        }
    )
    result = forecast_value(
        frame,
        {"MID": 80.0},
        {"threshold": 107.4, "gain": 0.35, "exponent": 1.25, "cap": 18.0},
    )
    assert np.isclose(result.loc[1, "annual_keeper_value_raw"], result.loc[0, "annual_keeper_value_raw"] / 2)


def test_key_position_multiplier_is_applied_once():
    frame = pd.DataFrame(
        {
            "stable_player_id": ["a", "b"],
            "lead": [1, 1],
            "claude_group": ["GEN_FWD", "KEY_FWD"],
            "cond_avg": [90.0, 90.0],
            "exp_games": [10.0, 10.0],
            "p_meaningful": [0.5, 0.5],
        }
    )
    result = forecast_value(
        frame,
        {"GEN_FWD": 70.0, "KEY_FWD": 70.0},
        {"threshold": 107.4, "gain": 0.35, "exponent": 1.25, "cap": 18.0},
    )
    ratio = result.loc[1, "annual_keeper_value_raw"] / result.loc[0, "annual_keeper_value_raw"]
    assert np.isclose(ratio, 1.05)
