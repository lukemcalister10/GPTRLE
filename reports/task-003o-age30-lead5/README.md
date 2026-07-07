# TASK-003O — adjudicate age-30+ lead-5 regression

Diagnostic-only PR for issue #22. The branch is intended to be stacked on `agent/task003k-event-logistic`, and the dedicated CI workflow is the authoritative way to generate the TASK-003O evidence from PR #19's unchanged-current and candidate code.

## GitHub Actions evidence workflow

`.github/workflows/task-003o-age30-lead5.yml` runs the complete end-to-end adjudication:

1. verifies the legacy manifest;
2. builds the locked historical cohorts;
3. generates unchanged-current vNext fold predictions and artifacts;
4. generates TASK-003K candidate fold predictions and artifacts;
5. runs `vnext/analyse_task003o_age30_lead5.py` against those two prediction tables;
6. enforces the expected age-30+ lead-5 population size of `n=278`;
7. runs `cd vnext && pytest -q`;
8. uploads the cohorts, unchanged-current outputs, candidate outputs and TASK-003O analysis outputs.

The workflow intentionally does not fetch or authenticate to GitHub from inside a job. It uses the checked-out PR stack and therefore evaluates the exact code under review.

## Analysis outputs

`vnext/analyse_task003o_age30_lead5.py` is diagnostic only. It reads committed/generated prediction CSVs and annual rows, then writes:

- `summary.csv`: age-30+ lead-5 and lead-4 current-versus-candidate metrics, row counts, unique-player counts, prevalence, calibrated probability bias, raw probability metrics when raw columns are present, and percentage deltas;
- `by_origin.csv`: age-30+ lead-5 metrics by historical origin/fold;
- `leave_one_origin_out.csv`: age-30+ lead-5 sensitivity after dropping each origin;
- `row_deltas.csv`: row-level candidate-minus-current paired error deltas;
- `influential_players.csv`: player-block contributions to candidate-minus-current error;
- `player_block_bootstrap.csv`: player-block bootstrap intervals and probability the candidate is better;
- `overlap_by_position.csv`: overlap with position groups;
- `overlap_by_tenure_band.csv`: overlap with tenure bands;
- `overlap_by_prior_games_band.csv`: overlap with prior-games bands;
- `overlap_by_task003j_support_risk.csv`: overlap with TASK-003J support-risk cohorts (`zero_prior_games`, `ruck`, `age_27_29`, `tenure_4_5`, `pick_61_undrafted`, and `none`);
- `recommendation.txt`: the single TASK-003O recommendation.

The analysis fails fast if the age-30+ lead-5 population is not exactly `n=278`, preventing accidental adjudication on the wrong population.

## Reproduction

The workflow command sequence is:

```bash
python scripts/verify_legacy_manifest.py
python vnext/build_historical_cohorts.py --out build/task-003o-cohorts
python vnext/run_historical_folds.py \
  --out build/task-003o-current \
  --cohort-dir build/task-003o-cohorts
python vnext/run_task003k_folds.py \
  --out build/task-003o-candidate \
  --cohort-dir build/task-003o-cohorts
python vnext/analyse_task003o_age30_lead5.py \
  --current build/task-003o-current/vnext_predictions.csv \
  --candidate build/task-003o-candidate/candidate_predictions.csv \
  --annual build/task-003o-current/training_dataset.csv \
  --out build/task-003o-analysis \
  --expected-age30-lead5-n 278 \
  --bootstrap-reps 2000
cd vnext && pytest -q
```

## Recommendation

**block TASK-003K**

Run 3 is the controlling TASK-003O evidence run for this adjudication. It uses PR #19's stacked TASK-003K code and the exact age-30+ lead-5 population (`n=278`). The critical subgroup regression is material across the declared operational metrics: Brier is approximately 8.96% worse, games MAE is approximately 11.76% worse, and total-points MAE is approximately 9.52% worse. Under the existing critical-subgroup rule, that is an explicit blocker for TASK-003K.

This recommendation does not introduce a retrospective threshold or named-player adjustment. It applies the existing rule to the run 3 evidence: a candidate with pooled gains is still blocked when a critical subgroup shows a reproduced, material degradation that survives the requested diagnostic review.
