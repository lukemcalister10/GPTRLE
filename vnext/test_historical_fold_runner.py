from pathlib import Path

import pandas as pd
import pytest

from benchmark import (
    LOCKED_FOLDS,
    PREDICTION_KEY,
    QUANTILE_COLUMNS,
    REQUIRED_PREDICTION_COLUMNS,
    normalise_predictions,
)
from build_annual_dataset import build_rows
from build_historical_cohorts import (
    align_entries_to_verified_history,
    canonical_players,
)
from historical_eligibility import DraftGuruEligibilityResolver, load_historical_players
from run_historical_folds import MODEL_ID, add_residual_quantiles, train_artifacts


def tiny_dataset():
    rows = []
    for origin in range(2008, 2018):
        for i in range(18):
            row = {
                "key": f"p{i}",
                "player": f"P{i}",
                "origin_year": origin,
                "position": "MID",
                "draft_type": "ND",
                "pick": i + 1,
                "tenure": origin - 2007,
                "age": 20 + i % 5,
                "total_games": 20 + i,
                "qualifying_seasons": 1,
                "last_avg": 60 + i,
                "last_games": 10,
                "prev_avg": 55 + i,
                "prev_games": 8,
                "weighted_avg": 58 + i,
                "career_best": 70 + i,
                "recent_best": 65 + i,
                "avg_trend": 1.0,
                "games_last_2": 18,
                "seasons_observed": 2,
            }
            for lead in range(1, 6):
                games = 0 if i % 7 == 0 else 8 + (i + lead) % 10
                average = 55 + i + lead
                meaningful = int(games >= 6)
                row[f"l{lead}_games"] = games
                row[f"l{lead}_avg"] = average if meaningful else 0.0
                row[f"l{lead}_points"] = games * average
                row[f"l{lead}_meaningful"] = meaningful
                for threshold in (80, 90, 100, 110, 120):
                    row[f"l{lead}_{threshold}"] = int(average >= threshold)
            rows.append(row)
    return pd.DataFrame(rows)


def base_pred(probability=0.7, n=2):
    return pd.DataFrame(
        {
            "p_meaningful": [probability] * n,
            "cond_games": [12.0] * n,
            "cond_avg": [80.0] * n,
            "exp_games": [probability * 12.0] * n,
            "exp_avg": [probability * 80.0] * n,
            "exp_points": [probability * 12.0 * 80.0] * n,
            "p80": [0.4] * n,
            "p90": [0.3] * n,
            "p100": [0.2] * n,
            "p110": [0.1] * n,
            "p120": [0.05] * n,
        }
    )


def test_every_locked_origin_and_lead_present():
    assert {
        (lead, origin)
        for lead, origins in LOCKED_FOLDS.items()
        for origin in origins
    }
    assert sum(len(origins) for origins in LOCKED_FOLDS.values()) == 25


def test_strict_historical_training_cutoff(tmp_path: Path):
    artifacts, _, counts = train_artifacts(tiny_dataset(), tmp_path)
    for _, row in counts.iterrows():
        assert row.train_max_origin + row.lead < row.origin_year
        assert row.training_target_max_year < row.origin_year
    assert set(artifacts) == {
        (lead, origin)
        for lead, origins in LOCKED_FOLDS.items()
        for origin in origins
    }


def test_no_current_or_future_fields_needed_for_prediction_quantiles():
    class Artifact:
        games_resid_sd = 2.0
        avg_resid_sd = 5.0

    rows = pd.DataFrame(
        {
            "player_key": ["a", "b"],
            "origin_year": [2018, 2018],
            "lead": [1, 1],
            "current_club": ["X", "Y"],
            "future_position": ["RUC", "MID"],
        }
    )
    with_future = add_residual_quantiles(base_pred(n=2), Artifact(), rows)
    without_future = add_residual_quantiles(
        base_pred(n=2),
        Artifact(),
        rows.drop(columns=["current_club", "future_position"]),
    )
    pd.testing.assert_frame_equal(with_future, without_future)


def test_quantiles_are_exact_mixture_non_crossing_and_deterministic():
    class Artifact:
        games_resid_sd = 3.0
        avg_resid_sd = 12.0

    rows = pd.DataFrame(
        {"player_key": ["a"], "origin_year": [2018], "lead": [1]}
    )
    first = add_residual_quantiles(base_pred(n=1), Artifact(), rows)
    second = add_residual_quantiles(base_pred(n=1), Artifact(), rows)
    pd.testing.assert_frame_equal(first, second)
    quantiles = first[list(QUANTILE_COLUMNS)]
    assert (quantiles.diff(axis=1).iloc[:, 1:] >= -1e-12).all().all()
    assert quantiles.nunique(axis=1).iloc[0] > 1


def test_low_probability_zero_quantiles_follow_exact_zero_mass():
    class Artifact:
        games_resid_sd = 3.0
        avg_resid_sd = 12.0

    rows = pd.DataFrame(
        {"player_key": ["a"], "origin_year": [2018], "lead": [1]}
    )
    result = add_residual_quantiles(base_pred(probability=0.02, n=1), Artifact(), rows)
    assert (result[list(QUANTILE_COLUMNS)] == 0.0).all(axis=None)


def test_training_history_applies_audited_entry_correction():
    resolver = DraftGuruEligibilityResolver()
    players = canonical_players(load_historical_players())
    aligned, corrections = align_entries_to_verified_history(
        players,
        resolver.evidence_frame(),
    )
    assert corrections["player_key"].tolist() == ["hugo-hall-kahan"]
    dataset = build_rows(aligned, min_origin=2008, max_origin=2024)
    assert not dataset.duplicated(["key", "origin_year"]).any()
    hugo_origins = dataset.loc[
        dataset["key"] == "hugo-hall-kahan",
        "origin_year",
    ].tolist()
    assert hugo_origins == [2022, 2023, 2024]


def test_schema_validation_and_malformed_output_failures():
    row = {
        "player_key": "p1",
        "origin_year": 2018,
        "lead": 1,
        "p_meaningful": 0.5,
        "cond_games": 10,
        "cond_avg": 80,
        "exp_games": 5,
        "exp_points": 400,
        "p_avg_ge_80": 0.4,
        "p_avg_ge_90": 0.3,
        "p_avg_ge_100": 0.2,
        "p_avg_ge_110": 0.1,
        "p_avg_ge_120": 0.05,
    }
    for column in QUANTILE_COLUMNS:
        row[column] = 400.0
    valid = normalise_predictions(MODEL_ID, pd.DataFrame([row]))
    assert list(valid.columns) == ["model_id", *REQUIRED_PREDICTION_COLUMNS]
    malformed = pd.DataFrame([row]).drop(columns=[QUANTILE_COLUMNS[-1]])
    with pytest.raises(ValueError, match="missing columns"):
        normalise_predictions(MODEL_ID, malformed)


def test_exact_locked_key_coverage_fixture():
    targets = pd.DataFrame(
        {
            "player_key": ["a", "b"],
            "origin_year": [2018, 2018],
            "lead": [1, 1],
        }
    )
    predictions = targets.copy()
    for column in [
        column
        for column in REQUIRED_PREDICTION_COLUMNS
        if column not in PREDICTION_KEY
    ]:
        predictions[column] = 0.1 if column.startswith("p_") else 1.0
    predictions["p_avg_ge_90"] = 0.09
    predictions["p_avg_ge_100"] = 0.08
    predictions["p_avg_ge_110"] = 0.07
    predictions["p_avg_ge_120"] = 0.06
    normalised = normalise_predictions(MODEL_ID, predictions)
    assert normalised[PREDICTION_KEY].equals(targets[PREDICTION_KEY])
