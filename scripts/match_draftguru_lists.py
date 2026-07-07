#!/usr/bin/env python3
"""Match scraped DraftGuru people to the repository's historical player keys.

Automatic matching is deliberately conservative. Uncertain cases are retained in
an explicit review file with ranked suggestions; they are never silently accepted.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from dateutil import parser as date_parser
from rapidfuzz import fuzz, process


def clean(value: Any) -> str:
    return " ".join(str(value or "").replace("\xa0", " ").split())


def norm_name(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def to_int(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_dg_dob(value: str) -> date | None:
    value = clean(value)
    match = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{2})", value)
    if not match:
        return None
    day, month_text, year_text = match.groups()
    month = datetime.strptime(month_text.title(), "%b").month
    yy = int(year_text)
    year = 2000 + yy if yy <= 10 else 1900 + yy
    try:
        return date(year, month, int(day))
    except ValueError:
        return None


def parse_db_dob(value: Any, birth_year: Any = None) -> date | None:
    text = clean(value)
    if text:
        for dayfirst in (False, True):
            try:
                parsed = date_parser.parse(text, dayfirst=dayfirst, fuzzy=False).date()
                if 1940 <= parsed.year <= 2010:
                    return parsed
            except (ValueError, TypeError, OverflowError):
                pass
    return None


def parse_draft_text(value: str) -> dict[str, Any]:
    text = clean(value)
    pick_match = re.search(r"#(\d+)", text)
    year_match = re.search(r"(19|20)\d{2}", text)
    type_match = re.search(
        r"National|Rookie|Pre-Season|Mid-Season|International|Zone|SSP|Prelist|"
        r"Supplemental|Unregistered|Priority|Mini-Draft|Scholarship",
        text,
        re.IGNORECASE,
    )
    return {
        "draft_pick": int(pick_match.group(1)) if pick_match else None,
        "draft_year": int(year_match.group(0)) if year_match else None,
        "draft_type_text": type_match.group(0).title() if type_match else "",
    }


def choose(values: list[str]) -> str:
    nonblank = [clean(value) for value in values if clean(value)]
    return Counter(nonblank).most_common(1)[0][0] if nonblank else ""


def load_draftguru_people(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["draftguru_player_slug"]].append(row)

    people = []
    for slug, group in sorted(grouped.items()):
        draft_text = choose([row.get("draft_text", "") for row in group])
        parsed_draft = parse_draft_text(draft_text)
        dob_text = choose([row.get("dob_text", "") for row in group])
        dob = parse_dg_dob(dob_text)
        names = [row.get("player_name", "") for row in group]
        player_name = choose(names)
        people.append(
            {
                "draftguru_player_slug": slug,
                "draftguru_player_url": choose([row.get("draftguru_player_url", "") for row in group]),
                "draftguru_name": player_name,
                "draftguru_name_norm": norm_name(player_name),
                "draftguru_name_aliases": "|".join(sorted(set(clean(name) for name in names if clean(name)))),
                "dob_text": dob_text,
                "dob_iso": dob.isoformat() if dob else "",
                "birth_year": dob.year if dob else None,
                "draft_text": draft_text,
                **parsed_draft,
                "first_list_season": min(int(row["season"]) for row in group),
                "last_list_season": max(int(row["season"]) for row in group),
                "listed_seasons": "|".join(str(year) for year in sorted({int(row["season"]) for row in group})),
                "clubs": "|".join(sorted({row["club"] for row in group})),
            }
        )
    return people, rows


def extract_player_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("players", "data", "active"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError("historical player data does not contain a recognised player list")


def load_database_people(path: Path) -> list[dict[str, Any]]:
    raw = extract_player_list(json.loads(path.read_text(encoding="utf-8")))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in raw:
        key = clean(row.get("key"))
        if key:
            grouped[key].append(row)

    people = []
    for key, group in sorted(grouped.items()):
        richest = max(
            group,
            key=lambda row: (
                len(row.get("scoring") or []),
                bool(row.get("_bd")),
                bool(row.get("pick")),
                -int(row.get("year") or 9999),
            ),
        )
        aliases = sorted({clean(row.get("player")) for row in group if clean(row.get("player"))})
        name = clean(richest.get("player")) or (aliases[0] if aliases else key)
        birth_year = to_int(richest.get("_by"))
        dob = parse_db_dob(richest.get("_bd"), birth_year)
        people.append(
            {
                "legacy_key": key,
                "database_name": name,
                "database_name_norm": norm_name(name),
                "database_name_aliases": "|".join(aliases),
                "dob_iso": dob.isoformat() if dob else "",
                "birth_year": dob.year if dob else birth_year,
                "draft_year": to_int(richest.get("year")),
                "draft_pick": to_int(richest.get("pick")),
                "draft_type": clean(richest.get("type") or richest.get("_draft")),
                "source_record_count": len(group),
            }
        )
    return people


def evidence(dg: dict[str, Any], db: dict[str, Any]) -> dict[str, Any]:
    name_score = float(fuzz.ratio(dg["draftguru_name_norm"], db["database_name_norm"]))
    dob_exact = bool(dg["dob_iso"] and db["dob_iso"] and dg["dob_iso"] == db["dob_iso"])
    birth_year_exact = bool(dg["birth_year"] and db["birth_year"] and dg["birth_year"] == db["birth_year"])
    draft_year_exact = bool(dg["draft_year"] and db["draft_year"] and dg["draft_year"] == db["draft_year"])
    draft_pick_exact = bool(dg["draft_pick"] and db["draft_pick"] and dg["draft_pick"] == db["draft_pick"])
    support = 0
    support += 50 if dob_exact else 15 if birth_year_exact else 0
    support += 20 if draft_year_exact else 0
    support += 20 if draft_pick_exact else 0
    return {
        "name_score": round(name_score, 2),
        "dob_exact": dob_exact,
        "birth_year_exact": birth_year_exact,
        "draft_year_exact": draft_year_exact,
        "draft_pick_exact": draft_pick_exact,
        "support_score": support,
    }


def rank_candidates(dg: dict[str, Any], database: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    names = {row["legacy_key"]: row["database_name_norm"] for row in database}
    by_key = {row["legacy_key"]: row for row in database}
    fuzzy = process.extract(dg["draftguru_name_norm"], names, scorer=fuzz.ratio, limit=min(25, len(names)))
    candidate_keys = {match[2] for match in fuzzy}

    # Add all candidates supported by DOB/birth year or exact draft evidence, even if the name differs materially.
    for row in database:
        if dg["dob_iso"] and row["dob_iso"] == dg["dob_iso"]:
            candidate_keys.add(row["legacy_key"])
        elif dg["birth_year"] and row["birth_year"] == dg["birth_year"] and dg["draft_year"] and row["draft_year"] == dg["draft_year"]:
            candidate_keys.add(row["legacy_key"])
        elif dg["draft_year"] and dg["draft_pick"] and row["draft_year"] == dg["draft_year"] and row["draft_pick"] == dg["draft_pick"]:
            candidate_keys.add(row["legacy_key"])

    ranked = []
    for key in candidate_keys:
        row = by_key[key]
        ev = evidence(dg, row)
        # Name remains primary; independent identity evidence can promote nickname/short-name cases.
        rank_score = ev["name_score"] + ev["support_score"]
        ranked.append({**row, **ev, "rank_score": round(rank_score, 2)})
    ranked.sort(key=lambda row: (-row["rank_score"], -row["name_score"], row["legacy_key"]))
    return ranked[:limit]


def decide_match(dg: dict[str, Any], database: list[dict[str, Any]], exact_index: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any] | None, str, str, list[dict[str, Any]]]:
    exact = exact_index.get(dg["draftguru_name_norm"], [])
    ranked = rank_candidates(dg, database, limit=5)

    if len(exact) == 1:
        return exact[0], "matched", "exact_normalised_name", ranked

    if len(exact) > 1:
        exact_ranked = sorted(
            ({**row, **evidence(dg, row)} for row in exact),
            key=lambda row: (-(row["support_score"]), row["legacy_key"]),
        )
        if exact_ranked[0]["support_score"] > exact_ranked[1]["support_score"] and exact_ranked[0]["support_score"] >= 20:
            return exact_ranked[0], "matched", "exact_name_disambiguated_by_identity", ranked
        return None, "review", "duplicate_exact_name", ranked

    if ranked:
        top = ranked[0]
        second_score = ranked[1]["rank_score"] if len(ranked) > 1 else -999.0
        margin = top["rank_score"] - second_score
        strong_identity = top["dob_exact"] or (top["draft_year_exact"] and top["draft_pick_exact"])
        if top["name_score"] >= 88 and strong_identity and margin >= 5:
            return top, "matched", "supported_fuzzy_name", ranked
        if top["name_score"] >= 96 and top["birth_year_exact"] and margin >= 8:
            return top, "matched", "high_name_birth_year", ranked
    return None, "review", "no_conservative_automatic_match", ranked


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draftguru", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    people, eligibility_rows = load_draftguru_people(Path(args.draftguru))
    database = load_database_people(Path(args.database))
    exact_index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in database:
        exact_index[row["database_name_norm"]].append(row)

    mapping_rows = []
    review_rows = []
    selected_by_slug: dict[str, str] = {}
    for dg in people:
        selected, status, method, ranked = decide_match(dg, database, exact_index)
        top = ranked[0] if ranked else {}
        mapping = {
            **dg,
            "match_status": status,
            "match_method": method,
            "legacy_key": selected["legacy_key"] if selected else "",
            "database_name": selected["database_name"] if selected else "",
            "name_score": evidence(dg, selected)["name_score"] if selected else top.get("name_score", ""),
            "support_score": evidence(dg, selected)["support_score"] if selected else top.get("support_score", ""),
            "suggestions_json": json.dumps(
                [
                    {
                        "legacy_key": row["legacy_key"],
                        "database_name": row["database_name"],
                        "name_score": row["name_score"],
                        "support_score": row["support_score"],
                        "dob_exact": row["dob_exact"],
                        "draft_year_exact": row["draft_year_exact"],
                        "draft_pick_exact": row["draft_pick_exact"],
                    }
                    for row in ranked
                ],
                separators=(",", ":"),
            ),
        }
        mapping_rows.append(mapping)
        if selected:
            selected_by_slug[dg["draftguru_player_slug"]] = selected["legacy_key"]
        else:
            review = {**mapping}
            for i, suggestion in enumerate(ranked, start=1):
                review[f"suggestion_{i}_key"] = suggestion["legacy_key"]
                review[f"suggestion_{i}_name"] = suggestion["database_name"]
                review[f"suggestion_{i}_name_score"] = suggestion["name_score"]
                review[f"suggestion_{i}_support"] = suggestion["support_score"]
            review["accepted_legacy_key"] = ""
            review_rows.append(review)

    matched_eligibility = []
    unresolved_eligibility = []
    for row in eligibility_rows:
        key = selected_by_slug.get(row["draftguru_player_slug"], "")
        out = {**row, "legacy_key": key, "eligibility_source": "draftguru_verified" if key else "draftguru_unresolved_identity"}
        (matched_eligibility if key else unresolved_eligibility).append(out)

    out_dir = Path(args.out)
    mapping_fields = [
        "draftguru_player_slug", "draftguru_player_url", "draftguru_name", "draftguru_name_aliases",
        "dob_text", "dob_iso", "birth_year", "draft_text", "draft_year", "draft_pick", "draft_type_text",
        "first_list_season", "last_list_season", "listed_seasons", "clubs", "match_status", "match_method",
        "legacy_key", "database_name", "name_score", "support_score", "suggestions_json",
    ]
    write_csv(out_dir / "draftguru_player_key_map.csv", mapping_rows, mapping_fields)

    review_fields = mapping_fields[:-1] + [
        item for i in range(1, 6) for item in (
            f"suggestion_{i}_key", f"suggestion_{i}_name", f"suggestion_{i}_name_score", f"suggestion_{i}_support"
        )
    ] + ["accepted_legacy_key", "suggestions_json"]
    write_csv(out_dir / "draftguru_match_review.csv", review_rows, review_fields)

    eligibility_fields = list(eligibility_rows[0].keys()) + ["legacy_key", "eligibility_source"]
    write_csv(out_dir / "draftguru_eligibility_matched_2018_2024.csv", matched_eligibility, eligibility_fields)
    write_csv(out_dir / "draftguru_eligibility_unresolved_2018_2024.csv", unresolved_eligibility, eligibility_fields)

    summary = {
        "draftguru_unique_people": len(people),
        "database_unique_keys": len(database),
        "automatic_matches": len(selected_by_slug),
        "review_people": len(review_rows),
        "matched_player_season_rows": len(matched_eligibility),
        "unresolved_player_season_rows": len(unresolved_eligibility),
        "match_methods": dict(sorted(Counter(row["match_method"] for row in mapping_rows).items())),
    }
    (out_dir / "match_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not selected_by_slug:
        raise RuntimeError("matching produced zero automatic matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
