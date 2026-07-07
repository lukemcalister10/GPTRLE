"""Leakage-safe rolling-origin benchmark scaffold for TASK-003.

The module deliberately owns benchmark-only cohort, target, adapter, metric and
artifact plumbing so it can run beside active-universe work without changing the
current-season pipeline or frozen legacy behaviour.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, roc_auc_score

from snapshot import build_snapshot, season_at

LOCKED_FOLDS: dict[int, list[int]] = {
    1: list(range(2018, 2025)),
    2: list(range(2018, 2024)),
    3: list(range(2018, 2023)),
    4: list(range(2018, 2022)),
    5: list(range(2018, 2021)),
}
THRESHOLDS = (80, 90, 100, 110, 120)
PINBALL_QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90, 0.97)
PREDICTION_KEY = ["player_key", "origin_year", "lead"]


@dataclass(frozen=True)
class AsOfContract:
    """Strict historical snapshot contract for an origin-year cutoff."""

    origin_year: int
    cutoff_label: str
    allowed_fields: tuple[str, ...] = (
        "key",
        "player",
        "year",
        "pick",
        "type",
        "_draft",
        "drafted_position",
        "_by",
        "_bd",
        "scoring",
    )
    forbidden_future_fields: tuple[str, ...] = (
        "future_position",
        "present_position",
        "current_position",
        "position",
        "current_club",
        "_club",
        "club",
        "current_list",
        "list_status",
        "afl_list_status",
        "retired",
        "_retired",
        "delisted",
    )


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def hash_records(records: Iterable[dict[str, Any]]) -> str:
    h = hashlib.sha256()
    for record in sorted(records, key=stable_json):
        h.update(stable_json(record).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def _fail(player: dict[str, Any], origin_year: int, reason: str) -> dict[str, Any]:
    return {
        "player_key": str(player.get("key") or player.get("player") or ""),
        "player": str(player.get("player") or ""),
        "origin_year": int(origin_year),
        "reason": reason,
    }


def validate_source_player(player: dict[str, Any], origin_year: int) -> list[str]:
    """Return explicit reasons that make a source row unusable for a snapshot."""

    reasons: list[str] = []
    if not (player.get("key") or player.get("player")):
        reasons.append("missing_stable_player_identifier")
    try:
        draft_year = int(player.get("year"))
    except (TypeError, ValueError):
        reasons.append("missing_or_invalid_draft_year")
        draft_year = None
    if draft_year is not None and draft_year > origin_year:
        reasons.append("draft_after_origin")
    for row in player.get("scoring") or []:
        try:
            year = int(row["year"])
            float(row.get("avg", 0.0) or 0.0)
            int(row.get("games", 0) or 0)
        except (KeyError, TypeError, ValueError):
            reasons.append("malformed_scoring_row")
            break
        if year > origin_year:
            continue
    return reasons


def build_asof_snapshot(player: dict[str, Any], contract: AsOfContract) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Build one strict snapshot and a reportable exclusion if it cannot be used."""

    reasons = validate_source_player(player, contract.origin_year)
    if reasons:
        return None, _fail(player, contract.origin_year, ";".join(reasons))
    snapshot = build_snapshot(player, contract.origin_year)
    if snapshot is None:
        return None, _fail(player, contract.origin_year, "snapshot_builder_returned_none")
    row = snapshot.to_dict()
    row["player_key"] = row.pop("key")
    row["asof_cutoff"] = contract.cutoff_label
    return row, None


def realised_targets(player: dict[str, Any], origin_year: int, lead: int) -> dict[str, Any]:
    target_year = origin_year + lead
    s = season_at(player, target_year)
    games = int(s["games"])
    avg = float(s["avg"])
    meaningful = int(games >= 6)
    out = {
        "player_key": str(player.get("key") or player.get("player") or ""),
        "origin_year": int(origin_year),
        "lead": int(lead),
        "target_year": int(target_year),
        "games": games,
        "avg": avg if meaningful else 0.0,
        "points": avg * games,
        "meaningful": meaningful,
    }
    for threshold in THRESHOLDS:
        out[f"avg_ge_{threshold}"] = int(meaningful and avg >= threshold)
    return out


def build_evaluation_cohorts(players: list[dict[str, Any]], folds: dict[int, list[int]] | None = None) -> dict[str, pd.DataFrame]:
    folds = folds or LOCKED_FOLDS
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    seen_snapshot_keys: set[tuple[str, int]] = set()
    by_key = {str(p.get("key") or p.get("player") or ""): p for p in players}
    for lead, origins in folds.items():
        for origin in origins:
            contract = AsOfContract(origin, f"end_of_{origin}_season")
            for p in players:
                row, fail = build_asof_snapshot(p, contract)
                if fail is not None:
                    excluded.append({**fail, "lead": lead})
                    continue
                assert row is not None
                row_key = (row["player_key"], origin)
                if row_key not in seen_snapshot_keys:
                    included.append(row)
                    seen_snapshot_keys.add(row_key)
                targets.append(realised_targets(by_key[row["player_key"]], origin, lead))
    return {
        "folds": pd.DataFrame([{"lead": l, "origin_year": y} for l, ys in folds.items() for y in ys]),
        "included": pd.DataFrame(included).sort_values(["origin_year", "player_key"]).reset_index(drop=True),
        "excluded": pd.DataFrame(excluded).sort_values(["origin_year", "lead", "player_key"]).reset_index(drop=True) if excluded else pd.DataFrame(columns=["player_key", "player", "origin_year", "lead", "reason"]),
        "targets": pd.DataFrame(targets).sort_values(PREDICTION_KEY).reset_index(drop=True),
    }


class PredictionAdapter(Protocol):
    model_id: str

    def predict(self, snapshots: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame: ...


def normalise_predictions(model_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    required = set(PREDICTION_KEY + ["p_meaningful", "exp_games", "exp_avg", "exp_points"])
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{model_id} predictions missing columns: {missing}")
    out = frame.copy()
    out["model_id"] = model_id
    for threshold in THRESHOLDS:
        col = f"p_avg_ge_{threshold}"
        if col not in out:
            out[col] = out["p_meaningful"] if threshold == 80 else 0.001
    return out[["model_id"] + PREDICTION_KEY + ["p_meaningful", "exp_games", "exp_avg", "exp_points"] + [f"p_avg_ge_{t}" for t in THRESHOLDS]].sort_values(PREDICTION_KEY).reset_index(drop=True)


@dataclass
class BaselineAdapter:
    model_id: str = "baseline_recent_scoring"

    def predict(self, snapshots: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
        base = targets[PREDICTION_KEY].merge(snapshots, on=["player_key", "origin_year"], how="left", validate="many_to_one")
        if base.isna().any(axis=None):
            bad = base[base.isna().any(axis=1)][PREDICTION_KEY].to_dict("records")
            raise ValueError(f"baseline snapshot join failed for rows: {bad[:5]}")
        p = np.clip((base["last_games"].astype(float) + base["games_last_2"].astype(float) / 2.0) / 25.0, 0.001, 0.999)
        cond_games = np.clip(base["last_games"].where(base["last_games"] > 0, base["prev_games"]).astype(float), 1.0, 23.0)
        cond_avg = np.clip(base["weighted_avg"].where(base["weighted_avg"] > 0, base["last_avg"]).astype(float), 0.0, 145.0)
        out = pd.DataFrame({"player_key": base.player_key, "origin_year": base.origin_year, "lead": base.lead, "p_meaningful": p, "exp_games": p * cond_games, "exp_avg": p * cond_avg, "exp_points": p * cond_games * cond_avg})
        for threshold in THRESHOLDS:
            out[f"p_avg_ge_{threshold}"] = np.clip(p * (cond_avg >= threshold).astype(float), 0.001, 0.999)
        return normalise_predictions(self.model_id, out)


@dataclass
class VNextAdapter:
    artifacts: dict[int, Any]
    model_id: str = "vnext_artifact"

    def predict(self, snapshots: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
        from model_artifacts import predict as predict_lead

        pieces = []
        for lead, target_rows in targets.groupby("lead", sort=True):
            if int(lead) not in self.artifacts:
                raise ValueError(f"missing vNext artifact for lead {lead}")
            joined = target_rows[PREDICTION_KEY].merge(snapshots, on=["player_key", "origin_year"], how="left", validate="many_to_one")
            pred = predict_lead(self.artifacts[int(lead)], joined)
            pieces.append(pd.concat([joined[PREDICTION_KEY].reset_index(drop=True), pred.reset_index(drop=True).rename(columns={f"p{t}": f"p_avg_ge_{t}" for t in THRESHOLDS})], axis=1))
        return normalise_predictions(self.model_id, pd.concat(pieces, ignore_index=True))


@dataclass
class LegacyAdapter:
    legacy_runner: Any
    model_id: str = "legacy_frozen"

    def predict(self, snapshots: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
        raw = self.legacy_runner(snapshots.copy(), targets.copy())
        return normalise_predictions(self.model_id, raw)


def assert_common_keys_and_targets(predictions: dict[str, pd.DataFrame], targets: pd.DataFrame) -> None:
    expected = targets[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    for model_id, pred in predictions.items():
        got = pred[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
        if not got.equals(expected):
            raise AssertionError(f"{model_id} prediction keys differ from benchmark cohort")


def _safe_auc(y: pd.Series, p: pd.Series) -> float:
    return float(roc_auc_score(y, p)) if y.nunique() > 1 else float("nan")


def calibration_intercept_slope(y: pd.Series, p: pd.Series) -> tuple[float, float]:
    yv = y.to_numpy(float)
    pv = np.clip(p.to_numpy(float), 0.001, 0.999)
    logit = np.log(pv / (1.0 - pv))
    if len(np.unique(yv)) < 2 or np.std(logit) == 0:
        return float("nan"), float("nan")
    slope, intercept = np.polyfit(logit, yv, 1)
    return float(intercept), float(slope)


def pinball_loss(y: pd.Series, q: pd.Series, tau: float) -> float:
    diff = y.to_numpy(float) - q.to_numpy(float)
    return float(np.mean(np.maximum(tau * diff, (tau - 1.0) * diff)))


def score_predictions(predictions: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    joined = predictions.merge(targets, on=PREDICTION_KEY, how="inner", validate="one_to_one")
    if len(joined) != len(predictions) or len(joined) != len(targets):
        raise ValueError("prediction/target merge did not preserve one-to-one benchmark rows")
    rows: list[dict[str, Any]] = []
    for (model_id, lead), g in joined.groupby(["model_id", "lead"], sort=True):
        inter, slope = calibration_intercept_slope(g["meaningful"], g["p_meaningful"])
        row = {
            "model_id": model_id,
            "lead": int(lead),
            "n": int(len(g)),
            "brier_meaningful": brier_score_loss(g["meaningful"], g["p_meaningful"]),
            "log_loss_meaningful": log_loss(g["meaningful"], np.clip(g["p_meaningful"], 0.001, 0.999), labels=[0, 1]),
            "calibration_intercept_meaningful": inter,
            "calibration_slope_meaningful": slope,
            "auc_meaningful": _safe_auc(g["meaningful"], g["p_meaningful"]),
            "mae_games": mean_absolute_error(g["games"], g["exp_games"]),
            "mae_total_points": mean_absolute_error(g["points"], g["exp_points"]),
        }
        meaningful = g[g["meaningful"] == 1]
        row["mae_avg_conditional_meaningful"] = mean_absolute_error(meaningful["avg"], meaningful["exp_avg"]) if len(meaningful) else float("nan")
        for threshold in THRESHOLDS:
            actual = g[f"avg_ge_{threshold}"]
            prob = g[f"p_avg_ge_{threshold}"]
            row[f"brier_avg_ge_{threshold}"] = brier_score_loss(actual, prob)
            row[f"auc_avg_ge_{threshold}"] = _safe_auc(actual, prob)
        for tau in PINBALL_QUANTILES:
            row[f"pinball_points_q{int(tau * 100):02d}"] = pinball_loss(g["points"], g["exp_points"], tau)
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["model_id", "lead"]).reset_index(drop=True)


def write_benchmark_artifacts(out_dir: Path, cohorts: dict[str, pd.DataFrame], predictions: dict[str, pd.DataFrame], metrics: pd.DataFrame, reproduction_commands: list[str]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_predictions = pd.concat(predictions.values(), ignore_index=True).sort_values(["model_id"] + PREDICTION_KEY).reset_index(drop=True)
    frames = {**cohorts, "predictions": all_predictions, "metrics": metrics}
    manifest: dict[str, Any] = {
        "task": "TASK-003-LEGACY-BENCHMARK",
        "folds": LOCKED_FOLDS,
        "model_identifiers": sorted(predictions),
        "cohort_counts": {
            "included_snapshot_rows": int(len(cohorts["included"])),
            "excluded_rows": int(len(cohorts["excluded"])),
            "target_rows": int(len(cohorts["targets"])),
        },
        "target_definitions": {"meaningful": "games >= 6", "points": "season average times games", "zero_game_future_outcomes": "retained with games=0, avg=0, points=0"},
        "reproduction_commands": reproduction_commands,
        "artifacts": {},
    }
    for name, frame in frames.items():
        path = out_dir / f"{name}.csv"
        frame.to_csv(path, index=False)
        manifest["artifacts"][f"{name}.csv"] = {"rows": int(len(frame)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest
