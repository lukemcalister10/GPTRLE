import numpy as np
import pandas as pd
import pytest

import model_artifacts_joint_season_distribution as task050
from model_artifacts_joint_season_distribution import (
    ALL_POOL,
    MeaningfulResidualPool,
    ShortResidualPool,
    allocate_state_counts,
    predict_with_diagnostics,
    seed_for,
    state_target,
)


class IdentityPreprocessor:
    def transform(self, rows):
        return np.zeros((len(rows), 1), dtype=float)


class FixedStateModel:
    classes_ = np.array([0, 1, 2])

    def predict_proba(self, rows):
        return np.tile(np.array([[0.20, 0.30, 0.50]]), (len(rows), 1))


class FixedShortRateModel:
    def predict(self, rows):
        return np.full(len(rows), np.log(60.0), dtype=float)


class FakeTask047:
    selected_avg_alpha = 10.0



def rows():
    return pd.DataFrame(
        {
            "player_key": ["a", "b"],
            "origin_year": [2020, 2020],
            "lead": [1, 1],
            "position": ["MID", "RUC"],
            "pick": [10, 30],
            "tenure": [3, 2],
            "age": [24, 23],
            "total_games": [50, 25],
            "qualifying_seasons": [2, 1],
            "last_avg": [90, 80],
            "last_games": [20, 15],
            "prev_avg": [85, 75],
            "prev_games": [18, 12],
            "weighted_avg": [88, 78],
            "career_best": [95, 85],
            "recent_best": [95, 85],
            "avg_trend": [2, 3],
            "games_last_2": [38, 27],
            "seasons_observed": [3, 2],
            "draft_type": ["ND", "ND"],
        }
    )



def fake_artifact():
    short = ShortResidualPool(
        games=np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        log_rate_residuals=np.array([-0.1, -0.05, 0.0, 0.05, 0.1]),
    )
    meaningful = MeaningfulResidualPool(
        games_residuals=np.array([-2.0, -1.0, 0.0, 1.0, 2.0]),
        avg_residuals=np.array([-8.0, -4.0, 0.0, 4.0, 8.0]),
    )
    return task050.JointSeasonArtifact(
        lead=1,
        state_preprocessor=IdentityPreprocessor(),
        state_model=FixedStateModel(),
        selected_state_c=0.3,
        state_c_scores={0.3: 1.0},
        short_rate_model=FixedShortRateModel(),
        selected_short_alpha=10.0,
        short_alpha_scores={10.0: 5.0},
        short_pools={ALL_POOL: short},
        meaningful_pools={ALL_POOL: meaningful},
        task047_artifact=FakeTask047(),
        games_resid_sd=2.0,
        avg_resid_sd=8.0,
        train_max_origin=2017,
        n_fit=100,
        n_cal=50,
    )



def test_seed_and_sample_contract():
    assert task050.SAMPLE_COUNT == 4096
    assert seed_for("player-a", 2020, 3) == 1482170304
    assert task050.SEED_PREFIX == "TASK-050"



def test_allocate_state_counts_preserves_total_and_positive_support():
    counts = allocate_state_counts(np.array([0.9998, 0.0001, 0.0001]), 4096)
    assert counts.sum() == 4096
    assert (counts > 0).all()
    assert counts[0] > counts[1]



def test_state_target_has_exact_three_state_contract():
    frame = pd.DataFrame(
        {
            "key": ["z", "s", "m"],
            "origin_year": [2010, 2010, 2010],
            "l1_games": [0, 4, 8],
            "l1_points": [0.0, 200.0, 700.0],
        }
    )
    assert state_target(frame, 1).tolist() == [0, 1, 2]
    bad = frame.copy()
    bad.loc[1, "l1_points"] = 0.0
    with pytest.raises(ValueError, match="unsupported season-state"):
        state_target(bad, 1)



def test_joint_draws_are_deterministic_coherent_and_supported(monkeypatch):
    def fake_task047_predict(_artifact, input_rows):
        return pd.DataFrame(
            {
                "cond_games": np.full(len(input_rows), 12.0),
                "cond_avg": np.full(len(input_rows), 80.0),
            },
            index=input_rows.index,
        )

    monkeypatch.setattr(task050, "predict_task047", fake_task047_predict)
    artifact = fake_artifact()
    prediction, diagnostics = predict_with_diagnostics(artifact, rows())
    prediction_2, diagnostics_2 = predict_with_diagnostics(artifact, rows())

    pd.testing.assert_frame_equal(prediction, prediction_2)
    pd.testing.assert_frame_equal(diagnostics, diagnostics_2)

    assert np.allclose(
        diagnostics[["draw_p_zero", "draw_p_short", "draw_p_meaningful"]].sum(axis=1),
        1.0,
    )
    assert (diagnostics[["zero_draw_count", "short_draw_count", "meaningful_draw_count"]] > 0).all(axis=None)
    assert diagnostics.short_games_min.between(1, 5).all()
    assert diagnostics.short_games_max.between(1, 5).all()
    assert diagnostics.short_points_min.gt(0).all()
    assert diagnostics.meaningful_games_min.between(6, 23).all()
    assert diagnostics.meaningful_games_max.between(6, 23).all()
    assert diagnostics.threshold_monotonic.eq(1).all()

    assert np.allclose(prediction.p_meaningful, diagnostics.draw_p_meaningful)
    assert np.allclose(prediction.exp_games, diagnostics.draw_exp_games)
    assert np.allclose(prediction.exp_points, diagnostics.draw_exp_points)

    quantiles = prediction[task050.QUANTILE_COLUMNS].to_numpy(float)
    assert (quantiles >= 0).all()
    assert (np.diff(quantiles, axis=1) >= -1e-12).all()
    threshold_columns = [f"p{threshold}" for threshold in task050.TH]
    thresholds = prediction[threshold_columns].to_numpy(float)
    assert (np.diff(thresholds, axis=1) <= 1e-12).all()



def test_joint_prediction_is_not_forced_to_task047_mean(monkeypatch):
    def fake_task047_predict(_artifact, input_rows):
        return pd.DataFrame(
            {
                "cond_games": np.full(len(input_rows), 12.0),
                "cond_avg": np.full(len(input_rows), 80.0),
                "exp_points": np.full(len(input_rows), 9999.0),
            },
            index=input_rows.index,
        )

    monkeypatch.setattr(task050, "predict_task047", fake_task047_predict)
    prediction, _ = predict_with_diagnostics(fake_artifact(), rows())
    assert not np.allclose(prediction.exp_points, 9999.0)



def test_invalid_state_probabilities_fail_loudly():
    with pytest.raises(ValueError):
        allocate_state_counts(np.array([0.5, np.nan, 0.5]), 4096)
    with pytest.raises(ValueError):
        allocate_state_counts(np.array([0.5, -0.1, 0.6]), 4096)
