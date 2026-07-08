from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error

KEY = ["player_key", "origin_year", "lead"]
METRICS = ("brier", "log_loss", "games_mae", "points_mae")


def score(frame: pd.DataFrame, prefix: str) -> dict[str, float]:
    probability = np.clip(frame[f"{prefix}_p"].to_numpy(float), 0.001, 0.999)
    actual = frame["meaningful"].astype(int).to_numpy()
    return {
        "n": int(len(frame)),
        "players": int(frame["player_key"].nunique()),
        "brier": float(brier_score_loss(actual, probability)),
        "log_loss": float(log_loss(actual, probability, labels=[0, 1])),
        "games_mae": float(mean_absolute_error(frame["games"], frame[f"{prefix}_games"])),
        "points_mae": float(mean_absolute_error(frame["points"], frame[f"{prefix}_points"])),
    }


def changes(base: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    return {
        metric: 100.0 * (candidate[metric] - base[metric]) / base[metric]
        for metric in METRICS
    }


def bootstrap(frame: pd.DataFrame, draws: int = 1000) -> dict[str, dict[str, float]]:
    blocks = []
    for _, group in frame.groupby("player_key", sort=True):
        actual = group["meaningful"].to_numpy(float)
        blocks.append(
            {
                "n": len(group),
                "base_brier": float(np.square(group["baseline_p"].to_numpy(float) - actual).sum()),
                "candidate_brier": float(np.square(group["candidate_p"].to_numpy(float) - actual).sum()),
                "base_points": float(np.abs(group["baseline_points"] - group["points"]).sum()),
                "candidate_points": float(np.abs(group["candidate_points"] - group["points"]).sum()),
            }
        )
    values = pd.DataFrame(blocks)
    rng = np.random.default_rng(9011)
    brier_differences: list[float] = []
    points_differences: list[float] = []
    for _ in range(draws):
        sample = values.iloc[rng.integers(0, len(values), len(values))]
        n = float(sample["n"].sum())
        brier_differences.append(
            float((sample["candidate_brier"].sum() - sample["base_brier"].sum()) / n)
        )
        points_differences.append(
            float((sample["candidate_points"].sum() - sample["base_points"].sum()) / n)
        )

    def interval(samples: list[float]) -> dict[str, float]:
        quantiles = np.quantile(samples, [0.025, 0.5, 0.975])
        return {
            "lower": float(quantiles[0]),
            "median": float(quantiles[1]),
            "upper": float(quantiles[2]),
        }

    return {
        "brier_difference": interval(brier_differences),
        "points_mae_difference": interval(points_differences),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--snapshots", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    baseline = pd.read_csv(args.baseline)
    candidate = pd.read_csv(args.candidate)
    targets = pd.read_csv(args.targets)
    snapshots = pd.read_csv(args.snapshots)
    if baseline.duplicated(KEY).any() or candidate.duplicated(KEY).any():
        raise ValueError("duplicate prediction key")
    if set(map(tuple, baseline[KEY].to_numpy())) != set(map(tuple, candidate[KEY].to_numpy())):
        raise ValueError("prediction key mismatch")

    frame = (
        baseline[KEY + ["p_meaningful", "exp_games", "exp_points"]]
        .rename(
            columns={
                "p_meaningful": "baseline_p",
                "exp_games": "baseline_games",
                "exp_points": "baseline_points",
            }
        )
        .merge(
            candidate[KEY + ["p_meaningful", "exp_games", "exp_points"]].rename(
                columns={
                    "p_meaningful": "candidate_p",
                    "exp_games": "candidate_games",
                    "exp_points": "candidate_points",
                }
            ),
            on=KEY,
            validate="one_to_one",
        )
        .merge(
            targets[KEY + ["meaningful", "games", "points"]],
            on=KEY,
            validate="one_to_one",
        )
        .merge(
            snapshots[["player_key", "origin_year", "total_games"]],
            on=["player_key", "origin_year"],
            validate="many_to_one",
        )
    )
    total_games = pd.to_numeric(frame["total_games"], errors="coerce").fillna(0.0)
    cohorts = {
        "all": pd.Series(True, index=frame.index),
        "established_50_plus": total_games >= 50,
        "established_100_plus": total_games >= 100,
        "under_50": total_games < 50,
        "zero_history": total_games == 0,
    }

    results: dict[str, Any] = {}
    metric_rows = []
    for cohort, mask in cohorts.items():
        part = frame.loc[mask]
        base = score(part, "baseline")
        candidate_score = score(part, "candidate")
        delta = changes(base, candidate_score)
        results[cohort] = {
            "task009": base,
            "task011": candidate_score,
            "change_pct": delta,
        }
        metric_rows.extend(
            [
                {"cohort": cohort, "model": "task009", **base},
                {"cohort": cohort, "model": "task011", **candidate_score},
            ]
        )
    pd.DataFrame(metric_rows).to_csv(args.out / "metrics_by_cohort.csv", index=False)

    established = frame.loc[cohorts["established_50_plus"]]
    boot = bootstrap(established)
    (args.out / "established_bootstrap.json").write_text(
        json.dumps(boot, indent=2, sort_keys=True) + "\n"
    )

    e50 = results["established_50_plus"]["change_pct"]
    e100 = results["established_100_plus"]["change_pct"]
    under = results["under_50"]["change_pct"]
    zero = results["zero_history"]["change_pct"]
    overall = results["all"]["change_pct"]
    gates = {
        "established_brier_improves": e50["brier"] < 0,
        "established_log_loss_improves": e50["log_loss"] < 0,
        "established_games_mae_improves": e50["games_mae"] < 0,
        "established_points_mae_improves": e50["points_mae"] < 0,
        "established_100_no_metric_regresses_over_1pct": all(value <= 1.0 for value in e100.values()),
        "under_50_no_metric_regresses_over_0_5pct": all(value <= 0.5 for value in under.values()),
        "zero_history_no_metric_regresses_over_1pct": all(value <= 1.0 for value in zero.values()),
        "overall_no_metric_regresses_over_0_5pct": all(value <= 0.5 for value in overall.values()),
        "bootstrap_median_brier_improves": boot["brier_difference"]["median"] < 0,
        "bootstrap_median_points_improves": boot["points_mae_difference"]["median"] < 0,
    }
    report = {
        "status": "pass" if all(gates.values()) else "reject",
        "baseline": "TASK-009",
        "hypothesis": "draft pedigree should fade to neutral as observed AFL evidence reaches 50 games",
        "single_change": "origin-safe draft pick and draft type representation",
        "gates": gates,
        "scores": results,
        "bootstrap": boot,
        "rows": int(len(frame)),
    }
    (args.out / "final_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
