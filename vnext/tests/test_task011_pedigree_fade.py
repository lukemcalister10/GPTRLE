from __future__ import annotations

import pandas as pd
import pytest

from model_artifacts_pedigree_fade import fade_pedigree_features


def test_pedigree_is_unchanged_at_zero_and_neutral_at_fifty_games() -> None:
    rows = pd.DataFrame(
        [
            {"total_games": 0, "pick": 5, "draft_type": "ND"},
            {"total_games": 25, "pick": 20, "draft_type": "RD"},
            {"total_games": 50, "pick": 1, "draft_type": "ND"},
            {"total_games": 150, "pick": 40, "draft_type": "RD"},
        ]
    )
    out = fade_pedigree_features(rows)
    assert out.loc[0, "pick"] == pytest.approx(5)
    assert out.loc[0, "draft_type"] == "ND"
    assert out.loc[1, "pick"] == pytest.approx(50)
    assert out.loc[1, "draft_type"] == "RD"
    assert out.loc[2, "pick"] == pytest.approx(80)
    assert out.loc[2, "draft_type"] == "ESTABLISHED"
    assert out.loc[3, "pick"] == pytest.approx(80)
    assert out.loc[3, "draft_type"] == "ESTABLISHED"


def test_transform_is_origin_safe_and_does_not_mutate_input() -> None:
    rows = pd.DataFrame(
        [{"total_games": 10, "pick": None, "draft_type": None, "age": 20}]
    )
    original = rows.copy(deep=True)
    out = fade_pedigree_features(rows)
    pd.testing.assert_frame_equal(rows, original)
    assert out.loc[0, "pick"] == pytest.approx(80)
    assert out.loc[0, "age"] == 20
