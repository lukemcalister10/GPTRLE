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


def test_select_ridge_alpha_breaks_ties_toward_smaller_alpha():
    assert task047.select_ridge_alpha({30.0: 8.0, 10.0: 8.0, 3.0: 8.1}) == 10.0


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

from analyse_task047_pooled_ridge import build_tables


def _prediction_rows(model: str, cond_avgs: list[float], exp_points: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player_key": ["a", "b"],
            "origin_year": [2020, 2020],
            "lead": [1, 1],
            "p_meaningful": [0.5, 0.25],
            "exp_games": [5.0, 2.0],
            "cond_games": [10.0, 8.0],
            "cond_avg": cond_avgs,
            "exp_avg": [0.5 * cond_avgs[0], 0.25 * cond_avgs[1]],
            "exp_points": exp_points,
            "p_avg_ge_80": [0.2, 0.1],
            "p_avg_ge_90": [0.1, 0.05],
            "points_q10": [0.0, 0.0],
            "points_q50": [100.0 + exp_points[0], 50.0 + exp_points[1]],
            "points_q90": [200.0 + exp_points[0], 100.0 + exp_points[1]],
            "model": model,
        }
    )


def test_analysis_adds_expected_points_invariants_and_uncertainty_blocker(tmp_path):
    targets = pd.DataFrame(
        {
            "player_key": ["a", "b"],
            "origin_year": [2020, 2020],
            "lead": [1, 1],
            "games": [10.0, 2.0],
            "avg": [80.0, 25.0],
            "points": [800.0, 50.0],
            "meaningful": [True, False],
        }
    )
    features = pd.DataFrame(
        {
            "key": ["a", "b"],
            "origin_year": [2020, 2020],
            "position": ["MID", "RUC"],
            "total_games": [60, 5],
            "weighted_avg": [82.0, 40.0],
            "last_avg": [80.0, 0.0],
            "career_best": [90.0, 0.0],
        }
    )
    alpha_path = tmp_path / "alpha.csv"
    pd.DataFrame({"lead": [1], "origin_year": [2020], "selected_alpha": [10.0], "alpha_scores_json": ["{}"]}).to_csv(alpha_path, index=False)

    _, tables, _ = build_tables(
        _prediction_rows("task012", [70.0, 55.0], [700.0, 25.0]),
        _prediction_rows("task047", [82.0, 60.0], [820.0, 30.0]),
        targets,
        features,
        alpha_by_fold=alpha_path,
    )

    points = tables["expected_points_whole_population"].set_index("model")
    assert points.loc["task012", "mae"] == 62.5
    assert points.loc["task047", "mae"] == 20.0

    invariants = tables["unchanged_output_invariants"].set_index("column")
    assert invariants.loc["p_meaningful", "max_abs_delta"] == 0.0
    assert invariants.loc["cond_games", "violations_gt_1e_12"] == 0

    blocker = tables["uncertainty_acceptance_blocker"].iloc[0]
    assert blocker["status"] == "blocked_for_acceptance"
    assert "quantile calibration" in blocker["reason"]

    uncertainty = tables["uncertainty_output_changes_by_lead"]
    assert set(uncertainty["quantile"]) == {"points_q10", "points_q50", "points_q90"}
