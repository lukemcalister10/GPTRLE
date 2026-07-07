import pandas as pd

from benchmark import REQUIRED_PREDICTION_COLUMNS, normalise_predictions
from legacy_historical_adapter import (
    ADAPTER_VERSION,
    BLOCKERS,
    DIAGNOSTIC_MODEL_ID,
    FORBIDDEN_INPUT_FIELDS,
    FORMAL_BENCHMARK_ELIGIBLE,
    FORMAL_MODEL_ID,
    POINT_POLICY,
    frame_hash,
    runtime_dependency_report,
    sanitized_legacy_records,
)


def test_legacy_schema_uses_authoritative_quantile_names():
    assert "points_q10" in REQUIRED_PREDICTION_COLUMNS
    assert "q10_points" not in REQUIRED_PREDICTION_COLUMNS


def test_sanitized_records_neutralise_current_and_future_fields(monkeypatch):
    source = {
        "key": "p1",
        "player": "Player One",
        "year": 2016,
        "pick": 10,
        "type": "ND",
        "_draft": "ND",
        "drafted_position": "MID",
        "present_position": "RUC",
        "future_position": "RUC",
        "_club": "Future Club",
        "_retired": True,
        "_last_listed": 2026,
        "scoring": [
            {"year": 2018, "avg": 80, "games": 12},
            {"year": 2019, "avg": 200, "games": 22},
        ],
    }
    monkeypatch.setattr(
        "legacy_historical_adapter._all_historical_players",
        lambda: [source],
    )
    snapshots = pd.DataFrame([{"player_key": "p1", "origin_year": 2018}])
    records = sanitized_legacy_records(snapshots, 2018)
    assert len(records) == 1
    record = records[0]
    for field in FORBIDDEN_INPUT_FIELDS:
        assert field not in record
    assert record["_force_active"] is True
    assert record["drafted_position"] == "MID"
    assert record["scoring"] == [
        {"year": 2018, "avg": 80.0, "games": 12}
    ]


def test_proxy_uses_diagnostic_model_id_and_is_not_formal_legacy():
    row = {"player_key": "p1", "origin_year": 2018, "lead": 1}
    for column in REQUIRED_PREDICTION_COLUMNS:
        if column not in row:
            row[column] = 0.0
    row.update(
        {
            "cond_games": 1.0,
            "cond_avg": 80.0,
            "exp_games": 0.0,
            "exp_points": 0.0,
        }
    )
    prediction = normalise_predictions(
        DIAGNOSTIC_MODEL_ID,
        pd.DataFrame([row]),
    )
    assert prediction["model_id"].iloc[0] == "legacy_diagnostic_proxy"
    assert FORMAL_MODEL_ID == "legacy_frozen"
    assert FORMAL_BENCHMARK_ELIGIBLE is False
    assert POINT_POLICY == "legacy_point_distribution_diagnostic_proxy"
    assert ADAPTER_VERSION.endswith("_v2")


def test_blockers_are_explicit_and_runtime_dependencies_are_classified():
    codes = {blocker["code"] for blocker in BLOCKERS}
    assert codes == {
        "no_horizon_specific_frozen_forecast",
        "learned_assets_without_origin_cutoff",
        "wrapper_constructed_probability_outputs",
    }
    dependencies = runtime_dependency_report()
    by_name = {row["path"].split("/")[-1]: row for row in dependencies}
    for filename in (
        "peak_model_v4.pkl",
        "pvc_snapshot.json",
        "bust_prior_table.json",
        "params.json",
        "rl_passmark.json",
    ):
        assert by_name[filename]["classification"] == (
            "blocking_current_learned_asset"
        )
        assert by_name[filename]["asof_origin_cutoff_proven"] is False
    assert by_name["rl_model.py"]["listed_in_frozen_manifest"] is True


def test_frame_hash_is_deterministic():
    first = pd.DataFrame(
        [
            {"player_key": "b", "origin_year": 2018, "lead": 1},
            {"player_key": "a", "origin_year": 2018, "lead": 1},
        ]
    )
    second = first.iloc[::-1].reset_index(drop=True)
    assert frame_hash(first) == frame_hash(second)
