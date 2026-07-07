#!/usr/bin/env python3
"""Apply reviewed DraftGuru identity decisions and emit full player-year evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

YEARS = tuple(range(2018, 2025))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def extract_players(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("players", "data", "active"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError("unrecognised historical player data structure")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eligibility", required=True)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--manual-decisions", required=True)
    ap.add_argument("--database", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    eligibility = read_csv(Path(args.eligibility))
    mapping = read_csv(Path(args.mapping))
    decisions = read_csv(Path(args.manual_decisions))
    raw_players = extract_players(json.loads(Path(args.database).read_text(encoding="utf-8")))

    database_names: dict[str, str] = {}
    for row in raw_players:
        key = str(row.get("key") or "").strip()
        if key and key not in database_names:
            database_names[key] = str(row.get("player") or key)
    database_keys = sorted(database_names)

    decision_by_slug = {row["draftguru_player_slug"]: row for row in decisions}
    if len(decision_by_slug) != len(decisions):
        raise ValueError("manual decision file contains duplicate DraftGuru slugs")

    final_map: list[dict[str, Any]] = []
    map_key_by_slug: dict[str, str] = {}
    excluded_slugs: set[str] = set()
    review_slugs: set[str] = set()

    for row in mapping:
        slug = row["draftguru_player_slug"]
        status = row["match_status"]
        method = row["match_method"]
        key = row["legacy_key"].strip()
        reason = ""
        if status == "matched":
            if not key:
                raise ValueError(f"automatic match missing key: {slug}")
            final_status = "matched"
            final_method = method
        else:
            review_slugs.add(slug)
            decision = decision_by_slug.get(slug)
            if decision is None:
                raise ValueError(f"review slug missing manual decision: {slug}")
            if decision["decision"] == "match":
                key = decision["legacy_key"].strip()
                final_status = "matched"
                final_method = decision["reason"]
                reason = decision.get("reviewer_notes", "")
            elif decision["decision"] == "exclude":
                key = ""
                final_status = "excluded"
                final_method = decision["reason"]
                reason = decision.get("reviewer_notes", "")
                excluded_slugs.add(slug)
            else:
                raise ValueError(f"invalid manual decision for {slug}: {decision['decision']}")

        if key:
            if key not in database_names:
                raise ValueError(f"mapped key is absent from database: {slug} -> {key}")
            map_key_by_slug[slug] = key

        final_map.append(
            {
                "draftguru_player_slug": slug,
                "draftguru_player_url": row["draftguru_player_url"],
                "draftguru_name": row["draftguru_name"],
                "dob_iso": row["dob_iso"],
                "draft_year": row["draft_year"],
                "draft_pick": row["draft_pick"],
                "listed_seasons": row["listed_seasons"],
                "clubs": row["clubs"],
                "final_status": final_status,
                "final_match_method": final_method,
                "legacy_key": key,
                "database_name": database_names.get(key, ""),
                "reviewer_notes": reason,
            }
        )

    if set(decision_by_slug) != review_slugs:
        extras = sorted(set(decision_by_slug) - review_slugs)
        missing = sorted(review_slugs - set(decision_by_slug))
        raise ValueError(f"manual decision coverage mismatch extras={extras[:5]} missing={missing[:5]}")

    positive: dict[tuple[str, int], dict[str, Any]] = {}
    excluded_rows: list[dict[str, Any]] = []
    for row in eligibility:
        slug = row["draftguru_player_slug"]
        key = map_key_by_slug.get(slug, "")
        year = int(row["season"])
        if key:
            pair = (key, year)
            if pair in positive:
                raise ValueError(f"duplicate listed evidence for repository key/year: {pair}")
            positive[pair] = row
        else:
            excluded_rows.append(
                {
                    "season": year,
                    "draftguru_player_slug": slug,
                    "player_name": row["player_name"],
                    "club": row["club"],
                    "source_url": row["source_url"],
                    "reason": "reviewed_no_repository_identity",
                }
            )

    matrix: list[dict[str, Any]] = []
    for key in database_keys:
        for year in YEARS:
            evidence = positive.get((key, year))
            if evidence:
                matrix.append(
                    {
                        "player_key": key,
                        "database_name": database_names[key],
                        "origin_year": year,
                        "eligible": True,
                        "decision_method": "draftguru_verified_presence",
                        "club": evidence["club"],
                        "draftguru_player_slug": evidence["draftguru_player_slug"],
                        "draftguru_name": evidence["player_name"],
                        "source_url": evidence["source_url"],
                    }
                )
            else:
                matrix.append(
                    {
                        "player_key": key,
                        "database_name": database_names[key],
                        "origin_year": year,
                        "eligible": False,
                        "decision_method": "draftguru_verified_absence",
                        "club": "",
                        "draftguru_player_slug": "",
                        "draftguru_name": "",
                        "source_url": f"https://www.draftguru.com.au/lists/{year}",
                    }
                )

    expected_rows = len(database_keys) * len(YEARS)
    if len(matrix) != expected_rows:
        raise AssertionError((len(matrix), expected_rows))
    if len({(row["player_key"], row["origin_year"]) for row in matrix}) != expected_rows:
        raise AssertionError("player-year matrix contains duplicate keys")

    out = Path(args.out)
    final_map_path = out / "draftguru_player_key_map_final.csv"
    matrix_path = out / "historical_eligibility_2018_2024.csv"
    excluded_path = out / "draftguru_players_excluded_from_repository_mapping.csv"
    database_path = out / "database_player_keys.csv"

    write_csv(
        final_map_path,
        sorted(final_map, key=lambda row: row["draftguru_name"]),
        [
            "draftguru_player_slug", "draftguru_player_url", "draftguru_name", "dob_iso",
            "draft_year", "draft_pick", "listed_seasons", "clubs", "final_status",
            "final_match_method", "legacy_key", "database_name", "reviewer_notes",
        ],
    )
    write_csv(
        matrix_path,
        matrix,
        [
            "player_key", "database_name", "origin_year", "eligible", "decision_method",
            "club", "draftguru_player_slug", "draftguru_name", "source_url",
        ],
    )
    write_csv(
        excluded_path,
        sorted(excluded_rows, key=lambda row: (row["season"], row["player_name"])),
        ["season", "draftguru_player_slug", "player_name", "club", "source_url", "reason"],
    )
    write_csv(
        database_path,
        [{"player_key": key, "database_name": database_names[key]} for key in database_keys],
        ["player_key", "database_name"],
    )

    summary = {
        "years": list(YEARS),
        "database_unique_keys": len(database_keys),
        "draftguru_unique_people": len(final_map),
        "matched_draftguru_people": sum(row["final_status"] == "matched" for row in final_map),
        "excluded_draftguru_people": sum(row["final_status"] == "excluded" for row in final_map),
        "manual_matches": sum(row["final_match_method"] in {"user_confirmed_match", "manual_identity_resolution"} for row in final_map),
        "manual_exclusions": len(excluded_slugs),
        "verified_present_player_years": len(positive),
        "verified_absent_player_years": expected_rows - len(positive),
        "matrix_rows": len(matrix),
        "match_methods": dict(sorted(Counter(row["final_match_method"] for row in final_map).items())),
    }
    summary_path = out / "finalization_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {
        "source": "DraftGuru annual AFL club-list pages",
        "years": list(YEARS),
        "eligibility_semantics": "presence on any of the 18 annual club lists is eligible; absence is ineligible",
        "files": {},
    }
    for path in [final_map_path, matrix_path, excluded_path, database_path, summary_path]:
        manifest["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    manifest_path = out / "final_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
