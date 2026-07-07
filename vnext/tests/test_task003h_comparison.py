import pandas as pd
import pytest

from run_task003h_comparison import (
    CANDIDATE_MODEL_ID,
    CURRENT_MODEL_ID,
    probability_invariance,
    slice_differences,
)


def _prediction(model_id: str, p: float) -> dict:
    row = {
        "model_id": model_id,
        "player_key": "p1",
        "origin_year": 2020,
        "lead": 1,
        "p_meaningful": p,
    }
    for threshold in (80, 90, 100, 110, 120):
        row[f"p_avg_ge_{threshold}"] = 0.1
    return row


def test_probability_invariance_accepts_identical_probability_outputs():
    predictions = pd.DataFrame(
        [_prediction(CURRENT_MODEL_ID, 0.4), _prediction(CANDIDATE_MODEL_ID, 0.4)]
    )
    result = probability_invariance(predictions)
    assert result["p_meaningful"] == 0.0


def test_probability_invariance_rejects_event_model_changes():
    predictions = pd.DataFrame(
        [_prediction(CURRENT_MODEL_ID, 0.4), _prediction(CANDIDATE_MODEL_ID, 0.5)]
    )
    with pytest.raises(ValueError, match="changed probability outputs"):
        probability_invariance(predictions)


def test_slice_differences_use_current_vnext_as_baseline():
    rows = []
    for model_id, mae in [(CURRENT_MODEL_ID, 100.0), (CANDIDATE_MODEL_ID, 90.0)]:
        rows.append(
            {
                "model_id": model_id,
                "lead": 1,
                "slice_type": "position",
                "slice_value": "RUC",
                "n": 200,
                "brier_meaningful": 0.2,
                "mae_games": 5.0,
                "mae_total_points": mae,
            }
        )
    result = slice_differences(pd.DataFrame(rows))
    assert result["mae_total_points_change"].item() == -10.0
    assert result["mae_total_points_change_pct"].item() == -10.0
