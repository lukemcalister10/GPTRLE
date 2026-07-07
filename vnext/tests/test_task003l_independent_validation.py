from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark import LOCKED_FOLDS
from validate_task003l_independent import legal_fold_table, score, validate_predictions, Check


def test_task003l_legal_fold_table_has_locked_25_cutoffs():
    table = legal_fold_table()
    assert len(table) == 25
    assert table.groupby("lead")["origin_year"].apply(list).to_dict() == LOCKED_FOLDS
    assert (table["training_target_max_year"] == table["origin_year"] - 1).all()


def test_task003l_score_reproduces_raw_and_calibrated_metrics_for_toy_data():
    pred = pd.DataFrame({"player_key": ["a", "b", "c", "d"], "origin_year": [2020]*4, "lead": [1]*4, "p_meaningful": [0.9,0.8,0.2,0.1], "exp_games": [10,8,2,1], "exp_points": [900,640,40,10]})
    targets = pd.DataFrame({"player_key": ["a", "b", "c", "d"], "origin_year": [2020]*4, "lead": [1]*4, "meaningful": [1,1,0,0], "games": [11,7,0,0], "points": [990,560,0,0]})
    by_fold, by_lead = score(pred, targets, "toy", pd.Series([0.6, 0.6, 0.4, 0.4]))
    assert by_fold.loc[0, "n"] == 4
    assert by_fold.loc[0, "auc_meaningful"] == 1.0
    assert by_fold.loc[0, "raw_brier_meaningful"] != by_fold.loc[0, "calibrated_brier_meaningful"]
    assert by_lead.loc[0, "model_id"] == "toy"


def test_task003l_prediction_validation_fails_duplicate_keys(tmp_path):
    path = tmp_path / "pred.csv"
    base = {"player_key": "a", "origin_year": 2020, "lead": 1, "p_meaningful": .5, "cond_games": 1, "cond_avg": 50, "exp_games": .5, "exp_points": 25}
    for threshold in [80,90,100,110,120]: base[f"p_avg_ge_{threshold}"] = .1
    for q in [10,25,50,75,90,97]: base[f"points_q{q:02d}"] = 0
    pd.DataFrame([base, base]).to_csv(path, index=False)
    targets = pd.DataFrame([{"player_key":"a", "origin_year":2020, "lead":1}])
    checks: list[Check] = []
    validate_predictions(checks, "x", path, targets)
    assert any(c.name == "x duplicate prediction keys" and c.status == "fail" for c in checks)
