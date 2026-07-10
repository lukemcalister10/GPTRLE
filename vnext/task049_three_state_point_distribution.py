"""TASK-049 target-compatible three-state point distribution generator."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

KEY = ["player_key", "origin_year", "lead"]
QLEVELS = np.array([0.10, 0.25, 0.50, 0.75, 0.90, 0.97])
QCOLS = ["points_q10", "points_q25", "points_q50", "points_q75", "points_q90", "points_q97"]
SAMPLE_COUNT = 2048

@dataclass(frozen=True)
class ShortSeasonEvidence:
    lead: int
    origin_year: int
    p_zero_given_nonmeaningful: float
    p_short_given_nonmeaningful: float
    short_games: tuple[int, ...]
    short_rates: tuple[float, ...]
    n_zero: int
    n_short: int
    n_meaningful: int


def seed_for(player_key: str, origin_year: int, lead: int) -> int:
    digest = hashlib.sha256(f"TASK-049|{player_key}|{origin_year}|{lead}".encode()).digest()
    return int.from_bytes(digest[:8], "little") & 0xFFFFFFFF


def legal_training_rows(dataset: pd.DataFrame, lead: int, origin_year: int) -> pd.DataFrame:
    train = dataset[(dataset.origin_year >= 2008) & ((dataset.origin_year + lead) < origin_year)].copy()
    if train.empty:
        raise ValueError(f"no legal TASK-049 training rows for lead={lead} origin_year={origin_year}")
    if int((train.origin_year + lead).max()) >= origin_year:
        raise ValueError(f"leaky TASK-049 training rows for lead={lead} origin_year={origin_year}")
    return train


def estimate_short_season_evidence(dataset: pd.DataFrame, lead: int, origin_year: int) -> ShortSeasonEvidence:
    train = legal_training_rows(dataset, lead, origin_year)
    gcol, pcol = f"l{lead}_games", f"l{lead}_points"
    if gcol not in train or pcol not in train:
        raise ValueError(f"training dataset missing {gcol}/{pcol}")
    games = train[gcol].astype(float)
    points = train[pcol].astype(float)
    zero = games.eq(0) & points.eq(0)
    short = games.between(1, 5, inclusive="both") & points.gt(0)
    meaningful = games.ge(6)
    n_zero, n_short, n_meaningful = int(zero.sum()), int(short.sum()), int(meaningful.sum())
    if n_short <= 0:
        raise ValueError(f"missing short-season training support for lead={lead} origin_year={origin_year}")
    short_games = games.loc[short].astype(int).to_numpy()
    if not np.isin(short_games, [1,2,3,4,5]).all():
        raise ValueError("invalid short-season game support outside 1-5")
    rates = (points.loc[short] / games.loc[short]).astype(float).to_numpy()
    if (rates <= 0).any() or not np.isfinite(rates).all():
        raise ValueError("invalid short-season scoring-rate support")
    denom = n_zero + n_short
    if denom <= 0:
        raise ValueError(f"missing non-meaningful training support for lead={lead} origin_year={origin_year}")
    return ShortSeasonEvidence(lead, origin_year, n_zero/denom, n_short/denom, tuple(map(int, short_games)), tuple(map(float, rates)), n_zero, n_short, n_meaningful)


def _row_quantiles(row: pd.Series, ev: ShortSeasonEvidence, games_sd: float, avg_sd: float, sample_count: int) -> tuple[list[float], float, float, float]:
    p_meaningful = float(row.p_meaningful)
    p_non = max(0.0, 1.0 - p_meaningful)
    p_zero = p_non * ev.p_zero_given_nonmeaningful
    p_short = p_non * ev.p_short_given_nonmeaningful
    probs = np.array([p_zero, p_short, p_meaningful], dtype=float)
    probs = probs / probs.sum() if probs.sum() > 0 else np.array([1.0, 0.0, 0.0])
    rng = np.random.default_rng(seed_for(str(row.player_key), int(row.origin_year), int(row.lead)))
    states = rng.choice(3, size=sample_count, p=probs)
    draws = np.zeros(sample_count, dtype=float)
    if (states == 1).any():
        sg = rng.choice(np.array(ev.short_games), size=int((states == 1).sum()), replace=True)
        sr = rng.choice(np.array(ev.short_rates), size=int((states == 1).sum()), replace=True)
        draws[states == 1] = sg * sr
    if (states == 2).any():
        mg = np.clip(rng.normal(float(row.cond_games), games_sd, int((states == 2).sum())), 6.0, 23.0)
        ma = np.clip(rng.normal(float(row.cond_avg), avg_sd, int((states == 2).sum())), 1e-6, 145.0)
        draws[states == 2] = mg * ma
    raw_mean = float(draws.mean())
    target = float(row.exp_points)
    if target < -1e-12:
        raise ValueError("negative accepted point forecast")
    if raw_mean <= 0 and target > 1e-12:
        raise ValueError("cannot reconcile positive point forecast with zero simulated mean")
    scale = 0.0 if target <= 1e-12 else target / raw_mean
    adjusted = draws * scale
    qs = np.maximum.accumulate(np.quantile(adjusted, QLEVELS)).clip(min=0.0)
    return [float(x) for x in qs], float(adjusted.mean()), float(probs[0]), float(probs[1])


def generate_three_state_predictions(predictions: pd.DataFrame, training_dataset: pd.DataFrame, fold_manifest: pd.DataFrame, sample_count: int = SAMPLE_COUNT) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    out = predictions.copy()
    evidence_rows: list[dict[str, Any]] = []
    recon_rows: list[dict[str, Any]] = []
    for (lead, origin), idx in out.groupby(["lead", "origin_year"]).groups.items():
        ev = estimate_short_season_evidence(training_dataset, int(lead), int(origin))
        fm = fold_manifest[(fold_manifest.lead == lead) & (fold_manifest.origin_year == origin)]
        games_sd = float(fm.games_resid_sd.iloc[0]) if len(fm) and "games_resid_sd" in fm else 3.0
        avg_sd = float(fm.avg_resid_sd.iloc[0]) if len(fm) and "avg_resid_sd" in fm else 12.0
        evidence_rows.append(ev.__dict__ | {"short_games": "|".join(map(str, ev.short_games)), "short_rates_count": len(ev.short_rates), "games_resid_sd": games_sd, "avg_resid_sd": avg_sd})
        for ridx in idx:
            qs, sim_mean, pz, ps = _row_quantiles(out.loc[ridx], ev, games_sd, avg_sd, sample_count)
            for c, v in zip(QCOLS, qs, strict=True):
                out.at[ridx, c] = v
            recon_rows.append({"player_key": out.at[ridx,"player_key"], "origin_year": int(origin), "lead": int(lead), "exp_points": float(out.at[ridx,"exp_points"]), "simulated_mean": sim_mean, "abs_delta": abs(sim_mean - float(out.at[ridx,"exp_points"])), "p_zero_state": pz, "p_short_state": ps, "p_meaningful_state": float(out.at[ridx,"p_meaningful"])})
    return out, pd.DataFrame(evidence_rows), pd.DataFrame(recon_rows)
