from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark import LOCKED_FOLDS
from validate_task003k_candidate import legal_fold_table, score


def test_task003k_legal_fold_table_has_locked_25_cutoffs():
    table = legal_fold_table()
    assert len(table) == 25
    assert table.groupby("lead")["origin_year"].apply(list).to_dict() == LOCKED_FOLDS
    assert (table["training_target_max_year"] == table["origin_year"] - 1).all()


def test_task003k_score_reproduces_core_metrics_for_toy_data():
    pred = pd.DataFrame(
        {
            "player_key": ["a", "b", "c", "d"],
            "origin_year": [2020, 2020, 2020, 2020],
            "lead": [1, 1, 1, 1],
            "p_meaningful": [0.9, 0.8, 0.2, 0.1],
            "exp_games": [10.0, 8.0, 2.0, 1.0],
            "exp_points": [900.0, 640.0, 40.0, 10.0],
        }
    )
    targets = pd.DataFrame(
        {
            "player_key": ["a", "b", "c", "d"],
            "origin_year": [2020, 2020, 2020, 2020],
            "lead": [1, 1, 1, 1],
            "meaningful": [1, 1, 0, 0],
            "games": [11, 7, 0, 0],
            "points": [990, 560, 0, 0],
        }
    )
    by_lead, summary = score(pred, targets, "toy")
    assert by_lead.loc[0, "n"] == 4
    assert by_lead.loc[0, "auc_meaningful"] == 1.0
    assert summary.loc[0, "model_id"] == "toy"
