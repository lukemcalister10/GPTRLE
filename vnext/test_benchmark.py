import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from benchmark import (
    AsOfContract,
    BaselineAdapter,
    EligibilityDecision,
    StaticEligibilityResolver,
    calibration_intercept_slope,
    LOCKED_FOLDS,
    QUANTILE_COLUMNS,
    REQUIRED_PREDICTION_COLUMNS,
    assert_common_keys_and_targets,
    build_asof_snapshot,
    build_evaluation_cohorts,
    normalise_predictions,
    score_predictions,
    write_benchmark_artifacts,
)


def player(key="p1", scoring=None, **extra):
    data = {
        "key": key,
        "player": key.upper(),
        "year": 2017,
        "pick": 10,
        "type": "ND",
        "drafted_position": "MID",
        "_by": 1999,
        "scoring": scoring if scoring is not None else [
            {"year": 2018, "avg": 60, "games": 8},
            {"year": 2019, "avg": 90, "games": 20},
            {"year": 2020, "avg": 100, "games": 22},
        ],
    }
    data.update(extra)
    return data


def eligible(players, origins=(2018,), value=True):
    return StaticEligibilityResolver({(p["key"], y): value for p in players for y in origins})


def prediction_frame(**overrides):
    row = {
        "player_key": "p1",
        "origin_year": 2018,
        "lead": 1,
        "p_meaningful": 0.5,
        "cond_games": 10.0,
        "cond_avg": 80.0,
        "exp_games": 5.0,
        "exp_points": 400.0,
        "p_avg_ge_80": 0.4,
        "p_avg_ge_90": 0.3,
        "p_avg_ge_100": 0.2,
        "p_avg_ge_110": 0.1,
        "p_avg_ge_120": 0.05,
        "points_q10": 400.0,
        "points_q25": 400.0,
        "points_q50": 400.0,
        "points_q75": 400.0,
        "points_q90": 400.0,
        "points_q97": 400.0,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_asof_snapshot_ignores_future_mutations_after_cutoff():
    base = player(scoring=[{"year": 2018, "avg": 70, "games": 10}, {"year": 2020, "avg": 120, "games": 22}], surprise_current_field="ignored")
    contract = AsOfContract(2018, "end_of_2018_season")
    original, fail = build_asof_snapshot(base, contract)
    assert fail is None
    for field, value in {
        "scoring": [{"year": 2018, "avg": 70, "games": 10}, {"year": 2020, "avg": 10, "games": 1}],
        "afl_list_status": "delisted",
        "_retired": True,
        "_club": "ZZZ",
        "present_position": "RUC",
        "unknown_future_field": "ignored",
    }.items():
        mutated = dict(base)
        mutated[field] = value
        changed, fail = build_asof_snapshot(mutated, contract)
        assert fail is None
        assert changed == original


def test_malformed_post_origin_scoring_is_ignored_but_origin_data_fails():
    contract = AsOfContract(2018, "end_of_2018_season")
    ok, fail = build_asof_snapshot(player(scoring=[{"year": 2018, "avg": 70, "games": 10}, {"year": 2019, "avg": "bad", "games": "bad"}]), contract)
    assert fail is None
    assert ok["last_avg"] == 70 and ok["last_games"] == 10
    bad, fail = build_asof_snapshot(player(scoring=[{"year": 2018, "avg": "bad", "games": 10}]), contract)
    assert bad is None
    assert fail["reason"] == "malformed_scoring_row"


def test_future_season_games_change_cannot_change_earlier_snapshot():
    contract = AsOfContract(2018, "end_of_2018_season")
    a, _ = build_asof_snapshot(player(scoring=[{"year": 2018, "avg": 70, "games": 10}, {"year": 2019, "avg": 90, "games": 22}]), contract)
    b, _ = build_asof_snapshot(player(scoring=[{"year": 2018, "avg": 70, "games": 10}, {"year": 2019, "avg": 0, "games": 0}]), contract)
    assert a == b


def test_locked_rolling_origin_folds_match_protocol():
    assert LOCKED_FOLDS[1] == list(range(2018, 2025))
    assert LOCKED_FOLDS[5] == list(range(2018, 2021))
    for lead, origins in LOCKED_FOLDS.items():
        assert all(origin + lead <= 2025 for origin in origins)


def test_eligibility_required_and_retired_player_excluded():
    active = player("active")
    retired = player("retired")
    resolver = StaticEligibilityResolver({("active", 2018): True, ("retired", 2018): EligibilityDecision(False, "retired_before_origin")})
    cohorts = build_evaluation_cohorts([active, retired], folds={1: [2018]}, eligibility_resolver=resolver)
    assert cohorts["included"]["player_key"].tolist() == ["active"]
    assert cohorts["targets"]["player_key"].tolist() == ["active"]
    assert cohorts["excluded"].iloc[0]["reason"] == "retired_before_origin"


def test_missing_historical_eligibility_prevents_definitive_benchmark():
    with pytest.raises(ValueError, match="historical eligibility unavailable"):
        build_evaluation_cohorts([player("p1")], folds={1: [2018]})
    cohorts = build_evaluation_cohorts([player("p1")], folds={1: [2018]}, fail_on_unavailable_eligibility=False)
    assert cohorts["excluded"].iloc[0]["reason"] == "historical_eligibility_unavailable"


def test_identical_keys_targets_and_zero_game_outcomes_remain():
    players = [
        player("p1", scoring=[{"year": 2018, "avg": 50, "games": 5}]),
        player("p2", scoring=[{"year": 2018, "avg": 80, "games": 12}, {"year": 2019, "avg": 90, "games": 0}]),
    ]
    cohorts = build_evaluation_cohorts(players, folds={1: [2018]}, eligibility_resolver=eligible(players))
    assert len(cohorts["targets"]) == 2
    assert (cohorts["targets"]["games"] == 0).any()
    pred_a = BaselineAdapter("baseline_a").predict(cohorts["included"], cohorts["targets"])
    pred_b = pred_a.assign(model_id="baseline_b")
    assert_common_keys_and_targets({"baseline_a": pred_a, "baseline_b": pred_b}, cohorts["targets"])
    pd.testing.assert_frame_equal(
        pred_a[["player_key", "origin_year", "lead"]].reset_index(drop=True),
        pred_b[["player_key", "origin_year", "lead"]].reset_index(drop=True),
    )


def test_row_failures_are_reported_not_silently_ignored():
    players = [player("ok"), player("bad", scoring=[{"year": "oops"}])]
    cohorts = build_evaluation_cohorts(players, folds={1: [2018]}, eligibility_resolver=eligible(players))
    assert len(cohorts["included"]) == 1
    assert len(cohorts["excluded"]) == 1
    assert cohorts["excluded"].iloc[0]["reason"] == "malformed_scoring_year"


def test_logistic_calibration_well_calibrated_is_intercept_zero_slope_one():
    y = pd.Series([0] * 80 + [1] * 20 + [0] * 20 + [1] * 80)
    p = pd.Series([0.2] * 100 + [0.8] * 100)
    intercept, slope = calibration_intercept_slope(y, p)
    assert intercept == pytest.approx(0.0, abs=1e-3)
    assert slope == pytest.approx(1.0, abs=1e-3)


def test_metrics_use_conditional_average_and_matching_quantiles():
    targets = pd.DataFrame([{"player_key": "p1", "origin_year": 2018, "lead": 1, "games": 10, "avg": 80.0, "points": 800.0, "meaningful": 1, "avg_ge_80": 1, "avg_ge_90": 0, "avg_ge_100": 0, "avg_ge_110": 0, "avg_ge_120": 0}])
    pred = normalise_predictions("m", prediction_frame(p_meaningful=0.5, cond_avg=80.0, exp_points=400.0, points_q10=100.0, points_q25=200.0, points_q50=300.0, points_q75=400.0, points_q90=500.0, points_q97=600.0)).assign(model_id="m")
    metrics = score_predictions(pred, targets)
    assert metrics.iloc[0]["mae_avg_conditional_meaningful"] == 0.0
    assert metrics.iloc[0]["pinball_points_q10"] == pytest.approx(70.0)
    assert metrics.iloc[0]["pinball_points_q97"] == pytest.approx(194.0)


def test_prediction_validation_missing_duplicate_invalid_probability_and_crossing_quantiles():
    with pytest.raises(ValueError, match="missing columns"):
        normalise_predictions("m", prediction_frame().drop(columns=["p_avg_ge_120"]))
    with pytest.raises(ValueError, match="duplicate keys"):
        normalise_predictions("m", pd.concat([prediction_frame(), prediction_frame()], ignore_index=True))
    with pytest.raises(ValueError, match=r"outside \[0, 1\]"):
        normalise_predictions("m", prediction_frame(p_meaningful=1.5))
    with pytest.raises(ValueError, match="crossing point quantiles"):
        normalise_predictions("m", prediction_frame(points_q10=500.0, points_q25=400.0))
    with pytest.raises(ValueError, match="non-monotonic threshold"):
        normalise_predictions("m", prediction_frame(p_avg_ge_90=0.7))


def test_baseline_emits_required_prediction_schema_and_degenerate_quantiles():
    players = [player("p1")]
    cohorts = build_evaluation_cohorts(players, folds={1: [2018]}, eligibility_resolver=eligible(players))
    pred = BaselineAdapter().predict(cohorts["included"], cohorts["targets"])
    assert set(REQUIRED_PREDICTION_COLUMNS).issubset(pred.columns)
    assert all((pred[col] == pred["exp_points"]).all() for col in QUANTILE_COLUMNS)


def test_metrics_and_artifacts_are_deterministic(tmp_path: Path):
    players = [player("p1"), player("p2", pick=50)]
    cohorts = build_evaluation_cohorts(players, folds={1: [2018]}, eligibility_resolver=eligible(players))
    pred = BaselineAdapter().predict(cohorts["included"], cohorts["targets"])
    metrics = score_predictions(pred, cohorts["targets"])
    first = write_benchmark_artifacts(tmp_path / "a", cohorts, {"baseline_recent_scoring": pred}, metrics, ["pytest vnext/test_benchmark.py"])
    second = write_benchmark_artifacts(tmp_path / "b", cohorts, {"baseline_recent_scoring": pred}, metrics, ["pytest vnext/test_benchmark.py"])
    assert json.dumps(first, sort_keys=True).replace(str(tmp_path / "a"), "") == json.dumps(second, sort_keys=True).replace(str(tmp_path / "b"), "")
    assert first["cohort_counts"]["target_rows"] == 2


def test_common_key_assertion_fails_loudly_on_missing_prediction_row():
    players = [player("p1"), player("p2")]
    cohorts = build_evaluation_cohorts(players, folds={1: [2018]}, eligibility_resolver=eligible(players))
    pred = BaselineAdapter().predict(cohorts["included"], cohorts["targets"]).iloc[:1]
    with pytest.raises(AssertionError):
        assert_common_keys_and_targets({"bad_model": pred}, cohorts["targets"])
