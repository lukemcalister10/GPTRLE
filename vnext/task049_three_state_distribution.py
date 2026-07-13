"""TASK-049 three-state point-distribution utilities.

This module is intentionally limited to uncertainty output generation and audit
helpers. It transforms locked TASK-047 rows; it must not refit point models or
change non-quantile outputs.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

KEY = ["player_key", "origin_year", "lead"]
QCOLS = ["points_q10", "points_q25", "points_q50", "points_q75", "points_q90", "points_q97"]
QLEVELS = np.array([0.10, 0.25, 0.50, 0.75, 0.90, 0.97])
NON_QUANTILE_TOL = 1e-10
MEAN_TOL = 1e-8
SAMPLE_COUNT = 2048
GENERATOR_ID = "TASK-049"


def seed_for(player_key: str, origin_year: int, lead: int) -> int:
    digest = hashlib.sha256(f"TASK-049|{player_key}|{origin_year}|{lead}".encode()).digest()
    return int.from_bytes(digest[:8], "little") & 0xFFFFFFFF


@dataclass(frozen=True)
class ShortSupport:
    origin_year: int
    lead: int
    zero_prob: float
    short_prob: float
    meaningful_prob: float
    game_probs: dict[int, float]
    short_games_values: np.ndarray
    rate_values: np.ndarray
    games_resid_sd: float
    avg_resid_sd: float
    training_rows: int
    short_rows: int


def _finite_positive(value: Any, name: str, origin: int, lead: int) -> float:
    val = float(value)
    if not np.isfinite(val) or val <= 0.0:
        raise ValueError(f"invalid {name} for origin_year={origin} lead={lead}: {value}")
    return val


def validate_fold_manifest(fold_manifest: pd.DataFrame) -> pd.DataFrame:
    required = {"origin_year", "lead", "games_resid_sd", "avg_resid_sd"}
    missing = sorted(required - set(fold_manifest.columns))
    if missing:
        raise ValueError(f"TASK-047 fold manifest missing columns: {missing}")
    dup = fold_manifest.duplicated(["origin_year", "lead"], keep=False)
    if dup.any():
        bad = fold_manifest.loc[dup, ["origin_year", "lead"]].drop_duplicates().to_dict("records")
        raise ValueError(f"TASK-047 fold manifest has duplicate origin/lead rows: {bad}")
    out = fold_manifest.copy()
    for row in out.itertuples(index=False):
        origin = int(getattr(row, "origin_year")); lead = int(getattr(row, "lead"))
        _finite_positive(getattr(row, "games_resid_sd"), "games_resid_sd", origin, lead)
        _finite_positive(getattr(row, "avg_resid_sd"), "avg_resid_sd", origin, lead)
    return out


def build_short_support(training: pd.DataFrame, fold_manifest: pd.DataFrame) -> dict[tuple[int, int], ShortSupport]:
    """Build origin-safe empirical short-season support for each TASK-047 fold."""
    need = {"origin_year", "lead", "games", "points"}
    missing = sorted(need - set(training.columns))
    if missing:
        raise ValueError(f"training support missing columns: {missing}")
    manifest = validate_fold_manifest(fold_manifest)
    supports: dict[tuple[int, int], ShortSupport] = {}
    for fm in manifest.itertuples(index=False):
        origin = int(fm.origin_year); lead = int(fm.lead)
        target_year = pd.to_numeric(training["target_year"], errors="coerce") if "target_year" in training.columns else (pd.to_numeric(training.origin_year, errors="coerce") + lead)
        hist = training[(training.lead.astype(int) == lead) & (training.origin_year >= 2008) & (target_year < origin)].copy()
        if hist.empty:
            raise ValueError(f"missing short-season support for origin_year={origin} lead={lead}")
        games = pd.to_numeric(hist.games, errors="coerce")
        points = pd.to_numeric(hist.points, errors="coerce")
        if games.isna().any() or points.isna().any():
            raise ValueError(f"non-finite training support for origin_year={origin} lead={lead}")
        zero = games.eq(0) & points.eq(0)
        short = games.between(1, 5, inclusive="both") & points.gt(0)
        meaningful = games.ge(6)
        non_meaningful = zero | short
        if int(short.sum()) == 0:
            raise ValueError(f"missing short-season support for origin_year={origin} lead={lead}")
        denom = int(non_meaningful.sum())
        if denom == 0:
            raise ValueError(f"missing non-meaningful support for origin_year={origin} lead={lead}")
        short_games = games.loc[short].astype(int)
        rates = (points.loc[short] / short_games).astype(float).to_numpy()
        if len(rates) == 0 or not np.isfinite(rates).all() or (rates <= 0).any():
            raise ValueError(f"invalid short scoring-rate support for origin_year={origin} lead={lead}")
        freqs = short_games.value_counts(normalize=True).reindex([1, 2, 3, 4, 5], fill_value=0.0)
        supports[(origin, lead)] = ShortSupport(
            origin, lead, float(zero.sum() / denom), float(short.sum() / denom), float(meaningful.mean()),
            {int(k): float(v) for k, v in freqs.items()}, short_games.to_numpy(dtype=float), rates,
            _finite_positive(fm.games_resid_sd, "games_resid_sd", origin, lead),
            _finite_positive(fm.avg_resid_sd, "avg_resid_sd", origin, lead), int(len(hist)), int(short.sum())
        )
    return supports


def generate_three_state_predictions(predictions: pd.DataFrame, supports: dict[tuple[int, int], ShortSupport], sample_count: int = SAMPLE_COUNT) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = set(KEY + ["p_meaningful", "cond_games", "cond_avg", "exp_points"] + QCOLS)
    missing = sorted(required - set(predictions.columns))
    if missing:
        raise ValueError(f"predictions missing columns: {missing}")
    out = predictions.copy()
    for _q in QCOLS:
        out[_q] = out[_q].astype(float)
    diagnostics = []
    for idx, row in out.iterrows():
        key = (int(row.origin_year), int(row.lead))
        if key not in supports:
            raise ValueError(f"missing short-season support for origin_year={key[0]} lead={key[1]}")
        sup = supports[key]
        p_meaningful = float(np.clip(row.p_meaningful, 0.0, 1.0))
        non_mean = max(0.0, 1.0 - p_meaningful)
        p_short = non_mean * sup.short_prob
        p_zero = max(0.0, 1.0 - p_meaningful - p_short)
        rng = np.random.default_rng(seed_for(str(row.player_key), int(row.origin_year), int(row.lead)))
        states = rng.choice(3, size=sample_count, p=np.array([p_zero, p_short, p_meaningful]) / max(p_zero + p_short + p_meaningful, 1e-12))
        values = np.zeros(sample_count, dtype=float)
        short_mask = states == 1; meaningful_mask = states == 2
        if short_mask.any():
            sg = rng.choice(sup.short_games_values, size=int(short_mask.sum()), replace=True)
            sr = rng.choice(sup.rate_values, size=int(short_mask.sum()), replace=True)
            raw_short = sg * sr
            values[short_mask] = raw_short
        else:
            sg = np.array([], dtype=int); raw_short = np.array([], dtype=float); sr = np.array([], dtype=float)
        if meaningful_mask.any():
            mg = np.clip(rng.normal(float(row.cond_games), sup.games_resid_sd, int(meaningful_mask.sum())), 6.0, 23.0)
            ma = np.clip(rng.normal(float(row.cond_avg), sup.avg_resid_sd, int(meaningful_mask.sum())), 1e-6, 145.0)
            values[meaningful_mask] = mg * ma
        else:
            mg = np.array([], dtype=float)
        before = float(values.mean())
        target_mean = float(row.exp_points)
        if before > 0.0:
            values = values * (target_mean / before)
        elif target_mean > MEAN_TOL:
            raise ValueError(f"cannot reconcile positive exp_points without positive draws for {row[KEY].to_dict()}")
        delta = target_mean - before
        qs = np.maximum.accumulate(np.maximum(0.0, np.quantile(values, QLEVELS)))
        for col, val in zip(QCOLS, qs, strict=True): out.at[idx, col] = float(val)
        diagnostics.append({**{k: row[k] for k in KEY}, "p_zero": p_zero, "p_short": p_short, "p_meaningful": p_meaningful,
            "short_draw_count": int(short_mask.sum()), "short_games_min": int(sg.min()) if len(sg) else np.nan,
            "short_games_max": int(sg.max()) if len(sg) else np.nan, "adjusted_short_points_min": float(values[short_mask].min()) if short_mask.any() else np.nan,
            "adjusted_short_points_max": float(values[short_mask].max()) if short_mask.any() else np.nan,
            "meaningful_draw_count": int(meaningful_mask.sum()), "meaningful_games_min": float(mg.min()) if len(mg) else np.nan,
            "meaningful_games_max": float(mg.max()) if len(mg) else np.nan, "pred_short_games_mean": float(sum(k*v for k,v in sup.game_probs.items())),
            "pred_short_rate_mean": float(np.mean(sup.rate_values)), "moment_delta": delta, "moment_error_after": float(values.mean() - target_mean), "draw_mean_after": float(values.mean())})
    return out, pd.DataFrame(diagnostics)


def short_support_training_summary(supports: dict[tuple[int, int], ShortSupport]) -> pd.DataFrame:
    rows = []
    for (origin, lead), sup in sorted(supports.items()):
        rec = {
            "origin_year": origin,
            "lead": lead,
            "training_rows": sup.training_rows,
            "short_rows": sup.short_rows,
            "zero_prob_in_non_meaningful_training": sup.zero_prob,
            "short_prob_in_non_meaningful_training": sup.short_prob,
            "rate_mean": float(np.mean(sup.rate_values)),
            "rate_sd": float(np.std(sup.rate_values, ddof=1)) if len(sup.rate_values) > 1 else 0.0,
            "rate_q10": float(np.quantile(sup.rate_values, 0.10)),
            "rate_q25": float(np.quantile(sup.rate_values, 0.25)),
            "rate_q50": float(np.quantile(sup.rate_values, 0.50)),
            "rate_q75": float(np.quantile(sup.rate_values, 0.75)),
            "rate_q90": float(np.quantile(sup.rate_values, 0.90)),
            "games_resid_sd": sup.games_resid_sd,
            "avg_resid_sd": sup.avg_resid_sd,
        }
        for games in range(1, 6):
            rec[f"games_{games}_prob"] = sup.game_probs[games]
        rows.append(rec)
    return pd.DataFrame(rows)


def compare_unchanged_outputs(baseline: pd.DataFrame, candidate: pd.DataFrame, exclude: list[str] | None = None, tol: float = NON_QUANTILE_TOL) -> pd.DataFrame:
    exclude = QCOLS if exclude is None else exclude
    if list(baseline.columns) != list(candidate.columns):
        raise ValueError("baseline and candidate prediction schemas differ")
    b = baseline.sort_values(KEY).reset_index(drop=True); c = candidate.sort_values(KEY).reset_index(drop=True)
    if not b[KEY].equals(c[KEY]):
        raise ValueError("baseline and candidate keys differ")
    rows=[]
    for col in b.columns:
        if col in exclude: continue
        if pd.api.types.is_numeric_dtype(b[col]) and pd.api.types.is_numeric_dtype(c[col]):
            diff=(pd.to_numeric(b[col])-pd.to_numeric(c[col])).abs(); changed=int((diff>tol).sum()); maxdiff=float(diff.max()) if len(diff) else 0.0; mismatch=0
        else:
            eq=b[col].fillna("__NA__").astype(str).eq(c[col].fillna("__NA__").astype(str)); changed=int((~eq).sum()); maxdiff=np.nan; mismatch=changed
        rows.append({"column":col,"baseline_dtype":str(b[col].dtype),"candidate_dtype":str(c[col].dtype),"changed_rows":changed,"max_abs_difference":maxdiff,"mismatch_count":mismatch})
    comp=pd.DataFrame(rows)
    if (comp.changed_rows>0).any():
        bad=comp.loc[comp.changed_rows>0,"column"].tolist(); raise ValueError(f"non-quantile output columns changed: {bad}")
    return comp


def candidate_minus_baseline_bootstrap(wide: pd.DataFrame, qcols: list[str] = QCOLS, reps: int = 2000, seed: int = 49049) -> tuple[pd.DataFrame, pd.DataFrame]:
    def pin(y,q,t):
        d=y-q; return np.maximum(t*d,(t-1)*d)
    taus={"points_q10":.1,"points_q25":.25,"points_q50":.5,"points_q75":.75,"points_q90":.9,"points_q97":.97}
    per=wide[["player_key"]].copy(); metrics=[]
    for col in qcols:
        per[col]=pin(wide.points.astype(float), wide[f"{col}_candidate"].astype(float), taus[col])-pin(wide.points.astype(float), wide[f"{col}_baseline"].astype(float), taus[col])
        metrics.append(col)
    per["primary_mean_pinball"]=per[metrics].mean(axis=1); metrics=["primary_mean_pinball"]+metrics
    observed={m:float(per[m].mean()) for m in metrics}
    blocks=per.groupby("player_key").agg({**{m:"sum" for m in metrics},"player_key":"size"}).rename(columns={"player_key":"row_count"})
    players=blocks.index.to_numpy(); rng=np.random.default_rng(seed); rows=[]
    for m in metrics:
        draws=np.empty(reps)
        for i in range(reps):
            s=blocks.loc[rng.choice(players,size=len(players),replace=True)]
            draws[i]=float(s[m].sum()/s.row_count.sum())
        rows.append({"metric":m,"observed_diff_candidate_minus_baseline":observed[m],"bootstrap_median":float(np.median(draws)),"ci_low":float(np.quantile(draws,.025)),"ci_high":float(np.quantile(draws,.975)),"bootstrap_seed":seed,"replications":reps})
    ci=pd.DataFrame(rows)
    inv=pd.DataFrame({"metric":list(observed),"pooled_table_diff":[observed[m] for m in observed],"bootstrap_observed_diff":[observed[m] for m in observed]})
    inv["abs_delta"]=(inv.pooled_table_diff-inv.bootstrap_observed_diff).abs()
    return ci, inv
