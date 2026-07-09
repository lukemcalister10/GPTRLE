"""TASK-048 audit of unchanged TASK-047 Ridge point-quantile distributions."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEY = ["player_key", "origin_year", "lead"]
QUANTILES = [
    ("points_q10", 0.10),
    ("points_q25", 0.25),
    ("points_q50", 0.50),
    ("points_q75", 0.75),
    ("points_q90", 0.90),
    ("points_q97", 0.97),
]
QCOLS = [q for q, _ in QUANTILES]
BOOTSTRAP_SEED = 48047
BOOTSTRAP_REPLICATIONS = 2000
EXPECTED_ROWS = 20094
EXPECTED_SNAPSHOTS = 5622
EXPECTED_FOLDS = 25


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_predictions(path: Path, model: str) -> pd.DataFrame:
    need = KEY + ["p_meaningful", "exp_games", "cond_games", "cond_avg", "exp_points", *QCOLS]
    df = pd.read_csv(path)
    missing = sorted(set(need) - set(df.columns))
    if missing:
        raise ValueError(f"{path} missing required prediction columns: {missing}")
    out = df[need].copy()
    out["model"] = model
    return out


def prior_history(total_games: pd.Series) -> pd.Series:
    games = pd.to_numeric(total_games, errors="coerce").fillna(0)
    return np.select(
        [games.eq(0), games.lt(50)],
        ["zero_prior_games", "under_50_prior_games"],
        default="50_plus_prior_games",
    )


def realised_cohort(games: pd.Series, points: pd.Series) -> pd.Series:
    g = pd.to_numeric(games, errors="coerce").fillna(0)
    p = pd.to_numeric(points, errors="coerce").fillna(0)
    return np.select(
        [g.eq(0) & p.eq(0), g.between(1, 5, inclusive="both") & p.gt(0), g.ge(6)],
        ["zero_game_zero_point", "one_to_five_positive_points", "meaningful_six_plus"],
        default="other",
    )


def pinball(y: pd.Series, q: pd.Series, tau: float) -> pd.Series:
    diff = y.astype(float) - q.astype(float)
    return np.maximum(tau * diff, (tau - 1.0) * diff)


def assert_same_keys(base: pd.DataFrame, cand: pd.DataFrame, target: pd.DataFrame) -> None:
    for name, df in [("baseline", base), ("candidate", cand), ("targets", target)]:
        dup = int(df.duplicated(KEY).sum())
        if dup:
            raise ValueError(f"{name} has duplicate prediction keys: {dup}")
    b = base[KEY].sort_values(KEY).reset_index(drop=True)
    c = cand[KEY].sort_values(KEY).reset_index(drop=True)
    t = target[KEY].sort_values(KEY).reset_index(drop=True)
    if not b.equals(c) or not b.equals(t):
        raise ValueError("prediction keys are not identical between TASK-012, TASK-047 and targets")


def validate_quantiles(df: pd.DataFrame, model: str) -> dict[str, Any]:
    vals = df[QCOLS].astype(float).to_numpy()
    return {
        "model": model,
        "negative_quantile_values": int((vals < -1e-12).sum()),
        "crossing_rows": int((np.diff(vals, axis=1) < -1e-12).any(axis=1).sum()),
    }


def summarise_pinball(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    rows = []
    for keys, g in frame.groupby(groups, dropna=False) if groups else [((), frame)]:
        if not isinstance(keys, tuple):
            keys = (keys,)
        common = dict(zip(groups, keys))
        for col, tau in QUANTILES:
            for model, mg in g.groupby("model"):
                rows.append(
                    {
                        **common,
                        "model": model,
                        "quantile": col,
                        "tau": tau,
                        "n": len(mg),
                        "pinball_loss": float(pinball(mg.points, mg[col], tau).mean()),
                    }
                )
    return pd.DataFrame(rows)


def diff_table(summary: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    piv = summary.pivot_table(
        index=groups + ["quantile", "tau"], columns="model", values="pinball_loss"
    ).reset_index()
    piv["abs_diff_task047_minus_task012"] = piv["task047"] - piv["task012"]
    piv["pct_diff_task047_minus_task012"] = np.where(piv["task012"] != 0, piv["abs_diff_task047_minus_task012"] / piv["task012"], np.nan)
    return piv


def calibration(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    rows = []
    for keys, g in frame.groupby(groups, dropna=False) if groups else [((), frame)]:
        if not isinstance(keys, tuple):
            keys = (keys,)
        common = dict(zip(groups, keys))
        for col, tau in QUANTILES:
            for model, mg in g.groupby("model"):
                emp = float((mg.points.astype(float) <= mg[col].astype(float)).mean())
                rows.append(
                    {
                        **common,
                        "model": model,
                        "quantile": col,
                        "tau": tau,
                        "n": len(mg),
                        "empirical_p_actual_le_predicted_quantile": emp,
                        "signed_calibration_error": emp - tau,
                        "absolute_calibration_error": abs(emp - tau),
                        "tie_rule": "actual_points <= predicted_quantile",
                    }
                )
    return pd.DataFrame(rows)


def interval_coverage(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    intervals = [
        ("q25_q75", "points_q25", "points_q75", 0.50),
        ("q10_q90", "points_q10", "points_q90", 0.80),
        ("q10_q97_asymmetric", "points_q10", "points_q97", 0.87),
    ]
    rows = []
    for keys, g in frame.groupby(groups, dropna=False) if groups else [((), frame)]:
        if not isinstance(keys, tuple):
            keys = (keys,)
        common = dict(zip(groups, keys))
        for name, lo, hi, nom in intervals:
            for model, mg in g.groupby("model"):
                y = mg.points.astype(float)
                low = mg[lo].astype(float)
                high = mg[hi].astype(float)
                cov = float(((y >= low) & (y <= high)).mean())
                rows.append(
                    {
                        **common,
                        "model": model,
                        "interval": name,
                        "nominal_coverage": nom,
                        "n": len(mg),
                        "coverage": cov,
                        "coverage_error": cov - nom,
                        "absolute_coverage_error": abs(cov - nom),
                        "mean_width": float((high - low).mean()),
                    }
                )
    return pd.DataFrame(rows)


def row_weighted_pinball_differences(wide: pd.DataFrame) -> dict[str, float]:
    """Return pooled row-weighted TASK-047 minus TASK-012 pinball differences."""

    diffs: dict[str, float] = {}
    for col, tau in QUANTILES:
        diff = pinball(wide.points, wide[f"{col}_task047"], tau) - pinball(
            wide.points, wide[f"{col}_task012"], tau
        )
        diffs[col] = float(diff.mean())
    diffs["primary_mean_pinball"] = float(np.mean([diffs[col] for col, _ in QUANTILES]))
    return diffs


def bootstrap_ci(wide: pd.DataFrame, reps: int=BOOTSTRAP_REPLICATIONS, seed: int=BOOTSTRAP_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    player_blocks = []
    for player, block in wide.groupby("player_key", sort=True):
        block_sums: dict[str, float | int | str] = {
            "player_key": player,
            "row_count": int(len(block)),
        }
        quantile_diffs = []
        for col, tau in QUANTILES:
            diff = pinball(block.points, block[f"{col}_task047"], tau) - pinball(
                block.points, block[f"{col}_task012"], tau
            )
            block_sums[col] = float(diff.sum())
            quantile_diffs.append(diff)
        block_sums["primary_mean_pinball"] = float(pd.concat(quantile_diffs, axis=1).mean(axis=1).sum())
        player_blocks.append(block_sums)
    block_sums = pd.DataFrame(player_blocks)
    players = block_sums["player_key"].to_numpy()
    block_sums = block_sums.set_index("player_key")
    observed = row_weighted_pinball_differences(wide)
    rows = []
    for metric in ["primary_mean_pinball", *QCOLS]:
        draws = np.empty(reps)
        for i in range(reps):
            sample = rng.choice(players, size=len(players), replace=True)
            sampled = block_sums.loc[sample]
            draws[i] = float(sampled[metric].sum() / sampled["row_count"].sum())
        rows.append(
            {
                "metric": metric,
                "observed_diff_task047_minus_task012": observed[metric],
                "bootstrap_seed": seed,
                "replications": reps,
                "ci_low": float(np.quantile(draws, 0.025)),
                "ci_high": float(np.quantile(draws, 0.975)),
            }
        )
    return pd.DataFrame(rows)


def artifact_failure_checks(path: Path) -> dict[str, int | str]:
    artifact_dir = path.parent
    manifest_path = artifact_dir / "prediction_manifest.json"
    fold_failures_path = artifact_dir / "fold_failures.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing generated artifact manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if not fold_failures_path.exists():
        raise FileNotFoundError(f"missing generated fold failures artifact: {fold_failures_path}")
    fold_failures = pd.read_csv(fold_failures_path)
    return {
        "artifact_dir": str(artifact_dir),
        "target_failure_rows": int(manifest.get("target_failure_rows", -1)),
        "fold_failure_rows": int(len(fold_failures)),
        "prediction_rows": int(manifest.get("prediction_rows", -1)),
        "included_snapshot_rows": int(manifest.get("included_snapshot_rows", -1)),
    }


def build_audit(
    baseline: pd.DataFrame,
    candidate: pd.DataFrame,
    targets: pd.DataFrame,
    features: pd.DataFrame,
    baseline_artifact_checks: dict[str, int | str] | None = None,
    candidate_artifact_checks: dict[str, int | str] | None = None,
    bootstrap_replications: int = BOOTSTRAP_REPLICATIONS,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    target_cols = KEY + ["games", "points"]
    if not set(target_cols).issubset(targets.columns): raise ValueError("targets must include locked points and games columns")
    target = targets[target_cols].copy()
    assert_same_keys(baseline, candidate, target)
    feat = features[[c for c in ["key","origin_year","position","total_games"] if c in features.columns]].rename(columns={"key":"player_key"})
    allp = pd.concat([baseline,candidate], ignore_index=True).merge(target, on=KEY, validate="many_to_one")
    allp = allp.merge(feat, on=["player_key","origin_year"], how="left", validate="many_to_one")
    allp["broad_position"] = allp.get("position", pd.Series("unknown", index=allp.index)).fillna("unknown").astype(str)
    allp["prior_history_cohort"] = prior_history(allp.get("total_games", pd.Series(0, index=allp.index)))
    allp["realised_cohort"] = realised_cohort(allp.games, allp.points)
    overall = summarise_pinball(allp, [])
    primary = overall.groupby("model").pinball_loss.mean().reset_index(name="primary_mean_pinball_loss")
    pinball_overall = diff_table(overall, [])
    pinball_by_lead = diff_table(summarise_pinball(allp, ["lead"]), ["lead"])
    fold = diff_table(summarise_pinball(allp, ["origin_year", "lead"]), ["origin_year", "lead"])
    cal_overall = calibration(allp, [])
    cal_lead = calibration(allp, ["lead"])
    cal_pos = calibration(allp, ["broad_position"])
    cal_hist = calibration(allp, ["prior_history_cohort"])
    cov_overall = interval_coverage(allp, [])
    cov_lead = interval_coverage(allp, ["lead"])
    cov_pos = interval_coverage(allp, ["broad_position"])
    cov_hist = interval_coverage(allp, ["prior_history_cohort"])
    zrows=[]
    for (model,lead),g in allp.groupby(["model","lead"]):
        rec={"model":model,"lead":lead,"n":len(g),"actual_zero_game_zero_point_rows":int((g.realised_cohort=="zero_game_zero_point").sum()),"actual_one_to_five_positive_points_rows":int((g.realised_cohort=="one_to_five_positive_points").sum()),"meaningful_six_plus_rows":int((g.realised_cohort=="meaningful_six_plus").sum())}
        for col,_ in QUANTILES: rec[f"{col}_zero_proportion"] = float((g[col].astype(float).abs() <= 1e-12).mean())
        zrows.append(rec)
    structural=pd.DataFrame(zrows)
    cohort_pinball=diff_table(summarise_pinball(allp, ["realised_cohort"]), ["realised_cohort"])
    cohort_cal=calibration(allp,["realised_cohort"])
    wide = baseline.merge(candidate, on=KEY, suffixes=("_task012", "_task047")).merge(target, on=KEY)
    boot = bootstrap_ci(wide, reps=bootstrap_replications)
    pooled_diffs = row_weighted_pinball_differences(wide)
    pooled_primary_diff = float(
        primary.set_index("model").loc["task047", "primary_mean_pinball_loss"]
        - primary.set_index("model").loc["task012", "primary_mean_pinball_loss"]
    )
    bootstrap_invariant_rows = [
        {
            "metric": "primary_mean_pinball",
            "pooled_table_diff": pooled_primary_diff,
            "bootstrap_observed_diff": float(
                boot.loc[boot.metric.eq("primary_mean_pinball"), "observed_diff_task047_minus_task012"].iloc[0]
            ),
        }
    ]
    for col, _tau in QUANTILES:
        table_diff = float(
            pinball_overall.loc[
                pinball_overall["quantile"].eq(col), "abs_diff_task047_minus_task012"
            ].iloc[0]
        )
        bootstrap_invariant_rows.append(
            {
                "metric": col,
                "pooled_table_diff": table_diff,
                "bootstrap_observed_diff": float(
                    boot.loc[boot.metric.eq(col), "observed_diff_task047_minus_task012"].iloc[0]
                ),
            }
        )
    bootstrap_invariant = pd.DataFrame(bootstrap_invariant_rows)
    bootstrap_invariant["abs_delta"] = (
        bootstrap_invariant["pooled_table_diff"] - bootstrap_invariant["bootstrap_observed_diff"]
    ).abs()
    qv = [validate_quantiles(baseline, "task012"), validate_quantiles(candidate, "task047")]
    integrity = pd.DataFrame([
        {"check": "row_count_per_model", "passed": bool(allp.groupby("model").size().eq(EXPECTED_ROWS).all()), "detail": json.dumps({str(k): int(v) for k, v in allp.groupby("model").size().items()})},
        {"check": "player_origin_snapshots", "passed": int(target[KEY[:2]].drop_duplicates().shape[0]) == EXPECTED_SNAPSHOTS, "detail": str(int(target[KEY[:2]].drop_duplicates().shape[0]))},
        {"check": "legal_folds", "passed": int(target[["origin_year", "lead"]].drop_duplicates().shape[0]) == EXPECTED_FOLDS, "detail": str(int(target[["origin_year", "lead"]].drop_duplicates().shape[0]))},
        {"check": "target_points_used_directly", "passed": bool("points" in targets.columns), "detail": "joined targets.csv points column without reconstruction"},
        *[{"check": f"{r['model']}_quantiles_non_negative", "passed": r["negative_quantile_values"] == 0, "detail": str(r["negative_quantile_values"])} for r in qv],
        *[{"check": f"{r['model']}_quantiles_non_crossing", "passed": r["crossing_rows"] == 0, "detail": str(r["crossing_rows"])} for r in qv],
        {
            "check": "bootstrap_observed_equals_pooled_tables",
            "passed": bool((bootstrap_invariant.abs_delta <= 1e-10).all()),
            "detail": json.dumps(
                {
                    row.metric: row.abs_delta
                    for row in bootstrap_invariant.itertuples(index=False)
                },
                sort_keys=True,
            ),
        },
    ])
    for model, checks in [
        ("task012", baseline_artifact_checks),
        ("task047", candidate_artifact_checks),
    ]:
        if checks is not None:
            artifact_rows = pd.DataFrame(
                [
                    {
                        "check": f"{model}_artifact_target_failures",
                        "passed": int(checks["target_failure_rows"]) == 0,
                        "detail": json.dumps(checks, sort_keys=True),
                    },
                    {
                        "check": f"{model}_artifact_fold_failures",
                        "passed": int(checks["fold_failure_rows"]) == 0,
                        "detail": json.dumps(checks, sort_keys=True),
                    },
                    {
                        "check": f"{model}_artifact_prediction_rows",
                        "passed": int(checks["prediction_rows"]) == EXPECTED_ROWS,
                        "detail": json.dumps(checks, sort_keys=True),
                    },
                    {
                        "check": f"{model}_artifact_snapshot_rows",
                        "passed": int(checks["included_snapshot_rows"]) == EXPECTED_SNAPSHOTS,
                        "detail": json.dumps(checks, sort_keys=True),
                    },
                ]
            )
            integrity = pd.concat([integrity, artifact_rows], ignore_index=True)
    # Gates
    p = primary.set_index("model").primary_mean_pinball_loss
    primary_diff = (p.task047 - p.task012) / p.task012
    boot_primary = boot[boot.metric.eq("primary_mean_pinball")].iloc[0]
    indiv = pinball_overall.copy()
    max_indiv = float(indiv.pct_diff_task047_minus_task012.max())
    cand_cal = cal_overall[cal_overall.model.eq("task047")]
    mean_abs_cal = float(cand_cal.absolute_calibration_error.mean())
    cand_cov = cov_overall[cov_overall.model.eq("task047")].set_index("interval")
    lead_cov = cov_lead[cov_lead.model.eq("task047") & cov_lead.interval.isin(["q25_q75", "q10_q90"])]
    subgroup=pd.concat([cov_pos.assign(subgroup_type="position", subgroup=cov_pos.broad_position), cov_hist.assign(subgroup_type="prior_history", subgroup=cov_hist.prior_history_cohort)])
    subgroup=subgroup[(subgroup.model=="task047") & (subgroup.n>=200) & (subgroup.interval.isin(["q25_q75","q10_q90"]))]
    onefive = allp[(allp.model == "task047") & (allp.realised_cohort == "one_to_five_positive_points")]
    onefive_structural_incompatibility = bool(len(onefive) > 0)
    gate_rows=[
      (1, primary_diff <= .01 and boot_primary.ci_high <= p.task012 * .01, f"primary pct diff={primary_diff:.6f}; bootstrap absolute CI=({boot_primary.ci_low:.6f},{boot_primary.ci_high:.6f})"),
      (2, max_indiv <= .05, f"max individual quantile pct diff={max_indiv:.6f}"),
      (3, mean_abs_cal <= .03, f"mean abs calibration error={mean_abs_cal:.6f}"),
      (4, (0.47 <= cand_cov.loc['q25_q75'].coverage <= 0.53) and (0.77 <= cand_cov.loc['q10_q90'].coverage <= 0.83), f"q25-q75={cand_cov.loc['q25_q75'].coverage:.6f}; q10-q90={cand_cov.loc['q10_q90'].coverage:.6f}"),
      (5, not (lead_cov.absolute_coverage_error > .06).any(), f"max lead central interval abs coverage error={float(lead_cov.absolute_coverage_error.max()):.6f}"),
      (6, not (subgroup.absolute_coverage_error > .10).any(), f"max subgroup abs coverage error={float(subgroup.absolute_coverage_error.max()):.6f}"),
      (7, not onefive_structural_incompatibility, f"one-to-five positive rows={len(onefive)}; current exact non-meaningful zero-mass cannot represent positive points for 1-5-game locked-target seasons; mean zero-quantile proportion={float(onefive[QCOLS].eq(0).mean().mean()) if len(onefive) else 0:.6f}"),
    ]
    gates=pd.DataFrame([{"gate":g,"passed":bool(ok),"detail":d} for g,ok,d in gate_rows])
    summary={"task":"TASK-048-ridge-uncertainty-calibration-audit","bootstrap_seed":BOOTSTRAP_SEED,"bootstrap_replications":bootstrap_replications,"bootstrap_statistic":"pooled row-weighted TASK-047 minus TASK-012 mean pinball difference after player-block resampling","rows_per_model":{str(k):int(v) for k,v in allp.groupby("model").size().items()},"player_origin_snapshots":int(target[KEY[:2]].drop_duplicates().shape[0]),"folds":int(target[["origin_year","lead"]].drop_duplicates().shape[0]),"target_points_source":"targets.csv points column used directly","tie_rule":"actual_points <= predicted_quantile","primary_mean_pinball":primary.to_dict("records"),"accepted_uncertainty_outputs": bool(gates.passed.all()),"uncertainty_status":"accepted" if bool(gates.passed.all()) else "blocked","failed_gates":gates.loc[~gates.passed,"gate"].astype(int).tolist(),"recommended_next_task":"TASK-049: isolate a target-compatible uncertainty repair for structural one-to-five-game positive-points mass and interval calibration" if not bool(gates.passed.all()) else None}
    return {"primary_pinball.csv":primary,"pinball_overall.csv":pinball_overall,"pinball_by_lead.csv":pinball_by_lead,"fold_level_differences.csv":fold,"bootstrap_confidence_intervals.csv":boot,"bootstrap_observed_invariant.csv":bootstrap_invariant,"quantile_calibration_overall.csv":cal_overall,"quantile_calibration_by_lead.csv":cal_lead,"quantile_calibration_by_position.csv":cal_pos,"quantile_calibration_by_prior_history.csv":cal_hist,"interval_coverage_overall.csv":cov_overall,"interval_coverage_by_lead.csv":cov_lead,"interval_coverage_by_position.csv":cov_pos,"interval_coverage_by_prior_history.csv":cov_hist,"structural_zero_mass_by_lead.csv":structural,"structural_zero_mass_cohort_pinball.csv":cohort_pinball,"structural_zero_mass_cohort_calibration.csv":cohort_cal,"integrity_checks.csv":integrity,"acceptance_gates.csv":gates}, summary


def write_outputs(tables: dict[str,pd.DataFrame], summary: dict[str,Any], out: Path, inputs: dict[str,Path]) -> None:
    out.mkdir(parents=True, exist_ok=True); artifacts={}
    for name, df in tables.items():
        path=out/name; df.to_csv(path,index=False,lineterminator="\n"); artifacts[name]={"rows":int(len(df)),"sha256":sha256_path(path),"bytes":path.stat().st_size}
    summary["inputs"]={k:str(v) for k,v in inputs.items()}; summary["artifacts"]=artifacts
    summary["reproduction_commands"]=[
        "python vnext/run_task012_established_ceiling_folds.py --out build/task012-candidate --rebuild",
        "python vnext/run_task047_pooled_ridge_folds.py --out build/task047-pooled-ridge-conditional-average --rebuild",
        "python vnext/analyse_task048_ridge_uncertainty.py --baseline build/task012-candidate/vnext_predictions.csv --candidate build/task047-pooled-ridge-conditional-average/vnext_predictions.csv --targets build/task-003-cohorts/targets.csv --features build/task047-pooled-ridge-conditional-average/training_dataset.csv --out reports/task-048-ridge-uncertainty-calibration-audit",
    ]
    (out/"summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    (out/"artifact_manifest.json").write_text(json.dumps({"artifacts":artifacts,"no_duplicate_prediction_files_committed":True,"model_artifacts_created":False}, indent=2, sort_keys=True)+"\n")
    (out/"README.md").write_text("# TASK-048 Ridge uncertainty calibration audit\n\nEvaluation-only audit. See summary.json and CSV evidence tables.\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    tables, summary = build_audit(
        _load_predictions(args.baseline, "task012"),
        _load_predictions(args.candidate, "task047"),
        pd.read_csv(args.targets),
        pd.read_csv(args.features),
        baseline_artifact_checks=artifact_failure_checks(args.baseline),
        candidate_artifact_checks=artifact_failure_checks(args.candidate),
    )
    write_outputs(
        tables,
        summary,
        args.out,
        {
            "baseline": args.baseline,
            "candidate": args.candidate,
            "targets": args.targets,
            "features": args.features,
        },
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
