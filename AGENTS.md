# AFL RL Engine — Agent Instructions

These rules apply to Codex and any other coding agent working in this repository.

## Mission
Predict future SuperCoach outcomes as accurately as possible, then convert those outcomes into values for this specific 16-team keeper league. Do not train the model to imitate human trades, drafts, rankings, or named-player opinions.

## Authoritative paths
- Legacy production engine: `engine/rl_after/`
- vNext challenger: `vnext/`
- Current project documents: `docs/current/`
- Accepted experiment reports: `reports/`
- Persisted model artifacts: `artifacts/`

Claude-era process documents remain historical context unless explicitly referenced by a file under `docs/current/`.

## Non-negotiable rules
1. Do not modify the legacy production engine unless the task explicitly authorises it.
2. Historical features must contain only information observable at the forecast origin.
3. Include zero-game careers, middle outcomes, and busts in cohort evaluation.
4. No player-specific forecast adjustments, named-player ordering rules, or market-derived training targets.
5. Forecast, keeper utility, and optional owner policy must remain separate layers.
6. No model fitting during production inference or export.
7. One modelling hypothesis per pull request.
8. Every model-changing PR must show before/after metrics on the locked validation protocol and full-population output effects.
9. Never silently drop failed rows. Unexpected exceptions fail the run and must identify affected records.
10. Do not change the validation protocol and the model under test in the same PR.

## Required evidence for model PRs
- Hypothesis and expected mechanism.
- Exact files and model layer changed.
- Baselines and current-engine comparison.
- Metrics by horizon and important subgroups.
- Calibration results, not only ranking metrics.
- Largest current-board rises and falls as diagnostics, not acceptance targets.
- Reproduction commands and artifact manifest.

## Standard commands
```bash
python -m pip install -r requirements-vnext.txt
cd vnext && pytest -q
python scripts/verify_legacy_manifest.py
python scripts/generate_handover.py
```

## Pull-request states
- `experiment`: evidence gathering; not eligible for production.
- `candidate`: implementation complete and protocol results attached.
- `accepted`: approved after review; may be merged into the vNext integration branch.
- `release`: eligible to change the production board.

Do not claim that a model is better because selected players look more intuitive. It is better only when the declared outcome-based validation supports that conclusion.
