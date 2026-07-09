from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import analyse_task048_ridge_uncertainty as audit


def _pred(model: str) -> pd.DataFrame:
    return pd.DataFrame({
        "player_key": ["p1", "p2"], "origin_year": [2020, 2020], "lead": [1, 1],
        "p_meaningful": [0.5, 0.8], "exp_games": [4.0, 10.0], "cond_games": [8.0, 12.0],
        "cond_avg": [50.0, 80.0], "exp_avg": [25.0, 64.0], "exp_points": [200.0, 960.0],
        "points_q10": [0.0, 500.0], "points_q25": [0.0, 700.0], "points_q50": [100.0, 900.0],
        "points_q75": [300.0, 1100.0], "points_q90": [500.0, 1300.0], "points_q97": [700.0, 1500.0],
        "model": model,
    })


def test_pinball_and_calibration_tie_rule_uses_actual_less_equal_predicted_quantile():
    frame = _pred("task047").assign(points=[0.0, 900.0])
    cal = audit.calibration(frame, [])
    q10 = cal[cal["quantile"].eq("points_q10")].iloc[0]
    q50 = cal[cal["quantile"].eq("points_q50")].iloc[0]
    assert q10.empirical_p_actual_le_predicted_quantile == 0.5
    assert q50.empirical_p_actual_le_predicted_quantile == 1.0
    assert q50.tie_rule == "actual_points <= predicted_quantile"


def test_realised_cohort_separates_zero_short_positive_and_meaningful_rows():
    cohorts = list(audit.realised_cohort(pd.Series([0, 3, 6]), pd.Series([0, 12, 500])))
    assert cohorts == ["zero_game_zero_point", "one_to_five_positive_points", "meaningful_six_plus"]


def test_build_audit_rejects_mismatched_keys_before_scoring():
    baseline = _pred("task012")
    candidate = _pred("task047")
    targets = pd.DataFrame({"player_key": ["p1", "different"], "origin_year": [2020, 2020], "lead": [1, 1], "games": [0, 10], "points": [0, 900]})
    features = pd.DataFrame({"key": ["p1", "p2"], "origin_year": [2020, 2020], "position": ["MID", "RUC"], "total_games": [0, 50]})
    try:
        audit.build_audit(baseline, candidate, targets, features)
    except ValueError as exc:
        assert "prediction keys are not identical" in str(exc)
    else:
        raise AssertionError("mismatched target keys must fail")
