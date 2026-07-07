import json
from pathlib import Path

import pandas as pd

from benchmark import REQUIRED_PREDICTION_COLUMNS, normalise_predictions
from legacy_historical_adapter import (
    FORBIDDEN_INPUT_FIELDS,
    POINT_POLICY,
    ADAPTER_VERSION,
    frame_hash,
    sanitized_legacy_records,
)


def test_legacy_adapter_schema_uses_authoritative_quantile_names():
    assert "points_q10" in REQUIRED_PREDICTION_COLUMNS
    assert "q10_points" not in REQUIRED_PREDICTION_COLUMNS


def test_sanitized_legacy_records_neutralise_current_and_future_fields(monkeypatch):
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
    monkeypatch.setattr("legacy_historical_adapter._all_historical_players", lambda: [source])
    snapshots = pd.DataFrame([{"player_key": "p1", "origin_year": 2018}])
    records = sanitized_legacy_records(snapshots, 2018)
    assert len(records) == 1
    record = records[0]
    for field in FORBIDDEN_INPUT_FIELDS:
        assert field not in record
    assert record["_force_active"] is True
    assert record["drafted_position"] == "MID"
    assert record["scoring"] == [{"year": 2018, "avg": 80.0, "games": 12}]


def test_prediction_schema_accepts_point_adapter_policy_names():
    row = {"player_key": "p1", "origin_year": 2018, "lead": 1}
    for col in REQUIRED_PREDICTION_COLUMNS:
        if col not in row:
            row[col] = 0.0
    row.update({"cond_games": 1.0, "cond_avg": 80.0, "exp_games": 0.0, "exp_points": 0.0})
    pred = normalise_predictions("legacy_frozen", pd.DataFrame([row]))
    assert list(pred.columns)[0] == "model_id"
    assert POINT_POLICY == "legacy_point_distribution_adapter"
    assert ADAPTER_VERSION.startswith("task-003c_")


def test_frame_hash_is_deterministic():
    a = pd.DataFrame([{"player_key": "b", "origin_year": 2018, "lead": 1}, {"player_key": "a", "origin_year": 2018, "lead": 1}])
    b = a.iloc[::-1].reset_index(drop=True)
    assert frame_hash(a) == frame_hash(b)
