from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

KEY = ["player_key", "origin_year", "lead"]
UNCHANGED_COLUMNS = [
    "p_meaningful",
    "cond_games",
    "exp_games",
    "p_avg_ge_80",
    "p_avg_ge_90",
    "p_avg_ge_100",
    "p_avg_ge_110",
    "p_avg_ge_120",
]


def score(frame: pd.DataFrame, prefix: str) -> dict[str, float]:
    meaningful = frame["meaningful"].astype(bool)
    result = {
        "n": int(len(frame)),
        "players": int(frame["player_key"].nunique()),
        "meaningful_rows": int(meaningful.sum()),
        "points_mae": float(mean_absolute_error(frame["points"], frame[f"{prefix}_points"])),
    }
    result["conditional_avg_mae"] = (
        float(mean_absolute_error(frame.loc[meaningful, "avg"], frame.loc[meaningful, f"{prefix}_avg"]))
        if meaningful.any()
        else float("nan")
    )
    return result


def pct_change(base: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    return {
        metric: 100.0 * (candidate[metric] - base[metric]) / base[metric]
        for metric in ("conditional_avg_mae", "points_mae")
    }


def player_bootstrap(frame: pd.DataFrame, draws: int = 1000) -> dict[str, dict[str, float]]:
    blocks: list[dict[str, float]] = []
    for _, group in frame.groupby("player_key", sort=True):
        meaningful = group["meaningful"].astype(bool).to_numpy()
        blocks.append(
            {
                "rows": float(len(group)),
                "meaningful_rows": float(meaningful.sum()),
                "base_avg_error": float(
                    np.abs(group.loc[meaningful, "baseline_avg"] - group.loc[meaningful, "avg"]).sum()
                ),
                "candidate_avg_error": float(
                    np.abs(group.loc[meaningful, "candidate_avg"] - group.loc[meaningful, "avg"]).sum()
                ),
                "base_points_error": float(np.abs(group["baseline_points"] - group["points"]).sum()),
                "candidate_points_error": float(np.abs(group["candidate_points"] - group["points"]).sum()),
            }
        )
    values = pd.DataFrame(blocks)
    rng = np.random.default_rng(9012)
    avg_differences: list[float] = []
    points_differences: list[float] = []
    for _ in range(draws):
        sample = values.iloc[rng.integers(0, len(values), len(values))]
        meaningful_n = float(sample["meaningful_rows"].sum())
        row_n = float(sample["rows"].sum())
        avg_differences.append(
            float(
                (sample["candidate_avg_error"].sum() - sample["base_avg_error"].sum())
                / meaningful_n
            )
        )
        points_differences.append(
            float(
                (sample["candidate_points_error"].sum() - sample["base_points_error"].sum())
                / row_n
            )
        )

    def interval(samples: list[float]) -> dict[str, float]:
        q = np.quantile(samples, [0.025, 0.5, 0.975])
        return {"lower": float(q[0]), "median": float(q[1]), "upper": float(q[2])}

    return {
        "conditional_avg_mae_difference": interval(avg_differences),
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
        raise ValueError("baseline and candidate prediction keys differ")

    invariant_differences = {
        column: float(
            np.max(
                np.abs(
                    baseline.sort_values(KEY)[column].to_numpy(float)
                    - candidate.sort_values(KEY)[column].to_numpy(float)
                )
            )
        )
        for column in UNCHANGED_COLUMNS
    }

    frame = (
        baseline[KEY + ["cond_avg", "exp_points"]]
        .rename(columns={"cond_avg": "baseline_avg", "exp_points": "baseline_points"})
        .merge(
            candidate[KEY + ["cond_avg", "exp_points"]].rename(
                columns={"cond_avg": "candidate_avg", "exp_points": "candidate_points"}
            ),
            on=KEY,
            validate="one_to_one",
        )
        .merge(
            targets[KEY + ["meaningful", "avg", "points"]],
            on=KEY,
            validate="one_to_one",
        )
        .merge(
            snapshots[["player_key", "origin_year", "total_games", "career_best"]],
            on=["player_key", "origin_year"],
            validate="many_to_one",
        )
    )
    total_games = pd.to_numeric(frame["total_games"], errors="coerce").fillna(0.0)
    career_best = pd.to_numeric(frame["career_best"], errors="coerce").fillna(0.0)
    established = total_games >= 50
    low_ceiling = established & (career_best < 65.0)
    cohorts = {
        "all": pd.Series(True, index=frame.index),
        "established_all": established,
        "established_low_ceiling": low_ceiling,
        "established_other": established & ~low_ceiling,
        "under_50": total_games < 50,
        "zero_history": total_games == 0,
    }

    report_scores: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for cohort, mask in cohorts.items():
        part = frame.loc[mask]
        base = score(part, "baseline")
        cand = score(part, "candidate")
        change = pct_change(base, cand)
        report_scores[cohort] = {"task009": base, "task012": cand, "change_pct": change}
        rows.extend(
            [
                {"cohort": cohort, "model": "task009", **base},
                {"cohort": cohort, "model": "task012", **cand},
            ]
        )
    pd.DataFrame(rows).to_csv(args.out / "metrics_by_cohort.csv", index=False)

    bootstrap = player_bootstrap(frame.loc[low_ceiling])
    (args.out / "low_ceiling_bootstrap.json").write_text(
        json.dumps(bootstrap, indent=2, sort_keys=True) + "\n"
    )

    low = report_scores["established_low_ceiling"]["change_pct"]
    established_change = report_scores["established_all"]["change_pct"]
    overall = report_scores["all"]["change_pct"]
    under = report_scores["under_50"]["change_pct"]
    gates = {
        "event_games_threshold_outputs_identical": max(invariant_differences.values()) <= 1e-12,
        "low_ceiling_conditional_avg_mae_improves": low["conditional_avg_mae"] < 0,
        "low_ceiling_points_mae_improves": low["points_mae"] < 0,
        "established_no_metric_regresses_over_0_5pct": all(value <= 0.5 for value in established_change.values()),
        "overall_no_metric_regresses_over_0_5pct": all(value <= 0.5 for value in overall.values()),
        "under_50_no_metric_regresses_over_0_5pct": all(value <= 0.5 for value in under.values()),
        "bootstrap_median_conditional_avg_improves": (
            bootstrap["conditional_avg_mae_difference"]["median"] < 0
        ),
        "bootstrap_median_points_improves": bootstrap["points_mae_difference"]["median"] < 0,
    }
    report = {
        "status": "pass" if all(gates.values()) else "reject",
        "hypothesis": "an evidence-weighted demonstrated-ceiling interaction improves conditional averages for established low-ceiling players",
        "single_change": "conditional-average feature representation",
        "gates": gates,
        "invariant_max_absolute_differences": invariant_differences,
        "scores": report_scores,
        "bootstrap": bootstrap,
        "rows": int(len(frame)),
        "low_ceiling_rows": int(low_ceiling.sum()),
        "low_ceiling_players": int(frame.loc[low_ceiling, "player_key"].nunique()),
    }
    (args.out / "final_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
