from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error

from task003q_hybrid import blend_predictions

KEY = ["player_key", "origin_year", "lead"]


def score(predictions: pd.DataFrame, targets: pd.DataFrame) -> dict[str, float]:
    frame = predictions.merge(targets, on=KEY, validate="one_to_one")
    return {
        "brier": brier_score_loss(frame["meaningful"], frame["p_meaningful"]),
        "log_loss": log_loss(frame["meaningful"], np.clip(frame["p_meaningful"], 0.001, 0.999), labels=[0, 1]),
        "games_mae": mean_absolute_error(frame["games"], frame["exp_games"]),
        "points_mae": mean_absolute_error(frame["points"], frame["exp_points"]),
    }


def changes(current: dict[str, float], hybrid: dict[str, float]) -> dict[str, float]:
    return {name: 100.0 * (hybrid[name] - current[name]) / current[name] for name in current}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    current = pd.read_csv(args.root / "current/vnext_predictions.csv")
    candidate = pd.read_csv(args.root / "candidate/vnext_predictions.csv")
    targets = pd.read_csv(args.root / "cohorts/targets.csv")
    snapshots = pd.read_csv(args.root / "cohorts/included_snapshots.csv")
    hybrid = blend_predictions(current, candidate, snapshots)
    hybrid.to_csv(args.out / "hybrid_predictions.csv", index=False)

    current_score = score(current, targets)
    candidate_score = score(candidate, targets)
    hybrid_score = score(hybrid, targets)
    summary = pd.DataFrame([
        {"model": "current", **current_score},
        {"model": "task003k", **candidate_score},
        {"model": "task003q", **hybrid_score},
    ])
    summary.to_csv(args.out / "metrics_summary.csv", index=False)

    detail = hybrid.merge(targets, on=KEY, validate="one_to_one").merge(
        snapshots[["player_key", "origin_year", "age"]],
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )
    current_detail = current.merge(targets, on=KEY, validate="one_to_one").merge(
        snapshots[["player_key", "origin_year", "age"]],
        on=["player_key", "origin_year"],
        validate="many_to_one",
    )

    slices = []
    for label, mask in {
        "age_28_29": (detail["age"] >= 28) & (detail["age"] < 30),
        "age_30_plus_lead_5": (detail["age"] >= 30) & (detail["lead"] == 5),
    }.items():
        h = detail.loc[mask, KEY + ["p_meaningful", "exp_games", "exp_points"]]
        c = current_detail.loc[mask, KEY + ["p_meaningful", "exp_games", "exp_points"]]
        t = targets.merge(detail.loc[mask, KEY], on=KEY, validate="one_to_one")
        cs = score(c, t)
        hs = score(h, t)
        slices.append({"slice": label, "n": len(h), **changes(cs, hs)})
    slice_frame = pd.DataFrame(slices)
    slice_frame.to_csv(args.out / "slice_changes_pct.csv", index=False)

    pooled_change = changes(current_score, hybrid_score)
    pooled_ok = all(value < 0 for value in pooled_change.values())
    age_28_29 = slice_frame[slice_frame["slice"] == "age_28_29"].iloc[0]
    age_28_29_ok = sum(float(age_28_29[name]) < 0 for name in ["brier", "log_loss", "games_mae", "points_mae"]) >= 3
    older = slice_frame[slice_frame["slice"] == "age_30_plus_lead_5"].iloc[0]
    older_ok = all(float(older[name]) <= 3.0 for name in ["brier", "games_mae", "points_mae"])
    status = "pass" if pooled_ok and age_28_29_ok and older_ok else "fail"
    report = {
        "status": status,
        "pooled_change_pct": pooled_change,
        "pooled_ok": pooled_ok,
        "age_28_29_ok": age_28_29_ok,
        "age_30_plus_lead_5_ok": older_ok,
    }
    (args.out / "final_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
