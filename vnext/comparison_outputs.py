"""Write fold, bootstrap, reliability and slice artifacts for TASK-003."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from comparison_diagnostics import (
    fold_differences,
    metrics_by_origin_lead,
    player_block_bootstrap,
    reliability_tables,
    row_losses,
    slice_metrics,
)
from comparison_harness import sha256_file, write_csv

BOOTSTRAP_COLUMNS = [
    "model_id",
    "baseline_model_id",
    "metric",
    "difference",
    "ci_low",
    "ci_high",
    "probability_challenger_better",
    "bootstrap_repetitions",
    "player_blocks",
    "seed",
]


def build_diagnostic_outputs(
    out_dir: Path,
    predictions: pd.DataFrame,
    targets: pd.DataFrame,
    snapshots: pd.DataFrame,
    *,
    bootstrap_repetitions: int = 1000,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    losses = row_losses(predictions, targets)
    origin_lead = metrics_by_origin_lead(losses)
    fold_delta = fold_differences(origin_lead)
    bootstrap = player_block_bootstrap(
        losses,
        repetitions=bootstrap_repetitions,
        seed=3003,
    )
    if bootstrap.empty:
        bootstrap = pd.DataFrame(columns=BOOTSTRAP_COLUMNS)
    reliability = reliability_tables(predictions, targets)
    slices = slice_metrics(predictions, targets, snapshots, minimum_n=200)

    artifacts = {
        "metrics_by_origin_lead.csv": write_csv(
            out_dir / "metrics_by_origin_lead.csv", origin_lead
        ),
        "fold_differences_vs_baseline.csv": write_csv(
            out_dir / "fold_differences_vs_baseline.csv", fold_delta
        ),
        "player_block_bootstrap.csv": write_csv(
            out_dir / "player_block_bootstrap.csv", bootstrap
        ),
        "reliability.csv": write_csv(out_dir / "reliability.csv", reliability),
        "slice_metrics.csv": write_csv(out_dir / "slice_metrics.csv", slices),
    }

    models = sorted(predictions["model_id"].astype(str).unique())
    lines = [
        "# TASK-003 comparison report",
        "",
        f"- Locked rows per model: **{len(targets):,}**",
        f"- Models: {', '.join(f'`{model}`' for model in models)}",
        f"- Formal frozen-legacy evidence included: **{'yes' if 'legacy_frozen' in models else 'no'}**",
        "",
        "## Status",
        "",
    ]
    if len(bootstrap):
        lines.extend(
            [
                "Paired player-block bootstrap results are available in `player_block_bootstrap.csv`. Differences are challenger minus baseline, so negative values favour the challenger.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "No challenger input was supplied, so paired differences have not yet been calculated.",
                "",
            ]
        )
    if "legacy_frozen" not in models:
        lines.extend(
            [
                "No artifact labelled `legacy_frozen` was included. Diagnostic legacy proxy outputs are deliberately rejected and cannot support formal model-selection claims.",
                "",
            ]
        )
    report_path = out_dir / "comparison_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    artifacts["comparison_report.md"] = {
        "rows": len(lines),
        "bytes": int(report_path.stat().st_size),
        "sha256": sha256_file(report_path),
    }

    metadata = {
        "bootstrap": {
            "method": "paired player-block bootstrap",
            "repetitions": int(bootstrap_repetitions),
            "seed": 3003,
            "difference_sign": "challenger_minus_baseline_negative_is_better",
        },
        "minimum_slice_n": 200,
        "formal_legacy_included": "legacy_frozen" in models,
        "diagnostic_legacy_proxy_allowed": False,
    }
    return artifacts, metadata
