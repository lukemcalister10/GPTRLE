import pandas as pd
import pytest

import run_task041_combined_export as task041


def _frame(players=2):
    rows = []
    for index in range(players):
        for year in task041.FORECAST_YEARS:
            rows.append({
                "stable_player_id": f"player-{index}",
                "player_name": f"Player {index}",
                "affl_team": "Free Agents",
                "eligibilities": "MID" if index == 0 else "G-DEF,K-DEF",
                "forecast_year": year,
                "exp_points": 100.0,
                "p_meaningful": 0.5,
                "cond_games": 10.0,
                "cond_avg": 20.0,
            })
    return pd.DataFrame(rows)


def test_position_parser_preserves_complete_current_eligibility():
    assert task041._parse_positions("G-DEF,K-DEF") == frozenset({"GDEF", "KDEF"})
    assert task041._parse_positions("RUCK,G-FWD,K-FWD") == frozenset(
        {"RUC", "GFWD", "KFWD"}
    )


def test_loader_requires_complete_horizon_and_constant_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(task041, "EXPECTED_PLAYERS", 2)
    path = tmp_path / "annual.csv"
    _frame().to_csv(path, index=False)

    frame, metadata = task041._load(path)

    assert len(frame) == 10
    assert len(metadata) == 2
    assert "uncertainty_proxy" in frame


def test_loader_rejects_missing_annual_row(tmp_path, monkeypatch):
    monkeypatch.setattr(task041, "EXPECTED_PLAYERS", 2)
    path = tmp_path / "annual.csv"
    _frame().iloc[:-1].to_csv(path, index=False)

    with pytest.raises(ValueError, match="annual rows"):
        task041._load(path)


def test_loader_rejects_conflicting_player_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(task041, "EXPECTED_PLAYERS", 2)
    frame = _frame()
    frame.loc[frame.index[-1], "affl_team"] = "Adelaide"
    path = tmp_path / "annual.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(ValueError, match="metadata"):
        task041._load(path)


def test_intrinsic_values_are_positive_and_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(task041, "EXPECTED_PLAYERS", 2)
    path = tmp_path / "annual.csv"
    _frame().to_csv(path, index=False)
    frame, _ = task041._load(path)

    comparisons = task041._intrinsic_values(frame)

    assert len(comparisons) == 2
    assert all(row.contender_value > 0 for row in comparisons)
    assert all(row.balanced_value > 0 for row in comparisons)
    assert all(row.rebuilder_value > 0 for row in comparisons)
