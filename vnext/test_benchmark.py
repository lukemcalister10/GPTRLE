import json
from pathlib import Path

import pandas as pd
import pytest

from benchmark import (
    AsOfContract,
    BaselineAdapter,
    LOCKED_FOLDS,
    assert_common_keys_and_targets,
    build_asof_snapshot,
    build_evaluation_cohorts,
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


def test_asof_snapshot_ignores_future_mutations_after_cutoff():
    base = player(scoring=[{"year": 2018, "avg": 70, "games": 10}, {"year": 2020, "avg": 120, "games": 22}])
    contract = AsOfContract(2018, "end_of_2018_season")
    original, fail = build_asof_snapshot(base, contract)
    assert fail is None
    for field, value in {
        "scoring": [{"year": 2018, "avg": 70, "games": 10}, {"year": 2020, "avg": 10, "games": 1}],
        "afl_list_status": "delisted",
        "_retired": True,
        "_club": "ZZZ",
        "present_position": "RUC",
    }.items():
        mutated = dict(base)
        mutated[field] = value
        changed, fail = build_asof_snapshot(mutated, contract)
        assert fail is None
        assert changed == original


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


def test_identical_keys_targets_and_zero_game_outcomes_remain():
    players = [
        player("p1", scoring=[{"year": 2018, "avg": 50, "games": 5}]),
        player("p2", scoring=[{"year": 2018, "avg": 80, "games": 12}, {"year": 2019, "avg": 90, "games": 0}]),
    ]
    cohorts = build_evaluation_cohorts(players, folds={1: [2018]})
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
    cohorts = build_evaluation_cohorts([player("ok"), player("bad", scoring=[{"year": "oops"}])], folds={1: [2018]})
    assert len(cohorts["included"]) == 1
    assert len(cohorts["excluded"]) == 1
    assert cohorts["excluded"].iloc[0]["reason"] == "malformed_scoring_row"


def test_metrics_and_artifacts_are_deterministic(tmp_path: Path):
    cohorts = build_evaluation_cohorts([player("p1"), player("p2", pick=50)], folds={1: [2018]})
    pred = BaselineAdapter().predict(cohorts["included"], cohorts["targets"])
    metrics = score_predictions(pred, cohorts["targets"])
    first = write_benchmark_artifacts(tmp_path / "a", cohorts, {"baseline_recent_scoring": pred}, metrics, ["pytest vnext/test_benchmark.py"])
    second = write_benchmark_artifacts(tmp_path / "b", cohorts, {"baseline_recent_scoring": pred}, metrics, ["pytest vnext/test_benchmark.py"])
    assert json.dumps(first, sort_keys=True).replace(str(tmp_path / "a"), "") == json.dumps(second, sort_keys=True).replace(str(tmp_path / "b"), "")
    assert first["cohort_counts"]["target_rows"] == 2


def test_common_key_assertion_fails_loudly_on_missing_prediction_row():
    cohorts = build_evaluation_cohorts([player("p1"), player("p2")], folds={1: [2018]})
    pred = BaselineAdapter().predict(cohorts["included"], cohorts["targets"]).iloc[:1]
    with pytest.raises(AssertionError):
        assert_common_keys_and_targets({"bad_model": pred}, cohorts["targets"])
