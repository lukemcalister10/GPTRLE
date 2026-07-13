"""Locked TASK-050 audit for the coherent joint season distribution."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "task-050-joint-season-outcome-distribution"
KEY = ["player_key", "origin_year", "lead"]
QLEVELS = {
    "points_q10": 0.10,
    "points_q25": 0.25,
    "points_q50": 0.50,
    "points_q75": 0.75,
    "points_q90": 0.90,
    "points_q97": 0.97,
}
QCOLS = list(QLEVELS)
THRESHOLDS = (80, 90, 100, 110, 120)
THRESHOLD_COLS = [f"p_avg_ge_{value}" for value in THRESHOLDS]
EXPECTED_ROWS = 20094
EXPECTED_SNAPSHOTS = 5622
EXPECTED_FOLDS = 25
BOOTSTRAP_SEED = 50050
BOOTSTRAP_REPLICATIONS = 2000


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(path: Path, label: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"missing mandatory {label}: {path}")
    return path


def load_predictions(path: Path, model: str) -> pd.DataFrame:
    required = KEY + [
        "p_meaningful",
        "cond_games",
        "cond_avg",
        "exp_games",
        "exp_points",
        *THRESHOLD_COLS,
        *QCOLS,
    ]
    frame = pd.read_csv(path)
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{path} missing prediction columns: {missing}")
    if frame.duplicated(KEY).any():
        raise ValueError(f"{path} contains duplicate prediction keys")
    out = frame[required].copy()
    out["model"] = model
    return out


def artifact_checks(path: Path) -> dict[str, Any]:
    directory = path.parent
    manifest_path = require(directory / "prediction_manifest.json", "prediction manifest")
    failure_path = require(directory / "fold_failures.csv", "fold failures")
    manifest = json.loads(manifest_path.read_text())
    failures = pd.read_csv(failure_path)
    return {
        "directory": str(directory.relative_to(ROOT)),
        "manifest_sha256": sha256_path(manifest_path),
        "prediction_sha256": sha256_path(path),
        "prediction_rows": int(manifest.get("prediction_rows", -1)),
        "snapshot_rows": int(manifest.get("included_snapshot_rows", -1)),
        "target_failure_rows": int(manifest.get("target_failure_rows", -1)),
        "fold_failure_rows": int(len(failures)),
        "sample_count": manifest.get("sample_count"),
        "seed_contract": manifest.get("seed_contract"),
        "partial_season_data_used": manifest.get("partial_season_data_used"),
        "row_level_moment_forcing": manifest.get("quantile_method", {}).get(
            "row_level_moment_forcing"
        ),
    }


def pinball(y: pd.Series, q: pd.Series, tau: float) -> pd.Series:
    diff = y.astype(float) - q.astype(float)
    return np.maximum(tau * diff, (tau - 1.0) * diff)


def weighted_interval_score(frame: pd.DataFrame) -> pd.Series:
    y = frame["points"].astype(float)
    median = frame["points_q50"].astype(float)
    numerator = 0.5 * (y - median).abs()
    denominator = 0.5
    for alpha, lower, upper in [
        (0.50, "points_q25", "points_q75"),
        (0.20, "points_q10", "points_q90"),
    ]:
        low = frame[lower].astype(float)
        high = frame[upper].astype(float)
        interval_score = (
            (high - low)
            + (2.0 / alpha) * (low - y).clip(lower=0.0)
            + (2.0 / alpha) * (y - high).clip(lower=0.0)
        )
        weight = alpha / 2.0
        numerator = numerator + weight * interval_score
        denominator += weight
    return numerator / denominator


def age_band(values: pd.Series) -> pd.Series:
    age = pd.to_numeric(values, errors="coerce")
    return pd.cut(
        age,
        bins=[-np.inf, 21, 24, 27, 30, np.inf],
        labels=["21_or_under", "22_24", "25_27", "28_30", "31_plus"],
    ).astype(str)


def tenure_band(values: pd.Series) -> pd.Series:
    tenure = pd.to_numeric(values, errors="coerce").fillna(0)
    return np.select(
        [
            tenure.eq(0),
            tenure.eq(1),
            tenure.eq(2),
            tenure.eq(3),
            tenure.between(4, 5, inclusive="both"),
        ],
        ["0", "1", "2", "3", "4_5"],
        default="6_plus",
    )


def pick_band(values: pd.Series) -> pd.Series:
    pick = pd.to_numeric(values, errors="coerce").fillna(999)
    return np.select(
        [
            pick.between(1, 5),
            pick.between(6, 10),
            pick.between(11, 20),
            pick.between(21, 40),
            pick.between(41, 60),
        ],
        ["1_5", "6_10", "11_20", "21_40", "41_60"],
        default="61_plus_or_undrafted",
    )


def prior_history(values: pd.Series) -> pd.Series:
    games = pd.to_numeric(values, errors="coerce").fillna(0)
    return np.select(
        [games.eq(0), games.lt(50)],
        ["zero_prior_games", "under_50_prior_games"],
        default="50_plus_prior_games",
    )


def realised_state(games: pd.Series, points: pd.Series) -> np.ndarray:
    g = pd.to_numeric(games, errors="coerce")
    p = pd.to_numeric(points, errors="coerce")
    zero = g.eq(0) & p.eq(0)
    short = g.between(1, 5, inclusive="both") & p.gt(0)
    meaningful = g.ge(6)
    valid = zero | short | meaningful
    if not valid.all():
        raise ValueError("locked targets contain unsupported realised state rows")
    return np.select([zero, short, meaningful], [0, 1, 2]).astype(int)


def add_slices(
    joined: pd.DataFrame, features: pd.DataFrame
) -> pd.DataFrame:
    feature_columns = [
        column
        for column in [
            "key",
            "origin_year",
            "position",
            "total_games",
            "age",
            "tenure",
            "draft_type",
            "pick",
        ]
        if column in features.columns
    ]
    feat = features[feature_columns].rename(columns={"key": "player_key"})
    out = joined.merge(
        feat,
        on=["player_key", "origin_year"],
        how="left",
        validate="many_to_one",
    )
    out["broad_position"] = out.get(
        "position", pd.Series("unknown", index=out.index)
    ).fillna("unknown").astype(str)
    out["prior_history"] = prior_history(
        out.get("total_games", pd.Series(0, index=out.index))
    )
    out["age_band"] = age_band(out.get("age", pd.Series(np.nan, index=out.index)))
    out["tenure_band"] = tenure_band(
        out.get("tenure", pd.Series(0, index=out.index))
    )
    out["draft_type_group"] = out.get(
        "draft_type", pd.Series("unknown", index=out.index)
    ).fillna("unknown").astype(str)
    out["pick_band"] = pick_band(
        out.get("pick", pd.Series(np.nan, index=out.index))
    )
    return out


def point_metrics(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = frame.groupby(groups, dropna=False) if groups else [((), frame)]
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        common = dict(zip(groups, keys))
        for model, model_rows in group.groupby("model"):
            meaningful = model_rows["meaningful"].astype(bool)
            record: dict[str, Any] = {
                **common,
                "model": model,
                "n": int(len(model_rows)),
                "games_mae": float(
                    np.mean(
                        np.abs(
                            model_rows["games"].astype(float)
                            - model_rows["exp_games"].astype(float)
                        )
                    )
                ),
                "conditional_avg_mae": float(
                    np.mean(
                        np.abs(
                            model_rows.loc[meaningful, "avg"].astype(float)
                            - model_rows.loc[meaningful, "cond_avg"].astype(float)
                        )
                    )
                ),
                "total_points_mae": float(
                    np.mean(
                        np.abs(
                            model_rows["points"].astype(float)
                            - model_rows["exp_points"].astype(float)
                        )
                    )
                ),
                "brier_meaningful": float(
                    brier_score_loss(
                        model_rows["meaningful"], model_rows["p_meaningful"]
                    )
                ),
                "weighted_interval_score": float(
                    weighted_interval_score(model_rows).mean()
                ),
            }
            for threshold in THRESHOLDS:
                record[f"brier_{threshold}"] = float(
                    brier_score_loss(
                        model_rows[f"avg_ge_{threshold}"],
                        model_rows[f"p_avg_ge_{threshold}"],
                    )
                )
            rows.append(record)
    return pd.DataFrame(rows)


def pinball_summary(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = frame.groupby(groups, dropna=False) if groups else [((), frame)]
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        common = dict(zip(groups, keys))
        for model, model_rows in group.groupby("model"):
            for column, tau in QLEVELS.items():
                rows.append(
                    {
                        **common,
                        "model": model,
                        "quantile": column,
                        "tau": tau,
                        "n": int(len(model_rows)),
                        "pinball_loss": float(
                            pinball(model_rows.points, model_rows[column], tau).mean()
                        ),
                    }
                )
    return pd.DataFrame(rows)


def comparison_table(
    summary: pd.DataFrame, groups: list[str], value: str
) -> pd.DataFrame:
    index = groups + [column for column in ["quantile", "tau"] if column in summary.columns]
    pivot = summary.pivot_table(index=index, columns="model", values=value).reset_index()
    pivot["abs_diff_task050_minus_task047"] = pivot["task050"] - pivot["task047"]
    pivot["pct_diff_task050_minus_task047"] = np.where(
        pivot["task047"] != 0,
        pivot["abs_diff_task050_minus_task047"] / pivot["task047"],
        np.nan,
    )
    return pivot


def quantile_calibration(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = frame.groupby(groups, dropna=False) if groups else [((), frame)]
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        common = dict(zip(groups, keys))
        for model, model_rows in group.groupby("model"):
            for column, tau in QLEVELS.items():
                empirical = float(
                    (model_rows.points.astype(float) <= model_rows[column].astype(float)).mean()
                )
                rows.append(
                    {
                        **common,
                        "model": model,
                        "quantile": column,
                        "tau": tau,
                        "n": int(len(model_rows)),
                        "empirical": empirical,
                        "signed_error": empirical - tau,
                        "absolute_error": abs(empirical - tau),
                    }
                )
    return pd.DataFrame(rows)


def interval_coverage(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    intervals = [
        ("q25_q75", "points_q25", "points_q75", 0.50),
        ("q10_q90", "points_q10", "points_q90", 0.80),
        ("q10_q97", "points_q10", "points_q97", 0.87),
    ]
    rows: list[dict[str, Any]] = []
    grouped = frame.groupby(groups, dropna=False) if groups else [((), frame)]
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        common = dict(zip(groups, keys))
        for model, model_rows in group.groupby("model"):
            y = model_rows.points.astype(float)
            for name, lower, upper, nominal in intervals:
                low = model_rows[lower].astype(float)
                high = model_rows[upper].astype(float)
                coverage = float(((y >= low) & (y <= high)).mean())
                rows.append(
                    {
                        **common,
                        "model": model,
                        "interval": name,
                        "nominal": nominal,
                        "n": int(len(model_rows)),
                        "coverage": coverage,
                        "coverage_error": coverage - nominal,
                        "absolute_coverage_error": abs(coverage - nominal),
                        "mean_width": float((high - low).mean()),
                    }
                )
    return pd.DataFrame(rows)


def bootstrap_metrics(
    wide: pd.DataFrame,
    reps: int = BOOTSTRAP_REPLICATIONS,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    row_differences = pd.DataFrame({"player_key": wide.player_key})
    quantile_columns: list[str] = []
    for column, tau in QLEVELS.items():
        name = column
        row_differences[name] = pinball(
            wide.points, wide[f"{column}_task050"], tau
        ) - pinball(wide.points, wide[f"{column}_task047"], tau)
        quantile_columns.append(name)
    row_differences["primary_mean_pinball"] = row_differences[
        quantile_columns
    ].mean(axis=1)
    row_differences["weighted_interval_score"] = weighted_interval_score(
        wide.rename(
            columns={f"{column}_task050": column for column in QCOLS}
        )
    ) - weighted_interval_score(
        wide.rename(
            columns={f"{column}_task047": column for column in QCOLS}
        )
    )
    metrics = ["primary_mean_pinball", "weighted_interval_score", *QCOLS]
    observed = {metric: float(row_differences[metric].mean()) for metric in metrics}
    blocks = row_differences.groupby("player_key").agg(
        {**{metric: "sum" for metric in metrics}, "player_key": "size"}
    ).rename(columns={"player_key": "row_count"})
    players = blocks.index.to_numpy()
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for metric in metrics:
        draws = np.empty(reps, dtype=float)
        for index in range(reps):
            sample = rng.choice(players, size=len(players), replace=True)
            selected = blocks.loc[sample]
            draws[index] = float(selected[metric].sum() / selected.row_count.sum())
        rows.append(
            {
                "metric": metric,
                "observed_diff_task050_minus_task047": observed[metric],
                "bootstrap_median": float(np.median(draws)),
                "ci_low": float(np.quantile(draws, 0.025)),
                "ci_high": float(np.quantile(draws, 0.975)),
                "seed": seed,
                "replications": reps,
            }
        )
    confidence = pd.DataFrame(rows)
    invariant = pd.DataFrame(
        {
            "metric": metrics,
            "pooled_difference": [observed[metric] for metric in metrics],
            "bootstrap_observed_difference": [observed[metric] for metric in metrics],
        }
    )
    invariant["absolute_delta"] = (
        invariant.pooled_difference - invariant.bootstrap_observed_difference
    ).abs()
    return confidence, invariant


def state_tables(
    base: pd.DataFrame,
    candidate: pd.DataFrame,
    targets: pd.DataFrame,
    diagnostics: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    actual = targets[KEY + ["games", "points"]].copy()
    actual["state"] = realised_state(actual.games, actual.points)
    base_state = base[KEY + ["p_meaningful"]].merge(actual, on=KEY)
    candidate_state = candidate[KEY + ["p_meaningful"]].merge(
        diagnostics[
            KEY
            + [
                "draw_p_zero",
                "draw_p_short",
                "draw_p_meaningful",
            ]
        ],
        on=KEY,
        validate="one_to_one",
    ).merge(actual, on=KEY)

    epsilon = 1e-9
    base_prob = np.column_stack(
        [
            1.0 - base_state.p_meaningful.to_numpy(float),
            np.zeros(len(base_state), dtype=float),
            base_state.p_meaningful.to_numpy(float),
        ]
    )
    base_prob = np.clip(base_prob, epsilon, 1.0)
    base_prob /= base_prob.sum(axis=1, keepdims=True)
    candidate_prob = candidate_state[
        ["draw_p_zero", "draw_p_short", "draw_p_meaningful"]
    ].to_numpy(float)
    candidate_prob = np.clip(candidate_prob, epsilon, 1.0)
    candidate_prob /= candidate_prob.sum(axis=1, keepdims=True)

    metric_rows: list[dict[str, Any]] = []
    reliability_rows: list[dict[str, Any]] = []
    for model, states, probabilities in [
        ("task047", base_state.state.to_numpy(int), base_prob),
        ("task050", candidate_state.state.to_numpy(int), candidate_prob),
    ]:
        one_hot = np.eye(3)[states]
        metric: dict[str, Any] = {
            "model": model,
            "n": int(len(states)),
            "multiclass_brier": float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1))),
            "multiclass_log_loss": float(log_loss(states, probabilities, labels=[0, 1, 2])),
        }
        state_errors: list[float] = []
        for state_index, state_name in enumerate(["zero", "short", "meaningful"]):
            actual_binary = (states == state_index).astype(float)
            metric[f"brier_{state_name}"] = float(
                np.mean((probabilities[:, state_index] - actual_binary) ** 2)
            )
            bins = pd.cut(
                probabilities[:, state_index],
                bins=np.linspace(0.0, 1.0, 11),
                include_lowest=True,
                duplicates="drop",
            )
            temp = pd.DataFrame(
                {
                    "probability": probabilities[:, state_index],
                    "actual": actual_binary,
                    "bin": bins,
                }
            )
            weighted_error = 0.0
            for bin_value, group in temp.groupby("bin", observed=True):
                predicted = float(group.probability.mean())
                realised = float(group.actual.mean())
                weighted_error += len(group) * abs(predicted - realised)
                reliability_rows.append(
                    {
                        "model": model,
                        "state": state_name,
                        "bin": str(bin_value),
                        "n": int(len(group)),
                        "predicted": predicted,
                        "realised": realised,
                        "absolute_error": abs(predicted - realised),
                    }
                )
            state_errors.append(weighted_error / len(temp))
        metric["mean_absolute_state_calibration_error"] = float(np.mean(state_errors))
        metric_rows.append(metric)
    return pd.DataFrame(metric_rows), pd.DataFrame(reliability_rows)


def subgroup_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for subgroup_type in [
        "broad_position",
        "prior_history",
        "age_band",
        "tenure_band",
        "draft_type_group",
        "pick_band",
    ]:
        for subgroup, group in frame.groupby(subgroup_type, dropna=False):
            for model, model_rows in group.groupby("model"):
                rows.append(
                    {
                        "subgroup_type": subgroup_type,
                        "subgroup": str(subgroup),
                        "model": model,
                        "n": int(len(model_rows)),
                        "weighted_interval_score": float(
                            weighted_interval_score(model_rows).mean()
                        ),
                        "total_points_mae": float(
                            np.mean(
                                np.abs(
                                    model_rows.points.astype(float)
                                    - model_rows.exp_points.astype(float)
                                )
                            )
                        ),
                    }
                )
    summary = pd.DataFrame(rows)
    pivot = summary.pivot_table(
        index=["subgroup_type", "subgroup", "n"],
        columns="model",
        values=["weighted_interval_score", "total_points_mae"],
    ).reset_index()
    pivot.columns = [
        "_".join([str(part) for part in column if str(part)])
        if isinstance(column, tuple)
        else str(column)
        for column in pivot.columns
    ]
    for metric in ["weighted_interval_score", "total_points_mae"]:
        base = pivot[f"{metric}_task047"]
        candidate = pivot[f"{metric}_task050"]
        pivot[f"{metric}_pct_diff_task050_minus_task047"] = np.where(
            base != 0, (candidate - base) / base, np.nan
        )
    return pivot


def build_audit(
    baseline: pd.DataFrame,
    candidate: pd.DataFrame,
    targets: pd.DataFrame,
    features: pd.DataFrame,
    diagnostics: pd.DataFrame,
    baseline_checks: dict[str, Any],
    candidate_checks: dict[str, Any],
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    target_columns = KEY + [
        "games",
        "avg",
        "points",
        "meaningful",
        *[f"avg_ge_{value}" for value in THRESHOLDS],
    ]
    missing_targets = sorted(set(target_columns) - set(targets.columns))
    if missing_targets:
        raise ValueError(f"targets missing columns: {missing_targets}")
    target = targets[target_columns].copy()
    expected_keys = target[KEY].sort_values(KEY).reset_index(drop=True)
    for name, frame in [("task047", baseline), ("task050", candidate), ("diagnostics", diagnostics)]:
        got = frame[KEY].sort_values(KEY).reset_index(drop=True)
        if not got.equals(expected_keys):
            raise ValueError(f"{name} keys differ from locked targets")

    long = pd.concat([baseline, candidate], ignore_index=True).merge(
        target, on=KEY, validate="many_to_one"
    )
    long = add_slices(long, features)
    point_overall = point_metrics(long, [])
    point_by_lead = point_metrics(long, ["lead"])
    pin_overall_raw = pinball_summary(long, [])
    pin_by_lead_raw = pinball_summary(long, ["lead"])
    pin_by_fold_raw = pinball_summary(long, ["origin_year", "lead"])
    primary_pinball = (
        pin_overall_raw.groupby("model", as_index=False)
        .pinball_loss.mean()
        .rename(columns={"pinball_loss": "primary_mean_pinball"})
    )
    pin_overall = comparison_table(pin_overall_raw, [], "pinball_loss")
    pin_by_lead = comparison_table(pin_by_lead_raw, ["lead"], "pinball_loss")
    pin_by_fold = comparison_table(
        pin_by_fold_raw, ["origin_year", "lead"], "pinball_loss"
    )
    calibration_overall = quantile_calibration(long, [])
    calibration_by_lead = quantile_calibration(long, ["lead"])
    coverage_overall = interval_coverage(long, [])
    coverage_by_lead = interval_coverage(long, ["lead"])
    coverage_by_position = interval_coverage(long, ["broad_position"])
    coverage_by_history = interval_coverage(long, ["prior_history"])
    subgroups = subgroup_metrics(long)

    wide = baseline.merge(candidate, on=KEY, suffixes=("_task047", "_task050")).merge(
        target, on=KEY
    )
    bootstrap, bootstrap_invariant = bootstrap_metrics(wide)
    state_metric, state_reliability = state_tables(
        baseline, candidate, target, diagnostics
    )

    candidate_values = candidate[QCOLS].to_numpy(float)
    threshold_values = candidate[THRESHOLD_COLS].to_numpy(float)
    reconciliation = candidate[KEY + ["p_meaningful", "exp_games", "exp_points"]].merge(
        diagnostics[
            KEY
            + [
                "draw_p_meaningful",
                "draw_exp_games",
                "draw_exp_points",
                "short_games_min",
                "short_games_max",
                "short_points_min",
                "meaningful_games_min",
                "meaningful_games_max",
                "threshold_monotonic",
            ]
        ],
        on=KEY,
        validate="one_to_one",
    )
    reconciliation["p_meaningful_abs_delta"] = (
        reconciliation.p_meaningful - reconciliation.draw_p_meaningful
    ).abs()
    reconciliation["exp_games_abs_delta"] = (
        reconciliation.exp_games - reconciliation.draw_exp_games
    ).abs()
    reconciliation["exp_points_abs_delta"] = (
        reconciliation.exp_points - reconciliation.draw_exp_points
    ).abs()

    integrity_rows = [
        ("row_count_per_model", len(baseline) == EXPECTED_ROWS and len(candidate) == EXPECTED_ROWS, f"task047={len(baseline)} task050={len(candidate)}"),
        ("player_origin_snapshots", target[KEY[:2]].drop_duplicates().shape[0] == EXPECTED_SNAPSHOTS, str(target[KEY[:2]].drop_duplicates().shape[0])),
        ("legal_folds", target[["origin_year", "lead"]].drop_duplicates().shape[0] == EXPECTED_FOLDS, str(target[["origin_year", "lead"]].drop_duplicates().shape[0])),
        ("target_and_fold_failures_zero", baseline_checks["target_failure_rows"] == 0 and candidate_checks["target_failure_rows"] == 0 and baseline_checks["fold_failure_rows"] == 0 and candidate_checks["fold_failure_rows"] == 0, json.dumps({"task047": baseline_checks, "task050": candidate_checks}, sort_keys=True)),
        ("task050_sample_count", candidate_checks["sample_count"] == 4096, str(candidate_checks["sample_count"])),
        ("task050_seed_contract", candidate_checks["seed_contract"] == "sha256(TASK-050|player_key|origin_year|lead)", str(candidate_checks["seed_contract"])),
        ("partial_season_excluded", candidate_checks["partial_season_data_used"] is False, str(candidate_checks["partial_season_data_used"])),
        ("no_row_level_moment_forcing", candidate_checks["row_level_moment_forcing"] is False, str(candidate_checks["row_level_moment_forcing"])),
        ("quantiles_non_negative", bool((candidate_values >= -1e-12).all()), str(float(candidate_values.min()))),
        ("quantiles_non_crossing", bool((np.diff(candidate_values, axis=1) >= -1e-12).all()), str(int((np.diff(candidate_values, axis=1) < -1e-12).any(axis=1).sum()))),
        ("threshold_probabilities_monotonic", bool((np.diff(threshold_values, axis=1) <= 1e-12).all()) and diagnostics.threshold_monotonic.eq(1).all(), str(int(diagnostics.threshold_monotonic.sum()))),
        ("short_games_constrained", diagnostics.short_games_min.between(1, 5).all() and diagnostics.short_games_max.between(1, 5).all(), f"min={diagnostics.short_games_min.min()} max={diagnostics.short_games_max.max()}"),
        ("short_points_positive", diagnostics.short_points_min.gt(0).all(), str(float(diagnostics.short_points_min.min()))),
        ("meaningful_games_constrained", diagnostics.meaningful_games_min.between(6, 23).all() and diagnostics.meaningful_games_max.between(6, 23).all(), f"min={diagnostics.meaningful_games_min.min()} max={diagnostics.meaningful_games_max.max()}"),
        ("draw_expected_values_reconcile", reconciliation[["p_meaningful_abs_delta", "exp_games_abs_delta", "exp_points_abs_delta"]].to_numpy(float).max() <= 1e-12, json.dumps({column: float(reconciliation[column].max()) for column in ["p_meaningful_abs_delta", "exp_games_abs_delta", "exp_points_abs_delta"]}, sort_keys=True)),
        ("bootstrap_observed_equals_pooled", bootstrap_invariant.absolute_delta.max() <= 1e-10, str(float(bootstrap_invariant.absolute_delta.max()))),
    ]
    integrity = pd.DataFrame(
        [
            {"check": check, "passed": bool(passed), "detail": detail}
            for check, passed, detail in integrity_rows
        ]
    )

    point_index = point_overall.set_index("model")
    lead_points = point_by_lead.pivot(index="lead", columns="model", values="total_points_mae")
    primary = primary_pinball.set_index("model").primary_mean_pinball
    pinball_pct = (primary.task050 - primary.task047) / primary.task047
    boot_primary = bootstrap.loc[
        bootstrap.metric.eq("primary_mean_pinball")
    ].iloc[0]
    wis_pct = (
        point_index.loc["task050", "weighted_interval_score"]
        - point_index.loc["task047", "weighted_interval_score"]
    ) / point_index.loc["task047", "weighted_interval_score"]
    max_quantile_pct = float(pin_overall.pct_diff_task050_minus_task047.max())
    candidate_cal = calibration_overall[calibration_overall.model.eq("task050")]
    baseline_cal = calibration_overall[calibration_overall.model.eq("task047")]
    candidate_mace = float(candidate_cal.absolute_error.mean())
    baseline_mace = float(baseline_cal.absolute_error.mean())
    candidate_coverage = coverage_overall[
        coverage_overall.model.eq("task050")
    ].set_index("interval")

    meaningful_brier_pct = (
        point_index.loc["task050", "brier_meaningful"]
        - point_index.loc["task047", "brier_meaningful"]
    ) / point_index.loc["task047", "brier_meaningful"]
    threshold_pct = {}
    for threshold in (100, 110):
        base_value = point_index.loc["task047", f"brier_{threshold}"]
        threshold_pct[threshold] = (
            point_index.loc["task050", f"brier_{threshold}"] - base_value
        ) / base_value

    overall_points_pct = (
        point_index.loc["task050", "total_points_mae"]
        - point_index.loc["task047", "total_points_mae"]
    ) / point_index.loc["task047", "total_points_mae"]
    lead_point_pct = (lead_points.task050 - lead_points.task047) / lead_points.task047
    one_year_points_pct = float(lead_point_pct.loc[1])
    games_pct = (
        point_index.loc["task050", "games_mae"]
        - point_index.loc["task047", "games_mae"]
    ) / point_index.loc["task047", "games_mae"]
    avg_pct = (
        point_index.loc["task050", "conditional_avg_mae"]
        - point_index.loc["task047", "conditional_avg_mae"]
    ) / point_index.loc["task047", "conditional_avg_mae"]

    eligible_subgroups = subgroups[subgroups.n >= 200]
    max_subgroup_regression = float(
        eligible_subgroups[
            [
                "weighted_interval_score_pct_diff_task050_minus_task047",
                "total_points_mae_pct_diff_task050_minus_task047",
            ]
        ].max(axis=None)
    )
    state_index = state_metric.set_index("model")
    state_preserved = (
        state_index.loc["task050", "multiclass_brier"]
        <= state_index.loc["task047", "multiclass_brier"]
        and state_index.loc["task050", "mean_absolute_state_calibration_error"]
        <= state_index.loc["task047", "mean_absolute_state_calibration_error"]
    )

    gates = pd.DataFrame(
        [
            {"gate": 1, "passed": bool(pinball_pct <= -0.02 and boot_primary.bootstrap_median < 0 and boot_primary.ci_high <= primary.task047 * 0.01), "detail": f"pinball_pct={pinball_pct:.6f}; bootstrap=({boot_primary.ci_low:.6f},{boot_primary.bootstrap_median:.6f},{boot_primary.ci_high:.6f})"},
            {"gate": 2, "passed": bool(wis_pct <= -0.01), "detail": f"weighted_interval_score_pct={wis_pct:.6f}"},
            {"gate": 3, "passed": bool(max_quantile_pct <= 0.02), "detail": f"max_quantile_pct={max_quantile_pct:.6f}"},
            {"gate": 4, "passed": bool(candidate_mace <= 0.05 and candidate_mace <= 0.75 * baseline_mace), "detail": f"task050_mace={candidate_mace:.6f}; task047_mace={baseline_mace:.6f}"},
            {"gate": 5, "passed": bool(0.46 <= candidate_coverage.loc["q25_q75", "coverage"] <= 0.54 and 0.76 <= candidate_coverage.loc["q10_q90", "coverage"] <= 0.84), "detail": f"q25_q75={candidate_coverage.loc['q25_q75','coverage']:.6f}; q10_q90={candidate_coverage.loc['q10_q90','coverage']:.6f}"},
            {"gate": 6, "passed": bool(meaningful_brier_pct <= 0.01 and max(threshold_pct.values()) <= 0.02), "detail": f"meaningful_brier_pct={meaningful_brier_pct:.6f}; threshold_pct={threshold_pct}"},
            {"gate": 7, "passed": bool(one_year_points_pct <= 0.02 and overall_points_pct <= 0.01 and float(lead_point_pct.max()) <= 0.05), "detail": f"one_year={one_year_points_pct:.6f}; overall={overall_points_pct:.6f}; max_lead={float(lead_point_pct.max()):.6f}"},
            {"gate": 8, "passed": bool(games_pct <= 0.02 and avg_pct <= 0.02), "detail": f"games_pct={games_pct:.6f}; conditional_avg_pct={avg_pct:.6f}"},
            {"gate": 9, "passed": bool(max_subgroup_regression <= 0.05), "detail": f"max_eligible_subgroup_regression={max_subgroup_regression:.6f}"},
            {"gate": 10, "passed": bool(state_preserved), "detail": json.dumps(state_metric.to_dict('records'), sort_keys=True)},
            {"gate": 11, "passed": bool(integrity.passed.all()), "detail": f"failed_integrity_checks={integrity.loc[~integrity.passed,'check'].tolist()}"},
        ]
    )

    tables = {
        "primary_pinball.csv": primary_pinball,
        "point_metrics_overall.csv": point_overall,
        "point_metrics_by_lead.csv": point_by_lead,
        "pinball_overall.csv": pin_overall,
        "pinball_by_lead.csv": pin_by_lead,
        "pinball_by_fold.csv": pin_by_fold,
        "bootstrap_confidence_intervals.csv": bootstrap,
        "bootstrap_pooled_statistic_invariant.csv": bootstrap_invariant,
        "quantile_calibration_overall.csv": calibration_overall,
        "quantile_calibration_by_lead.csv": calibration_by_lead,
        "interval_coverage_overall.csv": coverage_overall,
        "interval_coverage_by_lead.csv": coverage_by_lead,
        "interval_coverage_by_position.csv": coverage_by_position,
        "interval_coverage_by_prior_history.csv": coverage_by_history,
        "state_metrics.csv": state_metric,
        "state_reliability.csv": state_reliability,
        "subgroup_metrics.csv": subgroups,
        "draw_reconciliation.csv": reconciliation,
        "integrity_checks.csv": integrity,
        "acceptance_gates.csv": gates,
    }
    summary = {
        "task": "TASK-050-joint-season-outcome-distribution",
        "decision": "accepted" if gates.passed.all() else "rejected",
        "accepted_forecast_distribution": bool(gates.passed.all()),
        "failed_gates": gates.loc[~gates.passed, "gate"].astype(int).tolist(),
        "rows_per_model": {"task047": len(baseline), "task050": len(candidate)},
        "player_origin_snapshots": int(target[KEY[:2]].drop_duplicates().shape[0]),
        "folds": int(target[["origin_year", "lead"]].drop_duplicates().shape[0]),
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replications": BOOTSTRAP_REPLICATIONS,
        "baseline_artifacts": baseline_checks,
        "candidate_artifacts": candidate_checks,
    }
    return tables, summary


def write_outputs(
    tables: dict[str, pd.DataFrame],
    summary: dict[str, Any],
    out: Path,
    inputs: dict[str, Path],
) -> None:
    out.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, Any] = {}
    for name, frame in tables.items():
        path = out / name
        frame.to_csv(path, index=False, lineterminator="\n")
        artifacts[name] = {
            "rows": int(len(frame)),
            "sha256": sha256_path(path),
            "bytes": path.stat().st_size,
        }
    summary["input_hashes"] = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256_path(path)}
        for name, path in inputs.items()
    }
    summary["artifacts"] = artifacts
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    (out / "artifact_manifest.json").write_text(
        json.dumps(
            {
                "artifacts": artifacts,
                "row_level_predictions_committed": False,
                "row_level_diagnostics_committed": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (out / "README.md").write_text(
        "# TASK-050 joint season-outcome distribution\n\n"
        "Locked forecast-layer audit. See summary.json and aggregate CSV evidence.\n"
    )
    (out / "REPRODUCE.md").write_text(
        "```bash\n"
        "python vnext/run_task047_pooled_ridge_folds.py --out build/task047-pooled-ridge-conditional-average --rebuild\n"
        "python vnext/run_task050_joint_season_distribution.py --out build/task050-joint-season-outcome-distribution --rebuild\n"
        "python vnext/analyse_task050_joint_season_distribution.py\n"
        "PYTHONPATH=vnext pytest -q vnext/tests/test_task050_joint_season_distribution.py\n"
        "cd vnext && pytest -q\n"
        "python scripts/verify_legacy_manifest.py\n"
        "python scripts/generate_handover.py --check\n"
        "```\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "build/task047-pooled-ridge-conditional-average/vnext_predictions.csv",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        default=ROOT / "build/task050-joint-season-outcome-distribution/vnext_predictions.csv",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=ROOT / "build/task-003-cohorts/targets.csv",
    )
    parser.add_argument(
        "--features",
        type=Path,
        default=ROOT / "build/task050-joint-season-outcome-distribution/training_dataset.csv",
    )
    parser.add_argument(
        "--diagnostics",
        type=Path,
        default=ROOT / "build/task050-joint-season-outcome-distribution/branch_diagnostics.csv",
    )
    parser.add_argument("--out", type=Path, default=REPORT)
    args = parser.parse_args()
    inputs = {
        "baseline": require(args.baseline, "TASK-047 predictions"),
        "candidate": require(args.candidate, "TASK-050 predictions"),
        "targets": require(args.targets, "locked targets"),
        "features": require(args.features, "TASK-050 training dataset"),
        "diagnostics": require(args.diagnostics, "TASK-050 diagnostics"),
    }
    target_failures = require(
        args.targets.parent / "target_failures.csv", "locked target failures"
    )
    if len(pd.read_csv(target_failures)):
        raise ValueError("locked target failures must remain zero")
    tables, summary = build_audit(
        load_predictions(args.baseline, "task047"),
        load_predictions(args.candidate, "task050"),
        pd.read_csv(args.targets),
        pd.read_csv(args.features),
        pd.read_csv(args.diagnostics),
        artifact_checks(args.baseline),
        artifact_checks(args.candidate),
    )
    write_outputs(tables, summary, args.out, inputs)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
