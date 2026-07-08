from __future__ import annotations

import pandas as pd

from compare_task009_zero_history import scores_from_metrics
from model_artifacts_zero_history import add_zero_history_features


def test_zero_history_state_separates_origin_safe_pathways_and_tenure() -> None:
    rows = pd.DataFrame(
        [
            {"total_games": 0, "tenure": 0, "draft_type": "ND", "pick": 5},
            {"total_games": 0, "tenure": 2, "draft_type": "RD", "pick": 45},
            {"total_games": 12, "tenure": 2, "draft_type": "RD", "pick": 45},
            {"total_games": 100, "tenure": 8, "draft_type": "ND", "pick": 1},
        ]
    )

    out = add_zero_history_features(rows)

    assert out.loc[0, "zero_history_flag"] == 1
    assert out.loc[1, "zero_history_flag"] == 1
    assert out.loc[0, "zero_history_state"] != out.loc[1, "zero_history_state"]
    assert out.loc[2, "zero_history_state"] == "played"
    assert out.loc[3, "zero_history_state"] == "played"
    assert out.loc[2, "zero_history_tenure"] == "played"
    assert out.loc[3, "zero_history_tenure"] == "played"


def test_feature_builder_does_not_mutate_input_or_require_current_status() -> None:
    rows = pd.DataFrame(
        [{"total_games": 0, "tenure": 1, "draft_type": "MSD", "pick": None}]
    )
    original = rows.copy(deep=True)

    out = add_zero_history_features(rows)

    pd.testing.assert_frame_equal(rows, original)
    assert out.loc[0, "zero_history_state"] == "zero|t1|supplemental|61+/undrafted"
    assert set(out.columns) == set(rows.columns) | {
        "zero_history_flag",
        "zero_history_tenure",
        "zero_history_state",
    }


def test_metrics_report_excludes_string_cohort_column() -> None:
    rows = []
    for cohort in ("all", "zero_history", "played_history"):
        rows.extend(
            [
                {
                    "cohort": cohort,
                    "model": "task003q",
                    "brier": 0.2,
                    "log_loss": 0.5,
                    "games_mae": 5.0,
                    "points_mae": 400.0,
                },
                {
                    "cohort": cohort,
                    "model": "task009",
                    "brier": 0.19,
                    "log_loss": 0.49,
                    "games_mae": 4.9,
                    "points_mae": 395.0,
                },
            ]
        )
    scores = scores_from_metrics(pd.DataFrame(rows))
    assert scores["zero_history"]["change_pct"]["brier"] < 0
    assert "cohort" not in scores["all"]["task003q"]
