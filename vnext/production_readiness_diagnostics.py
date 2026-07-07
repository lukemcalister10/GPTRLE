"""Diagnostic-only production-readiness/current-board comparison scaffold.

This module intentionally performs no model fitting and changes no production values.
It reads already-produced CSV/JSON artifacts, validates comparability, and emits
coverage, forecast/value deltas, validity checks, hashes, rollback notes and
shadow-mode gates for a future release decision.
"""
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

KEY_ALIASES = ("key", "legacy_key", "stable_player_id", "player_key")
NAME_ALIASES = ("player", "name", "player_name", "legacy_name")
LEAD_ALIASES = ("lead", "forecast_lead", "year_ahead")
FORECAST_COLS = ("p_meaningful", "cond_games", "cond_avg", "exp_games", "exp_avg", "exp_points", "p80", "p90", "p100", "p110", "p120")
VALUE_COLS = ("five_year_utility_mean", "five_year_utility_median", "future_value_y1_mean", "future_value_y2_mean", "value", "v", "keeper_value")
THRESHOLD_COLS = ("p80", "p90", "p100", "p110", "p120")
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".json":
        obj = json.loads(path.read_text())
        if isinstance(obj, list):
            return pd.DataFrame(obj)
        if isinstance(obj, dict):
            for v in obj.values():
                if isinstance(v, list):
                    return pd.DataFrame(v)
        return pd.json_normalize(obj)
    return pd.read_csv(path)


def first_col(df: pd.DataFrame, aliases: Iterable[str]) -> str | None:
    lower = {c.lower(): c for c in df.columns}
    for a in aliases:
        if a in lower:
            return lower[a]
    return None


def normalize(df: pd.DataFrame, label: str) -> pd.DataFrame:
    out = df.copy()
    key = first_col(out, KEY_ALIASES)
    if key is None:
        raise ValueError(f"{label} has no player key column; expected one of {KEY_ALIASES}")
    if key != "key":
        out = out.rename(columns={key: "key"})
    name = first_col(out, NAME_ALIASES)
    if name and name != "player":
        out = out.rename(columns={name: "player"})
    lead = first_col(out, LEAD_ALIASES)
    if lead and lead != "lead":
        out = out.rename(columns={lead: "lead"})
    out["key"] = out["key"].astype(str)
    return out


def add_bands(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "age" in out:
        out["age_band"] = pd.cut(pd.to_numeric(out["age"], errors="coerce"), [0, 20, 23, 26, 29, 99], labels=["<=20", "21-23", "24-26", "27-29", "30+"])
    if "tenure" in out:
        out["tenure_band"] = pd.cut(pd.to_numeric(out["tenure"], errors="coerce"), [-1, 0, 2, 5, 99], labels=["0", "1-2", "3-5", "6+"])
    pick_col = "pick" if "pick" in out else None
    if pick_col:
        out["draft_pick_band"] = pd.cut(pd.to_numeric(out[pick_col], errors="coerce"), [0, 10, 30, 60, 999], labels=["1-10", "11-30", "31-60", "61+"])
    games_col = "prior_games" if "prior_games" in out else ("games" if "games" in out else ("cg" if "cg" in out else None))
    if games_col:
        out["prior_games_band"] = pd.cut(pd.to_numeric(out[games_col], errors="coerce"), [-1, 0, 20, 80, 999], labels=["0", "1-20", "21-80", "81+"])
    return out


def coverage(universe: pd.DataFrame, datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    u = set(universe["key"])
    rows = []
    for label, df in datasets.items():
        keys = set(df["key"])
        rows.append({"dataset": label, "universe_players": len(u), "dataset_players": len(keys), "covered": len(u & keys), "missing_from_dataset": len(u - keys), "extra_not_in_universe": len(keys - u)})
    return pd.DataFrame(rows)


def exclusions(universe: pd.DataFrame, datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows=[]
    names = universe.set_index("key")["player"].to_dict() if "player" in universe else {}
    u=set(universe["key"])
    for label, df in datasets.items():
        keys=set(df["key"])
        for k in sorted(u-keys): rows.append({"dataset": label, "key": k, "player": names.get(k), "exclusion": "missing_from_dataset"})
        for k in sorted(keys-u): rows.append({"dataset": label, "key": k, "player": None, "exclusion": "extra_not_in_universe"})
    return pd.DataFrame(rows)


def compare_by_key(base: pd.DataFrame, other: pd.DataFrame, base_label: str, other_label: str) -> pd.DataFrame:
    common_cols = [c for c in FORECAST_COLS + VALUE_COLS if c in base.columns and c in other.columns]
    by = ["key"] + (["lead"] if "lead" in base.columns and "lead" in other.columns else [])
    if not common_cols:
        return pd.DataFrame([{"base": base_label, "other": other_label, "comparison_status": "incompatible_no_shared_forecast_or_value_columns"}])
    m = base[by + common_cols].merge(other[by + common_cols], on=by, how="inner", suffixes=(f"_{base_label}", f"_{other_label}"))
    for c in common_cols:
        m[f"delta_{c}"] = pd.to_numeric(m[f"{c}_{other_label}"], errors="coerce") - pd.to_numeric(m[f"{c}_{base_label}"], errors="coerce")
    return m


def largest_changes(comp: pd.DataFrame, n: int) -> pd.DataFrame:
    if comp.empty or "comparison_status" in comp.columns:
        return comp
    rows=[]
    id_cols=[c for c in ["key","lead"] if c in comp.columns]
    for col in [c for c in comp.columns if c.startswith("delta_")]:
        tmp=comp[id_cols+[col]].dropna().copy()
        for direction, asc in [("decrease", True),("increase", False)]:
            for _, r in tmp.sort_values(col, ascending=asc).head(n).iterrows():
                rows.append({"metric": col.removeprefix("delta_"), "direction": direction, **{c:r[c] for c in id_cols}, "delta": r[col]})
    return pd.DataFrame(rows)


def rank_changes(base: pd.DataFrame, other: pd.DataFrame, metric: str) -> pd.DataFrame:
    if metric not in base or metric not in other:
        return pd.DataFrame([{"comparison_status": f"rank_metric_missing:{metric}"}])
    b=base[["key",metric]].drop_duplicates("key").copy(); o=other[["key",metric]].drop_duplicates("key").copy()
    b["base_rank"] = pd.to_numeric(b[metric], errors="coerce").rank(ascending=False, method="min")
    o["other_rank"] = pd.to_numeric(o[metric], errors="coerce").rank(ascending=False, method="min")
    m=b[["key","base_rank"]].merge(o[["key","other_rank"]], on="key")
    m["rank_change"] = m["base_rank"] - m["other_rank"]
    return m.sort_values("rank_change", key=lambda s: s.abs(), ascending=False)


def validity(df: pd.DataFrame, label: str) -> pd.DataFrame:
    rows=[]
    for c in df.columns:
        s=pd.to_numeric(df[c], errors="coerce")
        if s.notna().any():
            rows.append({"dataset": label,"column": c,"rows": len(df),"missing": int(df[c].isna().sum()),"non_finite": int((~np.isfinite(s.fillna(0))).sum())})
        is_probability = c.startswith("p_") or c in THRESHOLD_COLS or c in {"p_meaningful"}
        if is_probability and s.notna().any():
            rows[-1]["prob_out_of_bounds"] = int(((s<0)|(s>1)).sum())
    for cols in [THRESHOLD_COLS, ("q10","q50","q90"), ("p10","median","p90")]:
        present=[c for c in cols if c in df]
        if len(present) >= 2:
            bad=0
            vals=df[present].apply(pd.to_numeric, errors="coerce")
            for a,b in zip(present, present[1:]):
                # Threshold probabilities should be non-increasing; quantiles non-decreasing.
                if present == list(THRESHOLD_COLS)[:len(present)]: bad += int((vals[a] < vals[b]).sum())
                else: bad += int((vals[a] > vals[b]).sum())
            rows.append({"dataset": label,"column": ">".join(present),"rows": len(df),"missing": int(vals.isna().sum().sum()),"non_finite": 0,"monotonicity_violations": bad})
    return pd.DataFrame(rows)


def artifact_check(paths: list[Path]) -> pd.DataFrame:
    rows=[]
    for p in paths:
        if not p.exists():
            rows.append({"path": str(p), "exists": False})
            continue
        if p.is_file():
            rows.append({"path": str(p), "exists": True, "kind":"file", "sha256": sha256(p), "loaded_without_fitting": True})
        else:
            files=sorted(x for x in p.rglob("*") if x.is_file())
            rows.append({"path": str(p), "exists": True, "kind":"directory", "file_count": len(files), "sha256": hashlib.sha256("".join(sha256(x) for x in files).encode()).hexdigest(), "loaded_without_fitting": True})
    return pd.DataFrame(rows)


def _md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_(no rows)_"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_md(path: Path, cov: pd.DataFrame, valid: pd.DataFrame, artifacts: pd.DataFrame, thresholds: dict) -> None:
    path.write_text("\n".join([
        "# Production readiness diagnostic scaffold report",
        "",
        "Diagnostic only: this report does not approve a model, alter production, fit models, or transform keeper utility.",
        "",
        "## Coverage summary", _md_table(cov), "",
        "## Validity summary", _md_table(valid.head(80)), "",
        "## Artifact loading / reproducibility", _md_table(artifacts), "",
        "## Acceptance thresholds for future shadow mode", json.dumps(thresholds, indent=2), "",
        "## Rejection thresholds", "Reject or block release if any hard gate fails: player-key coverage below threshold, non-finite required outputs, invalid probabilities, threshold/quantile crossing, model fitting during inference, missing rollback artifact, or undocumented production/vNext incompatibility.",
        "", "## Rollback requirements", "Keep the frozen legacy export path and hashes available; record exact input/output artifact hashes; verify the candidate can be disabled without changing keeper utility or UI behaviour.",
    ]))


def main(argv=None) -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--universe", required=True); ap.add_argument("--legacy"); ap.add_argument("--vnext", required=True); ap.add_argument("--candidate")
    ap.add_argument("--artifacts", action="append", default=[]); ap.add_argument("--out", required=True); ap.add_argument("--top-n", type=int, default=20)
    args=ap.parse_args(argv)
    out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    universe=normalize(read_table(Path(args.universe)), "universe")
    datasets={"vnext": normalize(read_table(Path(args.vnext)), "vnext")}
    if args.legacy: datasets["legacy"] = normalize(read_table(Path(args.legacy)), "legacy")
    if args.candidate: datasets["candidate"] = normalize(read_table(Path(args.candidate)), "candidate")
    cov=coverage(universe,datasets); cov.to_csv(out/"coverage_summary.csv", index=False)
    exclusions(universe,datasets).to_csv(out/"coverage_exclusions.csv", index=False)
    valid=pd.concat([validity(df,l) for l,df in datasets.items()], ignore_index=True); valid.to_csv(out/"validity_checks.csv", index=False)
    artifacts=artifact_check([Path(p) for p in args.artifacts]); artifacts.to_csv(out/"artifact_reproducibility.csv", index=False)
    for label, df in datasets.items(): add_bands(df).to_csv(out/f"{label}_with_slice_bands.csv", index=False)
    pairs=[]
    if "legacy" in datasets: pairs.append(("legacy","vnext"))
    if "candidate" in datasets: pairs.append(("vnext","candidate"))
    for a,b in pairs:
        comp=compare_by_key(datasets[a],datasets[b],a,b); comp.to_csv(out/f"compare_{a}_to_{b}.csv", index=False)
        largest_changes(comp,args.top_n).to_csv(out/f"largest_changes_{a}_to_{b}.csv", index=False)
        metric=next((m for m in VALUE_COLS+FORECAST_COLS if m in datasets[a].columns and m in datasets[b].columns), "")
        if metric: rank_changes(datasets[a],datasets[b],metric).to_csv(out/f"rank_changes_{a}_to_{b}.csv", index=False)
    thresholds={"hard_player_coverage_min": 804, "probability_bounds": "all probability columns within [0,1]", "threshold_probabilities": "non-increasing p80>=p90>=p100>=p110>=p120", "non_finite_required_outputs": 0, "inference_fitting_allowed": False, "shadow_mode_min_duration": "one full refresh cycle before release decision", "approval": "requires separate release PR and explicit owner approval"}
    manifest={"inputs": {"universe": args.universe, "legacy": args.legacy, "vnext": args.vnext, "candidate": args.candidate}, "hashes": {k: sha256(Path(v)) for k,v in {"universe":args.universe,"legacy":args.legacy,"vnext":args.vnext,"candidate":args.candidate}.items() if v}, "thresholds": thresholds}
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2))
    write_md(out/"README.md", cov, valid, artifacts, thresholds)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
