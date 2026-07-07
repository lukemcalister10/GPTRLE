from pathlib import Path
import hashlib

from active_universe import (
    VALID_ELIGIBILITIES,
    build_reconciliation,
    canonical_legacy_eligibility,
    load_authoritative,
    load_legacy_board,
    load_vnext_previous,
    stable_player_id,
    write_reports,
)
from snapshot import build_snapshot

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "data/current/Players_2026.csv"
LEGACY = ROOT / "data/rl_build/rl_app_data.json"
PREVIOUS = ROOT / "engine/rl_after/rl_model_data.json"


def reports():
    return build_reconciliation(load_authoritative(AUTH), load_legacy_board(LEGACY), load_vnext_previous(PREVIOUS))


def test_authoritative_rows_and_accounting():
    r = reports()
    assert len(r["authoritative_universe"]) == 804
    assert len(r["matched_players"]) == 804
    assert len(r["unmatched_authoritative_players"]) == 0
    assert len(r["ambiguous_matches"]) == 0


def test_stable_ids_are_unique_and_not_name_only():
    m = reports()["matched_players"]
    assert m.stable_player_id.notna().all()
    assert not (m.stable_player_id == "").any()
    assert m.stable_player_id.is_unique
    assert not (m.stable_player_id == m.player_name).any()
    assert not (m.stable_player_id == m.legacy_key).any()
    assert m.stable_player_id.str.startswith("afl-player-v1-").all()


def test_stable_id_ignores_display_name_changes():
    legacy = {"key": "same-key", "name": "Original Name", "yr": 2024, "ty": "ND", "pk": 7}
    historical = {"key": "same-key", "player": "Original Name", "_by": 2006, "_bd": "2006-01-02"}
    renamed_legacy = dict(legacy, name="Changed Name")
    renamed_historical = dict(historical, player="Changed Name")
    assert stable_player_id(legacy, historical) == stable_player_id(renamed_legacy, renamed_historical)


def test_same_display_name_with_different_identity_facts_gets_different_ids():
    player_a = {"key": "sam-player-a", "name": "Sam Player", "yr": 2024, "ty": "ND", "pk": 7}
    player_b = {"key": "sam-player-b", "name": "Sam Player", "yr": 2025, "ty": "RD", "pk": 8}
    hist_a = {"key": "sam-player-a", "_by": 2006, "_bd": "2006-01-02"}
    hist_b = {"key": "sam-player-b", "_by": 2007, "_bd": "2007-03-04"}
    assert stable_player_id(player_a, hist_a) != stable_player_id(player_b, hist_b)


def test_repeated_runs_produce_identical_stable_ids():
    first = reports()["matched_players"][["legacy_key", "stable_player_id"]].sort_values("legacy_key").reset_index(drop=True)
    second = reports()["matched_players"][["legacy_key", "stable_player_id"]].sort_values("legacy_key").reset_index(drop=True)
    assert first.equals(second)


def test_legacy_eligibility_code_normalisation():
    assert canonical_legacy_eligibility([["GEN_DEF", 1]]) == ("G-DEF",)
    assert canonical_legacy_eligibility([["GEN_FWD", 1]]) == ("G-FWD",)
    assert canonical_legacy_eligibility([["KEY_DEF", 1]]) == ("K-DEF",)
    assert canonical_legacy_eligibility([["KEY_FWD", 1]]) == ("K-FWD",)
    assert canonical_legacy_eligibility([["RUC", 1]]) == ("RUCK",)
    assert canonical_legacy_eligibility([["RUCK", 1]]) == ("RUCK",)
    assert canonical_legacy_eligibility([["MID", 1]]) == ("MID",)


def test_affl_ownership_comparison_is_not_against_afl_club():
    r = reports()
    assert "affl_ownership_comparison_unavailable" in r
    assert len(r["affl_ownership_comparison_unavailable"]) == 0
    assert "affl_team_disagreements" not in r
    assert "legacy_afl_club" in r["matched_players"].columns


def test_eligibilities_are_valid_and_multi_position_preserved():
    m = reports()["matched_players"]
    values = [v for cell in m.eligibilities for v in cell.split(",")]
    assert values
    assert set(values) <= VALID_ELIGIBILITIES
    assert all(cell for cell in m.eligibilities)
    assert (m.eligibilities.str.contains(",")).any()
    assert m.loc[m.player_name == "Matt Whitlock", "eligibilities"].item() == "G-DEF,G-FWD,K-DEF"


def test_zero_current_scoring_does_not_exclude_listed_player():
    omitted = reports()["players_wrongly_excluded_by_current_scoring_or_recent_play_logic"]
    assert len(omitted) == 53
    flynn = omitted.loc[omitted.player_name == "Flynn Riley"].iloc[0]
    assert flynn.match_status == "matched"
    assert "no_current_or_historical_scoring_games" in flynn.previous_vnext_exclusion_reason


def test_current_season_source_fields_do_not_affect_historical_snapshots():
    player = next(p for p in load_vnext_previous(PREVIOUS) if p["player"] == "Flynn Riley")
    baseline = build_snapshot(player, 2025)
    mutated = dict(player)
    mutated["_club"] = "Injected Club"
    mutated["present_position"] = "RUCK"
    mutated["future_position"] = "RUCK"
    mutated["_retired"] = True
    assert build_snapshot(mutated, 2025) == baseline


def test_report_export_hashes_are_deterministic(tmp_path):
    r = reports()
    out1 = tmp_path / "one"
    out2 = tmp_path / "two"
    h1 = write_reports(r, out1)
    h2 = write_reports(r, out2)
    assert h1 == h2
    assert hashlib.sha256((out1 / "authoritative_universe.csv").read_bytes()).hexdigest() == h1["authoritative_universe.csv"]


def test_taylor_adams_is_sole_legacy_only_difference():
    legacy_only = reports()["legacy_only_players"]
    assert len(legacy_only) == 1
    assert legacy_only.iloc[0].player_name == "Taylor Adams"
    assert legacy_only.iloc[0].legacy_key == "taylor-adams"
