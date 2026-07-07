import json
from pathlib import Path

import pandas as pd
import pytest

from benchmark import PREDICTION_KEY, QUANTILE_COLUMNS
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
