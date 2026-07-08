from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, roc_auc_score

KEY = ["player_key", "origin_year", "lead"]
METRICS = ("brier", "log_loss", "games_mae", "points_mae")


def score(frame: pd.DataFrame) -> dict[str, float]:
    actual = frame["meaningful"].astype(int).to_numpy()
    probability = np.clip(frame["p_meaningful"].to_numpy(float), 0.001, 0.999)
    result = {
        "n": int(len(frame)),
        "players": int(frame["player_key"].nunique()),
        "actual_rate": float(actual.mean()),
        "predicted_rate": float(probability.mean()),
        "probability_std": float(probability.std(ddof=0)),
        "probability_range": float(probability.max() - probability.min()),
        "probability_unique_6dp": int(np.unique(np.round(probability, 6)).size),
        "brier": float(brier_score_loss(actual, probability)),
        "log_loss": float(log_loss(actual, probability, labels=[0, 1])),
        "games_mae": float(mean_absolute_error(frame["games"], frame["exp_games"])),
        "points_mae": float(mean_absolute_error(frame["points"], frame["exp_points"])),
    }
    result["auc"] = (
        float(roc_auc_score(actual, probability))
        if len(np.unique(actual)) > 1
        else float("nan")
    )
    return result


def pct_change(baseline: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    return {
        metric: 100.0 * (candidate[metric] - baseline[metric]) / baseline[metric]
        for metric in METRICS
    }


def scores_from_metrics(metrics: pd.DataFrame) -> dict[str, dict[str, dict[str, float]]]:
    scores: dict[str, dict[str, dict[str, float]]] = {}
    for cohort in ("all", "zero_history", "played_history"):
        part = (
            metrics.loc[metrics["cohort"] == cohort]
            .drop(columns="cohort")
            .set_index("model")
        )
        if set(part.index) != {"task003q", "task009"}:
            raise ValueError(f"{cohort} metrics must contain task003q and task009")
        base = {key: float(part.loc["task003q", key]) for key in part.columns}
        cand = {key: float(part.loc["task009", key]) for key in part.columns}
        scores[cohort] = {
            "task003q": base,
            "task009": cand,
            "change_pct": pct_change(base, cand),
        }
    return scores


def block_bootstrap(frame: pd.DataFrame, draws: int = 1000) -> dict[str, dict[str, float]]:
    grouped = []
    for _, group in frame.groupby("player_key", sort=True):
        actual = group["meaningful"].to_numpy(float)
        grouped.append(
            {
                "n": len(group),
                "base_brier": float(np.square(group["baseline_p"].to_numpy(float) - actual).sum()),
                "cand_brier": float(np.square(group["candidate_p"].to_numpy(float) - actual).sum()),
                "base_points": float(np.abs(group["baseline_points"] - group["points"]).sum()),
                "cand_points": float(np.abs(group["candidate_points"] - group["points"]).sum()),
            }
        )
    values = pd.DataFrame(grouped)
    rng = np.random.default_rng(9009)
    brier = []
    points = []
    for _ in range(draws):
        sample = values.iloc[rng.integers(0, len(values), len(values))]
        n = float(sample["n"].sum())
        brier.append(float((sample["cand_brier"].sum() - sample["base_brier"].sum()) / n))
        points.append(float((sample["cand_points"].sum() - sample["base_points"].sum()) / n))

    def interval(samples: list[float]) -> dict[str, float]:
        q = np.quantile(samples, [0.025, 0.5, 0.975])
        return {"lower": float(q[0]), "median": float(q[1]), "upper": float(q[2])}

    return {"brier_difference": interval(brier), "points_mae_difference": interval(points)}


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
        raise ValueError("baseline and candidate keys differ")

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
        .merge(targets[KEY + ["meaningful", "games", "points"]], on=KEY, validate="one_to_one")
        .merge(
            snapshots[["player_key", "origin_year", "total_games", "tenure", "draft_type", "pick"]],
            on=["player_key", "origin_year"],
            validate="many_to_one",
        )
    )
    frame["zero_history"] = pd.to_numeric(frame["total_games"], errors="coerce").fillna(0).eq(0)

    def model_frame(prefix: str, subset: pd.DataFrame) -> pd.DataFrame:
        return subset.assign(
            p_meaningful=subset[f"{prefix}_p"],
            exp_games=subset[f"{prefix}_games"],
            exp_points=subset[f"{prefix}_points"],
        )

    rows: list[dict[str, Any]] = []
    for cohort, subset in {
        "all": frame,
        "zero_history": frame[frame["zero_history"]],
        "played_history": frame[~frame["zero_history"]],
    }.items():
        baseline_score = score(model_frame("baseline", subset))
        candidate_score = score(model_frame("candidate", subset))
        rows.append({"cohort": cohort, "model": "task003q", **baseline_score})
        rows.append({"cohort": cohort, "model": "task009", **candidate_score})
    metrics = pd.DataFrame(rows)
    metrics.to_csv(args.out / "metrics_by_cohort.csv", index=False)

    zero = frame[frame["zero_history"]]
    lead_rows = []
    for lead, subset in zero.groupby("lead"):
        base = score(model_frame("baseline", subset))
        cand = score(model_frame("candidate", subset))
        lead_rows.append({"lead": int(lead), "n": len(subset), **pct_change(base, cand)})
    pd.DataFrame(lead_rows).to_csv(args.out / "zero_history_changes_by_lead.csv", index=False)

    scores = scores_from_metrics(metrics)
    bootstrap = block_bootstrap(zero)
    (args.out / "zero_history_bootstrap.json").write_text(
        json.dumps(bootstrap, indent=2, sort_keys=True) + "\n"
    )

    zero_change = scores["zero_history"]["change_pct"]
    overall_change = scores["all"]["change_pct"]
    played_change = scores["played_history"]["change_pct"]
    separation = (
        scores["zero_history"]["task009"]["probability_std"]
        > scores["zero_history"]["task003q"]["probability_std"]
    )
    gates = {
        "zero_brier_improves": zero_change["brier"] < 0,
        "zero_log_loss_improves": zero_change["log_loss"] < 0,
        "zero_games_mae_within_1pct": zero_change["games_mae"] <= 1.0,
        "zero_points_mae_within_1pct": zero_change["points_mae"] <= 1.0,
        "overall_no_metric_regresses_over_0_5pct": all(v <= 0.5 for v in overall_change.values()),
        "played_no_metric_regresses_over_1pct": all(v <= 1.0 for v in played_change.values()),
        "zero_probability_separation_increases": bool(separation),
        "bootstrap_median_brier_improves": bootstrap["brier_difference"]["median"] < 0,
    }
    report = {
        "status": "pass" if all(gates.values()) else "reject",
        "hypothesis": "origin-safe zero-history state features improve event discrimination",
        "single_change": "meaningful-event feature representation",
        "gates": gates,
        "scores": scores,
        "bootstrap": bootstrap,
        "rows": int(len(frame)),
        "zero_history_rows": int(frame["zero_history"].sum()),
        "zero_history_players": int(zero["player_key"].nunique()),
    }
    (args.out / "final_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
