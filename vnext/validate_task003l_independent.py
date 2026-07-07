"""TASK-003L independent validation of the TASK-003K candidate.

Diagnostic-only: this script reads already-produced fold artifacts, predictions,
locked cohorts, and PR evidence. It never fits or changes a model.
"""
from __future__ import annotations

import argparse, json, pickle, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
VNEXT = ROOT / "vnext"
if str(VNEXT) not in sys.path:
    sys.path.insert(0, str(VNEXT))

from benchmark import LOCKED_FOLDS, PREDICTION_KEY, REQUIRED_PREDICTION_COLUMNS
from build_historical_cohorts import build_locked_cohorts
from comparison_diagnostics import player_block_bootstrap, row_losses, slice_metrics
from comparison_harness import calibration_intercept_slope_stable, weighted_metric_summary
from analyse_task003e_regressions import material_regressions
from analyse_task003g_components import zero_history_outcome_split, add_slice_columns

EXPECTED_TARGET_ROWS = 20094
KEY = PREDICTION_KEY
SCHEMA = set(REQUIRED_PREDICTION_COLUMNS)
TOL = 1e-9
INVARIANT_COMPONENTS = (
    "preprocessor", "games_model", "avg_model", "threshold_models",
    "threshold_calibrators", "games_resid_sd", "avg_resid_sd", "n_fit", "n_cal",
)
EVENT_ALLOWED_COMPONENTS = ("event_model", "event_calibrator")

@dataclass(frozen=True)
class Check:
    name: str
    status: str
    details: str


def stable(value: Any) -> Any:
    if hasattr(value, "coef_"):
        return {"class": type(value).__name__, "coef": np.asarray(value.coef_).round(12).tolist(), "intercept": np.asarray(value.intercept_).round(12).tolist()}
    if hasattr(value, "X_thresholds_"):
        return {"class": type(value).__name__, "x": np.asarray(value.X_thresholds_).round(12).tolist(), "y": np.asarray(value.y_thresholds_).round(12).tolist()}
    if isinstance(value, dict):
        return {str(k): stable(v) for k, v in sorted(value.items())}
    if isinstance(value, (float, int, str, type(None))):
        return value
    return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)


def equal_component(a: Any, b: Any) -> bool:
    sa, sb = stable(a), stable(b)
    if isinstance(sa, (bytes, bytearray)) or isinstance(sb, (bytes, bytearray)):
        return sa == sb
    return json.dumps(sa, sort_keys=True, default=str) == json.dumps(sb, sort_keys=True, default=str)


def add(checks: list[Check], name: str, ok: bool, details: str) -> None:
    checks.append(Check(name, "pass" if ok else "fail", details))


def incomplete(checks: list[Check], name: str, details: str) -> None:
    checks.append(Check(name, "incomplete", details))


def read(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


def legal_fold_table() -> pd.DataFrame:
    rows = []
    for lead, origins in LOCKED_FOLDS.items():
        for origin in origins:
            rows.append({"lead": lead, "origin_year": origin, "training_target_max_year": origin - 1})
    return pd.DataFrame(rows).sort_values(["lead", "origin_year"]).reset_index(drop=True)


def validate_predictions(checks: list[Check], label: str, path: Path, targets: pd.DataFrame) -> pd.DataFrame | None:
    if not path.exists():
        incomplete(checks, f"{label} predictions present", f"missing {path}")
        return None
    pred = pd.read_csv(path)
    missing = sorted(SCHEMA - set(pred.columns))
    extra_dupes = int(pred.duplicated(KEY, keep=False).sum())
    add(checks, f"{label} prediction schema", not missing, f"missing={missing}")
    add(checks, f"{label} duplicate prediction keys", extra_dupes == 0, f"duplicate_rows={extra_dupes}")
    target_dupes = int(targets.duplicated(KEY, keep=False).sum())
    add(checks, "locked target duplicate keys", target_dupes == 0, f"duplicate_rows={target_dupes}")
    if missing or extra_dupes or target_dupes:
        return pred
    pk = pred[KEY].sort_values(KEY).reset_index(drop=True)
    tk = targets[KEY].sort_values(KEY).reset_index(drop=True)
    add(checks, f"{label} locked 20,094-row cohort", len(pred) == EXPECTED_TARGET_ROWS and pk.equals(tk), f"rows={len(pred)}")
    return pred


def validate_folds(checks: list[Check], label: str, run_dir: Path) -> pd.DataFrame | None:
    manifest = read(run_dir / "fold_artifact_manifest.csv")
    if manifest is None:
        incomplete(checks, f"{label} fold manifest present", f"missing {run_dir / 'fold_artifact_manifest.csv'}")
        return None
    got = manifest[["lead", "origin_year", "training_target_max_year"]].sort_values(["lead", "origin_year"]).reset_index(drop=True)
    expected = legal_fold_table()
    add(checks, f"{label} all 25 legal folds", len(got) == 25 and got.equals(expected), f"fold_rows={len(got)}")
    return manifest


def raw_event_probs(run_dir: Path, manifest: pd.DataFrame, pred: pd.DataFrame, snapshots: pd.DataFrame) -> pd.Series | None:
    values: list[pd.DataFrame] = []
    for row in manifest.itertuples(index=False):
        lead, origin = int(row.lead), int(row.origin_year)
        keys = pred[(pred.lead == lead) & (pred.origin_year == origin)][KEY]
        rows = keys.merge(snapshots, on=["player_key", "origin_year"], validate="one_to_one")
        art = joblib.load(run_dir / str(row.artifact_path))
        z = art.preprocessor.transform(rows)
        raw = art.event_model.predict_proba(z)[:, 1]
        values.append(keys.assign(raw_p_meaningful=raw))
    if not values:
        return None
    raw_frame = pd.concat(values, ignore_index=True)
    return pred[KEY].merge(raw_frame, on=KEY, validate="one_to_one")["raw_p_meaningful"]


def score(pred: pd.DataFrame, targets: pd.DataFrame, model_id: str, raw_p: pd.Series | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    joined = pred.merge(targets, on=KEY, how="inner", validate="one_to_one")
    if raw_p is None:
        raw_p = joined["p_meaningful"]
    joined = joined.assign(raw_p_meaningful=np.asarray(raw_p, float))
    rows: list[dict[str, Any]] = []
    for keys, group in joined.groupby(["origin_year", "lead"], sort=True):
        origin, lead = int(keys[0]), int(keys[1])
        ci, cs = calibration_intercept_slope_stable(group["meaningful"], group["p_meaningful"])
        rows.append({
            "model_id": model_id, "origin_year": origin, "lead": lead, "n": int(len(group)),
            "raw_brier_meaningful": brier_score_loss(group["meaningful"], group["raw_p_meaningful"]),
            "calibrated_brier_meaningful": brier_score_loss(group["meaningful"], group["p_meaningful"]),
            "raw_log_loss_meaningful": log_loss(group["meaningful"], np.clip(group["raw_p_meaningful"], .001, .999), labels=[0,1]),
            "calibrated_log_loss_meaningful": log_loss(group["meaningful"], np.clip(group["p_meaningful"], .001, .999), labels=[0,1]),
            "auc_meaningful": float(roc_auc_score(group["meaningful"], group["p_meaningful"])) if group["meaningful"].nunique() > 1 else float("nan"),
            "probability_bias": float((group["p_meaningful"] - group["meaningful"]).mean()),
            "calibration_intercept_meaningful": ci, "calibration_slope_meaningful": cs,
            "mae_games": mean_absolute_error(group["games"], group["exp_games"]),
            "mae_total_points": mean_absolute_error(group["points"], group["exp_points"]),
        })
    by_fold = pd.DataFrame(rows).sort_values(["model_id", "origin_year", "lead"]).reset_index(drop=True)
    by_lead = by_fold.groupby(["model_id", "lead"], as_index=False).apply(lambda g: pd.Series({c: np.average(g[c], weights=g["n"]) for c in by_fold.columns if c not in {"model_id","origin_year","lead","n"}}), include_groups=False).reset_index(drop=True)
    by_lead["n"] = by_fold.groupby(["model_id", "lead"])["n"].sum().to_numpy()
    return by_fold, by_lead


def compare_artifacts(checks: list[Check], current_dir: Path, candidate_dir: Path, current_manifest: pd.DataFrame | None, candidate_manifest: pd.DataFrame | None, snapshots: pd.DataFrame, pred: pd.DataFrame | None) -> None:
    if current_manifest is None or candidate_manifest is None or pred is None:
        incomplete(checks, "artifact invariant validation", "requires both fold manifests and predictions")
        return
    changed = {c: 0 for c in INVARIANT_COMPONENTS + EVENT_ALLOWED_COMPONENTS}
    pred_mismatches = 0
    for row in current_manifest.itertuples(index=False):
        lead, origin = int(row.lead), int(row.origin_year)
        cand = candidate_manifest[(candidate_manifest.lead == lead) & (candidate_manifest.origin_year == origin)]
        if len(cand) != 1:
            add(checks, "candidate artifact paired by fold", False, f"missing lead={lead} origin={origin}")
            return
        ca = joblib.load(current_dir / str(row.artifact_path)); cb = joblib.load(candidate_dir / str(cand.iloc[0].artifact_path))
        for comp in INVARIANT_COMPONENTS + EVENT_ALLOWED_COMPONENTS:
            if not equal_component(getattr(ca, comp), getattr(cb, comp)):
                changed[comp] += 1
        sample_keys = pred[(pred.lead == lead) & (pred.origin_year == origin)][KEY].head(25)
        if len(sample_keys):
            rows = sample_keys.merge(snapshots, on=["player_key", "origin_year"], validate="one_to_one")
            za, zb = ca.preprocessor.transform(rows), cb.preprocessor.transform(rows)
            if not np.allclose(ca.games_model.predict(za), cb.games_model.predict(zb), atol=1e-10): pred_mismatches += 1
            if not np.allclose(ca.avg_model.predict(za), cb.avg_model.predict(zb), atol=1e-10): pred_mismatches += 1
    illegal = {k: v for k, v in changed.items() if k in INVARIANT_COMPONENTS and v}
    add(checks, "artifact invariants unchanged", not illegal and pred_mismatches == 0, json.dumps({"changed_components": changed, "conditional_prediction_mismatch_folds": pred_mismatches}, sort_keys=True))
    add(checks, "event model/calibrator allowed to change", changed["event_model"] > 0 and changed["event_calibrator"] >= 0, json.dumps({"event_model_changed_folds": changed["event_model"], "event_calibrator_changed_folds": changed["event_calibrator"]}, sort_keys=True))


def compare_evidence(name: str, reproduced: pd.DataFrame, evidence_path: Path, out_dir: Path, checks: list[Check], tol: float) -> pd.DataFrame:
    if not evidence_path.exists():
        incomplete(checks, f"evidence comparison: {name}", f"missing {evidence_path}")
        return pd.DataFrame([{"artifact": name, "status": "missing_evidence", "path": str(evidence_path)}])
    expected = pd.read_csv(evidence_path)
    common = [c for c in reproduced.columns if c in expected.columns]
    keys = [c for c in ["model_id", "origin_year", "lead", "metric", "slice_type", "slice_value", "eventual_played"] if c in common]
    if not keys:
        incomplete(checks, f"evidence comparison: {name}", "no common key columns")
        return pd.DataFrame([{"artifact": name, "status": "no_common_keys"}])
    merged = reproduced.merge(expected, on=keys, how="outer", suffixes=("_reproduced", "_expected"), indicator=True)
    rows = []
    for col in common:
        if col in keys: continue
        a, b = f"{col}_reproduced", f"{col}_expected"
        if a in merged and b in merged and pd.api.types.is_numeric_dtype(merged[a]) and pd.api.types.is_numeric_dtype(merged[b]):
            diff = (merged[a] - merged[b]).abs().max(skipna=True)
            rows.append({"artifact": name, "column": col, "max_abs_diff": float(diff) if pd.notna(diff) else 0.0, "tolerance": tol, "rows": len(merged)})
    disc = pd.DataFrame(rows)
    ok = len(disc) > 0 and bool((disc["max_abs_diff"] <= tol).all()) and merged["_merge"].eq("both").all()
    add(checks, f"evidence comparison: {name}", ok, f"rows={len(merged)} discrepancies={(~(disc['max_abs_diff'] <= tol)).sum() if len(disc) else 'n/a'}")
    return disc


def write(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, lineterminator="\n")


def run(args: argparse.Namespace) -> int:
    out = args.out; out.mkdir(parents=True, exist_ok=True)
    checks: list[Check] = []
    if not (args.cohort_dir / "targets.csv").exists():
        build_locked_cohorts(args.cohort_dir)
    targets = pd.read_csv(args.cohort_dir / "targets.csv")
    snapshots = pd.read_csv(args.cohort_dir / "included_snapshots.csv")
    add(checks, "exact locked target row count", len(targets) == EXPECTED_TARGET_ROWS, f"rows={len(targets)}")

    cur_pred = validate_predictions(checks, "current", args.current_predictions, targets)
    cand_pred = validate_predictions(checks, "candidate", args.candidate_predictions, targets)
    cur_manifest = validate_folds(checks, "current", args.current_run_dir)
    cand_manifest = validate_folds(checks, "candidate", args.candidate_run_dir)
    compare_artifacts(checks, args.current_run_dir, args.candidate_run_dir, cur_manifest, cand_manifest, snapshots, cand_pred)

    metric_frames = []; lead_frames = []
    for label, pred, run_dir, manifest in (("current", cur_pred, args.current_run_dir, cur_manifest), ("candidate", cand_pred, args.candidate_run_dir, cand_manifest)):
        if pred is None: continue
        raw = None
        if manifest is not None:
            try: raw = raw_event_probs(run_dir, manifest, pred, snapshots)
            except Exception as exc: incomplete(checks, f"{label} raw probability reproduction", repr(exc))
        by_fold, by_lead = score(pred, targets, label, raw)
        write(by_fold, out / f"{label}_metrics_by_fold.csv"); write(by_lead, out / f"{label}_metrics_by_lead.csv")
        metric_frames.append(by_fold); lead_frames.append(by_lead)
    all_fold = pd.concat(metric_frames, ignore_index=True) if metric_frames else pd.DataFrame()
    all_lead = pd.concat(lead_frames, ignore_index=True) if lead_frames else pd.DataFrame()
    write(all_fold, out / "metrics_by_fold.csv"); write(all_lead, out / "metrics_by_lead.csv")
    pooled = all_fold.groupby("model_id", as_index=False).apply(lambda g: pd.Series({c: np.average(g[c], weights=g["n"]) for c in all_fold.columns if c not in {"model_id","origin_year","lead","n"}}), include_groups=False).reset_index(drop=True) if len(all_fold) else pd.DataFrame()
    write(pooled, out / "pooled_metrics.csv")

    bootstrap = pd.DataFrame(); subgroups = pd.DataFrame(); zero = pd.DataFrame(); locked = pd.DataFrame(); disc_frames = []
    if cur_pred is not None and cand_pred is not None:
        cp = cur_pred.assign(model_id="current"); kp = cand_pred.assign(model_id="candidate")
        predictions = pd.concat([cp, kp], ignore_index=True)
        losses = row_losses(predictions, targets)
        bootstrap = player_block_bootstrap(losses, baseline_model_id="current", repetitions=args.bootstrap_repetitions, seed=3003)
        subgroups = slice_metrics(predictions, targets, snapshots, minimum_n=200)
        joined = predictions.merge(targets, on=KEY, validate="many_to_one").merge(snapshots, on=["player_key", "origin_year"], validate="many_to_one")
        zero = zero_history_outcome_split(add_slice_columns(joined))
        regs = material_regressions(subgroups.rename(columns={}).replace({"current":"baseline_recent_scoring","candidate":"vnext_fold_specific"}))
        locked = regs.head(15).copy()
        age30 = regs[(regs.lead.eq(5)) & (regs.slice_type.eq("age_band")) & (regs.slice_value.eq("30+"))]
        locked = pd.concat([locked, age30], ignore_index=True).drop_duplicates()
        add(checks, "independent validation computations complete", True, "candidate/current artifacts available")
    else:
        incomplete(checks, "independent validation computations complete", "missing current or candidate predictions/artifacts")
    write(bootstrap, out / "player_block_bootstrap.csv"); write(zero, out / "zero_history_results.csv"); write(subgroups, out / "subgroup_results.csv"); write(locked, out / "locked_regression_rows.csv")

    if args.evidence_dir.exists():
        comparisons = [
            ("pooled_metrics", pooled, args.evidence_dir / "pooled_metrics.csv"),
            ("metrics_by_lead", all_lead, args.evidence_dir / "metrics_by_lead.csv"),
            ("metrics_by_fold", all_fold, args.evidence_dir / "metrics_by_fold.csv"),
            ("player_block_bootstrap", bootstrap, args.evidence_dir / "player_block_bootstrap.csv"),
            ("zero_history_results", zero, args.evidence_dir / "zero_history_results.csv"),
            ("subgroup_results", subgroups, args.evidence_dir / "subgroup_results.csv"),
            ("locked_regression_rows", locked, args.evidence_dir / "locked_regression_rows.csv"),
        ]
        for name, frame, path in comparisons:
            disc_frames.append(compare_evidence(name, frame, path, out, checks, args.tolerance))
    else:
        incomplete(checks, "PR #19 evidence directory present", f"missing {args.evidence_dir}")
    discrepancies = pd.concat(disc_frames, ignore_index=True) if disc_frames else pd.DataFrame(columns=["artifact", "status"])
    write(discrepancies, out / "discrepancies.csv")

    has_failures = any(c.status == "fail" for c in checks)
    has_incomplete = any(c.status == "incomplete" for c in checks)
    if has_failures or (args.require_complete and has_incomplete):
        status = "independent validation failed"
    elif has_incomplete:
        status = "validation incomplete"
    else:
        status = "independent validation passed"
    report = {"task": "TASK-003L", "status": status, "checks": [c.__dict__ for c in checks], "tolerance": args.tolerance, "bootstrap_repetitions": args.bootstrap_repetitions, "require_complete": args.require_complete}
    (out / "task003l_final_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write(pd.DataFrame([c.__dict__ for c in checks]), out / "task003l_check_results.csv")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if status == "independent validation failed" else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT / "reports" / "task-003l-independent-validation")
    p.add_argument("--cohort-dir", type=Path, default=ROOT / "build" / "task-003b-cohorts")
    p.add_argument("--current-run-dir", type=Path, default=ROOT / "build" / "task-003b-vnext-folds")
    p.add_argument("--current-predictions", type=Path, default=ROOT / "build" / "task-003b-vnext-folds" / "vnext_predictions.csv")
    p.add_argument("--candidate-run-dir", type=Path, default=ROOT / "build" / "task-003k-candidate-folds")
    p.add_argument("--candidate-predictions", type=Path, default=ROOT / "build" / "task-003k-candidate-folds" / "vnext_predictions.csv")
    p.add_argument("--evidence-dir", type=Path, default=ROOT / "reports" / "task-003k-event-logistic")
    p.add_argument("--bootstrap-repetitions", type=int, default=1000)
    p.add_argument("--tolerance", type=float, default=TOL)
    p.add_argument("--require-complete", action="store_true", help="treat any incomplete check as an independent validation failure")
    return run(p.parse_args())

if __name__ == "__main__":
    raise SystemExit(main())
