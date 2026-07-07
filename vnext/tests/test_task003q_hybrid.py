import numpy as np
import pandas as pd

from task003q_hybrid import blend_predictions, blend_weight


def test_blend_weight_policy():
    ages = np.array([26, 27, 28, 29, 30, 31, 32], dtype=float)
    short = blend_weight(ages, np.ones_like(ages, dtype=int))
    long = blend_weight(ages, np.full_like(ages, 5, dtype=int))
    assert np.allclose(short, [1, 1, 1, .75, .5, .25, 0])
    assert np.allclose(long, [1, .5, 0, 0, 0, 0, 0])


def test_blend_predictions_changes_only_blend_columns():
    current = pd.DataFrame({
        "player_key": ["a"], "origin_year": [2020], "lead": [1],
        "p_meaningful": [.2], "exp_games": [2.0], "exp_points": [100.0],
        "exp_avg": [50.0],
    })
    candidate = current.copy()
    candidate[["p_meaningful", "exp_games", "exp_points"]] = [.6, 6.0, 300.0]
    snapshots = pd.DataFrame({"player_key": ["a"], "origin_year": [2020], "age": [30.0]})
    out = blend_predictions(current, candidate, snapshots)
    assert np.isclose(out.loc[0, "task003q_weight"], .5)
    assert np.isclose(out.loc[0, "p_meaningful"], .4)
    assert np.isclose(out.loc[0, "exp_games"], 4.0)
    assert np.isclose(out.loc[0, "exp_points"], 200.0)
    assert np.isclose(out.loc[0, "exp_avg"], 50.0)
