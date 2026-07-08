from __future__ import annotations

import pandas as pd

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
