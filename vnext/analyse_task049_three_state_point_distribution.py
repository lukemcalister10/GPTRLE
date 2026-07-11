"""TASK-049 audit for the locked three-state point-distribution hypothesis."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from analyse_task048_ridge_uncertainty import (
    EXPECTED_FOLDS,
    EXPECTED_ROWS,
    EXPECTED_SNAPSHOTS,
    KEY,
    QCOLS,
    QUANTILES,
    calibration,
    interval_coverage,
    pinball,
    prior_history,
    realised_cohort,
    summarise_pinball,
    validate_quantiles,
)

BOOTSTRAP_SEED = 49049
BOOTSTRAP_REPLICATIONS = 2000


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_predictions(path: Path, model: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = sorted(set(KEY + [*QCOLS]) - set(df.columns))
    if missing:
        raise ValueError(f"{path} missing required prediction columns: {missing}")
    if df.duplicated(KEY).any():
        sample = df.loc[df.duplicated(KEY, keep=False), KEY].head(10).to_dict("records")
        raise ValueError(f"{model} duplicate prediction keys: {sample}")
    return df.assign(model=model)


def assert_identical_keys(*frames: pd.DataFrame) -> None:
    first = frames[0][KEY].sort_values(KEY).reset_index(drop=True)
    for frame in frames[1:]:
        if not first.equals(frame[KEY].sort_values(KEY).reset_index(drop=True)):
            raise ValueError("prediction/target keys differ")


def compare_non_quantile_outputs(base: pd.DataFrame, cand: pd.DataFrame) -> pd.DataFrame:
    common = [c for c in base.columns if c in cand.columns and c not in QCOLS + ["model"]]
    b = base[common].sort_values(KEY).reset_index(drop=True)
    c = cand[common].sort_values(KEY).reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    for col in common:
        if pd.api.types.is_numeric_dtype(b[col]) and pd.api.types.is_numeric_dtype(c[col]):
            delta = np.abs(b[col].to_numpy(float) - c[col].to_numpy(float))
            max_abs = float(np.nanmax(delta)) if len(delta) else 0.0
            changed = int((delta > 1e-12).sum())
            rows.append({"column": col, "changed_rows": changed, "max_abs_delta": max_abs})
        else:
            neq = ~(b[col].fillna("__NA__").astype(str) == c[col].fillna("__NA__").astype(str))
            rows.append({"column": col, "changed_rows": int(neq.sum()), "max_abs_delta": np.nan})
    return pd.DataFrame(rows)


def row_weighted_diffs(wide: pd.DataFrame) -> dict[str, float]:
    diffs = {}
    for col, tau in QUANTILES:
        diff = pinball(wide.points, wide[f"{col}_task049"], tau) - pinball(
            wide.points, wide[f"{col}_task047"], tau
        )
        diffs[col] = float(diff.mean())
    diffs["primary_mean_pinball"] = float(np.mean([diffs[col] for col, _ in QUANTILES]))
    return diffs


def bootstrap_ci(wide: pd.DataFrame, reps: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    blocks = []
    for player, block in wide.groupby("player_key", sort=True):
        record: dict[str, Any] = {"player_key": player, "row_count": int(len(block))}
        row_primary_terms = []
        for col, tau in QUANTILES:
            diff = pinball(block.points, block[f"{col}_task049"], tau) - pinball(
                block.points, block[f"{col}_task047"], tau
            )
            record[col] = float(diff.sum())
            row_primary_terms.append(diff)
        record["primary_mean_pinball"] = float(pd.concat(row_primary_terms, axis=1).mean(axis=1).sum())
        blocks.append(record)
    block_sums = pd.DataFrame(blocks).set_index("player_key")
    players = block_sums.index.to_numpy()
    observed = row_weighted_diffs(wide)
    rows = []
    for metric in ["primary_mean_pinball", *QCOLS]:
        draws = np.empty(reps)
        for i in range(reps):
            sample = rng.choice(players, size=len(players), replace=True)
            sampled = block_sums.loc[sample]
            draws[i] = float(sampled[metric].sum() / sampled.row_count.sum())
        rows.append(
            {
                "metric": metric,
                "observed_diff_task049_minus_task047": observed[metric],
                "bootstrap_seed": seed,
                "replications": reps,
                "median": float(np.quantile(draws, 0.5)),
                "ci_low": float(np.quantile(draws, 0.025)),
                "ci_high": float(np.quantile(draws, 0.975)),
            }
        )
    return pd.DataFrame(rows)


def pooled_statistic_invariant(pinball_overall: pd.DataFrame, primary: pd.DataFrame, boot: pd.DataFrame) -> pd.DataFrame:
    rows = []
    p = primary.set_index("model").primary_mean_pinball_loss
    rows.append(
        {
            "metric": "primary_mean_pinball",
            "pooled_table_diff": float(p.task049 - p.task047),
            "bootstrap_observed_diff": float(
                boot.loc[boot.metric.eq("primary_mean_pinball"), "observed_diff_task049_minus_task047"].iloc[0]
            ),
        }
    )
    for col, _tau in QUANTILES:
        rows.append(
            {
                "metric": col,
                "pooled_table_diff": float(
                    pinball_overall.loc[pinball_overall["quantile"].eq(col), "abs_diff_task049_minus_task047"].iloc[0]
                ),
                "bootstrap_observed_diff": float(
                    boot.loc[boot.metric.eq(col), "observed_diff_task049_minus_task047"].iloc[0]
                ),
            }
        )
    out = pd.DataFrame(rows)
    out["abs_delta"] = (out.pooled_table_diff - out.bootstrap_observed_diff).abs()
    return out


def diff_table(summary: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    piv = summary.pivot_table(index=groups + ["quantile", "tau"], columns="model", values="pinball_loss").reset_index()
    piv["abs_diff_task049_minus_task047"] = piv.task049 - piv.task047
    piv["pct_diff_task049_minus_task047"] = piv["abs_diff_task049_minus_task047"] / piv.task047
    return piv


def artifact_failure_checks(prediction_path: Path) -> dict[str, Any]:
    artifact_dir = prediction_path.parent
    manifest_path = artifact_dir / "prediction_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing prediction manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    fold_failures_path = artifact_dir / "fold_failures.csv"
    fold_failure_rows = int(manifest.get("fold_failure_rows", -1))
    if fold_failures_path.exists():
        fold_failure_rows = int(len(pd.read_csv(fold_failures_path)))
    return {
        "artifact_dir": str(artifact_dir),
        "manifest_path": str(manifest_path),
        "target_failure_rows": int(manifest.get("target_failure_rows", -1)),
        "fold_failure_rows": fold_failure_rows,
        "prediction_rows": int(manifest.get("prediction_rows", -1)),
        "included_snapshot_rows": int(manifest.get("included_snapshot_rows", -1)),
    }


def predicted_vs_realised_state_frequency(allp: pd.DataFrame, mr: pd.DataFrame) -> pd.DataFrame:
    pred_state = mr.groupby(["origin_year", "lead"], as_index=False).agg(
        predicted_zero_frequency=("p_zero_state", "mean"),
        predicted_short_frequency=("p_short_state", "mean"),
        predicted_meaningful_frequency=("p_meaningful_state", "mean"),
    )
    realised = (
        allp[allp.model.eq("task049")]
        .groupby(["origin_year", "lead"], as_index=False)
        .agg(
            n=("player_key", "size"),
            realised_zero_frequency=("realised_cohort", lambda s: float((s == "zero_game_zero_point").mean())),
            realised_short_frequency=("realised_cohort", lambda s: float((s == "one_to_five_positive_points").mean())),
            realised_meaningful_frequency=("realised_cohort", lambda s: float((s == "meaningful_six_plus").mean())),
        )
    )
    return pred_state.merge(realised, on=["origin_year", "lead"], validate="one_to_one")


def short_season_calibration(allp: pd.DataFrame, mr: pd.DataFrame) -> pd.DataFrame:
    frame = allp[allp.model.eq("task049")].merge(mr[KEY + ["p_short_state"]], on=KEY, validate="one_to_one")
    rows = []
    for groups in [[], ["lead"], ["broad_position"], ["prior_history_cohort"]]:
        grouped = frame.groupby(groups, dropna=False) if groups else [((), frame)]
        for keys, g in grouped:
            if not isinstance(keys, tuple):
                keys = (keys,)
            rec = {"slice": "overall" if not groups else "+".join(groups), **dict(zip(groups, keys))}
            actual_short = g.realised_cohort.eq("one_to_five_positive_points")
            short_games = g.loc[actual_short, "games"].astype(float)
            short_rates = g.loc[actual_short, "points"].astype(float) / short_games.replace(0, np.nan)
            rec.update(
                {
                    "n": int(len(g)),
                    "realised_short_frequency": float(actual_short.mean()),
                    "predicted_short_frequency": float(g.p_short_state.mean()),
                    "frequency_error": float(g.p_short_state.mean() - actual_short.mean()),
                    "realised_short_rows": int(actual_short.sum()),
                    "realised_short_mean_games": float(short_games.mean()) if len(short_games) else np.nan,
                    "realised_short_mean_rate": float(short_rates.mean()) if len(short_rates) else np.nan,
                }
            )
            rows.append(rec)
    return pd.DataFrame(rows)


def write_outputs(tables: dict[str, pd.DataFrame], summary: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, df in tables.items():
        path = out / name
        df.to_csv(path, index=False, lineterminator="\n")
        artifacts[name] = {"rows": int(len(df)), "sha256": sha256_path(path), "bytes": path.stat().st_size}
    summary["artifacts"] = artifacts
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (out / "README.md").write_text("# TASK-049 three-state point distribution\n\nLocked audit artifacts. See `summary.json` and CSV evidence tables.\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--moment-reconciliation", type=Path, required=True)
    parser.add_argument("--short-evidence", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    base = load_predictions(args.baseline, "task047")
    cand = load_predictions(args.candidate, "task049")
    targets = pd.read_csv(args.targets)[KEY + ["games", "points"]]
    features = pd.read_csv(args.features)
    if targets.duplicated(KEY).any():
        raise ValueError("targets contain duplicate keys")
    assert_identical_keys(base, cand, targets)

    non_quantile_comparison = compare_non_quantile_outputs(base, cand)
    feat = features[[c for c in ["key", "origin_year", "position", "total_games"] if c in features.columns]].rename(columns={"key": "player_key"})
    allp = pd.concat([base, cand], ignore_index=True).merge(targets, on=KEY, validate="many_to_one").merge(feat, on=["player_key", "origin_year"], how="left", validate="many_to_one")
    allp["broad_position"] = allp.get("position", pd.Series("unknown", index=allp.index)).fillna("unknown").astype(str)
    allp["prior_history_cohort"] = prior_history(allp.get("total_games", pd.Series(0, index=allp.index)))
    allp["realised_cohort"] = realised_cohort(allp.games, allp.points)

    primary = summarise_pinball(allp, []).groupby("model").pinball_loss.mean().reset_index(name="primary_mean_pinball_loss")
    pinball_overall = diff_table(summarise_pinball(allp, []), [])
    tables: dict[str, pd.DataFrame] = {
        "primary_pinball.csv": primary,
        "pinball_overall.csv": pinball_overall,
        "pinball_by_lead.csv": diff_table(summarise_pinball(allp, ["lead"]), ["lead"]),
        "fold_level_differences.csv": diff_table(summarise_pinball(allp, ["origin_year", "lead"]), ["origin_year", "lead"]),
        "non_uncertainty_output_comparison.csv": non_quantile_comparison,
    }
    for name, groups in [("overall", []), ("by_lead", ["lead"]), ("by_position", ["broad_position"]), ("by_prior_history", ["prior_history_cohort"]), ("by_realised_cohort", ["realised_cohort"] )]:
        tables[f"quantile_calibration_{name}.csv"] = calibration(allp, groups)
        tables[f"interval_coverage_{name}.csv"] = interval_coverage(allp, groups)

    structural = []
    for (model, lead), g in allp.groupby(["model", "lead"]):
        rec = {
            "model": model,
            "lead": lead,
            "n": len(g),
            "actual_zero_game_zero_point_rows": int((g.realised_cohort == "zero_game_zero_point").sum()),
            "actual_one_to_five_positive_points_rows": int((g.realised_cohort == "one_to_five_positive_points").sum()),
            "meaningful_six_plus_rows": int((g.realised_cohort == "meaningful_six_plus").sum()),
        }
        for col, _ in QUANTILES:
            rec[f"{col}_zero_proportion"] = float((g[col].astype(float).abs() <= 1e-12).mean())
        structural.append(rec)
    tables["realised_state_cohorts_by_lead.csv"] = pd.DataFrame(structural)
    tables["one_to_five_cohort_pinball.csv"] = diff_table(summarise_pinball(allp[allp.realised_cohort.eq("one_to_five_positive_points")], []), [])
    tables["one_to_five_cohort_calibration.csv"] = calibration(allp[allp.realised_cohort.eq("one_to_five_positive_points")], [])

    mr = pd.read_csv(args.moment_reconciliation)
    short_evidence = pd.read_csv(args.short_evidence)
    tables["state_probability_reconciliation.csv"] = mr
    tables["short_season_evidence.csv"] = short_evidence
    tables["predicted_vs_realised_state_frequency.csv"] = predicted_vs_realised_state_frequency(allp, mr)
    tables["short_season_calibration.csv"] = short_season_calibration(allp, mr)

    wide = base.merge(cand, on=KEY, suffixes=("_task047", "_task049")).merge(targets, on=KEY, validate="one_to_one")
    boot = bootstrap_ci(wide, reps=BOOTSTRAP_REPLICATIONS, seed=BOOTSTRAP_SEED)
    tables["bootstrap_confidence_intervals.csv"] = boot
    tables["bootstrap_pooled_statistic_invariant.csv"] = pooled_statistic_invariant(pinball_overall, primary, boot)

    baseline_artifacts = artifact_failure_checks(args.baseline)
    candidate_artifacts = artifact_failure_checks(args.candidate)
    qv = [validate_quantiles(base, "task047"), validate_quantiles(cand, "task049")]
    integrity_rows = [
        {"check": "row_count_per_model", "passed": bool(allp.groupby("model").size().eq(EXPECTED_ROWS).all()), "detail": json.dumps({str(k): int(v) for k, v in allp.groupby("model").size().items()})},
        {"check": "player_origin_snapshots", "passed": int(targets[KEY[:2]].drop_duplicates().shape[0]) == EXPECTED_SNAPSHOTS, "detail": str(int(targets[KEY[:2]].drop_duplicates().shape[0]))},
        {"check": "legal_folds", "passed": int(targets[["origin_year", "lead"]].drop_duplicates().shape[0]) == EXPECTED_FOLDS, "detail": str(int(targets[["origin_year", "lead"]].drop_duplicates().shape[0]))},
        {"check": "non_uncertainty_outputs_unchanged", "passed": bool(non_quantile_comparison.changed_rows.eq(0).all()), "detail": "compared every common baseline/candidate field except the six point quantiles"},
        {"check": "moment_reconciliation_max_abs_delta_le_1e-8", "passed": float(mr.abs_delta.max()) <= 1e-8, "detail": str(float(mr.abs_delta.max()))},
        {"check": "bootstrap_observed_equals_pooled_tables", "passed": bool(tables["bootstrap_pooled_statistic_invariant.csv"].abs_delta.le(1e-10).all()), "detail": str(float(tables["bootstrap_pooled_statistic_invariant.csv"].abs_delta.max()))},
    ]
    for model, checks in [("task047", baseline_artifacts), ("task049", candidate_artifacts)]:
        integrity_rows.extend(
            [
                {"check": f"{model}_artifact_target_failures", "passed": checks["target_failure_rows"] == 0, "detail": json.dumps(checks, sort_keys=True)},
                {"check": f"{model}_artifact_fold_failures", "passed": checks["fold_failure_rows"] == 0, "detail": json.dumps(checks, sort_keys=True)},
                {"check": f"{model}_artifact_prediction_rows", "passed": checks["prediction_rows"] == EXPECTED_ROWS, "detail": json.dumps(checks, sort_keys=True)},
            ]
        )
    integrity_rows.extend(
        [{"check": f"{r['model']}_quantiles_non_negative", "passed": r["negative_quantile_values"] == 0, "detail": str(r["negative_quantile_values"])} for r in qv]
        + [{"check": f"{r['model']}_quantiles_non_crossing", "passed": r["crossing_rows"] == 0, "detail": str(r["crossing_rows"])} for r in qv]
    )
    tables["integrity_checks.csv"] = pd.DataFrame(integrity_rows)

    p = primary.set_index("model").primary_mean_pinball_loss
    diffpct = float((p.task049 - p.task047) / p.task047)
    max_worse = float(pinball_overall.pct_diff_task049_minus_task047.max())
    cal = tables["quantile_calibration_overall.csv"]
    cal_base = float(cal[cal.model.eq("task047")].absolute_calibration_error.mean())
    cal_cand = float(cal[cal.model.eq("task049")].absolute_calibration_error.mean())
    cov = tables["interval_coverage_overall.csv"]
    cand_cov = cov[cov.model.eq("task049")].set_index("interval")
    lead_cov = tables["interval_coverage_by_lead.csv"]
    lead_central = lead_cov[lead_cov.model.eq("task049") & lead_cov.interval.isin(["q25_q75", "q10_q90"])]
    subgroup_cov = pd.concat([tables["interval_coverage_by_position.csv"], tables["interval_coverage_by_prior_history.csv"]])
    subgroup_cov = subgroup_cov[subgroup_cov.model.eq("task049") & subgroup_cov.n.ge(200) & subgroup_cov.interval.isin(["q25_q75", "q10_q90"])]
    onefive = tables["one_to_five_cohort_pinball.csv"]
    onefive_improved = int((onefive.abs_diff_task049_minus_task047 < 0).sum())
    onefive_bad = bool((onefive.pct_diff_task049_minus_task047 > 0.05).any())
    short_support = bool(mr.p_short_state.gt(0).all() and np.isfinite(mr.p_short_state).all() and short_evidence.n_short.gt(0).all())
    bp = boot[boot.metric.eq("primary_mean_pinball")].iloc[0]
    gates = pd.DataFrame(
        [
            {"gate": 1, "passed": diffpct <= -0.01 and bp["median"] < 0 and bp.ci_high <= p.task047 * 0.01, "detail": f"primary pct diff={diffpct:.6f}; bootstrap median={bp['median']:.6f}; CI=({bp.ci_low:.6f},{bp.ci_high:.6f})"},
            {"gate": 2, "passed": max_worse <= 0.02, "detail": f"max quantile worsening={max_worse:.6f}"},
            {"gate": 3, "passed": cal_cand <= 0.05 and cal_cand <= cal_base * 0.75, "detail": f"candidate={cal_cand:.6f}; baseline={cal_base:.6f}"},
            {"gate": 4, "passed": 0.46 <= cand_cov.loc["q25_q75"].coverage <= 0.54 and 0.76 <= cand_cov.loc["q10_q90"].coverage <= 0.84, "detail": f"q25-q75={cand_cov.loc['q25_q75'].coverage:.6f}; q10-q90={cand_cov.loc['q10_q90'].coverage:.6f}"},
            {"gate": 5, "passed": not (lead_central.absolute_coverage_error > 0.08).any(), "detail": f"max={float(lead_central.absolute_coverage_error.max()):.6f}"},
            {"gate": 6, "passed": not (subgroup_cov.absolute_coverage_error > 0.12).any(), "detail": f"max={float(subgroup_cov.absolute_coverage_error.max()):.6f}"},
            {"gate": 7, "passed": short_support and onefive_improved >= 4 and not onefive_bad, "detail": f"short_support={short_support}; improved_quantiles={onefive_improved}; any_worse_gt_5pct={onefive_bad}"},
            {"gate": 8, "passed": bool(non_quantile_comparison.changed_rows.eq(0).all()) and float(mr.abs_delta.max()) <= 1e-8, "detail": f"unchanged={bool(non_quantile_comparison.changed_rows.eq(0).all())}; max_mean_delta={float(mr.abs_delta.max()):.12g}"},
            {"gate": 9, "passed": bool(tables["integrity_checks.csv"].passed.all()), "detail": "see integrity_checks.csv"},
        ]
    )
    tables["acceptance_gates.csv"] = gates

    summary = {
        "task": "TASK-049-three-state-point-distribution",
        "accepted_uncertainty_outputs": bool(gates.passed.all()),
        "uncertainty_status": "accepted" if bool(gates.passed.all()) else "blocked",
        "failed_gates": gates.loc[~gates.passed, "gate"].astype(int).tolist(),
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replications": BOOTSTRAP_REPLICATIONS,
        "rows_per_model": {str(k): int(v) for k, v in allp.groupby("model").size().items()},
        "player_origin_snapshots": int(targets[KEY[:2]].drop_duplicates().shape[0]),
        "folds": int(targets[["origin_year", "lead"]].drop_duplicates().shape[0]),
        "target_and_fold_failures": {"task047": baseline_artifacts, "task049": candidate_artifacts},
        "primary_mean_pinball": primary.to_dict("records"),
        "input_hashes": {"baseline": sha256_path(args.baseline), "candidate": sha256_path(args.candidate), "targets": sha256_path(args.targets), "features": sha256_path(args.features), "moment_reconciliation": sha256_path(args.moment_reconciliation), "short_evidence": sha256_path(args.short_evidence)},
        "recommended_next_hypothesis": None if bool(gates.passed.all()) else "Audit whether the moment-preserving short-season mixture needs a predeclared distribution-shape repair; do not tune TASK-049.",
    }
    write_outputs(tables, summary, args.out)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
