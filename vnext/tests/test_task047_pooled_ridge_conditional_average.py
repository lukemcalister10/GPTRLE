from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.linear_model import Ridge

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import model_artifacts_pooled_ridge_conditional_average as task047
from analyse_task047_pooled_ridge import _current_board_changes


def test_task047_declares_small_fold_local_ridge_alpha_grid():
    assert task047.RIDGE_ALPHA_GRID == (0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0)


def test_avg_layer_records_ridge_model_and_selected_alpha():
    layer = task047.AvgLayer(
        preprocessor=object(),
        model=Ridge(alpha=10.0),
        residual_sd=12.0,
        selected_alpha=10.0,
        alpha_scores={3.0: 9.5, 10.0: 9.0},
    )
    assert isinstance(layer.model, Ridge)
    assert layer.selected_alpha == 10.0
    assert layer.alpha_scores[10.0] < layer.alpha_scores[3.0]


def test_current_board_changes_require_complete_804_player_rollup(tmp_path):
    path = tmp_path / "rollup.csv"
    pd.DataFrame({"stable_player_id": ["only-one"]}).to_csv(path, index=False)
    try:
        _current_board_changes(path)
    except ValueError as exc:
        assert "missing required columns" in str(exc)
    else:
        raise AssertionError("incomplete current-board rollup must fail")
