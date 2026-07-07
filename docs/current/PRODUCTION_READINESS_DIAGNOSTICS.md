# Production-readiness diagnostics scaffold

This is a diagnostic-only process for comparing the frozen legacy board, the merged vNext current forecasts, and any future candidate forecast against the authoritative 804-player 2026 universe. It does **not** approve a model, alter production, change keeper utility, fit a model, or edit the UI.

## Inputs

- Authoritative universe: `reports/task-002-active-universe/authoritative_universe.csv`.
- Current merged vNext annual forecast: `vnext/output/current/current_annual_forecast.csv`.
- Optional current production/legacy export if a directly comparable CSV/JSON is available.
- Optional future candidate forecast file.
- Optional artifact paths whose hashes should be recorded.

## Command

```bash
python vnext/production_readiness_diagnostics.py \
  --universe reports/task-002-active-universe/authoritative_universe.csv \
  --vnext vnext/output/current/current_annual_forecast.csv \
  --candidate path/to/future_candidate.csv \
  --legacy path/to/legacy_export.csv \
  --artifacts vnext/output/artifacts \
  --out reports/production-readiness-diagnostics
```

Omit `--legacy` or `--candidate` when those files are unavailable. If the legacy and vNext outputs do not share player keys plus forecast/value columns, the scaffold writes an incompatibility row rather than forcing a misleading comparison.

## Outputs

- `coverage_summary.csv` and `coverage_exclusions.csv`: exact player-key coverage, missing players, and extras.
- `validity_checks.csv`: missing and non-finite values, probability bounds, and threshold/quantile monotonicity checks.
- `compare_*_to_*.csv`: forecast/value deltas for shared comparable columns.
- `largest_changes_*_to_*.csv`: largest increases and decreases by metric.
- `rank_changes_*_to_*.csv`: rank movements for the first shared value/forecast metric.
- `*_with_slice_bands.csv`: position, age, tenure, draft-pick, and prior-games slice bands when source fields exist.
- `artifact_reproducibility.csv` and `manifest.json`: reproducibility hashes and the assertion that artifacts were loaded without fitting during this diagnostic.
- `README.md`: rollback requirements and proposed shadow-mode gates.

## Future shadow-mode hard gates

Reject or block production release if any of these fail:

1. Authoritative player coverage is below 804 players unless every exclusion is documented and approved.
2. Required forecast/value outputs contain missing or non-finite values.
3. Probability columns are outside `[0, 1]`.
4. Threshold probabilities cross (`p80 >= p90 >= p100 >= p110 >= p120` must hold when present).
5. Quantile outputs cross.
6. Inference fits or mutates models instead of loading frozen artifacts.
7. Legacy rollback path, hashes, and reproduction command are missing.
8. Forecast-model comparison is mixed with keeper-utility or currency-mapping approval.

Passing this scaffold is not release approval; release still requires locked validation evidence and explicit owner approval.
