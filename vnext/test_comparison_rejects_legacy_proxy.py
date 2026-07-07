from pathlib import Path

import pandas as pd
import pytest

from comparison_harness import load_external_predictions
from run_comparison import run_comparison


def test_diagnostic_proxy_is_not_accepted_as_legacy_frozen(tmp_path: Path):
    run_comparison(tmp_path / "base")
    baseline = pd.read_csv(tmp_path / "base" / "baseline_predictions.csv")
    diagnostic = baseline.copy()
    diagnostic["model_id"] = "legacy_diagnostic_proxy"
    path = tmp_path / "legacy_diagnostic_predictions.csv"
    diagnostic.to_csv(path, index=False)

    with pytest.raises(ValueError, match="do not match expected legacy_frozen"):
        load_external_predictions(path, "legacy_frozen")

    with pytest.raises(ValueError, match="do not match expected legacy_frozen"):
        run_comparison(tmp_path / "attempt", legacy_predictions=path)
