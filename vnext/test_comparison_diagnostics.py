import pandas as pd

from comparison_diagnostics import (
    fold_differences,
    metrics_by_origin_lead,
    player_block_bootstrap,
    row_losses,
)


def _predictions():
    rows = []
    for model_id in ("baseline_recent_scoring", "challenger"):
        for player_key, event, points in (("a", 1, 800.0), ("b", 0, 0.0)):
            rows.append(
                {
                    "model_id": model_id,
                    "player_key": player_key,
                    "origin_year": 2018,
                    "lead": 1,
                    "p_meaningful": 0.5,
                    "cond_games": 10.0,
                    "cond_avg": 80.0,
                    "exp_games": 5.0,
                    "exp_points": 400.0,
                    "p_avg_ge_80": 0.4,
                    "p_avg_ge_90": 0.3,
                    "p_avg_ge_100": 0.2,
                    "p_avg_ge_110": 0.1,
                    "p_avg_ge_120": 0.05,
                    "points_q10": 0.0,
                    "points_q25": 100.0,
                    "points_q50": 400.0,
                    "points_q75": 700.0,
                    "points_q90": 900.0,
                    "points_q97": 1100.0,
                }
            )
    return pd.DataFrame(rows)


def _targets():
    return pd.DataFrame(
        [
            {
                "player_key": "a",
                "origin_year": 2018,
                "lead": 1,
                "target_year": 2019,
                "games": 10,
                "avg": 80.0,
                "points": 800.0,
                "meaningful": 1,
                "avg_ge_80": 1,
                "avg_ge_90": 0,
                "avg_ge_100": 0,
                "avg_ge_110": 0,
                "avg_ge_120": 0,
            },
            {
                "player_key": "b",
                "origin_year": 2018,
                "lead": 1,
                "target_year": 2019,
                "games": 0,
                "avg": 0.0,
                "points": 0.0,
                "meaningful": 0,
                "avg_ge_80": 0,
                "avg_ge_90": 0,
                "avg_ge_100": 0,
                "avg_ge_110": 0,
                "avg_ge_120": 0,
            },
        ]
    )


def test_identical_challenger_has_zero_fold_and_bootstrap_differences():
    losses = row_losses(_predictions(), _targets())
    folds = metrics_by_origin_lead(losses)
    differences = fold_differences(folds)
    metric_columns = [
        column
        for column in differences.columns
        if column not in {"model_id", "origin_year", "lead"}
    ]
    assert (differences[metric_columns].fillna(0.0) == 0.0).all(axis=None)

    bootstrap = player_block_bootstrap(losses, repetitions=50, seed=7)
    assert len(bootstrap)
    assert (bootstrap["difference"].fillna(0.0) == 0.0).all()
    assert (bootstrap["ci_low"].fillna(0.0) == 0.0).all()
    assert (bootstrap["ci_high"].fillna(0.0) == 0.0).all()
