"""Run fold-specific vNext predictions for locked TASK-003 historical cohorts."""
from __future__ import annotations

import argparse, hashlib, json, shutil, sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark import (LOCKED_FOLDS, PREDICTION_KEY, QUANTILE_COLUMNS, THRESHOLDS,
    VNextAdapter, assert_common_keys_and_targets, normalise_predictions, prediction_keys_from_targets)
from build_historical_cohorts import DEFAULT_OUT as DEFAULT_COHORT_OUT, build_locked_cohorts
from build_annual_dataset import build_rows
from model_artifacts import train_lead, predict as predict_lead
from historical_eligibility import load_historical_players

DEFAULT_OUT = ROOT / "build" / "task-003b-vnext-folds"
PLAYER_DATA = ROOT / "engine" / "rl_after" / "rl_model_data.json"
SAMPLE_COUNT = 512
MODEL_ID = "vnext_fold_specific"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, frame: pd.DataFrame) -> dict[str, Any]:
    frame.to_csv(path, index=False, lineterminator="\n")
    return {"rows": int(len(frame)), "sha256": sha256_path(path), "bytes": path.stat().st_size}


def seed_for(player_key: str, origin_year: int, lead: int) -> int:
    h = hashlib.sha256(f"TASK-003B|{player_key}|{origin_year}|{lead}".encode()).digest()
    return int.from_bytes(h[:8], "little") & 0xFFFFFFFF


def add_residual_quantiles(pred: pd.DataFrame, artifact: Any, rows: pd.DataFrame, sample_count: int = SAMPLE_COUNT) -> pd.DataFrame:
    out = pred.copy()
    qs = [0.10, 0.25, 0.50, 0.75, 0.90, 0.97]
    qvals = {c: [] for c in QUANTILE_COLUMNS}
    gsd = float(getattr(artifact, "games_resid_sd", 3.0))
    asd = float(getattr(artifact, "avg_resid_sd", 12.0))
    for i, r in out.iterrows():
        keyrow = rows.loc[i]
        rng = np.random.default_rng(seed_for(str(keyrow.player_key), int(keyrow.origin_year), int(keyrow.lead)))
        meaningful = rng.random(sample_count) < float(r.p_meaningful)
        games = np.zeros(sample_count, dtype=float)
        avg = np.zeros(sample_count, dtype=float)
        n = int(meaningful.sum())
        if n:
            games[meaningful] = np.clip(rng.normal(float(r.cond_games), gsd, n), 0.0, 23.0)
            avg[meaningful] = np.clip(rng.normal(float(r.cond_avg), asd, n), 0.0, 145.0)
        points = np.maximum(0.0, games * avg)
        vals = np.maximum.accumulate(np.quantile(points, qs))
        # genuinely degenerate all-zero forecasts may remain equal; otherwise deterministic simulation spreads values.
        for col, val in zip(QUANTILE_COLUMNS, vals, strict=True):
            qvals[col].append(float(val))
    for col, vals in qvals.items():
        out[col] = vals
    return out


def predict_with_quantiles(artifact: Any, rows: pd.DataFrame) -> pd.DataFrame:
    base = predict_lead(artifact, rows).rename(columns={f"p{t}": f"p_avg_ge_{t}" for t in THRESHOLDS})
    return add_residual_quantiles(base, artifact, rows)


def load_or_build_cohorts(cohort_dir: Path) -> dict[str, pd.DataFrame]:
    manifest_path = cohort_dir / "manifest.json"
    if not manifest_path.exists():
        build_locked_cohorts(cohort_dir)
    cohorts = {name: pd.read_csv(cohort_dir / f"{name}.csv") for name in ["fold_plan", "included_snapshots", "cohort_membership", "targets", "excluded", "target_failures"]}
    if len(cohorts["target_failures"]):
        raise ValueError("target-data failures must remain zero")
    return cohorts


def train_artifacts(dataset: pd.DataFrame, out_dir: Path) -> tuple[dict[tuple[int,int], Any], pd.DataFrame, pd.DataFrame]:
    artifacts: dict[tuple[int,int], Any] = {}
    manifest_rows=[]; count_rows=[]; failure_rows=[]
    art_dir = out_dir / "fold_artifacts"; art_dir.mkdir(parents=True, exist_ok=True)
    for lead, origins in LOCKED_FOLDS.items():
        for origin in origins:
            train = dataset[(dataset.origin_year >= 2008) & ((dataset.origin_year + lead) < origin)].copy()
            if train.empty:
                failure_rows.append({"lead":lead,"origin_year":origin,"reason":"no_legal_training_rows"}); continue
            if int((train.origin_year + lead).max()) >= origin:
                raise ValueError(f"illegal training cutoffs for lead {lead} origin {origin}")
            art = train_lead(train, lead)
            art.artifact_id = f"vnext_lead{lead}_origin{origin}"
            path = art_dir / f"lead_{lead}_origin_{origin}.joblib"
            joblib.dump(art, path, compress=3)
            artifacts[(lead, origin)] = art
            target_max = int(train.origin_year.max() + lead)
            manifest_rows.append({"lead":lead,"origin_year":origin,"artifact_path":str(path.relative_to(out_dir)),"artifact_sha256":sha256_path(path),"train_max_origin":int(train.origin_year.max()),"training_target_max_year":target_max,"allowed_training_origins":"|".join(map(str, sorted(map(int, train.origin_year.unique())))),"n_fit":int(art.n_fit),"n_cal":int(art.n_cal),"games_resid_sd":float(art.games_resid_sd),"avg_resid_sd":float(art.avg_resid_sd)})
            count_rows.append({"lead":lead,"origin_year":origin,"train_rows":len(train),"train_min_origin":int(train.origin_year.min()),"train_max_origin":int(train.origin_year.max()),"training_target_max_year":target_max})
    expected = {(l,o) for l, os in LOCKED_FOLDS.items() for o in os}
    missing = sorted(expected - set(artifacts))
    if missing:
        raise ValueError(f"missing fold artifact(s): {missing[:5]}")
    return artifacts, pd.DataFrame(manifest_rows), pd.DataFrame(count_rows)


def run(out_dir: Path = DEFAULT_OUT, cohort_dir: Path = DEFAULT_COHORT_OUT, rebuild: bool = False) -> dict[str, Any]:
    if rebuild and out_dir.exists(): shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cohorts = load_or_build_cohorts(cohort_dir)
    targets = cohorts["targets"].sort_values(PREDICTION_KEY).reset_index(drop=True)
    if len(targets) != 20094:
        raise ValueError(f"locked cohort row count changed: expected 20094 got {len(targets)}")
    if len(cohorts["included_snapshots"]) != 5622:
        raise ValueError(f"included snapshot count changed: expected 5622 got {len(cohorts['included_snapshots'])}")
    players = load_historical_players(PLAYER_DATA)
    dataset = build_rows(players, min_origin=2008, max_origin=2024)
    dataset_path = out_dir / "training_dataset.csv"; write_csv(dataset_path, dataset)
    artifacts, fold_manifest, fold_counts = train_artifacts(dataset, out_dir)
    adapter = VNextAdapter(artifacts=artifacts, prediction_function=predict_with_quantiles, model_id=MODEL_ID, quantile_method="two_part_deterministic_residual_simulation")
    preds = adapter.predict(cohorts["included_snapshots"], prediction_keys_from_targets(targets))
    preds = normalise_predictions(MODEL_ID, preds.drop(columns=["model_id"]))
    assert_common_keys_and_targets({MODEL_ID: preds}, targets)
    counts = preds.groupby(["origin_year","lead"], as_index=False).size().rename(columns={"size":"prediction_rows"})
    artifacts_meta = {}
    artifacts_meta["vnext_predictions.csv"] = write_csv(out_dir / "vnext_predictions.csv", preds)
    artifacts_meta["fold_artifact_manifest.csv"] = write_csv(out_dir / "fold_artifact_manifest.csv", fold_manifest.sort_values(["origin_year","lead"]))
    artifacts_meta["fold_training_counts.csv"] = write_csv(out_dir / "fold_training_counts.csv", fold_counts.sort_values(["origin_year","lead"]))
    failures = pd.DataFrame(columns=["lead","origin_year","reason"])
    artifacts_meta["fold_failures.csv"] = write_csv(out_dir / "fold_failures.csv", failures)
    artifacts_meta["counts_by_origin_lead.csv"] = write_csv(out_dir / "counts_by_origin_lead.csv", counts)
    qmethod = {"method":"two_part_deterministic_residual_simulation","sample_count":SAMPLE_COUNT,"seed":"sha256(TASK-003B|player_key|origin_year|lead)","components":["p_meaningful Bernoulli mass at zero","conditional games normal residual scale","conditional average normal residual scale"],"non_negative":True,"non_crossing_enforced":True}
    (out_dir / "quantile_method.json").write_text(json.dumps(qmethod, indent=2, sort_keys=True)+"\n")
    artifacts_meta["quantile_method.json"]={"rows":1,"sha256":sha256_path(out_dir/"quantile_method.json"),"bytes":(out_dir/"quantile_method.json").stat().st_size}
    manifest = {"task":"TASK-003B-vNext-fold-predictions","model_id":MODEL_ID,"prediction_rows":int(len(preds)),"included_snapshot_rows":int(len(cohorts["included_snapshots"])),"folds":LOCKED_FOLDS,"target_failure_rows":0,"quantile_method":qmethod,"input_hashes":{"player_data_sha256":sha256_path(PLAYER_DATA),"cohort_manifest_sha256":sha256_path(cohort_dir/"manifest.json"),"training_dataset_sha256":sha256_path(dataset_path)},"output_hashes":{k:v["sha256"] for k,v in artifacts_meta.items()},"artifacts":artifacts_meta,"reproduction_command":"python vnext/run_historical_folds.py --out build/task-003b-vnext-folds"}
    (out_dir / "prediction_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    return manifest


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--out', type=Path, default=DEFAULT_OUT); ap.add_argument('--cohort-dir', type=Path, default=DEFAULT_COHORT_OUT); ap.add_argument('--rebuild', action='store_true')
    args=ap.parse_args(); print(json.dumps(run(args.out, args.cohort_dir, args.rebuild), indent=2, sort_keys=True)); return 0
if __name__ == '__main__': raise SystemExit(main())
