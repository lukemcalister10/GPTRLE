from datetime import date
from pathlib import Path

from authoritative_eligibility import load_current_eligibility
from league_config import AUTHORITATIVE_LINEUP, build_authoritative_slots


def test_authoritative_lineup_counts():
    cfg = AUTHORITATIVE_LINEUP
    assert cfg.teams == 16
    assert cfg.active_slots == 18
    assert cfg.listed_lineup_slots == 23
    assert cfg.in_season_roster_size == 42
    assert cfg.offseason_roster_size == 37


def test_slot_mix_matches_league_rules():
    slots = build_authoritative_slots()
    counts = {}
    for slot in slots:
        prefix = slot.slot_id.split("-")[0]
        counts[prefix] = counts.get(prefix, 0) + 1

    assert counts == {
        "GDEF": 4,
        "KDEF": 2,
        "MID": 5,
        "RUC": 1,
        "GFWD": 4,
        "KFWD": 2,
        "BENCH": 5,
    }


def test_bench_accepts_every_position_and_defaults_to_zero_scoring_weight():
    bench = [slot for slot in build_authoritative_slots() if slot.slot_id.startswith("BENCH-")]
    assert len(bench) == 5
    assert all(slot.utility_multiplier == 0.0 for slot in bench)
    assert all(
        slot.accepted_positions == frozenset({"GDEF", "KDEF", "MID", "RUC", "GFWD", "KFWD"})
        for slot in bench
    )


def test_authoritative_csv_preserves_multi_position_sets():
    path = Path(__file__).resolve().parents[2] / "data" / "current" / "Players_2026.csv"
    records = load_current_eligibility(path, effective_date=date(2026, 7, 8))

    assert len(records) == 804
    assert any(len(record.positions) > 1 for record in records)
    assert all(record.positions for record in records)
