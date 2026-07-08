import pandas as pd

import run_task044_replacement_board as task044


def test_parse_positions_maps_complete_eligibility():
    assert task044._parse_positions("G-DEF,K-DEF") == frozenset({"GDEF", "KDEF"})


def test_replacement_levels_use_best_unselected_legal_player(monkeypatch):
    monkeypatch.setattr(task044, "build_league_scoring_slots", lambda: ())
    frame = pd.DataFrame(
        [
            {"forecast_year": 2027, "cond_avg": 80.0, "eligibilities": "MID"},
            {"forecast_year": 2027, "cond_avg": 70.0, "eligibilities": "RUCK"},
        ]
    )

    try:
        task044._replacement_levels(frame)
    except ValueError as exc:
        assert "replacement" in str(exc)
    else:
        raise AssertionError("missing position replacements must fail")
