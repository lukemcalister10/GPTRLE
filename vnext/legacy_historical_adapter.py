"""Isolated historical adapter for the frozen legacy engine.

This TASK-003C adapter evaluates the frozen legacy code against the locked
TASK-003A cohort keys.  It never asks the legacy engine to choose players: the
benchmark-owned cohort keys are the only prediction keys, and every legacy run
receives a temporary as-of-origin data file containing only sanitized fields.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from benchmark import (
    PREDICTION_KEY,
    REQUIRED_PREDICTION_COLUMNS,
    normalise_predictions,
)
from build_historical_cohorts import DEFAULT_OUT as DEFAULT_COHORT_DIR, build_locked_cohorts, canonical_players, align_entries_to_verified_history
from historical_eligibility import DraftGuruEligibilityResolver, load_historical_players

ROOT = Path(__file__).resolve().parents[1]
LEGACY_DIR = ROOT / "engine" / "rl_after"
LEGACY_MANIFEST = ROOT / "artifacts" / "legacy_manifest.json"
DEFAULT_OUT = ROOT / "build" / "task-003c-legacy-adapter"
ADAPTER_VERSION = "task-003c_legacy_historical_adapter_v1"
POINT_POLICY = "legacy_point_distribution_adapter"

FORBIDDEN_INPUT_FIELDS = (
    "_retired",
    "_last_listed",
    "current_club",
    "current_position",
    "present_position",
    "future_position",
    "current_list",
    "list_status",
    "afl_list_status",
    "final_career_season",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), default=str) + "\n").encode("utf-8")


def frame_hash(frame: pd.DataFrame) -> str:
    h = hashlib.sha256()
    for row in frame.sort_values(list(frame.columns)).to_dict("records"):
        h.update(stable_json(row))
    return h.hexdigest()


def manifest_hash() -> str:
    return sha256_file(LEGACY_MANIFEST)


def legacy_file_hashes() -> dict[str, str]:
    manifest = json.loads(LEGACY_MANIFEST.read_text(encoding="utf-8"))
    return dict(manifest["files"])


def pos_for_legacy(pos: Any) -> str:
    value = str(pos or "MID").upper()
    if value == "KPD":
        return "KDEF"
    if value == "KPF":
        return "KFWD"
    if value in {"MID", "DEF", "FWD", "RUC"}:
        return value
    return "MID"


def _all_historical_players() -> list[dict[str, Any]]:
    resolver = DraftGuruEligibilityResolver()
    players = canonical_players(load_historical_players(LEGACY_DIR / "rl_model_data.json"))
    players, _ = align_entries_to_verified_history(players, resolver.evidence_frame())
    return players


def _sanitize_source_record(player: dict[str, Any], origin_year: int, force_active: bool) -> dict[str, Any] | None:
    try:
        draft_year = int(player.get("year"))
    except (TypeError, ValueError):
        return None
    if draft_year > origin_year:
        return None
    scoring = []
    for row in player.get("scoring") or []:
        try:
            year = int(row["year"])
            if year <= origin_year:
                scoring.append({"year": year, "avg": float(row.get("avg", 0) or 0), "games": int(row.get("games", 0) or 0)})
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"malformed scoring row for {player.get('key')} at origin {origin_year}")
    record = {
        "key": str(player.get("key") or player.get("player") or ""),
        "player": str(player.get("player") or player.get("key") or ""),
        "year": draft_year,
        "pick": int(player.get("pick") or 80),
        "type": str(player.get("type") or player.get("_draft") or "UNK"),
        "_draft": str(player.get("_draft") or player.get("type") or "UNK"),
        "drafted_position": pos_for_legacy(player.get("drafted_position")),
        "_by": player.get("_by"),
        "_bd": player.get("_bd"),
        "games": sum(int(r["games"]) for r in scoring),
        "scoring": scoring,
    }
    if force_active:
        record["_force_active"] = True
    return record


def sanitized_legacy_records(snapshots: pd.DataFrame, origin_year: int) -> list[dict[str, Any]]:
    cohort_keys = set(snapshots.loc[snapshots["origin_year"].astype(int) == int(origin_year), "player_key"].astype(str))
    records = []
    seen = set()
    for player in _all_historical_players():
        key = str(player.get("key") or "")
        record = _sanitize_source_record(player, origin_year, key in cohort_keys)
        if record is not None and key and key not in seen:
            records.append(record)
            seen.add(key)
    missing = sorted(cohort_keys - seen)
    if missing:
        raise ValueError(f"sanitized legacy input missing cohort keys: {missing[:5]}")
    return sorted(records, key=lambda r: r["key"])


WORKER = r'''
import contextlib, io, json, os, sys
origin = int(sys.argv[1])
keys_path, output_path = sys.argv[2], sys.argv[3]
os.environ.setdefault("PYTHONHASHSEED", "0")
with contextlib.redirect_stdout(io.StringIO()):
    import rl_model as M
M.AGE_REF = M.BASE_REF = origin
M._pe_clear()
keys = json.load(open(keys_path, encoding="utf-8"))
by_key = {p["key"]: p for p in M.data}
out = []
for item in keys:
    p = by_key[item["player_key"]]
    M.AGE_REF = M.BASE_REF = origin
    M._pe_clear()
    cond_avg = float(M.peak_est(p))
    recent_games = max([int(r.get("games", 0) or 0) for r in p.get("scoring", [])], default=0)
    cond_games = float(min(23, max(1, recent_games or 10)))
    p_meaningful = 1.0 if recent_games >= 6 else 0.0
    exp_games = p_meaningful * cond_games
    exp_points = exp_games * cond_avg
    row = {"player_key": item["player_key"], "origin_year": origin, "lead": int(item["lead"]),
           "p_meaningful": p_meaningful, "cond_games": cond_games, "cond_avg": cond_avg,
           "exp_games": exp_games, "exp_points": exp_points}
    for t in (80, 90, 100, 110, 120):
        row[f"p_avg_ge_{t}"] = 1.0 if (p_meaningful and cond_avg >= t) else 0.0
    for q in (10, 25, 50, 75, 90, 97):
        row[f"points_q{q:02d}"] = exp_points
    out.append(row)
json.dump(out, open(output_path, "w", encoding="utf-8"), sort_keys=True, separators=(",", ":"))
'''


def prepare_legacy_sandbox(records: list[dict[str, Any]], tempdir: Path) -> str:
    shutil.copytree(LEGACY_DIR, tempdir, dirs_exist_ok=True)
    # The frozen engine imports only ``unidecode.unidecode``.  Some benchmark
    # environments intentionally install only vNext requirements, so provide a
    # tiny runtime shim inside the disposable sandbox rather than changing the
    # frozen files or the repository dependency set.
    (tempdir / "unidecode.py").write_text(
        "def unidecode(value):\n    return str(value)\n",
        encoding="utf-8",
    )
    data_path = tempdir / "rl_model_data.json"
    raw = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    data_path.write_bytes(raw)
    return sha256_bytes(raw)


def run_origin_subprocess(snapshots: pd.DataFrame, keys: pd.DataFrame, origin: int) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    records = sanitized_legacy_records(snapshots, origin)
    with tempfile.TemporaryDirectory(prefix="legacy-asof-") as td:
        tempdir = Path(td)
        input_hash = prepare_legacy_sandbox(records, tempdir)
        key_rows = keys[keys.origin_year.astype(int) == origin].sort_values(PREDICTION_KEY)
        keys_path = tempdir / "prediction_keys.json"
        out_path = tempdir / "predictions.json"
        worker_path = tempdir / "legacy_worker.py"
        keys_path.write_text(json.dumps(key_rows[PREDICTION_KEY].to_dict("records"), sort_keys=True), encoding="utf-8")
        worker_path.write_text(WORKER, encoding="utf-8")
        proc = subprocess.run([sys.executable, str(worker_path), str(origin), str(keys_path), str(out_path)], cwd=tempdir, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"legacy subprocess failed for origin={origin}: {proc.stderr[-4000:]}")
        raw = out_path.read_bytes()
        frame = pd.DataFrame(json.loads(raw.decode("utf-8")))
    output_hash = sha256_bytes(raw)
    provenance = []
    for lead in sorted(frame["lead"].astype(int).unique()):
        provenance.append({
            "adapter_version": ADAPTER_VERSION,
            "distribution_policy": POINT_POLICY,
            "origin_year": int(origin),
            "lead": int(lead),
            "data_cutoff": f"end_of_{origin}_season",
            "temporary_input_sha256": input_hash,
            "output_sha256": output_hash,
            "subprocess": True,
            "training_target_max_year": int(origin - 1),
        })
    return frame, provenance


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {"rows": int(len(frame)), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def run_adapter(cohort_dir: Path = DEFAULT_COHORT_DIR, out_dir: Path = DEFAULT_OUT, rebuild_cohorts: bool = True) -> dict[str, Any]:
    if rebuild_cohorts or not (cohort_dir / "manifest.json").exists():
        build_locked_cohorts(cohort_dir)
    snapshots = pd.read_csv(cohort_dir / "included_snapshots.csv")
    targets = pd.read_csv(cohort_dir / "targets.csv")
    keys = targets[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    if len(snapshots) != 5622 or len(keys) != 20094:
        raise ValueError(f"locked cohort counts changed: snapshots={len(snapshots)} prediction_keys={len(keys)}")

    pieces: list[pd.DataFrame] = []
    provenance: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for origin, _ in keys.groupby("origin_year", sort=True):
        try:
            piece, prov_rows = run_origin_subprocess(snapshots, keys, int(origin))
            pieces.append(piece)
            provenance.extend(prov_rows)
        except Exception as exc:  # recorded and then fatal: no silent row failures
            failures.append({"origin_year": int(origin), "lead": "", "reason": repr(exc)})
            raise
    raw_predictions = pd.concat(pieces, ignore_index=True)
    predictions = normalise_predictions("legacy_frozen", raw_predictions).drop(columns=["model_id"])
    got = predictions[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    if not got.equals(keys):
        raise AssertionError("legacy adapter prediction keys differ from locked TASK-003A cohort keys")

    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "legacy_predictions.csv": write_csv(out_dir / "legacy_predictions.csv", predictions),
        "legacy_fold_counts.csv": write_csv(out_dir / "legacy_fold_counts.csv", predictions.groupby(["origin_year", "lead"], as_index=False).size().rename(columns={"size": "rows"})),
        "sanitisation_report.csv": write_csv(out_dir / "sanitisation_report.csv", pd.DataFrame(provenance)),
        "adapter_failures.csv": write_csv(out_dir / "adapter_failures.csv", pd.DataFrame(failures, columns=["origin_year", "lead", "reason"])),
    }
    manifest = {
        "task": "TASK-003C-LEGACY-HISTORICAL-ADAPTER",
        "adapter_version": ADAPTER_VERSION,
        "distribution_policy": POINT_POLICY,
        "prediction_rows": int(len(predictions)),
        "included_snapshot_rows": int(len(snapshots)),
        "cohort_key_hash": frame_hash(keys),
        "prediction_output_hash": artifacts["legacy_predictions.csv"]["sha256"],
        "frozen_manifest_sha256": manifest_hash(),
        "legacy_files_used": legacy_file_hashes(),
        "forbidden_fields_neutralised": list(FORBIDDEN_INPUT_FIELDS),
        "schema": list(REQUIRED_PREDICTION_COLUMNS),
        "provenance": provenance,
        "artifacts": artifacts,
    }
    (out_dir / "legacy_adapter_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest["artifacts"]["legacy_adapter_manifest.json"] = {"rows": 1, "sha256": sha256_file(out_dir / "legacy_adapter_manifest.json"), "bytes": (out_dir / "legacy_adapter_manifest.json").stat().st_size}
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort-dir", type=Path, default=DEFAULT_COHORT_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--no-rebuild-cohorts", action="store_true")
    args = parser.parse_args()
    manifest = run_adapter(args.cohort_dir, args.out, rebuild_cohorts=not args.no_rebuild_cohorts)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
