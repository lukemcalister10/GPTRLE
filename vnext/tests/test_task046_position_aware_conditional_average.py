from __future__ import annotations

import numpy as np
import pandas as pd

import model_artifacts_position_aware_conditional_average as task046


class DummyPreprocessor:
    def transform(self, rows):
        return np.arange(len(rows), dtype=float).reshape(-1, 1)


class DummyModel:
    def __init__(self, value):
        self.value = value

    def predict(self, x):
        return np.full(x.shape[0], self.value, dtype=float)


def test_broad_position_values_normalises_missing_and_blank_positions():
    rows = pd.DataFrame({"position": [" ruc ", "", None, "nan", "MID"]})
    assert task046.broad_position_values(rows).tolist() == ["RUC", "UNK", "UNK", "UNK", "MID"]


def test_position_specific_prediction_uses_pooled_fallback_for_unfitted_position():
    layer = task046.PositionAwareAvgLayer(
        preprocessor=DummyPreprocessor(),
        pooled_model=DummyModel(70),
        position_models={"RUC": DummyModel(95)},
        residual_sd=12,
        iterations=1,
        position_training_rows={"RUC": 100, "DEF": 12},
        fallback_positions={"DEF": "pooled_insufficient_position_rows"},
    )
    rows = pd.DataFrame({"position": ["RUC", "DEF", "MID"]})
    assert task046._predict_avg(layer, rows).tolist() == [95.0, 70.0, 70.0]


def test_current_board_changes_require_complete_804_player_rollup(tmp_path):
    path = tmp_path / "rollup.csv"
    pd.DataFrame({"stable_player_id": ["only-one"]}).to_csv(path, index=False)
    from analyse_task046_position_aware import _current_board_changes

    try:
        _current_board_changes(path)
    except ValueError as exc:
        assert "missing required columns" in str(exc)
    else:
        raise AssertionError("incomplete current-board rollup must fail")
