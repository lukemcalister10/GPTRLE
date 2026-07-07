"""Explore exact-age TASK-003K crossover and predeclared age-blend policies.

Diagnostic only. Reads locked current/candidate predictions plus locked targets and
snapshots. It does not fit or alter a model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error

KEY = ["player_key", "origin_year", "lead"]


def metrics(frame: pd.DataFrame, prefix: str) -> dict[str, float]:
    return {
        f"{prefix}_brier": brier_score_loss(frame["meaningful"], frame[f"{prefix}_p"]),
        f"{prefix}_log_loss": log_loss(frame["meaningful"], np.clip(frame[f"{prefix}_p"], 0.001, 0.999), labels=[0, 1]),
        f"{prefix}_games_mae": mean_absolute_error(frame["games"], frame[f"{prefix}_games"]),
        f"{prefix}_points_mae": mean_absolute_error(frame["points"], frame[f"{prefix}_points"]),
    }


def compare_slice(frame: pd.DataFrame, group: dict[str, object]) -> dict[str, object]:
    row: dict[str, object] = {**group, "n": int(len(frame))}
    row.update(metrics(frame, "current"))
    row.update(metrics(frame, "candidate"))
    for metric in ("brier", "log_loss", "games_mae", "points_mae"):
        current = float(row[f"current_{metric}"])
        candidate = float(row[f"candidate_{metric}"])
        row[f"{metric}_change_pct"] = 100.0 * (candidate - current) / current if current else np.nan
        row[f"{metric}_delta"] = candidate - current
    improved = sum(float(row[f"{m}_delta"]) < 0 for m in ("brier", "log_loss", "games_mae", "points_mae"))
    row["metrics_improved"] = int(improved)
    return row


def add_policy(frame: pd.DataFrame, name: str, weight: np.ndarray) -> pd.DataFrame:
    out = frame.copy()
    w = np.asarray(weight, dtype=float)
    out[f"{name}_p"] = out["current_p"] + w * (out["candidate_p"] - out["current_p"])
    out[f"{name}_games"] = out["current_games"] + w * (out["candidate_games"] - out["current_games"])
    out[f"{name}_points"] = out["current_points"] + w * (out["candidate_points"] - out["current_points"])
    return out


def policy_metrics(frame: pd.DataFrame, name: str, weight: np.ndarray, policy: str) -> dict[str, object]:
    f = add_policy(frame, name, weight)
    current = metrics(f, "current")
    hybrid = metrics(f, name)
    row: dict[str, object] = {"policy": policy, "n": int(len(f))}
    for metric in ("brier", "log_loss", "games_mae", "points_mae"):
        c = current[f"current_{metric}"]
        h = hybrid[f"{name}_{metric}"]
        row[f"current_{metric}"] = c
        row[f"hybrid_{metric}"] = h
        row[f"change_pct"] = row.get(f"change_pct", np.nan)
        row[f"{metric}_change_pct"] = 100.0 * (h - c) / c if c else np.nan
    return row


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--current", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--snapshots", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--min-n", type=int, default=80)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    current = pd.read_csv(args.current)
    candidate = pd.read_csv(args.candidate)
    targets = pd.read_csv(args.targets)
    snapshots = pd.read_csv(args.snapshots)[["player_key", "origin_year", "age"]]

    ccols = {"p_meaningful": "current_p", "exp_games": "current_games", "exp_points": "current_points"}
    kcols = {"p_meaningful": "candidate_p", "exp_games": "candidate_games", "exp_points": "candidate_points"}
    frame = (
        current[KEY + list(ccols)].rename(columns=ccols)
        .merge(candidate[KEY + list(kcols)].rename(columns=kcols), on=KEY, validate="one_to_one")
        .merge(targets[KEY + ["meaningful", "games", "points"]], on=KEY, validate="one_to_one")
        .merge(snapshots, on=["player_key", "origin_year"], validate="many_to_one")
    )
    frame["age_int"] = np.floor(frame["age"] + 1e-9).astype(int)

    exact_rows = []
    for (age, lead), g in frame.groupby(["age_int", "lead"], sort=True):
        if len(g) >= args.min_n:
            exact_rows.append(compare_slice(g, {"age": int(age), "lead": int(lead)}))
    exact = pd.DataFrame(exact_rows).sort_values(["age", "lead"])
    exact.to_csv(args.out / "exact_age_by_lead.csv", index=False)

    pooled_rows = []
    for age, g in frame.groupby("age_int", sort=True):
        if len(g) >= args.min_n:
            pooled_rows.append(compare_slice(g, {"age": int(age), "lead": "all"}))
    pooled = pd.DataFrame(pooled_rows).sort_values("age")
    pooled.to_csv(args.out / "exact_age_pooled.csv", index=False)

    cutoff_rows = []
    for cutoff in range(26, 34):
        w = (frame["age"] < cutoff).astype(float).to_numpy()
        cutoff_rows.append(policy_metrics(frame, "hybrid", w, f"hard_under_{cutoff}"))
    for start in range(26, 31):
        for end in range(start + 1, 34):
            age = frame["age"].to_numpy(float)
            w = np.where(age <= start, 1.0, np.where(age >= end, 0.0, (end - age) / (end - start)))
            cutoff_rows.append(policy_metrics(frame, "hybrid", w, f"linear_{start}_to_{end}"))
    policies = pd.DataFrame(cutoff_rows)
    policies["mean_primary_change_pct"] = policies[[
        "brier_change_pct", "log_loss_change_pct", "games_mae_change_pct", "points_mae_change_pct"
    ]].mean(axis=1)
    policies.sort_values(["mean_primary_change_pct", "policy"]).to_csv(args.out / "exploratory_blend_policies.csv", index=False)

    ages_27_31 = pooled[pooled["age"].between(27, 31)].copy()
    summary = {
        "rows": int(len(frame)),
        "minimum_slice_n": int(args.min_n),
        "age_27_to_31": ages_27_31.to_dict(orient="records"),
        "first_pooled_age_with_points_harm": (
            int(pooled.loc[pooled["points_mae_delta"] > 0, "age"].min())
            if (pooled["points_mae_delta"] > 0).any() else None
        ),
        "first_pooled_age_with_brier_harm": (
            int(pooled.loc[pooled["brier_delta"] > 0, "age"].min())
            if (pooled["brier_delta"] > 0).any() else None
        ),
        "best_exploratory_policy": policies.sort_values("mean_primary_change_pct").iloc[0].to_dict(),
        "warning": "Blend-policy ranking is exploratory and must be locked before any confirmatory rerun.",
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
