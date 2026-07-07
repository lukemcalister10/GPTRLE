import pandas as pd
import pytest

from run_task003k_comparison import CANDIDATE, CURRENT, invariant_components


def make_row(model_id, p=0.4, games=10.0):
    row = {
        "model_id": model_id,
        "player_key": "p1",
        "origin_year": 2020,
        "lead": 1,
        "p_meaningful": p,
        "cond_games": games,
        "cond_avg": 70.0,
    }
    for threshold in (80, 90, 100, 110, 120):
        row[f"p_avg_ge_{threshold}"] = 0.1
    return row


def test_event_probability_may_change_when_other_components_do_not():
    frame = pd.DataFrame(
        [make_row(CURRENT, p=0.3), make_row(CANDIDATE, p=0.6)]
    )
    assert max(invariant_components(frame).values()) == 0.0


def test_conditional_change_is_rejected():
    frame = pd.DataFrame(
        [make_row(CURRENT), make_row(CANDIDATE, games=11.0)]
    )
    with pytest.raises(ValueError):
        invariant_components(frame)
