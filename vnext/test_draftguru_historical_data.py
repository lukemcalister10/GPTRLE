import base64
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "historical"
CSV_FILES = (
    "historical_eligibility_2018_2024.csv",
    "draftguru_player_key_map_final.csv",
    "draftguru_players_excluded_from_repository_mapping.csv",
    "database_player_keys.csv",
)


def decode(name):
    encoded = "".join((DATA / f"{name}.gz.b64").read_text(encoding="ascii").split())
    return gzip.decompress(base64.b64decode(encoded, validate=True))


def rows(name):
    text = decode(name).decode("utf-8").splitlines()
    return list(csv.DictReader(text))


def test_committed_sources_match_manifest():
    manifest = json.loads((DATA / "final_manifest.json").read_text(encoding="utf-8"))
    for name in CSV_FILES:
        raw = decode(name)
        assert len(raw) == manifest["files"][name]["bytes"]
        assert hashlib.sha256(raw).hexdigest() == manifest["files"][name]["sha256"]


def test_summary_and_matrix_accounting():
    summary = json.loads((DATA / "finalization_summary.json").read_text(encoding="utf-8"))
    matrix = rows("historical_eligibility_2018_2024.csv")

    assert summary["years"] == list(range(2018, 2025))
    assert summary["database_unique_keys"] == 2652
    assert summary["draftguru_unique_people"] == 1465
    assert summary["matched_draftguru_people"] == 1440
    assert summary["excluded_draftguru_people"] == 25
    assert summary["verified_present_player_years"] == 5622
    assert summary["verified_absent_player_years"] == 12942
    assert summary["matrix_rows"] == 18564

    assert len(matrix) == 18564
    pairs = {(row["player_key"], int(row["origin_year"])) for row in matrix}
    assert len(pairs) == len(matrix)
    assert {int(row["origin_year"]) for row in matrix} == set(range(2018, 2025))
    assert sum(row["eligible"] == "True" for row in matrix) == 5622
    assert sum(row["eligible"] == "False" for row in matrix) == 12942


def test_every_repository_key_has_all_seven_origins():
    origins_by_key = {}
    for row in rows("historical_eligibility_2018_2024.csv"):
        origins_by_key.setdefault(row["player_key"], set()).add(int(row["origin_year"]))
    assert len(origins_by_key) == 2652
    assert all(origins == set(range(2018, 2025)) for origins in origins_by_key.values())


def test_reviewed_identity_decisions_are_preserved():
    key_map = {row["draftguru_player_slug"]: row for row in rows("draftguru_player_key_map_final.csv")}
    expected = {
        "will_hayes/1": "will-hayes-a",
        "bailey_williams/1": "bailey-williams-wb",
        "bailey_williams/2": "bailey-williams-wc",
        "callum_brown/1": "callum-brown",
        "callum_brown/2": "callum-brown-ire",
        "josh_kennedy/1": "joshua-kennedy",
        "josh_kennedy/2": "josh-p-kennedy",
        "sam_reid/2": "samuel-reid",
        "sam_reid/3": "sam-reid-syd",
    }
    assert {slug: key_map[slug]["legacy_key"] for slug in expected} == expected
    assert len({key_map[slug]["legacy_key"] for slug in expected}) == len(expected)
    assert key_map["will_hayes/1"]["final_match_method"] == "manual_identity_resolution"


def test_intentional_exclusions_remain_unmatched():
    key_map = rows("draftguru_player_key_map_final.csv")
    excluded_people = [row for row in key_map if row["final_status"] == "excluded"]
    excluded_seasons = rows("draftguru_players_excluded_from_repository_mapping.csv")

    assert len(excluded_people) == 25
    assert all(not row["legacy_key"] for row in excluded_people)
    assert len(excluded_seasons) == 76
    assert {row["draftguru_player_slug"] for row in excluded_seasons} == {
        row["draftguru_player_slug"] for row in excluded_people
    }


def test_decoding_is_deterministic():
    first = {name: decode(name) for name in CSV_FILES}
    second = {name: decode(name) for name in CSV_FILES}
    assert first == second
