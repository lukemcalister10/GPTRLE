"""Authoritative current-season player-universe reconciliation.

This module treats data/current/Players_2026.csv as authoritative only for the
2026 current universe, AFFL team, and current eligibility. It deliberately keeps
those fields out of historical snapshot construction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

VALID_ELIGIBILITIES = {"K-DEF", "G-DEF", "K-FWD", "G-FWD", "RUCK", "MID"}
ELIGIBILITY_ALIASES = {"RUC": "RUCK", "SD": "G-DEF", "SF": "G-FWD"}
ROOT = Path(__file__).resolve().parents[1]

# Explicit identity-evidence corrections for known same/display-name hazards.
# These are deliberately narrow and evidence-only: they do not alter the current
# 2026 universe, AFFL ownership, current eligibility, historical scoring rows, or
# production legacy files. They prevent a bad upstream identity fact from changing
# stable ids or letting one player inherit another player's history.
KNOWN_IDENTITY_EVIDENCE_OVERRIDES: dict[str, dict[str, Any]] = {
    # St Kilda Max King: pick 4, 2018 national draft; born 2000-07-07.
    # The historical source can otherwise carry the younger Max/Maxwell King's
    # 2007 birth date for this legacy key, which is an impossible draft-age join.
    "max-king-stk": {
        "birth_date": "2000-07-07",
        "birth_year": 2000,
        "draft_pick": 4,
        "draft_type": "ND",
        "draft_year": 2018,
    },
    # Younger Sydney-origin Max/Maxwell King: keep a separate identity and alias.
    "max-king-syd": {
        "birth_date": "2007-01-09",
        "birth_year": 2007,
        "draft_pick": 49,
        "draft_type": "ND",
        "draft_year": 2025,
    },
}


def normalise_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def load_authoritative(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
    required = ["Player Name", "AFFL Team", "Position/s"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"authoritative source missing columns: {missing}")
    df = df[required].copy()
    df["source_row"] = range(1, len(df) + 1)
    df["name_norm"] = df["Player Name"].map(normalise_name)
    df["raw_eligibilities"] = df["Position/s"].map(lambda s: tuple(x.strip() for x in str(s).split(",") if x.strip()))
    df["eligibilities"] = df["raw_eligibilities"].map(lambda vals: tuple(ELIGIBILITY_ALIASES.get(x, x) for x in vals))
    return df


def load_legacy_board(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    return list(data["active"])


def load_vnext_previous(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def previous_vnext_inclusion(player: dict[str, Any]) -> tuple[bool, str]:
    if player.get("_retired"):
        return False, "retired"
    if player.get("_last_listed") is not None and int(player.get("_last_listed")) < 2026:
        return False, "last_listed_before_2026"
    scoring = player.get("scoring") or []
    played = any(int(r.get("games", 0) or 0) >= 1 for r in scoring)
    recent = bool(player.get("_has26")) or any(int(r.get("year", 0) or 0) >= 2024 for r in scoring) or int(player.get("year", 0) or 0) >= 2024
    unplayed = str(player.get("type") or "") in ("ND", "RD") and int(player.get("year", 0) or 0) >= 2024 and sum(int(r.get("games", 0) or 0) for r in scoring) == 0
    if (played and recent) or unplayed:
        return True, "included_by_previous_predicate"
    reasons = []
    if not played:
        reasons.append("no_current_or_historical_scoring_games")
    if not recent:
        reasons.append("no_recent_activity_signal")
    if not unplayed:
        reasons.append("not_recent_unplayed_draftee")
    return False, "+".join(reasons)


def identity_evidence(legacy_player: dict[str, Any], historical_player: dict[str, Any] | None = None) -> dict[str, Any]:
    historical_player = historical_player or {}
    fields = {
        "legacy_key": legacy_player.get("key") or "",
        "draft_year": legacy_player.get("yr") or historical_player.get("year") or "",
        "draft_type": legacy_player.get("ty") or historical_player.get("type") or historical_player.get("_draft") or "",
        "draft_pick": legacy_player.get("pk") or historical_player.get("pick") or "",
        "birth_year": historical_player.get("_by") or "",
        "birth_date": historical_player.get("_bd") or "",
    }
    overrides = KNOWN_IDENTITY_EVIDENCE_OVERRIDES.get(str(fields["legacy_key"]))
    if overrides:
        fields.update(overrides)
    return {k: fields[k] for k in sorted(fields)}


def stable_player_id(legacy_player: dict[str, Any], historical_player: dict[str, Any] | None = None) -> str:
    evidence = identity_evidence(legacy_player, historical_player)
    payload = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
    return f"afl-player-v1-{digest}"


def missing_identity_evidence(legacy_player: dict[str, Any], historical_player: dict[str, Any] | None = None) -> tuple[str, ...]:
    evidence = identity_evidence(legacy_player, historical_player)
    return tuple(k for k, v in evidence.items() if v in (None, ""))


def canonical_legacy_eligibility(fut: Any) -> tuple[str, ...]:
    out = []
    mapping = {"GEN_DEF": "G-DEF", "GEN_FWD": "G-FWD", "KEY_DEF": "K-DEF", "KEY_FWD": "K-FWD", "RUC": "RUCK", "RUCK": "RUCK", "MID": "MID", "DEF": "G-DEF", "FWD": "G-FWD"}
    for item in fut or []:
        raw = item[0] if isinstance(item, (list, tuple)) and item else item
        code = mapping.get(str(raw).upper(), str(raw).upper())
        if code not in out:
            out.append(code)
    return tuple(out)


def _as_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def identity_health_issues(matched: pd.DataFrame) -> pd.DataFrame:
    """Return machine-readable identity issues that should block registry release."""
    issues: list[dict[str, Any]] = []

    for column, code in (("stable_player_id", "duplicate_stable_player_id"), ("legacy_key", "duplicate_legacy_key")):
        duplicated = matched[(matched[column] != "") & matched[column].duplicated(keep=False)].sort_values(column)
        for _, row in duplicated.iterrows():
            issues.append({
                "severity": "critical",
                "issue_code": code,
                "legacy_key": row.get("legacy_key", ""),
                "stable_player_id": row.get("stable_player_id", ""),
                "player_name": row.get("player_name", ""),
                "detail": f"{column} is not unique",
                "recommended_disposition": "Fix identity evidence before release.",
            })

    display_dupes = matched[(matched["player_name"] != "") & matched["player_name"].duplicated(keep=False)].sort_values("player_name")
    for _, row in display_dupes.iterrows():
        issues.append({
            "severity": "review",
            "issue_code": "duplicate_display_name",
            "legacy_key": row.get("legacy_key", ""),
            "stable_player_id": row.get("stable_player_id", ""),
            "player_name": row.get("player_name", ""),
            "detail": "Display names can duplicate, but joins must use stable_player_id or legacy_key.",
            "recommended_disposition": "Allow only when stable_player_id and legacy_key remain distinct.",
        })

    for _, row in matched.iterrows():
        evidence = json.loads(row.get("identity_evidence_json") or "{}")
        birth_year = _as_int(evidence.get("birth_year"))
        draft_year = _as_int(evidence.get("draft_year"))
        draft_type = str(evidence.get("draft_type") or "")
        if birth_year is not None and draft_year is not None and draft_type in {"ND", "RD", "MSD"}:
            draft_age = draft_year - birth_year
            if draft_age < 16 or draft_age > 35:
                issues.append({
                    "severity": "critical",
                    "issue_code": "implausible_draft_age",
                    "legacy_key": row.get("legacy_key", ""),
                    "stable_player_id": row.get("stable_player_id", ""),
                    "player_name": row.get("player_name", ""),
                    "detail": f"{draft_type} draft age is {draft_age} from birth_year={birth_year}, draft_year={draft_year}",
                    "recommended_disposition": "Correct birth/draft evidence before release.",
                })

    return pd.DataFrame(issues, columns=["severity", "issue_code", "legacy_key", "stable_player_id", "player_name", "detail", "recommended_disposition"])


def build_reconciliation(auth: pd.DataFrame, legacy: list[dict[str, Any]], previous: list[dict[str, Any]]) -> dict[str, pd.DataFrame]:
    legacy_by_name = defaultdict(list)
    for p in legacy:
        legacy_by_name[normalise_name(p["name"])].append(p)
    historical_by_key = {p.get("key"): p for p in previous if p.get("key")}
    prev_by_name = defaultdict(list)
    prev_included = set()
    prev_reason = {}
    for p in previous:
        n = normalise_name(p.get("player", ""))
        prev_by_name[n].append(p)
        inc, reason = previous_vnext_inclusion(p)
        if inc:
            prev_included.add(n)
        prev_reason[n] = reason

    rows = []
    ambiguous = []
    for _, r in auth.iterrows():
        candidates = legacy_by_name.get(r.name_norm, [])
        status = "matched" if len(candidates) == 1 else "unmatched" if not candidates else "ambiguous"
        candidate = candidates[0] if status == "matched" else None
        historical_candidate = historical_by_key.get(candidate.get("key")) if candidate else None
        stable_id = stable_player_id(candidate, historical_candidate) if candidate else ""
        legacy_key = candidate.get("key", "") if candidate else ""
        identity = identity_evidence(candidate, historical_candidate) if candidate else {}
        if status == "ambiguous":
            ambiguous.append({"player_name": r["Player Name"], "candidate_keys": ";".join(c["key"] for c in candidates)})
        rows.append({
            "source_row": r.source_row, "stable_player_id": stable_id, "legacy_key": legacy_key, "player_name": r["Player Name"], "affl_team": r["AFFL Team"],
            "eligibilities": ",".join(r.eligibilities), "match_status": status,
            "legacy_name": candidate["name"] if candidate else "", "legacy_afl_club": candidate.get("club", "") if candidate else "",
            "legacy_eligibilities": ",".join(canonical_legacy_eligibility(candidate.get("fut"))) if candidate else "",
            "identity_evidence_json": json.dumps(identity, sort_keys=True, separators=(",", ":")), "missing_identity_evidence": ",".join(missing_identity_evidence(candidate, historical_candidate)) if candidate else "",
            "previous_vnext_included": r.name_norm in prev_included, "previous_vnext_exclusion_reason": "" if r.name_norm in prev_included else prev_reason.get(r.name_norm, "not_found_in_previous_vnext_source"),
        })
    matched = pd.DataFrame(rows).sort_values(["match_status", "player_name"])
    matched_legacy_keys = set(matched.loc[matched.match_status == "matched", "legacy_key"])
    legacy_only = pd.DataFrame([{"stable_player_id": stable_player_id(p, historical_by_key.get(p.get("key"))), "legacy_key": p["key"], "player_name": p["name"], "legacy_afl_club": p.get("club", ""), "identity_evidence_json": json.dumps(identity_evidence(p, historical_by_key.get(p.get("key"))), sort_keys=True, separators=(",", ":")), "missing_identity_evidence": ",".join(missing_identity_evidence(p, historical_by_key.get(p.get("key"))))} for p in legacy if p["key"] not in matched_legacy_keys]).sort_values("player_name")
    dup_auth = pd.DataFrame([{"name_norm": n, "count": c} for n, c in Counter(auth.name_norm).items() if c > 1])
    dup_legacy = pd.DataFrame([{"name_norm": n, "count": len(v), "keys": ";".join(p["key"] for p in v)} for n, v in legacy_by_name.items() if len(v) > 1])
    invalid = []
    for _, r in auth.iterrows():
        bad = [e for e in r.eligibilities if e not in VALID_ELIGIBILITIES]
        aliases = [raw for raw, norm in zip(r.raw_eligibilities, r.eligibilities) if raw != norm]
        if not r["Player Name"] or not r["AFFL Team"] or not r.eligibilities or bad or aliases:
            invalid.append({"source_row": r.source_row, "player_name": r["Player Name"], "raw_eligibilities": ",".join(r.raw_eligibilities), "normalised_eligibilities": ",".join(r.eligibilities), "bad_eligibilities_after_normalisation": ",".join(bad), "normalised_aliases": ",".join(aliases), "missing_name": not bool(r["Player Name"]), "missing_affl_team": not bool(r["AFFL Team"]), "missing_eligibility": not bool(r.eligibilities)})
    affl_unavailable = pd.DataFrame(columns=["status", "detail"])
    elig_dis = matched[(matched.match_status == "matched") & (matched.eligibilities != matched.legacy_eligibilities)].copy()
    missing_identity = matched[(matched.match_status == "matched") & (matched.missing_identity_evidence != "")].copy()
    wrongly = matched[(matched.match_status == "matched") & (~matched.previous_vnext_included)].copy()
    return {"authoritative_universe": matched, "matched_players": matched[matched.match_status == "matched"], "unmatched_authoritative_players": matched[matched.match_status == "unmatched"], "legacy_only_players": legacy_only, "ambiguous_matches": pd.DataFrame(ambiguous), "duplicate_name_cases": pd.concat([dup_auth.assign(source="authoritative"), dup_legacy.assign(source="legacy")], ignore_index=True), "affl_ownership_comparison_unavailable": affl_unavailable, "eligibility_disagreements": elig_dis, "invalid_or_missing_fields": pd.DataFrame(invalid), "missing_identity_evidence": missing_identity, "players_wrongly_excluded_by_current_scoring_or_recent_play_logic": wrongly, "identity_health_issues": identity_health_issues(matched[matched.match_status == "matched"])}


def write_reports(reports: dict[str, pd.DataFrame], out: Path) -> dict[str, str]:
    out.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, df in reports.items():
        path = out / f"{name}.csv"
        df.to_csv(path, index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {"reports": hashes, "authoritative_rows": int(len(reports["authoritative_universe"])), "matched_rows": int(len(reports["matched_players"])), "legacy_only_rows": int(len(reports["legacy_only_players"])), "previous_vnext_wrongly_excluded_rows": int(len(reports["players_wrongly_excluded_by_current_scoring_or_recent_play_logic"])), "critical_identity_issue_rows": int((reports["identity_health_issues"].get("severity") == "critical").sum()) if not reports["identity_health_issues"].empty else 0}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return hashes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authoritative", default=str(ROOT / "data/current/Players_2026.csv"))
    ap.add_argument("--legacy", default=str(ROOT / "data/rl_build/rl_app_data.json"))
    ap.add_argument("--previous-vnext", default=str(ROOT / "engine/rl_after/rl_model_data.json"))
    ap.add_argument("--out", default=str(ROOT / "reports/task-002-active-universe"))
    a = ap.parse_args()
    reports = build_reconciliation(load_authoritative(Path(a.authoritative)), load_legacy_board(Path(a.legacy)), load_vnext_previous(Path(a.previous_vnext)))
    write_reports(reports, Path(a.out))
    print(json.dumps({k: len(v) for k, v in reports.items()}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
