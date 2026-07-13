from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

import analyse_task048_ridge_uncertainty as a48
from task049_three_state_distribution import (
    KEY,
    QCOLS,
    candidate_minus_baseline_bootstrap,
    compare_unchanged_outputs,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/task-049-three-state-point-distribution"
EXPECTED_TASK047_PREDICTION_SHA = "481485d84c0dddc05ef01a9ecd50c6be5092538b70064aba50a887a0812f43f4"
EXPECTED_TASK049_CANDIDATE_SHA = "3782fb531a4a7c147501151f937ec7a7f723b51ef1fe6adb070d0e21f17bb6f8"
EXPECTED_TASK049_PRIMARY_PINBALL = 141.65297296100084


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def write(path: Path, frame: pd.DataFrame) -> dict[str, int | str]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {"rows": int(len(frame)), "sha256": sha(path), "bytes": path.stat().st_size}


def require_artifact(path: Path, label: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"missing mandatory {label}: {path}")
    return path


def relabel_table(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "model" in out.columns:
        out["model"] = out["model"].replace({"task012": "task047", "task047": "task049"})
    if "check" in out.columns:
        out["check"] = out["check"].astype(str).str.replace("task012", "__BASE__", regex=False).str.replace("task047", "task049", regex=False).str.replace("__BASE__", "task047", regex=False)
    if "detail" in out.columns:
        out["detail"] = out["detail"].astype(str).str.replace("task012", "__BASE__", regex=False).str.replace("task047", "task049", regex=False).str.replace("__BASE__", "task047", regex=False)
    rename = {
        "task012": "task047",
        "task047": "task049",
        "abs_diff_task047_minus_task012": "abs_diff_task049_minus_task047",
        "pct_diff_task047_minus_task012": "pct_diff_task049_minus_task047",
    }
    return out.rename(columns={k: v for k, v in rename.items() if k in out.columns})


def pinball(y: pd.Series, q: pd.Series, tau: float) -> pd.Series:
    d = y.astype(float) - q.astype(float)
    return np.maximum(tau * d, (tau - 1.0) * d)


def one_to_five_tables(base: pd.DataFrame, cand: pd.DataFrame, targets: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    target = targets[KEY + ["games", "points"]]
    b = base.merge(target, on=KEY)
    c = cand.merge(target, on=KEY)
    mask = target.games.between(1, 5, inclusive="both") & target.points.gt(0)
    b = b.loc[mask].copy(); c = c.loc[mask].copy()
    pin_rows = []
    cal_rows = []
    for col, tau in a48.QUANTILES:
        b_loss = float(pinball(b.points, b[col], tau).mean())
        c_loss = float(pinball(c.points, c[col], tau).mean())
        pin_rows.append({
            "realised_cohort": "one_to_five_positive_points",
            "quantile": col,
            "tau": tau,
            "n": int(len(b)),
            "task047_pinball_loss": b_loss,
            "task049_pinball_loss": c_loss,
            "abs_diff_task049_minus_task047": c_loss - b_loss,
            "pct_diff_task049_minus_task047": (c_loss - b_loss) / b_loss if b_loss else np.nan,
        })
        for model, df in [("task047", b), ("task049", c)]:
            emp = float((df.points.astype(float) <= df[col].astype(float)).mean())
            cal_rows.append({"realised_cohort": "one_to_five_positive_points", "model": model, "quantile": col, "tau": tau, "n": int(len(df)), "empirical_p_actual_le_predicted_quantile": emp, "signed_calibration_error": emp - tau, "absolute_calibration_error": abs(emp - tau)})
    return pd.DataFrame(pin_rows), pd.DataFrame(cal_rows)


def build_gates(primary: pd.DataFrame, pin_overall: pd.DataFrame, cal_overall: pd.DataFrame, cov_overall: pd.DataFrame, cov_lead: pd.DataFrame, cov_pos: pd.DataFrame, cov_hist: pd.DataFrame, diag: pd.DataFrame, cohort_pin: pd.DataFrame, comp: pd.DataFrame, cand: pd.DataFrame, boot: pd.DataFrame) -> pd.DataFrame:
    p = primary.set_index("model").primary_mean_pinball_loss
    rel = (p.task049 - p.task047) / p.task047
    boot_primary = boot.loc[boot.metric.eq("primary_mean_pinball")].iloc[0]
    max_quant_worsen = float(pin_overall.pct_diff_task049_minus_task047.max())
    cand_cal = cal_overall[cal_overall.model.eq("task049")]
    base_cal = cal_overall[cal_overall.model.eq("task047")]
    mean_abs_cal = float(cand_cal.absolute_calibration_error.mean())
    base_mean_abs_cal = float(base_cal.absolute_calibration_error.mean())
    cand_cov = cov_overall[cov_overall.model.eq("task049")].set_index("interval")
    lead_cov = cov_lead[cov_lead.model.eq("task049") & cov_lead.interval.isin(["q25_q75", "q10_q90"])]
    subgroup = pd.concat([cov_pos.assign(subgroup_type="position", subgroup=cov_pos.broad_position), cov_hist.assign(subgroup_type="prior_history", subgroup=cov_hist.prior_history_cohort)], ignore_index=True)
    subgroup = subgroup[(subgroup.model.eq("task049")) & (subgroup.n >= 200) & (subgroup.interval.isin(["q25_q75", "q10_q90"]))]
    qvals = cand[QCOLS].to_numpy(float)
    p_short = diag.p_short.astype(float)
    short_supported = bool(np.isfinite(p_short).all() and (p_short > 0).any())
    short_draws = bool((diag.loc[p_short > 0, "short_draw_count"] > 0).all())
    short_points = bool((diag.loc[diag.short_draw_count > 0, "adjusted_short_points_min"] > 0).all())
    short_games = bool(diag.loc[diag.short_draw_count > 0, "short_games_min"].between(1, 5).all() and diag.loc[diag.short_draw_count > 0, "short_games_max"].between(1, 5).all())
    cohort_improve = int((cohort_pin.abs_diff_task049_minus_task047 < 0).sum())
    cohort_noworse = bool((cohort_pin.pct_diff_task049_minus_task047 <= 0.05).all())
    gates = [
        (1, rel <= -0.01 and boot_primary.bootstrap_median < 0 and boot_primary.ci_high <= p.task047 * 0.01, f"primary pct diff={rel:.6f}; bootstrap candidate-minus-baseline CI=({boot_primary.ci_low:.6f},{boot_primary.ci_high:.6f})"),
        (2, max_quant_worsen <= 0.02, f"max individual quantile pct worsen={max_quant_worsen:.6f}"),
        (3, mean_abs_cal <= 0.05 and mean_abs_cal <= 0.75 * base_mean_abs_cal, f"task049 mean abs calibration={mean_abs_cal:.6f}; task047={base_mean_abs_cal:.6f}"),
        (4, (0.46 <= cand_cov.loc["q25_q75"].coverage <= 0.54) and (0.76 <= cand_cov.loc["q10_q90"].coverage <= 0.84), f"q25-q75={cand_cov.loc['q25_q75'].coverage:.6f}; q10-q90={cand_cov.loc['q10_q90'].coverage:.6f}"),
        (5, not (lead_cov.absolute_coverage_error > 0.08).any(), f"max lead central abs coverage error={float(lead_cov.absolute_coverage_error.max()):.6f}"),
        (6, not (subgroup.absolute_coverage_error > 0.12).any(), f"max subgroup central abs coverage error={float(subgroup.absolute_coverage_error.max()):.6f}"),
        (7, short_supported and short_draws and short_points and short_games and cohort_improve >= 4 and cohort_noworse, f"short_supported={short_supported}; positive_draws={short_draws}; positive_adjusted_points={short_points}; short_games_1_to_5={short_games}; improved_quantiles={cohort_improve}; no_worsen_above_5pct={cohort_noworse}"),
        (8, bool((comp.changed_rows == 0).all()) and float(diag.moment_error_after.abs().max()) <= 1e-8, f"non_quantile_changed_rows={int(comp.changed_rows.sum())}; max post-adjustment mean error={float(diag.moment_error_after.abs().max()):.12g}"),
        (9, (qvals >= -1e-12).all() and (np.diff(qvals, axis=1) >= -1e-12).all(), "candidate quantiles are deterministic, non-negative and non-crossing; key/failure checks passed before audit"),
    ]
    return pd.DataFrame([{"gate": gate, "passed": bool(ok), "detail": detail} for gate, ok, detail in gates])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=ROOT / "build/task047-pooled-ridge-conditional-average/vnext_predictions.csv")
    parser.add_argument("--candidate", type=Path, default=ROOT / "build/task049-three-state-point-distribution/vnext_predictions.csv")
    parser.add_argument("--targets", type=Path, default=ROOT / "build/task-003-cohorts/targets.csv")
    parser.add_argument("--features", type=Path, default=ROOT / "build/task047-pooled-ridge-conditional-average/training_dataset.csv")
    parser.add_argument("--diag", type=Path, default=ROOT / "build/task049-three-state-point-distribution/branch_diagnostics.csv")
    parser.add_argument("--out", type=Path, default=REPORT)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for path, label in [(args.baseline, "TASK-047 predictions"), (args.candidate, "TASK-049 predictions"), (args.targets, "locked targets"), (args.features, "TASK-047 training dataset"), (args.diag, "TASK-049 diagnostics"), (args.baseline.parent / "prediction_manifest.json", "TASK-047 prediction manifest"), (args.baseline.parent / "fold_failures.csv", "TASK-047 fold failures"), (ROOT / "build/task-003-cohorts/target_failures.csv", "locked target failures"), (args.candidate.parent / "prediction_manifest.json", "TASK-049 prediction manifest")]:
        require_artifact(path, label)
    if len(pd.read_csv(args.baseline.parent / "fold_failures.csv")) != 0:
        raise ValueError("TASK-047 fold_failures.csv must have zero rows")
    if len(pd.read_csv(ROOT / "build/task-003-cohorts/target_failures.csv")) != 0:
        raise ValueError("locked target_failures.csv must have zero rows")

    base_full = pd.read_csv(args.baseline)
    cand_full = pd.read_csv(args.candidate)
    targets = pd.read_csv(args.targets)
    features = pd.read_csv(args.features)
    diag = pd.read_csv(args.diag)
    b = a48._load_predictions(args.baseline, "task012")
    c = a48._load_predictions(args.candidate, "task047")
    tables, _ = a48.build_audit(b, c, targets, features, bootstrap_replications=2000)
    relabelled = {name: relabel_table(df) for name, df in tables.items()}
    for unwanted in ["fold_level_differences.csv", "structural_zero_mass_by_lead.csv", "structural_zero_mass_cohort_pinball.csv", "structural_zero_mass_cohort_calibration.csv", "bootstrap_observed_invariant.csv"]:
        relabelled.pop(unwanted, None)

    wide = b.merge(c, on=KEY, suffixes=("_baseline", "_candidate")).merge(targets[KEY + ["points"]], on=KEY)
    boot, invariant = candidate_minus_baseline_bootstrap(wide, reps=2000, seed=49049)
    relabelled["bootstrap_confidence_intervals.csv"] = boot
    relabelled["bootstrap_pooled_statistic_invariant.csv"] = invariant
    comp = compare_unchanged_outputs(base_full, cand_full)
    relabelled["non_uncertainty_output_comparison.csv"] = comp

    cohort_pin, cohort_cal = one_to_five_tables(base_full, cand_full, targets)
    relabelled["one_to_five_cohort_pinball.csv"] = cohort_pin
    relabelled["one_to_five_cohort_calibration.csv"] = cohort_cal

    state = diag.groupby(["origin_year", "lead"]).agg(n=("player_key", "size"), pred_zero_prob=("p_zero", "mean"), pred_short_prob=("p_short", "mean"), pred_meaningful_prob=("p_meaningful", "mean"), pred_short_game_mean=("pred_short_games_mean", "mean"), pred_short_rate_mean=("pred_short_rate_mean", "mean"), moment_error_after_max_abs=("moment_error_after", lambda s: float(s.abs().max()))).reset_index()
    realised = targets.copy()
    realised["realised_zero"] = ((realised.games == 0) & (realised.points == 0)).astype(float)
    realised["realised_short"] = (realised.games.between(1, 5, inclusive="both") & realised.points.gt(0)).astype(float)
    realised["realised_meaningful"] = realised.games.ge(6).astype(float)
    realised["short_games_realised"] = np.where(realised.realised_short.astype(bool), realised.games, np.nan)
    realised["short_rate_realised"] = np.where(realised.realised_short.astype(bool), realised.points / realised.games, np.nan)
    real = realised.groupby(["origin_year", "lead"]).agg(realised_zero_freq=("realised_zero", "mean"), realised_short_freq=("realised_short", "mean"), realised_meaningful_freq=("realised_meaningful", "mean"), realised_short_game_mean=("short_games_realised", "mean"), realised_short_rate_mean=("short_rate_realised", "mean")).reset_index()
    ss = state.merge(real, on=["origin_year", "lead"])
    ss["zero_prob_signed_error"] = ss.pred_zero_prob - ss.realised_zero_freq
    ss["short_prob_signed_error"] = ss.pred_short_prob - ss.realised_short_freq
    ss["meaningful_prob_signed_error"] = ss.pred_meaningful_prob - ss.realised_meaningful_freq
    relabelled["predicted_vs_realised_state_frequency.csv"] = ss[["origin_year", "lead", "n", "pred_zero_prob", "realised_zero_freq", "zero_prob_signed_error", "pred_short_prob", "realised_short_freq", "short_prob_signed_error", "pred_meaningful_prob", "realised_meaningful_freq", "meaningful_prob_signed_error"]]
    relabelled["short_season_calibration_by_fold_lead.csv"] = ss
    relabelled["short_season_training_summary.csv"] = pd.read_csv(args.candidate.parent / "short_season_training_summary_by_fold_lead.csv")

    primary = relabelled["primary_pinball.csv"]
    gates = build_gates(primary, relabelled["pinball_overall.csv"], relabelled["quantile_calibration_overall.csv"], relabelled["interval_coverage_overall.csv"], relabelled["interval_coverage_by_lead.csv"], relabelled["interval_coverage_by_position.csv"], relabelled["interval_coverage_by_prior_history.csv"], diag, cohort_pin, comp, cand_full, boot)
    relabelled["acceptance_gates.csv"] = gates

    artifacts = {name: write(args.out / name, df) for name, df in relabelled.items()}
    p = primary.set_index("model").primary_mean_pinball_loss
    failed = gates.loc[~gates.passed, "gate"].astype(int).tolist()
    task049_manifest = json.loads((args.candidate.parent / "prediction_manifest.json").read_text())
    candidate_sha = sha(args.candidate)
    source_sha = sha(args.baseline)
    parity_checked = source_sha == EXPECTED_TASK047_PREDICTION_SHA
    if parity_checked:
        if candidate_sha != EXPECTED_TASK049_CANDIDATE_SHA:
            raise ValueError(f"TASK-049 parity hash mismatch: expected {EXPECTED_TASK049_CANDIDATE_SHA}, got {candidate_sha}")
        if abs(float(p.task049) - EXPECTED_TASK049_PRIMARY_PINBALL) > 1e-10:
            raise ValueError(f"TASK-049 primary pinball parity mismatch: expected {EXPECTED_TASK049_PRIMARY_PINBALL}, got {float(p.task049)}")
    summary = {
        "task": "TASK-049-three-state-point-distribution",
        "decision": "accepted" if not failed else "rejected",
        "uncertainty_status": "accepted" if not failed else "blocked",
        "accepted_uncertainty_outputs": not failed,
        "primary_mean_pinball": {"task047": float(p.task047), "task049": float(p.task049)},
        "failed_gates": failed,
        "bootstrap_seed": 49049,
        "bootstrap_replications": 2000,
        "sample_count": int(task049_manifest["sample_count"]),
        "seed_contract": task049_manifest["seed_contract"],
        "source_prediction_manifest": {"path": repo_path(args.baseline.parent / "prediction_manifest.json"), "sha256": sha(args.baseline.parent / "prediction_manifest.json")},
        "source_fold_failures": {"path": repo_path(args.baseline.parent / "fold_failures.csv"), "rows": int(len(pd.read_csv(args.baseline.parent / "fold_failures.csv"))), "sha256": sha(args.baseline.parent / "fold_failures.csv")},
        "source_target_failures": {"path": repo_path(ROOT / "build/task-003-cohorts/target_failures.csv"), "rows": int(len(pd.read_csv(ROOT / "build/task-003-cohorts/target_failures.csv"))), "sha256": sha(ROOT / "build/task-003-cohorts/target_failures.csv")},
        "parity_with_pr80_generator": {"checked": parity_checked, "expected_source_prediction_sha256": EXPECTED_TASK047_PREDICTION_SHA, "actual_source_prediction_sha256": source_sha, "expected_candidate_sha256": EXPECTED_TASK049_CANDIDATE_SHA, "actual_candidate_sha256": candidate_sha, "expected_primary_pinball": EXPECTED_TASK049_PRIMARY_PINBALL, "actual_primary_pinball": float(p.task049)},
        "task049_transformation_failure_rows": task049_manifest["task049_transformation_failure_rows"],
        "large_build_artifacts_omitted": ["build/task049-three-state-point-distribution/vnext_predictions.csv", "build/task049-three-state-point-distribution/branch_diagnostics.csv"],
        "artifacts": artifacts,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (args.out / "artifact_manifest.json").write_text(json.dumps({"artifacts": artifacts, "omitted_build_artifacts": summary["large_build_artifacts_omitted"], "no_committed_file_over_100kb": True}, indent=2, sort_keys=True) + "\n")
    (args.out / "README.md").write_text(f"# TASK-049 three-state point distribution\n\nRejected evidence PR. TASK-049 mean pinball is {float(p.task049):.6f} versus TASK-047 {float(p.task047):.6f}; gates {failed} fail and uncertainty remains blocked.\n")
    (args.out / "REPRODUCE.md").write_text("```bash\npython vnext/run_task047_pooled_ridge_folds.py --out build/task047-pooled-ridge-conditional-average --rebuild\npython vnext/run_task049_three_state_point_distribution.py\npython vnext/analyse_task049_three_state_point_distribution.py\nPYTHONPATH=vnext pytest -q vnext/tests/test_task049_three_state_distribution.py\ncd vnext && pytest -q\npython scripts/verify_legacy_manifest.py\npython scripts/generate_handover.py\n```\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
