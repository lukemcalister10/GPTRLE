import json
from pathlib import Path

import pandas as pd
import pytest

from benchmark import PREDICTION_KEY, QUANTILE_COLUMNS, assert_common_keys_and_targets
from comparison_harness import load_external_predictions
from run_comparison import run_comparison


def test_baseline_harness_covers_locked_cohort(tmp_path: Path):
    manifest = run_comparison(tmp_path / "run")
    assert manifest["models"] == ["baseline_recent_scoring"]
    assert manifest["expected_rows_per_model"] == 20094
    assert manifest["cohort_target_rows"] == 20094

    predictions = pd.read_csv(tmp_path / "run" / "baseline_predictions.csv")
    targets = pd.read_csv(tmp_path / "run" / "cohorts" / "targets.csv")
    assert len(predictions) == len(targets) == 20094
    assert list(QUANTILE_COLUMNS) == [
        "points_q10",
        "points_q25",
        "points_q50",
        "points_q75",
        "points_q90",
        "points_q97",
    ]
    assert predictions[PREDICTION_KEY].equals(targets[PREDICTION_KEY])

    key_report = json.loads((tmp_path / "run" / "key_validation.json").read_text())
    assert key_report["models"]["baseline_recent_scoring"]["exact_target_key_match"]


def test_external_prediction_contract_accepts_exact_clone_and_rejects_missing_key(tmp_path: Path):
    run_comparison(tmp_path / "base")
    baseline = pd.read_csv(tmp_path / "base" / "baseline_predictions.csv")
    targets = pd.read_csv(tmp_path / "base" / "cohorts" / "targets.csv")
    external_path = tmp_path / "vnext_predictions.csv"
    baseline.drop(columns=["model_id"]).to_csv(external_path, index=False)

    external = load_external_predictions(external_path, "vnext_artifact")
    assert_common_keys_and_targets({"vnext_artifact": external}, targets)

    missing_path = tmp_path / "missing.csv"
    baseline.drop(columns=["model_id"]).iloc[:-1].to_csv(missing_path, index=False)
    missing = load_external_predictions(missing_path, "vnext_artifact")
    with pytest.raises(AssertionError, match="prediction keys differ"):
        assert_common_keys_and_targets({"vnext_artifact": missing}, targets)


def test_wrong_quantile_name_is_rejected(tmp_path: Path):
    run_comparison(tmp_path / "base")
    baseline = pd.read_csv(tmp_path / "base" / "baseline_predictions.csv")
    bad = baseline.drop(columns=["model_id"]).rename(columns={"points_q10": "q10_points"})
    path = tmp_path / "bad.csv"
    bad.to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        load_external_predictions(path, "vnext_artifact")
