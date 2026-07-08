from __future__ import annotations

import pandas as pd
import pytest

from model_artifacts_established_ceiling import add_ceiling_evidence_feature


def test_ceiling_interaction_is_smooth_and_origin_safe() -> None:
    rows = pd.DataFrame(
        [
            {"total_games": 0, "career_best": 80},
            {"total_games": 25, "career_best": 80},
            {"total_games": 50, "career_best": 80},
            {"total_games": 100, "career_best": 60},
        ]
    )
    out = add_ceiling_evidence_feature(rows)
    assert out.loc[0, "career_best_x_evidence"] == pytest.approx(0)
    assert out.loc[1, "career_best_x_evidence"] == pytest.approx(40)
    assert out.loc[2, "career_best_x_evidence"] == pytest.approx(80)
    assert out.loc[3, "career_best_x_evidence"] == pytest.approx(60)


def test_feature_builder_does_not_mutate_or_require_future_status() -> None:
    rows = pd.DataFrame(
        [{"total_games": 10, "career_best": None, "age": 20, "draft_type": "ND"}]
    )
    original = rows.copy(deep=True)
    out = add_ceiling_evidence_feature(rows)
    pd.testing.assert_frame_equal(rows, original)
    assert out.loc[0, "career_best_x_evidence"] == 0
    assert out.loc[0, "age"] == 20
    assert out.loc[0, "draft_type"] == "ND"
