"""TASK-050 coherent joint season-outcome distribution.

The model produces zero-game, short-season and meaningful-season outcomes from
one deterministic draw distribution. Expected outcomes, quantiles and scoring
threshold probabilities are all derived from those same draws. No row-level
moment forcing or post-hoc quantile correction is permitted.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import model_artifacts
import model_artifacts_zero_history
from evaluate_v3_fast import CAT as BASE_CAT
from evaluate_v3_fast import NUM as BASE_NUM
from evaluate_v3_fast import TH
from model_artifacts_pooled_ridge_conditional_average import (
    RIDGE_ALPHA_GRID,
    add_ceiling_evidence_feature,
    predict as predict_task047,
    train_lead as train_task047,
)

SAMPLE_COUNT = 4096
STATE_C_GRID = (0.03, 0.1, 0.3, 1.0, 3.0)
SEED_PREFIX = "TASK-050"
QUANTILE_LEVELS = np.array([0.10, 0.25, 0.50, 0.75, 0.90, 0.97])
QUANTILE_COLUMNS = [f"points_q{int(q * 100):02d}" for q in QUANTILE_LEVELS]
ALL_POOL = "__ALL__"
MIN_RESIDUAL_ROWS = 30
POSITION_POOL_MIN_ROWS = 100


@dataclass(frozen=True)
class ShortResidualPool:
    games: np.ndarray
    log_rate_residuals: np.ndarray


@dataclass(frozen=True)
class MeaningfulResidualPool:
    games_residuals: np.ndarray
    avg_residuals: np.ndarray


@dataclass
class JointSeasonArtifact:
    lead: int
    state_preprocessor: Any
    state_model: Any
    selected_state_c: float
    state_c_scores: dict[float, float]
    short_rate_model: Any
    selected_short_alpha: float
    short_alpha_scores: dict[float, float]
    short_pools: dict[str, ShortResidualPool]
    meaningful_pools: dict[str, MeaningfulResidualPool]
    task047_artifact: Any
    games_resid_sd: float
    avg_resid_sd: float
    train_max_origin: int
    n_fit: int
    n_cal: int
    artifact_id: str | None = None


def seed_for(player_key: str, origin_year: int, lead: int) -> int:
    digest = hashlib.sha256(
        f"{SEED_PREFIX}|{player_key}|{origin_year}|{lead}".encode()
    ).digest()
    return int.from_bytes(digest[:8], "little") & 0xFFFFFFFF


def broad_position(value: Any) -> str:
    text = str(value or "UNK").strip().upper()
    for token in ("RUC", "KPD", "KPF", "DEF", "FWD", "MID"):
        if token in text:
            return token
    return "UNK"


def add_joint_features(rows: pd.DataFrame) -> pd.DataFrame:
    out = add_ceiling_evidence_feature(rows)
    out = model_artifacts_zero_history.add_zero_history_features(out)
    return out


def make_joint_preprocessor() -> ColumnTransformer:
    numeric = list(BASE_NUM) + ["career_best_x_evidence", "zero_history_flag"]
    categorical = list(BASE_CAT) + ["zero_history_tenure", "zero_history_state"]
    return ColumnTransformer(
        [
            (
                "n",
                Pipeline(
                    [
                        ("i", SimpleImputer(strategy="median")),
                        ("s", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "c",
                Pipeline(
                    [
                        ("i", SimpleImputer(strategy="most_frequent")),
                        ("o", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )


def state_target(rows: pd.DataFrame, lead: int) -> np.ndarray:
    games = pd.to_numeric(rows[f"l{lead}_games"], errors="coerce")
    points = pd.to_numeric(rows[f"l{lead}_points"], errors="coerce")
    if games.isna().any() or points.isna().any():
        raise ValueError(f"lead {lead} contains non-finite state targets")
    zero = games.eq(0) & points.eq(0)
    short = games.between(1, 5, inclusive="both") & points.gt(0)
    meaningful = games.ge(6)
    valid = zero | short | meaningful
    if not valid.all():
        sample = rows.loc[~valid, ["key", "origin_year", f"l{lead}_games", f"l{lead}_points"]].head(5)
        raise ValueError(
            f"lead {lead} contains unsupported season-state rows: {sample.to_dict('records')}"
        )
    return np.select([zero, short, meaningful], [0, 1, 2]).astype(int)


def _choose_min_score(scores: dict[float, float]) -> float:
    if not scores:
        raise ValueError("selection scores must not be empty")
    return float(min(scores, key=lambda value: (scores[value], value)))


def _aligned_state_probabilities(model: LogisticRegression, x: Any) -> np.ndarray:
    raw = model.predict_proba(x)
    out = np.zeros((raw.shape[0], 3), dtype=float)
    for index, label in enumerate(model.classes_):
        out[:, int(label)] = raw[:, index]
    out = np.clip(out, 1e-9, 1.0)
    out /= out.sum(axis=1, keepdims=True)
    return out


def _build_short_pools(
    calibration: pd.DataFrame,
    lead: int,
    residuals: np.ndarray,
) -> dict[str, ShortResidualPool]:
    games = calibration[f"l{lead}_games"].to_numpy(float)
    positions = calibration["position"].map(broad_position).to_numpy(str)
    if len(games) < MIN_RESIDUAL_ROWS:
        raise ValueError(
            f"lead {lead} has only {len(games)} short-season calibration residuals; "
            f"requires at least {MIN_RESIDUAL_ROWS}"
        )
    pools: dict[str, ShortResidualPool] = {
        ALL_POOL: ShortResidualPool(games.copy(), residuals.copy())
    }
    for position in sorted(set(positions)):
        mask = positions == position
        if int(mask.sum()) >= POSITION_POOL_MIN_ROWS:
            pools[position] = ShortResidualPool(games[mask].copy(), residuals[mask].copy())
    return pools


def _build_meaningful_pools(
    calibration: pd.DataFrame,
    lead: int,
    games_residuals: np.ndarray,
    avg_residuals: np.ndarray,
) -> dict[str, MeaningfulResidualPool]:
    positions = calibration["position"].map(broad_position).to_numpy(str)
    if len(games_residuals) < MIN_RESIDUAL_ROWS:
        raise ValueError(
            f"lead {lead} has only {len(games_residuals)} meaningful calibration residuals; "
            f"requires at least {MIN_RESIDUAL_ROWS}"
        )
    pools: dict[str, MeaningfulResidualPool] = {
        ALL_POOL: MeaningfulResidualPool(games_residuals.copy(), avg_residuals.copy())
    }
    for position in sorted(set(positions)):
        mask = positions == position
        if int(mask.sum()) >= POSITION_POOL_MIN_ROWS:
            pools[position] = MeaningfulResidualPool(
                games_residuals[mask].copy(), avg_residuals[mask].copy()
            )
    return pools


def train_lead(train: pd.DataFrame, lead: int) -> JointSeasonArtifact:
    fit, calibration = model_artifacts.split_temporal(train, lead)
    if fit.empty or calibration.empty:
        raise ValueError(f"lead {lead} temporal split is empty")

    fit_features = add_joint_features(fit)
    calibration_features = add_joint_features(calibration)
    preprocessor = make_joint_preprocessor()
    x_fit = preprocessor.fit_transform(fit_features)
    x_cal = preprocessor.transform(calibration_features)

    y_fit = state_target(fit, lead)
    y_cal = state_target(calibration, lead)
    if set(np.unique(y_fit)) != {0, 1, 2}:
        raise ValueError(f"lead {lead} state fit rows do not contain all three states")

    state_scores: dict[float, float] = {}
    for c_value in STATE_C_GRID:
        candidate = LogisticRegression(
            C=float(c_value),
            solver="lbfgs",
            penalty="l2",
            max_iter=1000,
            tol=1e-5,
        ).fit(x_fit, y_fit)
        state_scores[float(c_value)] = float(
            log_loss(y_cal, _aligned_state_probabilities(candidate, x_cal), labels=[0, 1, 2])
        )
    selected_c = _choose_min_score(state_scores)
    state_model = LogisticRegression(
        C=selected_c,
        solver="lbfgs",
        penalty="l2",
        max_iter=1000,
        tol=1e-5,
    ).fit(x_fit, y_fit)
    if int(np.max(state_model.n_iter_)) >= 1000:
        raise RuntimeError(f"lead {lead} state model reached max_iter")

    fit_games = fit[f"l{lead}_games"].to_numpy(float)
    fit_points = fit[f"l{lead}_points"].to_numpy(float)
    cal_games = calibration[f"l{lead}_games"].to_numpy(float)
    cal_points = calibration[f"l{lead}_points"].to_numpy(float)
    short_fit = (fit_games >= 1) & (fit_games <= 5) & (fit_points > 0)
    short_cal = (cal_games >= 1) & (cal_games <= 5) & (cal_points > 0)
    if int(short_fit.sum()) < MIN_RESIDUAL_ROWS or int(short_cal.sum()) < MIN_RESIDUAL_ROWS:
        raise ValueError(
            f"lead {lead} lacks short-season fit/calibration support: "
            f"fit={int(short_fit.sum())} calibration={int(short_cal.sum())}"
        )

    y_short_fit_log = np.log(fit_points[short_fit] / fit_games[short_fit])
    y_short_cal_rate = cal_points[short_cal] / cal_games[short_cal]
    short_alpha_scores: dict[float, float] = {}
    for alpha in RIDGE_ALPHA_GRID:
        candidate = Ridge(alpha=float(alpha)).fit(x_fit[short_fit], y_short_fit_log)
        predicted_rate = np.exp(
            np.clip(candidate.predict(x_cal[short_cal]), np.log(1e-6), np.log(145.0))
        )
        short_alpha_scores[float(alpha)] = float(
            np.mean(np.abs(predicted_rate - y_short_cal_rate))
        )
    selected_short_alpha = _choose_min_score(short_alpha_scores)
    short_model = Ridge(alpha=selected_short_alpha).fit(x_fit[short_fit], y_short_fit_log)
    short_log_prediction = short_model.predict(x_cal[short_cal])
    short_log_actual = np.log(y_short_cal_rate)
    short_residuals = short_log_actual - short_log_prediction
    short_calibration = calibration.loc[short_cal].copy()
    short_pools = _build_short_pools(short_calibration, lead, short_residuals)

    task047_artifact = train_task047(train, lead)
    task047_calibration = predict_task047(task047_artifact, calibration)
    meaningful_cal = cal_games >= 6
    if int(meaningful_cal.sum()) < MIN_RESIDUAL_ROWS:
        raise ValueError(
            f"lead {lead} lacks meaningful calibration support: {int(meaningful_cal.sum())}"
        )
    games_residuals = (
        cal_games[meaningful_cal]
        - task047_calibration.loc[meaningful_cal, "cond_games"].to_numpy(float)
    )
    avg_residuals = (
        calibration.loc[meaningful_cal, f"l{lead}_avg"].to_numpy(float)
        - task047_calibration.loc[meaningful_cal, "cond_avg"].to_numpy(float)
    )
    meaningful_pools = _build_meaningful_pools(
        calibration.loc[meaningful_cal].copy(),
        lead,
        games_residuals,
        avg_residuals,
    )

    return JointSeasonArtifact(
        lead=lead,
        state_preprocessor=preprocessor,
        state_model=state_model,
        selected_state_c=selected_c,
        state_c_scores=state_scores,
        short_rate_model=short_model,
        selected_short_alpha=selected_short_alpha,
        short_alpha_scores=short_alpha_scores,
        short_pools=short_pools,
        meaningful_pools=meaningful_pools,
        task047_artifact=task047_artifact,
        games_resid_sd=float(max(np.std(games_residuals, ddof=1), 1.0)),
        avg_resid_sd=float(max(np.std(avg_residuals, ddof=1), 3.0)),
        train_max_origin=int(train.origin_year.max()),
        n_fit=int(len(fit)),
        n_cal=int(len(calibration)),
    )


def allocate_state_counts(probabilities: np.ndarray, sample_count: int) -> np.ndarray:
    probabilities = np.asarray(probabilities, dtype=float)
    if probabilities.shape != (3,) or not np.isfinite(probabilities).all():
        raise ValueError("state probabilities must be a finite length-three vector")
    if (probabilities < 0).any() or probabilities.sum() <= 0:
        raise ValueError("state probabilities must be non-negative with positive mass")
    probabilities = probabilities / probabilities.sum()
    raw = probabilities * int(sample_count)
    counts = np.floor(raw).astype(int)
    remaining = int(sample_count - counts.sum())
    if remaining:
        order = np.argsort(-(raw - counts))
        counts[order[:remaining]] += 1
    for state in np.flatnonzero((probabilities > 0) & (counts == 0)):
        donors = np.argsort(-counts)
        donor = next((int(value) for value in donors if value != state and counts[value] > 1), None)
        if donor is None:
            raise ValueError("cannot allocate positive support to every state")
        counts[donor] -= 1
        counts[state] += 1
    if int(counts.sum()) != int(sample_count) or (counts <= 0).any():
        raise ValueError(f"invalid state allocation: {counts.tolist()}")
    return counts


def _select_short_pool(artifact: JointSeasonArtifact, position: Any) -> tuple[str, ShortResidualPool]:
    key = broad_position(position)
    if key not in artifact.short_pools:
        key = ALL_POOL
    return key, artifact.short_pools[key]


def _select_meaningful_pool(
    artifact: JointSeasonArtifact, position: Any
) -> tuple[str, MeaningfulResidualPool]:
    key = broad_position(position)
    if key not in artifact.meaningful_pools:
        key = ALL_POOL
    return key, artifact.meaningful_pools[key]


def predict_with_diagnostics(
    artifact: JointSeasonArtifact,
    rows: pd.DataFrame,
    sample_count: int = SAMPLE_COUNT,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if sample_count < 100:
        raise ValueError("sample_count must be at least 100")
    features = add_joint_features(rows)
    x = artifact.state_preprocessor.transform(features)
    state_probabilities = _aligned_state_probabilities(artifact.state_model, x)
    short_log_means = artifact.short_rate_model.predict(x)
    task047 = predict_task047(artifact.task047_artifact, rows)

    prediction_rows: list[dict[str, float | str]] = []
    diagnostic_rows: list[dict[str, float | int | str]] = []
    for row_index, (_, row) in enumerate(rows.iterrows()):
        probabilities = state_probabilities[row_index]
        counts = allocate_state_counts(probabilities, sample_count)
        zero_count, short_count, meaningful_count = map(int, counts)
        rng = np.random.default_rng(
            seed_for(str(row["player_key"]), int(row["origin_year"]), int(row["lead"]))
        )

        points = np.zeros(sample_count, dtype=float)
        games = np.zeros(sample_count, dtype=float)
        averages = np.zeros(sample_count, dtype=float)
        states = np.zeros(sample_count, dtype=int)

        short_key, short_pool = _select_short_pool(artifact, row.get("position"))
        short_indices = rng.integers(0, len(short_pool.games), size=short_count)
        short_games = short_pool.games[short_indices].astype(float)
        short_log_rates = (
            float(short_log_means[row_index])
            + short_pool.log_rate_residuals[short_indices]
        )
        short_rates = np.exp(
            np.clip(short_log_rates, np.log(1e-6), np.log(145.0))
        )
        short_start = zero_count
        short_end = short_start + short_count
        states[short_start:short_end] = 1
        games[short_start:short_end] = short_games
        averages[short_start:short_end] = short_rates
        points[short_start:short_end] = short_games * short_rates

        meaningful_key, meaningful_pool = _select_meaningful_pool(
            artifact, row.get("position")
        )
        meaningful_indices = rng.integers(
            0, len(meaningful_pool.games_residuals), size=meaningful_count
        )
        meaningful_games = np.clip(
            np.rint(
                float(task047.iloc[row_index]["cond_games"])
                + meaningful_pool.games_residuals[meaningful_indices]
            ),
            6.0,
            23.0,
        )
        meaningful_avg = np.clip(
            float(task047.iloc[row_index]["cond_avg"])
            + meaningful_pool.avg_residuals[meaningful_indices],
            1e-6,
            145.0,
        )
        meaningful_start = short_end
        states[meaningful_start:] = 2
        games[meaningful_start:] = meaningful_games
        averages[meaningful_start:] = meaningful_avg
        points[meaningful_start:] = meaningful_games * meaningful_avg

        quantiles = np.maximum.accumulate(
            np.maximum(0.0, np.quantile(points, QUANTILE_LEVELS))
        )
        prediction: dict[str, float | str] = {
            "p_meaningful": meaningful_count / sample_count,
            "cond_games": float(meaningful_games.mean()),
            "cond_avg": float(meaningful_avg.mean()),
            "exp_games": float(games.mean()),
            "exp_points": float(points.mean()),
            "model_id": "vnext_task050_joint_season_distribution",
        }
        for threshold in TH:
            prediction[f"p{threshold}"] = float(
                np.mean((states == 2) & (averages >= threshold))
            )
        for column, value in zip(QUANTILE_COLUMNS, quantiles, strict=True):
            prediction[column] = float(value)
        prediction_rows.append(prediction)

        diagnostic_rows.append(
            {
                "player_key": str(row["player_key"]),
                "origin_year": int(row["origin_year"]),
                "lead": int(row["lead"]),
                "position_pool": broad_position(row.get("position")),
                "short_pool": short_key,
                "meaningful_pool": meaningful_key,
                "state_model_p_zero": float(probabilities[0]),
                "state_model_p_short": float(probabilities[1]),
                "state_model_p_meaningful": float(probabilities[2]),
                "draw_p_zero": zero_count / sample_count,
                "draw_p_short": short_count / sample_count,
                "draw_p_meaningful": meaningful_count / sample_count,
                "zero_draw_count": zero_count,
                "short_draw_count": short_count,
                "meaningful_draw_count": meaningful_count,
                "short_games_min": float(short_games.min()),
                "short_games_max": float(short_games.max()),
                "short_points_min": float((short_games * short_rates).min()),
                "short_points_max": float((short_games * short_rates).max()),
                "meaningful_games_min": float(meaningful_games.min()),
                "meaningful_games_max": float(meaningful_games.max()),
                "draw_exp_games": float(games.mean()),
                "draw_exp_points": float(points.mean()),
                "threshold_monotonic": int(
                    all(
                        prediction[f"p{left}"] >= prediction[f"p{right}"]
                        for left, right in zip(TH[:-1], TH[1:])
                    )
                ),
            }
        )

    return pd.DataFrame(prediction_rows, index=rows.index), pd.DataFrame(diagnostic_rows)


def predict(
    artifact: JointSeasonArtifact,
    rows: pd.DataFrame,
    sample_count: int = SAMPLE_COUNT,
) -> pd.DataFrame:
    prediction, _ = predict_with_diagnostics(artifact, rows, sample_count=sample_count)
    return prediction
