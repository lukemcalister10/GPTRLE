"""TASK-003N current-board impact review for TASK-003K.

Diagnostic-only: compare two persisted annual artifact sets on the authoritative
804-player 2026 universe. The script performs no model fitting and does not
apply player-specific adjustments.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from active_universe import build_reconciliation, load_authoritative, load_legacy_board, load_vnext_previous
from snapshot import build_snapshot, canonical_position

ROOT = Path(__file__).resolve().parents[1]
ANNUAL_METRICS = ["p_meaningful", "exp_games", "exp_avg", "exp_points", "cond_games", "cond_avg"]
QUANTILE_METRICS = ["p80", "p90", "p100", "p110"]
RANK_METRICS = ["exp_points_5y", "exp_games_5y", "p_meaningful_5y", "p100_any_5y"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, df: pd.DataFrame) -> str:
    df.to_csv(path, index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    return sha256_file(path)


def universe(authoritative: Path, legacy: Path, previous: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    reports = build_reconciliation(load_authoritative(authoritative), load_legacy_board(legacy), load_vnext_previous(previous))
    matched = reports["matched_players"].copy()
    if len(matched) != 804:
        raise ValueError(f"authoritative coverage must be exactly 804 matched players; got {len(matched)}")
    players = {p["key"]: p for p in load_vnext_previous(previous)}
    rows: list[dict[str, Any]] = []
    for _, m in matched.sort_values("source_row").iterrows():
        p = players[m.legacy_key]
        snap = build_snapshot(p, 2026)
        if snap is None:
            raise ValueError(f"could not build 2026 snapshot for {m.player_name} ({m.legacy_key})")
        d = snap.to_dict()
        d.update(
            stable_player_id=m.stable_player_id,
            source_row=int(m.source_row),
            player_name=m.player_name,
            affl_team=m.affl_team,
            eligibilities=m.eligibilities,
            position_utility=canonical_position((p.get("future_position") or p.get("present_position") or d.get("position"))),
            draft_pathway=str(p.get("type") or p.get("_draft") or "UNKNOWN"),
            prior_games=sum(int(r.get("games", 0) or 0) for r in (p.get("scoring") or []) if int(r.get("year", 0) or 0) <= 2025),
        )
        rows.append(d)
    snapshots = pd.DataFrame(rows)
    if snapshots["stable_player_id"].duplicated().any() or snapshots["key"].duplicated().any():
        raise ValueError("authoritative current board contains duplicate stable ids or legacy keys")
    return matched, snapshots


def predict_board(label: str, artifact_dir: Path, module_name: str, snapshots: pd.DataFrame) -> pd.DataFrame:
    mod = importlib.import_module(module_name)
    pieces = []
    for lead in range(1, 6):
        art_path = artifact_dir / f"lead_{lead}.joblib"
        if not art_path.exists():
            raise FileNotFoundError(f"{label} missing artifact {art_path}")
        art = joblib.load(art_path)
        pred = mod.predict(art, snapshots)
        pred = pred.rename(columns={"p80": "p80"})
        out = pd.concat(
            [
                snapshots[["stable_player_id", "key", "player_name", "affl_team", "eligibilities", "position", "position_utility", "age", "tenure", "pick", "draft_pathway", "prior_games"]].reset_index(drop=True),
                pred.reset_index(drop=True),
            ],
            axis=1,
        )
        out["model_id"] = label
        out["lead"] = lead
        out["forecast_year"] = 2026 + lead
        # Normalise threshold names produced by model_artifacts.
        for t in (80, 90, 100, 110):
            if f"p{t}" not in out.columns and f"p_avg_ge_{t}" in out.columns:
                out[f"p{t}"] = out[f"p_avg_ge_{t}"]
        pieces.append(out)
    annual = pd.concat(pieces, ignore_index=True)
    annual["zero_history"] = annual["prior_games"].eq(0)
    annual["age_band"] = pd.cut(annual["age"], bins=[0, 21, 25, 29, 200], labels=["<=21", "22-25", "26-29", "30+"])
    annual["tenure_band"] = pd.cut(annual["tenure"], bins=[-1, 0, 2, 5, 99], labels=["0", "1-2", "3-5", "6+"])
    return annual


def validation_checks(annual: pd.DataFrame) -> pd.DataFrame:
    keys = ["model_id", "stable_player_id", "lead"]
    required = ANNUAL_METRICS + QUANTILE_METRICS
    rows = []
    for model, g in annual.groupby("model_id"):
        rows.append({
            "model_id": model,
            "players": int(g.stable_player_id.nunique()),
            "rows": int(len(g)),
            "expected_rows": 804 * 5,
            "duplicate_keys": int(g.duplicated(keys).sum()),
            "missing_required_values": int(g[required].isna().sum().sum()),
            "non_finite_required_values": int((~np.isfinite(g[required].to_numpy(float))).sum()),
        })
    return pd.DataFrame(rows)


def deltas(current: pd.DataFrame, candidate: pd.DataFrame) -> pd.DataFrame:
    idx = ["stable_player_id", "lead"]
    cols = ["key", "player_name", "affl_team", "eligibilities", "position", "position_utility", "age", "tenure", "pick", "draft_pathway", "prior_games", "zero_history", "age_band", "tenure_band"]
    c = current[idx + cols + ANNUAL_METRICS + QUANTILE_METRICS].rename(columns={m: f"current_{m}" for m in ANNUAL_METRICS + QUANTILE_METRICS})
    k = candidate[idx + ANNUAL_METRICS + QUANTILE_METRICS].rename(columns={m: f"candidate_{m}" for m in ANNUAL_METRICS + QUANTILE_METRICS})
    out = c.merge(k, on=idx, validate="one_to_one")
    for m in ANNUAL_METRICS + QUANTILE_METRICS:
        out[f"delta_{m}"] = out[f"candidate_{m}"] - out[f"current_{m}"]
    return out


def player_rollup(d: pd.DataFrame) -> pd.DataFrame:
    q = d.groupby("stable_player_id", as_index=False).agg(
        key=("key", "first"), player_name=("player_name", "first"), affl_team=("affl_team", "first"), eligibilities=("eligibilities", "first"),
        position=("position", "first"), position_utility=("position_utility", "first"), age=("age", "first"), tenure=("tenure", "first"), pick=("pick", "first"), draft_pathway=("draft_pathway", "first"), prior_games=("prior_games", "first"), zero_history=("zero_history", "first"), age_band=("age_band", "first"), tenure_band=("tenure_band", "first"),
        current_exp_points_5y=("current_exp_points", "sum"), candidate_exp_points_5y=("candidate_exp_points", "sum"),
        current_exp_games_5y=("current_exp_games", "sum"), candidate_exp_games_5y=("candidate_exp_games", "sum"),
        current_p_meaningful_5y=("current_p_meaningful", "sum"), candidate_p_meaningful_5y=("candidate_p_meaningful", "sum"),
        current_p100_any_5y=("current_p100", lambda s: 1 - float(np.prod(1 - s))), candidate_p100_any_5y=("candidate_p100", lambda s: 1 - float(np.prod(1 - s))),
    )
    for m in RANK_METRICS:
        q[f"delta_{m}"] = q[f"candidate_{m}"] - q[f"current_{m}"]
        q[f"current_rank_{m}"] = q[f"current_{m}"].rank(method="first", ascending=False).astype(int)
        q[f"candidate_rank_{m}"] = q[f"candidate_{m}"].rank(method="first", ascending=False).astype(int)
        q[f"rank_change_{m}"] = q[f"current_rank_{m}"] - q[f"candidate_rank_{m}"]
    return q.sort_values("delta_exp_points_5y", ascending=False)


def slice_summary(d: pd.DataFrame) -> pd.DataFrame:
    specs = {"position": "position_utility", "age": "age_band", "tenure": "tenure_band", "draft_pathway": "draft_pathway", "prior_games": "zero_history"}
    rows = []
    for name, col in specs.items():
        for (lead, val), g in d.groupby(["lead", col], observed=False, dropna=False):
            rows.append({"slice_type": name, "slice_value": str(val), "lead": int(lead), "players": int(g.stable_player_id.nunique()), **{f"mean_delta_{m}": float(g[f"delta_{m}"].mean()) for m in ANNUAL_METRICS + QUANTILE_METRICS}})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--current-artifacts", default=str(ROOT / "artifacts/vnext/progress_05"))
    ap.add_argument("--candidate-artifacts", required=True)
    ap.add_argument("--current-module", default="model_artifacts")
    ap.add_argument("--candidate-module", default="model_artifacts")
    ap.add_argument("--authoritative", default=str(ROOT / "data/current/Players_2026.csv"))
    ap.add_argument("--legacy", default=str(ROOT / "data/rl_build/rl_app_data.json"))
    ap.add_argument("--previous-vnext", default=str(ROOT / "engine/rl_after/rl_model_data.json"))
    ap.add_argument("--out", default=str(ROOT / "reports/task-003n-current-board-impact"))
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    matched, snapshots = universe(Path(args.authoritative), Path(args.legacy), Path(args.previous_vnext))
    cur = predict_board("current", Path(args.current_artifacts), args.current_module, snapshots)
    cand = predict_board("candidate", Path(args.candidate_artifacts), args.candidate_module, snapshots)
    annual = pd.concat([cur, cand], ignore_index=True)
    checks = validation_checks(annual)
    if not ((checks.players == 804) & (checks.rows == 4020) & (checks.duplicate_keys == 0) & (checks.missing_required_values == 0) & (checks.non_finite_required_values == 0)).all():
        raise ValueError(f"current-board validation checks failed:\n{checks.to_string(index=False)}")
    d = deltas(cur, cand)
    roll = player_rollup(d)
    slices = slice_summary(d)
    age30_lead5 = d[(d.age >= 30) & (d.lead == 5)].sort_values("delta_exp_points", ascending=False)
    zero_history = d[d.zero_history].sort_values(["lead", "delta_exp_points"], ascending=[True, False])
    largest = pd.concat([roll.nlargest(50, "delta_exp_points_5y").assign(direction="increase"), roll.nsmallest(50, "delta_exp_points_5y").assign(direction="decrease")])
    hashes = {
        "authoritative_universe.csv": write_csv(out / "authoritative_universe.csv", matched),
        "current_board_annual.csv": write_csv(out / "current_board_annual.csv", cur),
        "candidate_board_annual.csv": write_csv(out / "candidate_board_annual.csv", cand),
        "annual_deltas.csv": write_csv(out / "annual_deltas.csv", d),
        "player_rollup_rank_changes.csv": write_csv(out / "player_rollup_rank_changes.csv", roll),
        "largest_changes.csv": write_csv(out / "largest_changes.csv", largest),
        "slice_summary.csv": write_csv(out / "slice_summary.csv", slices),
        "age30_plus_lead5.csv": write_csv(out / "age30_plus_lead5.csv", age30_lead5),
        "zero_history_players.csv": write_csv(out / "zero_history_players.csv", zero_history),
        "validation_checks.csv": write_csv(out / "validation_checks.csv", checks),
    }
    manifest = {
        "task": "TASK-003N-current-board-impact-review",
        "issue": 21,
        "players": 804,
        "forecast_origin_year": 2026,
        "diagnostic_only": True,
        "model_fitting_performed": False,
        "current_artifacts": str(Path(args.current_artifacts)),
        "candidate_artifacts": str(Path(args.candidate_artifacts)),
        "current_module": args.current_module,
        "candidate_module": args.candidate_module,
        "input_hashes": {p: sha256_file(Path(p)) for p in [args.authoritative, args.legacy, args.previous_vnext] if Path(p).is_file()},
        "artifact_hashes": hashes,
        "commands": ["python vnext/review_task003n_current_board.py --candidate-artifacts <TASK-003K_ARTIFACT_DIR> --candidate-module <TASK-003K_MODULE> --out reports/task-003n-current-board-impact"],
        "guardrail_confirmation": "Current-board outputs are generated after persisted candidate artifacts are supplied; this script performs no fitting and must not be used to tune the historical candidate.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(out), "players": 804, "rows_per_model": 4020, "manifest": str(out / "manifest.json")}, indent=2))


if __name__ == "__main__":
    main()
