import numpy as np
import pandas as pd
import pytest

import analyse_task050_joint_season_distribution as audit


def wide_predictions():
    frame = pd.DataFrame(
        {
            "player_key": ["a", "a", "b"],
            "origin_year": [2018, 2019, 2018],
            "lead": [1, 1, 1],
            "points": [10.0, 20.0, 30.0],
        }
    )
    for column in audit.QCOLS:
        frame[f"{column}_task047"] = frame.points
        frame[f"{column}_task050"] = frame.points
    frame["points_q10_task047"] = 0.0
    frame["points_q10_task050"] = [1.0, 2.0, 3.0]
    return frame


def test_bootstrap_observed_statistic_is_pooled_row_weighted():
    confidence, invariant = audit.bootstrap_metrics(
        wide_predictions(), reps=20, seed=audit.BOOTSTRAP_SEED
    )
    expected_q10_difference = np.mean([-0.1, -0.2, -0.3])
    q10 = confidence.loc[confidence.metric.eq("points_q10")].iloc[0]
    primary = confidence.loc[
        confidence.metric.eq("primary_mean_pinball")
    ].iloc[0]
    assert q10.observed_diff_task050_minus_task047 == pytest.approx(
        expected_q10_difference
    )
    assert primary.observed_diff_task050_minus_task047 == pytest.approx(
        expected_q10_difference / len(audit.QCOLS)
    )
    assert invariant.absolute_delta.max() <= 1e-12


def candidate_and_diagnostics():
    candidate = pd.DataFrame(
        {
            "player_key": ["a"],
            "origin_year": [2018],
            "lead": [1],
            "p_meaningful": [0.5],
            "cond_games": [12.0],
            "cond_avg": [80.0],
            "exp_games": [7.0],
            "exp_points": [560.0],
            **{f"p_avg_ge_{threshold}": [0.1] for threshold in audit.THRESHOLDS},
            **{column: [float(index * 100)] for index, column in enumerate(audit.QCOLS)},
        }
    )
    diagnostics = pd.DataFrame(
        {
            "player_key": ["a"],
            "origin_year": [2018],
            "lead": [1],
            "draw_p_meaningful": [0.5],
            "draw_cond_games": [12.0],
            "draw_cond_avg": [80.0],
            "draw_exp_games": [7.0],
            "draw_exp_points": [560.0],
            "state_probability_max_abs_discretization_error": [1 / 4096],
            "short_games_min": [1.0],
            "short_games_max": [5.0],
            "short_points_min": [10.0],
            "meaningful_games_min": [6.0],
            "meaningful_games_max": [23.0],
            "threshold_monotonic": [1],
            **{f"draw_p{threshold}": [0.1] for threshold in audit.THRESHOLDS},
            **{
                f"draw_{column}": [float(index * 100)]
                for index, column in enumerate(audit.QCOLS)
            },
        }
    )
    return candidate, diagnostics


def test_draw_reconciliation_is_aggregate_and_exact():
    candidate, diagnostics = candidate_and_diagnostics()
    summary = audit.draw_reconciliation_summary(candidate, diagnostics)
    assert len(summary) == 2
    overall = summary.iloc[-1]
    assert overall.origin_year == "ALL"
    assert overall.max_output_draw_abs_delta == pytest.approx(0.0)
    assert overall.min_short_games == 1.0
    assert overall.max_meaningful_games == 23.0


def test_draw_reconciliation_surfaces_mismatch():
    candidate, diagnostics = candidate_and_diagnostics()
    candidate.loc[0, "exp_points"] += 1.0
    summary = audit.draw_reconciliation_summary(candidate, diagnostics)
    assert summary.iloc[-1].max_output_draw_abs_delta == pytest.approx(1.0)


def test_weighted_interval_score_rewards_exact_distribution():
    exact = pd.DataFrame(
        {
            "points": [100.0],
            "points_q10": [100.0],
            "points_q25": [100.0],
            "points_q50": [100.0],
            "points_q75": [100.0],
            "points_q90": [100.0],
        }
    )
    assert audit.weighted_interval_score(exact).iloc[0] == pytest.approx(0.0)
