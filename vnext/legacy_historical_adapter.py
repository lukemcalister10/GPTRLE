"""Isolated historical diagnostic for the frozen legacy engine.

TASK-003C proved that the frozen engine can be run against sanitised historical
inputs and exact TASK-003A cohort keys.  It also proved that the frozen build
cannot currently supply an acceptance-grade rolling-origin forecast: the
available seam is a current learned peak estimate, not a lead-specific annual
forecast, and it depends on learned assets without origin-specific cutoffs.

This module therefore emits a clearly labelled diagnostic proxy and blocker
manifest.  It deliberately does not emit formal ``legacy_frozen`` predictions.
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

from benchmark import PREDICTION_KEY, REQUIRED_PREDICTION_COLUMNS, normalise_predictions
from build_historical_cohorts import (
    DEFAULT_OUT as DEFAULT_COHORT_DIR,
    align_entries_to_verified_history,
    build_locked_cohorts,
    canonical_players,
)
from historical_eligibility import DraftGuruEligibilityResolver, load_historical_players

ROOT = Path(__file__).resolve().parents[1]
LEGACY_DIR = ROOT / "engine" / "rl_after"
LEGACY_MANIFEST = ROOT / "artifacts" / "legacy_manifest.json"
DEFAULT_OUT = ROOT / "build" / "task-003c-legacy-diagnostic"
ADAPTER_VERSION = "task-003c_legacy_historical_diagnostic_v2"
DIAGNOSTIC_MODEL_ID = "legacy_diagnostic_proxy"
FORMAL_MODEL_ID = "legacy_frozen"
POINT_POLICY = "legacy_point_distribution_diagnostic_proxy"
FORMAL_BENCHMARK_ELIGIBLE = False

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

BLOCKERS = (
    {
        "code": "no_horizon_specific_frozen_forecast",
        "detail": (
            "The exposed frozen seam is peak_est plus wrapper-created games/event "
            "values. It does not produce distinct annual lead-1 to lead-5 forecasts."
        ),
    },
    {
        "code": "learned_assets_without_origin_cutoff",
        "detail": (
            "peak_model_v4.pkl, pvc_snapshot.json, bust_prior_table.json, "
            "params.json and rl_passmark.json are current-build learned inputs and "
            "do not carry fold-specific as-of-origin training cutoffs."
        ),
    },
    {
        "code": "wrapper_constructed_probability_outputs",
        "detail": (
            "p_meaningful, cond_games and threshold probabilities are diagnostic "
            "wrapper policies rather than outputs exposed by the frozen engine."
        ),
    },
)

RUNTIME_DEPENDENCIES = {
    "rl_model.py": "frozen_manifest_code",
    "pgrid.py": "unmanifested_algorithm_code",
    "params.json": "blocking_current_learned_asset",
    "rl_passmark.json": "blocking_current_learned_asset",
    "peak_model_v4.pkl": "blocking_current_learned_asset",
    "pvc_snapshot.json": "blocking_current_learned_asset",
    "bust_prior_table.json": "blocking_current_learned_asset",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def stable_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
        + "\n"
    ).encode("utf-8")


def frame_hash(frame: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    for row in frame.sort_values(list(frame.columns)).to_dict("records"):
        digest.update(stable_json(row))
    return digest.hexdigest()


def manifest_hash() -> str:
    return sha256_file(LEGACY_MANIFEST)


def legacy_manifest_file_hashes() -> dict[str, str]:
    manifest = json.loads(LEGACY_MANIFEST.read_text(encoding="utf-8"))
    return dict(manifest["files"])


def runtime_dependency_report() -> list[dict[str, Any]]:
    pinned = legacy_manifest_file_hashes()
    rows = []
    for filename, classification in RUNTIME_DEPENDENCIES.items():
        path = LEGACY_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"legacy runtime dependency missing: {path}")
        repo_path = str(path.relative_to(ROOT)).replace("\\", "/")
        rows.append(
            {
                "path": repo_path,
                "sha256": sha256_file(path),
                "classification": classification,
                "listed_in_frozen_manifest": repo_path in pinned,
                "asof_origin_cutoff_proven": classification
                not in {
                    "blocking_current_learned_asset",
                    "unmanifested_algorithm_code",
                },
            }
        )
    return rows


def pos_for_legacy(position: Any) -> str:
    value = str(position or "MID").upper()
    if value == "KPD":
        return "KDEF"
    if value == "KPF":
        return "KFWD"
    if value in {"MID", "DEF", "FWD", "RUC"}:
        return value
    return "MID"


def _all_historical_players() -> list[dict[str, Any]]:
    resolver = DraftGuruEligibilityResolver()
    players = canonical_players(
        load_historical_players(LEGACY_DIR / "rl_model_data.json")
    )
    players, _ = align_entries_to_verified_history(
        players,
        resolver.evidence_frame(),
    )
    return players


def _sanitize_source_record(
    player: dict[str, Any],
    origin_year: int,
    force_active: bool,
) -> dict[str, Any] | None:
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
                scoring.append(
                    {
                        "year": year,
                        "avg": float(row.get("avg", 0) or 0),
                        "games": int(row.get("games", 0) or 0),
                    }
                )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"malformed scoring row for {player.get('key')} at {origin_year}"
            ) from exc

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
        "games": sum(int(row["games"]) for row in scoring),
        "scoring": scoring,
    }
    if force_active:
        record["_force_active"] = True
    return record


def sanitized_legacy_records(
    snapshots: pd.DataFrame,
    origin_year: int,
) -> list[dict[str, Any]]:
    cohort_keys = set(
        snapshots.loc[
            snapshots["origin_year"].astype(int) == int(origin_year),
            "player_key",
        ].astype(str)
    )
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
        raise ValueError(f"sanitised legacy input missing cohort keys: {missing[:5]}")
    return sorted(records, key=lambda row: row["key"])


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
    recent_games = max(
        [int(r.get("games", 0) or 0) for r in p.get("scoring", [])],
        default=0,
    )
    cond_games = float(min(23, max(1, recent_games or 10)))
    p_meaningful = 1.0 if recent_games >= 6 else 0.0
    exp_games = p_meaningful * cond_games
    exp_points = exp_games * cond_avg
    row = {
        "player_key": item["player_key"],
        "origin_year": origin,
        "lead": int(item["lead"]),
        "p_meaningful": p_meaningful,
        "cond_games": cond_games,
        "cond_avg": cond_avg,
        "exp_games": exp_games,
        "exp_points": exp_points,
    }
    for threshold in (80, 90, 100, 110, 120):
        row[f"p_avg_ge_{threshold}"] = (
            1.0 if p_meaningful and cond_avg >= threshold else 0.0
        )
    for quantile in (10, 25, 50, 75, 90, 97):
        row[f"points_q{quantile:02d}"] = exp_points
    out.append(row)
json.dump(
    out,
    open(output_path, "w", encoding="utf-8"),
    sort_keys=True,
    separators=(",", ":"),
)
'''


def prepare_legacy_sandbox(
    records: list[dict[str, Any]],
    tempdir: Path,
) -> str:
    shutil.copytree(LEGACY_DIR, tempdir, dirs_exist_ok=True)
    (tempdir / "unidecode.py").write_text(
        "def unidecode(value):\n    return str(value)\n",
        encoding="utf-8",
    )
    raw = json.dumps(records, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    (tempdir / "rl_model_data.json").write_bytes(raw)
    return sha256_bytes(raw)


def run_origin_subprocess(
    snapshots: pd.DataFrame,
    keys: pd.DataFrame,
    origin: int,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    records = sanitized_legacy_records(snapshots, origin)
    with tempfile.TemporaryDirectory(prefix="legacy-asof-") as directory:
        tempdir = Path(directory)
        input_hash = prepare_legacy_sandbox(records, tempdir)
        key_rows = keys[keys.origin_year.astype(int) == origin].sort_values(
            PREDICTION_KEY
        )
        keys_path = tempdir / "prediction_keys.json"
        output_path = tempdir / "diagnostic_predictions.json"
        worker_path = tempdir / "legacy_worker.py"
        keys_path.write_text(
            json.dumps(
                key_rows[PREDICTION_KEY].to_dict("records"),
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        worker_path.write_text(WORKER, encoding="utf-8")
        process = subprocess.run(
            [
                sys.executable,
                str(worker_path),
                str(origin),
                str(keys_path),
                str(output_path),
            ],
            cwd=tempdir,
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(
                f"legacy subprocess failed for origin={origin}: "
                f"{process.stderr[-4000:]}"
            )
        raw = output_path.read_bytes()
        frame = pd.DataFrame(json.loads(raw.decode("utf-8")))

    output_hash = sha256_bytes(raw)
    provenance = []
    for lead in sorted(frame["lead"].astype(int).unique()):
        provenance.append(
            {
                "adapter_version": ADAPTER_VERSION,
                "model_id": DIAGNOSTIC_MODEL_ID,
                "distribution_policy": POINT_POLICY,
                "origin_year": int(origin),
                "lead": int(lead),
                "historical_input_cutoff": f"end_of_{origin}_season",
                "learned_asset_cutoff": "unproven_current_frozen_build",
                "formal_benchmark_eligible": False,
                "lead_specific_frozen_output": False,
                "temporary_input_sha256": input_hash,
                "output_sha256": output_hash,
                "subprocess": True,
            }
        )
    return frame, provenance


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {
        "rows": int(len(frame)),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def run_adapter(
    cohort_dir: Path = DEFAULT_COHORT_DIR,
    out_dir: Path = DEFAULT_OUT,
    rebuild_cohorts: bool = True,
) -> dict[str, Any]:
    if rebuild_cohorts or not (cohort_dir / "manifest.json").exists():
        build_locked_cohorts(cohort_dir)
    snapshots = pd.read_csv(cohort_dir / "included_snapshots.csv")
    targets = pd.read_csv(cohort_dir / "targets.csv")
    keys = targets[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    if len(snapshots) != 5622 or len(keys) != 20094:
        raise ValueError(
            "locked cohort counts changed: "
            f"snapshots={len(snapshots)} prediction_keys={len(keys)}"
        )

    pieces: list[pd.DataFrame] = []
    provenance: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for origin, _ in keys.groupby("origin_year", sort=True):
        try:
            piece, origin_provenance = run_origin_subprocess(
                snapshots,
                keys,
                int(origin),
            )
            pieces.append(piece)
            provenance.extend(origin_provenance)
        except Exception as exc:
            failures.append(
                {"origin_year": int(origin), "lead": "", "reason": repr(exc)}
            )
            raise

    raw_predictions = pd.concat(pieces, ignore_index=True)
    predictions = normalise_predictions(
        DIAGNOSTIC_MODEL_ID,
        raw_predictions,
    )
    got = predictions[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(
        drop=True
    )
    if not got.equals(keys):
        raise AssertionError(
            "legacy diagnostic keys differ from locked TASK-003A cohort keys"
        )

    prediction_columns = [
        column
        for column in predictions.columns
        if column not in {"model_id", "lead"}
    ]
    variation = predictions.groupby(["player_key", "origin_year"])[
        prediction_columns
    ].nunique()
    invariant_player_origins = int((variation.max(axis=1) == 1).sum())
    if invariant_player_origins != len(snapshots):
        raise AssertionError(
            "diagnostic proxy unexpectedly varies by lead; review the legacy seam"
        )

    dependencies = runtime_dependency_report()
    out_dir.mkdir(parents=True, exist_ok=True)
    dependency_frame = pd.DataFrame(dependencies)
    blocker_frame = pd.DataFrame(BLOCKERS)
    artifacts = {
        "legacy_diagnostic_predictions.csv": write_csv(
            out_dir / "legacy_diagnostic_predictions.csv",
            predictions,
        ),
        "legacy_diagnostic_fold_counts.csv": write_csv(
            out_dir / "legacy_diagnostic_fold_counts.csv",
            predictions.groupby(["origin_year", "lead"], as_index=False)
            .size()
            .rename(columns={"size": "rows"}),
        ),
        "sanitisation_provenance.csv": write_csv(
            out_dir / "sanitisation_provenance.csv",
            pd.DataFrame(provenance),
        ),
        "runtime_dependencies.csv": write_csv(
            out_dir / "runtime_dependencies.csv",
            dependency_frame,
        ),
        "legacy_blockers.csv": write_csv(
            out_dir / "legacy_blockers.csv",
            blocker_frame,
        ),
        "adapter_failures.csv": write_csv(
            out_dir / "adapter_failures.csv",
            pd.DataFrame(
                failures,
                columns=["origin_year", "lead", "reason"],
            ),
        ),
    }

    manifest = {
        "task": "TASK-003C-LEGACY-HISTORICAL-DIAGNOSTIC",
        "adapter_version": ADAPTER_VERSION,
        "diagnostic_model_id": DIAGNOSTIC_MODEL_ID,
        "reserved_formal_model_id": FORMAL_MODEL_ID,
        "formal_benchmark_eligible": FORMAL_BENCHMARK_ELIGIBLE,
        "formal_legacy_prediction_artifact_created": False,
        "distribution_policy": POINT_POLICY,
        "prediction_rows": int(len(predictions)),
        "included_snapshot_rows": int(len(snapshots)),
        "lead_invariant_player_origins": invariant_player_origins,
        "cohort_key_hash": frame_hash(keys),
        "diagnostic_prediction_hash": artifacts[
            "legacy_diagnostic_predictions.csv"
        ]["sha256"],
        "frozen_manifest_sha256": manifest_hash(),
        "legacy_manifest_files": legacy_manifest_file_hashes(),
        "runtime_dependencies": dependencies,
        "blockers": list(BLOCKERS),
        "forbidden_fields_neutralised": list(FORBIDDEN_INPUT_FIELDS),
        "schema": list(REQUIRED_PREDICTION_COLUMNS),
        "provenance": provenance,
        "artifacts": artifacts,
    }
    manifest_path = out_dir / "legacy_diagnostic_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort-dir", type=Path, default=DEFAULT_COHORT_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--no-rebuild-cohorts", action="store_true")
    args = parser.parse_args()
    manifest = run_adapter(
        args.cohort_dir,
        args.out,
        rebuild_cohorts=not args.no_rebuild_cohorts,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
