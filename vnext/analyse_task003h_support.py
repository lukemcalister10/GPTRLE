"""Diagnose conditional-regressor training support for TASK-003H.

Diagnostic only: this script reads fold artifacts/datasets and benchmark rows, then
compares raw and preprocessed feature support for the conditional games and
conditional average regressors. It does not fit, mutate or export models.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances

ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from evaluate_v3_fast import CAT, NUM
from model_artifacts import split_temporal

KEYS = ["player_key", "origin_year", "lead"]
COHORTS = {
    "zero_prior_games": lambda d: d["total_games"].eq(0),
    "ruck": lambda d: d["position"].astype(str).eq("RUC"),
    "established_regressing": lambda d: d["age"].between(24, 26, inclusive="both")
    | d["tenure"].between(4, 5, inclusive="both"),
}


def _artifact_path(fold_dir: Path, lead: int, origin: int) -> Path:
    manifest = fold_dir / "fold_artifact_manifest.csv"
    if manifest.exists():
        m = pd.read_csv(manifest)
        row = m[(m["lead"].eq(lead)) & (m["origin_year"].eq(origin))]
        if not row.empty and "artifact_path" in row:
            return fold_dir / str(row.iloc[0]["artifact_path"])
    return fold_dir / "fold_artifacts" / f"lead_{lead}_origin_{origin}.joblib"


def load_benchmark_rows(comparison_dir: Path) -> pd.DataFrame:
    predictions = pd.read_csv(comparison_dir / "predictions.csv")
    targets = pd.read_csv(comparison_dir / "cohorts" / "targets.csv")
    snapshots = pd.read_csv(comparison_dir / "cohorts" / "included_snapshots.csv")
    rows = predictions.merge(targets, on=KEYS, validate="many_to_one").merge(
        snapshots, on=["player_key", "origin_year"], validate="many_to_one"
    )
    return rows[rows["model_id"].eq("vnext_fold_specific")].copy()


def raw_feature_summary(reference: pd.DataFrame, probe: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for col in NUM:
        ref = pd.to_numeric(reference[col], errors="coerce")
        val = pd.to_numeric(probe[col], errors="coerce")
        q01, q99 = ref.quantile([0.01, 0.99]) if ref.notna().any() else (np.nan, np.nan)
        lo, hi = ref.min(), ref.max()
        records.append(
            {
                "feature": col,
                "reference_missing_rate": float(ref.isna().mean()),
                "probe_missing_rate": float(val.isna().mean()),
                "reference_min": float(lo) if pd.notna(lo) else np.nan,
                "reference_p01": float(q01) if pd.notna(q01) else np.nan,
                "reference_median": float(ref.median()) if ref.notna().any() else np.nan,
                "reference_p99": float(q99) if pd.notna(q99) else np.nan,
                "reference_max": float(hi) if pd.notna(hi) else np.nan,
                "probe_min": float(val.min()) if val.notna().any() else np.nan,
                "probe_median": float(val.median()) if val.notna().any() else np.nan,
                "probe_max": float(val.max()) if val.notna().any() else np.nan,
                "probe_below_reference_min": int((val < lo).sum()) if pd.notna(lo) else 0,
                "probe_above_reference_max": int((val > hi).sum()) if pd.notna(hi) else 0,
                "probe_outside_reference_1_99_pct": int(((val < q01) | (val > q99)).sum()) if pd.notna(q01) and pd.notna(q99) else 0,
            }
        )
    for col in CAT:
        ref = set(reference[col].dropna().astype(str))
        val = probe[col].astype(str)
        unseen = sorted(set(val.dropna()) - ref)
        records.append(
            {
                "feature": col,
                "reference_missing_rate": float(reference[col].isna().mean()),
                "probe_missing_rate": float(probe[col].isna().mean()),
                "unseen_categories": "|".join(unseen),
                "probe_unseen_category_rows": int(val.isin(unseen).sum()),
            }
        )
    return pd.DataFrame(records)


def transformed_summary(artifact: Any, reference: pd.DataFrame, probe: pd.DataFrame) -> dict[str, float]:
    xr = artifact.preprocessor.transform(reference)
    xp = artifact.preprocessor.transform(probe)
    xr = xr.toarray() if hasattr(xr, "toarray") else np.asarray(xr)
    xp = xp.toarray() if hasattr(xp, "toarray") else np.asarray(xp)
    if len(probe) == 0 or len(reference) == 0:
        return {"n_reference": len(reference), "n_probe": len(probe)}
    d = pairwise_distances(xp, xr, metric="euclidean").min(axis=1)
    ref_norm = np.linalg.norm(xr, axis=1)
    probe_norm = np.linalg.norm(xp, axis=1)
    return {
        "n_reference": int(len(reference)),
        "n_probe": int(len(probe)),
        "nearest_train_distance_median": float(np.median(d)),
        "nearest_train_distance_p90": float(np.quantile(d, 0.90)),
        "reference_transformed_norm_p99": float(np.quantile(ref_norm, 0.99)),
        "probe_transformed_norm_p99": float(np.quantile(probe_norm, 0.99)),
        "probe_norm_above_reference_p99_rows": int((probe_norm > np.quantile(ref_norm, 0.99)).sum()),
    }


def analyse_fold(dataset: pd.DataFrame, benchmark: pd.DataFrame, fold_dir: Path, lead: int, origin: int) -> tuple[list[dict[str, Any]], list[pd.DataFrame]]:
    artifact = joblib.load(_artifact_path(fold_dir, lead, origin))
    train = dataset[(dataset.origin_year >= 2008) & ((dataset.origin_year + lead) < origin)].copy()
    fit, cal = split_temporal(train, lead)
    fit_active = fit[fit[f"l{lead}_meaningful"].astype(int).eq(1)].copy()
    cal_active = cal[cal[f"l{lead}_meaningful"].astype(int).eq(1)].copy()
    bench = benchmark[(benchmark["lead"].eq(lead)) & (benchmark["origin_year"].eq(origin))].copy()
    bench = bench.rename(columns={"player_key": "key"})
    summary_rows: list[dict[str, Any]] = []
    raw_tables: list[pd.DataFrame] = []
    for name, masker in COHORTS.items():
        probe = bench[masker(bench)].copy()
        for ref_name, ref in [("meaningful_fit_rows", fit_active), ("temporal_calibration_rows", cal_active)]:
            row = {"lead": lead, "origin_year": origin, "cohort": name, "reference": ref_name}
            row.update(transformed_summary(artifact, ref, probe))
            summary_rows.append(row)
            raw = raw_feature_summary(ref, probe)
            raw.insert(0, "reference", ref_name)
            raw.insert(0, "cohort", name)
            raw.insert(0, "origin_year", origin)
            raw.insert(0, "lead", lead)
            raw_tables.append(raw)
    return summary_rows, raw_tables


def write_markdown(out: Path, summary: pd.DataFrame, raw: pd.DataFrame) -> None:
    risk = summary.sort_values("nearest_train_distance_p90", ascending=False).head(10)
    lines = ["# TASK-003H conditional regressor support diagnosis", "", "Diagnostic only. No model fitting, protocol, production, value, keeper utility or UI changes.", "", "## Highest transformed-distance cohort/fold checks", "", risk.to_markdown(index=False), "", "## Risk interpretation", "", "- `probe_unseen_category_rows` flags categories ignored by one-hot encoding (`handle_unknown='ignore'`).", "- `probe_below_reference_min`, `probe_above_reference_max` and transformed norm exceedances flag extrapolation after median imputation and scaling.", "- Compare benchmark rows with both meaningful fit rows and temporal calibration rows because the conditional games and average regressors are trained only on meaningful fit outcomes, while residual/calibration diagnostics come from later meaningful rows.", ""]
    out.joinpath("support_diagnosis.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fold-dir", type=Path, required=True, help="Directory from run_historical_folds output")
    parser.add_argument("--comparison-dir", type=Path, required=True, help="TASK-003E comparison directory")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    dataset = pd.read_csv(args.fold_dir / "training_dataset.csv")
    benchmark = load_benchmark_rows(args.comparison_dir)
    fold_pairs = benchmark[["lead", "origin_year"]].drop_duplicates().sort_values(["lead", "origin_year"])
    summaries: list[dict[str, Any]] = []
    raws: list[pd.DataFrame] = []
    for lead, origin in fold_pairs.itertuples(index=False, name=None):
        s, r = analyse_fold(dataset, benchmark, args.fold_dir, int(lead), int(origin))
        summaries.extend(s); raws.extend(r)
    args.out.mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(summaries)
    raw = pd.concat(raws, ignore_index=True)
    summary.to_csv(args.out / "transformed_support_summary.csv", index=False)
    raw.to_csv(args.out / "raw_feature_support.csv", index=False)
    write_markdown(args.out, summary, raw)
    manifest = {"folds_checked": int(len(fold_pairs)), "summary_rows": int(len(summary)), "raw_rows": int(len(raw)), "cohorts": sorted(COHORTS)}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
