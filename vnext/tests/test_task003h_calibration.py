from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest

from analyse_task003h_calibration import classify_origin, summarize_groups


def test_classify_origin_distinguishes_classifier_from_isotonic():
    assert classify_origin(0.60, 0.45, 0.46, 0.01) == "raw_classifier_underpredicts"
    assert classify_origin(0.60, 0.60, 0.52, 0.01) == "isotonic_introduces_underprediction"
    assert classify_origin(0.60, 0.70, 0.52, 0.01) == "isotonic_overcorrects_to_underprediction"


def test_summarize_groups_reports_raw_and_calibrated_bias():
    rows = pd.DataFrame(
        {
            "origin_year": [2020, 2020, 2020, 2020],
            "lead": [1, 1, 1, 1],
            "meaningful": [1, 1, 0, 0],
            "p_meaningful_raw": [0.4, 0.4, 0.4, 0.4],
            "p_meaningful": [0.5, 0.5, 0.5, 0.5],
        }
    )
    summary = summarize_groups(rows, ["origin_year", "lead"], tolerance=0.01)
    assert len(summary) == 1
    row = summary.iloc[0]
    assert row["actual_meaningful_rate"] == 0.5
    assert row["p_meaningful_raw_bias"] == pytest.approx(-0.1)
    assert row["p_meaningful_bias"] == 0.0
    assert row["isotonic_delta_mean"] == pytest.approx(0.1)
