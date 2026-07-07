"""Leakage-safe rolling-origin benchmark scaffold for TASK-003.

The module deliberately owns benchmark-only cohort, target, adapter, metric and
artifact plumbing so it can run beside active-universe work without changing the
current-season pipeline or frozen legacy behaviour.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

import numpy as np
import pandas as pd
from scipy.optimize import minimize
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
QUANTILE_COLUMNS = tuple(f"points_q{int(q * 100):02d}" for q in PINBALL_QUANTILES)
PREDICTION_KEY = ["player_key", "origin_year", "lead"]
BASE_PREDICTION_COLUMNS = ("p_meaningful", "cond_games", "cond_avg", "exp_games", "exp_points")
THRESHOLD_PROB_COLUMNS = tuple(f"p_avg_ge_{t}" for t in THRESHOLDS)
REQUIRED_PREDICTION_COLUMNS = tuple(PREDICTION_KEY) + BASE_PREDICTION_COLUMNS + THRESHOLD_PROB_COLUMNS + QUANTILE_COLUMNS


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


@dataclass(frozen=True)
class EligibilityDecision:
    """Historical list/eligibility decision for one player at one origin."""

    eligible: bool | None
    reason: str


EligibilityResolver = Callable[[dict[str, Any], int], EligibilityDecision | bool | None]


class StaticEligibilityResolver:
    """Resolve eligibility from explicit historical `(player_key, origin_year)` evidence."""

    def __init__(self, evidence: dict[tuple[str, int], bool | str | EligibilityDecision]):
        self.evidence = evidence

    def __call__(self, player: dict[str, Any], origin_year: int) -> EligibilityDecision:
        key = str(player.get("key") or player.get("player") or "")
        value = self.evidence.get((key, int(origin_year)))
        if value is None:
            return EligibilityDecision(None, "historical_eligibility_unavailable")
        if isinstance(value, EligibilityDecision):
            return value
        if isinstance(value, str):
            return EligibilityDecision(False, value)
        return EligibilityDecision(bool(value), "historically_eligible" if value else "not_listed_at_origin")


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


def sanitize_source_player(player: dict[str, Any], contract: AsOfContract) -> tuple[dict[str, Any], list[str]]:
    """Keep only as-of allowed fields and validate only information visible at origin."""

    sanitized = {field: player[field] for field in contract.allowed_fields if field in player and field != "scoring"}
    reasons: list[str] = []
    scoring: list[dict[str, Any]] = []
    for row in player.get("scoring") or []:
        try:
            year = int(row["year"])
        except (KeyError, TypeError, ValueError):
            reasons.append("malformed_scoring_year")
            break
        if year > contract.origin_year:
            continue
        try:
            scoring.append({"year": year, "avg": float(row.get("avg", 0.0) or 0.0), "games": int(row.get("games", 0) or 0)})
        except (TypeError, ValueError):
            reasons.append("malformed_scoring_row")
            break
    sanitized["scoring"] = scoring
    return sanitized, reasons


def validate_source_player(player: dict[str, Any], origin_year: int) -> list[str]:
    """Return explicit reasons that make a sanitized source row unusable."""

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
    return reasons


def build_asof_snapshot(player: dict[str, Any], contract: AsOfContract) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Build one strict sanitized snapshot and a reportable exclusion if unusable."""

    sanitized, sanitize_reasons = sanitize_source_player(player, contract)
    reasons = validate_source_player(sanitized, contract.origin_year) + sanitize_reasons
    if reasons:
        return None, _fail(player, contract.origin_year, ";".join(reasons))
    snapshot = build_snapshot(sanitized, contract.origin_year)
    if snapshot is None:
        return None, _fail(player, contract.origin_year, "snapshot_builder_returned_none")
    row = snapshot.to_dict()
    row["player_key"] = row.pop("key")
    row["asof_cutoff"] = contract.cutoff_label
    return row, None


def coerce_eligibility(decision: EligibilityDecision | bool | None) -> EligibilityDecision:
    if isinstance(decision, EligibilityDecision):
        return decision
    if decision is None:
        return EligibilityDecision(None, "historical_eligibility_unavailable")
    return EligibilityDecision(bool(decision), "historically_eligible" if decision else "not_listed_at_origin")


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


def build_evaluation_cohorts(
    players: list[dict[str, Any]],
    folds: dict[int, list[int]] | None = None,
    eligibility_resolver: EligibilityResolver | None = None,
    *,
    fail_on_unavailable_eligibility: bool = True,
) -> dict[str, pd.DataFrame]:
    folds = folds or LOCKED_FOLDS
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    seen_snapshot_keys: set[tuple[str, int]] = set()
    by_key = {str(p.get("key") or p.get("player") or ""): p for p in players}
    eligibility_unavailable = False
    for lead, origins in folds.items():
        for origin in origins:
            contract = AsOfContract(origin, f"end_of_{origin}_season")
            for p in players:
                decision = coerce_eligibility(eligibility_resolver(p, origin) if eligibility_resolver else None)
                if decision.eligible is not True:
                    excluded.append({**_fail(p, origin, decision.reason), "lead": lead})
                    eligibility_unavailable = eligibility_unavailable or decision.eligible is None
                    continue
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
    excluded_frame = pd.DataFrame(excluded).sort_values(["origin_year", "lead", "player_key"]).reset_index(drop=True) if excluded else pd.DataFrame(columns=["player_key", "player", "origin_year", "lead", "reason"])
    if eligibility_unavailable and fail_on_unavailable_eligibility:
        sample = excluded_frame[excluded_frame.reason == "historical_eligibility_unavailable"].head(5).to_dict("records")
        raise ValueError(f"historical eligibility unavailable for benchmark rows: {sample}")
    return {
        "folds": pd.DataFrame([{"lead": l, "origin_year": y} for l, ys in folds.items() for y in ys]),
        "included": pd.DataFrame(included).sort_values(["origin_year", "player_key"]).reset_index(drop=True) if included else pd.DataFrame(),
        "excluded": excluded_frame,
        "targets": pd.DataFrame(targets).sort_values(PREDICTION_KEY).reset_index(drop=True) if targets else pd.DataFrame(columns=PREDICTION_KEY),
    }


class PredictionAdapter(Protocol):
    model_id: str

    def predict(self, snapshots: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame: ...


def degenerate_point_quantiles(points: pd.Series | np.ndarray) -> dict[str, pd.Series | np.ndarray]:
    """Emit an explicit degenerate point distribution for deterministic adapters."""

    return {col: points for col in QUANTILE_COLUMNS}


def normalise_predictions(model_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(set(REQUIRED_PREDICTION_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"{model_id} predictions missing columns: {missing}")
    if frame.duplicated(PREDICTION_KEY).any():
        dupes = frame.loc[frame.duplicated(PREDICTION_KEY, keep=False), PREDICTION_KEY].head(5).to_dict("records")
        raise ValueError(f"{model_id} predictions contain duplicate keys: {dupes}")
    out = frame.copy()
    out["model_id"] = model_id
    numeric = list(BASE_PREDICTION_COLUMNS + THRESHOLD_PROB_COLUMNS + QUANTILE_COLUMNS)
    if out[numeric].isna().any(axis=None):
        raise ValueError(f"{model_id} predictions contain missing required numeric values")
    values = out[numeric].to_numpy(float)
    if not np.isfinite(values).all():
        raise ValueError(f"{model_id} predictions contain non-finite numeric values")
    prob_cols = ["p_meaningful", *THRESHOLD_PROB_COLUMNS]
    if ((out[prob_cols] < 0.0) | (out[prob_cols] > 1.0)).any(axis=None):
        raise ValueError(f"{model_id} predictions contain probabilities outside [0, 1]")
    nonnegative_cols = ["cond_games", "cond_avg", "exp_games", "exp_points", *QUANTILE_COLUMNS]
    if (out[nonnegative_cols] < 0.0).any(axis=None):
        raise ValueError(f"{model_id} predictions contain negative games or points forecasts")
    threshold_values = out[list(THRESHOLD_PROB_COLUMNS)].to_numpy(float)
    if (np.diff(threshold_values, axis=1) > 1e-12).any():
        raise ValueError(f"{model_id} predictions contain non-monotonic threshold probabilities")
    quantile_values = out[list(QUANTILE_COLUMNS)].to_numpy(float)
    if (np.diff(quantile_values, axis=1) < -1e-12).any():
        raise ValueError(f"{model_id} predictions contain crossing point quantiles")
    return out[["model_id", *REQUIRED_PREDICTION_COLUMNS]].sort_values(PREDICTION_KEY).reset_index(drop=True)


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
        exp_points = p * cond_games * cond_avg
        out = pd.DataFrame({"player_key": base.player_key, "origin_year": base.origin_year, "lead": base.lead, "p_meaningful": p, "cond_games": cond_games, "cond_avg": cond_avg, "exp_games": p * cond_games, "exp_points": exp_points})
        for threshold in THRESHOLDS:
            out[f"p_avg_ge_{threshold}"] = np.clip(p * (cond_avg >= threshold).astype(float), 0.0, 1.0)
        for col, values in degenerate_point_quantiles(exp_points).items():
            out[col] = values
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
            pred = predict_lead(self.artifacts[int(lead)], joined).rename(columns={f"p{t}": f"p_avg_ge_{t}" for t in THRESHOLDS})
            pred["cond_games"] = pred.get("cond_games", pred["exp_games"] / np.clip(pred["p_meaningful"], 0.001, None))
            pred["cond_avg"] = pred.get("cond_avg", np.where(pred["cond_games"] > 0, pred["exp_points"] / np.clip(pred["p_meaningful"] * pred["cond_games"], 0.001, None), 0.0))
            for col, values in degenerate_point_quantiles(pred["exp_points"]).items():
                pred[col] = values
            pieces.append(pd.concat([joined[PREDICTION_KEY].reset_index(drop=True), pred.reset_index(drop=True)], axis=1))
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


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p.astype(float), 1e-6, 1.0 - 1e-6)
    return np.log(p / (1.0 - p))


def calibration_intercept_slope(y: pd.Series, p: pd.Series) -> tuple[float, float]:
    yv = y.to_numpy(float)
    pv = p.to_numpy(float)
    x = _logit(pv)
    if len(np.unique(yv)) < 2 or np.std(x) < 1e-12:
        return float("nan"), float("nan")

    def objective(beta: np.ndarray) -> float:
        eta = beta[0] + beta[1] * x
        return float(np.sum(np.logaddexp(0.0, eta) - yv * eta))

    result = minimize(objective, np.array([0.0, 1.0]), method="BFGS")
    if not result.success:
        raise ValueError(f"logistic calibration fit failed: {result.message}")
    return float(result.x[0]), float(result.x[1])


def pinball_loss(y: pd.Series, q: pd.Series, tau: float) -> float:
    diff = y.to_numpy(float) - q.to_numpy(float)
    return float(np.mean(np.maximum(tau * diff, (tau - 1.0) * diff)))


def score_predictions(predictions: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    if "model_id" not in predictions.columns:
        raise ValueError("predictions must include model_id")
    validated = []
    for model_id, group in predictions.groupby("model_id", sort=True):
        validated.append(normalise_predictions(str(model_id), group.drop(columns=["model_id"])))
    predictions = pd.concat(validated, ignore_index=True)
    joined = predictions.merge(targets, on=PREDICTION_KEY, how="inner", validate="many_to_one")
    if len(joined) != len(predictions):
        raise ValueError("prediction/target merge did not preserve benchmark prediction rows")
    expected = targets[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
    for model_id, group in predictions.groupby("model_id", sort=True):
        got = group[PREDICTION_KEY].sort_values(PREDICTION_KEY).reset_index(drop=True)
        if not got.equals(expected):
            raise ValueError(f"{model_id} predictions do not cover exactly the target rows")
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
        row["mae_avg_conditional_meaningful"] = mean_absolute_error(meaningful["avg"], meaningful["cond_avg"]) if len(meaningful) else float("nan")
        for threshold in THRESHOLDS:
            actual = g[f"avg_ge_{threshold}"]
            prob = g[f"p_avg_ge_{threshold}"]
            row[f"brier_avg_ge_{threshold}"] = brier_score_loss(actual, prob)
            row[f"auc_avg_ge_{threshold}"] = _safe_auc(actual, prob)
        for tau, col in zip(PINBALL_QUANTILES, QUANTILE_COLUMNS, strict=True):
            row[f"pinball_points_q{int(tau * 100):02d}"] = pinball_loss(g["points"], g[col], tau)
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
        "prediction_schema": list(REQUIRED_PREDICTION_COLUMNS),
        "deferred_protocol_components": ["reliability_tables", "multi_season_events", "crps_or_coverage", "keeper_utility_metrics", "required_slices", "block_bootstrap_confidence_intervals"],
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
