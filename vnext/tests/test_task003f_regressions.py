import pandas as pd

from analyse_task003e_regressions import material_regressions


def test_material_regressions_rank_severity_and_burden():
    rows = []
    for model_id, age_mae, ruck_mae in [
        ("baseline_recent_scoring", 100.0, 100.0),
        ("vnext_fold_specific", 110.0, 104.0),
    ]:
        rows.extend([
            {"model_id": model_id, "lead": 1, "slice_type": "age_band", "slice_value": "24-26", "n": 100, "mae_total_points": age_mae},
            {"model_id": model_id, "lead": 1, "slice_type": "position", "slice_value": "RUC", "n": 1000, "mae_total_points": ruck_mae},
        ])
    result = material_regressions(pd.DataFrame(rows))
    assert list(result.slice_value) == ["24-26", "RUC"]
    assert list(result.severity_rank) == [1, 2]
    assert result.loc[result.slice_value.eq("RUC"), "burden_rank"].item() == 1


def test_threshold_is_strictly_greater_than_three_percent():
    slices = pd.DataFrame([
        {"model_id": "baseline_recent_scoring", "lead": 1, "slice_type": "position", "slice_value": "DEF", "n": 10, "mae_total_points": 100.0},
        {"model_id": "vnext_fold_specific", "lead": 1, "slice_type": "position", "slice_value": "DEF", "n": 10, "mae_total_points": 103.0},
    ])
    assert material_regressions(slices).empty
