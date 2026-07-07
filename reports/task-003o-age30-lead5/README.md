# TASK-003O — adjudicate age-30+ lead-5 regression

Draft PR state: diagnostic only. References issue #22.

## GitHub state and rebase/retarget status

A second review requested that this branch be rebased or merged onto `agent/task003k-event-logistic`, that the PR base be retargeted to that branch, and that the analysis use PR #19's actual code and committed evidence. The local environment still cannot fetch the private GitHub repository or PR #19 because no GitHub credentials are available and the `gh` CLI is not installed.

```text
$ git fetch origin agent/task003k-event-logistic
fatal: could not read Username for 'https://github.com': No such device or address
```

Consequently this checkout remains unable to verify issue #22, inspect PR #19's committed evidence, rebase onto `agent/task003k-event-logistic`, or retarget the existing GitHub PR from inside this environment. The local pre-existing history still ends at `e5f90c4` (`TASK-003J: diagnose conditional-regressor feature support (#15)`) before this TASK-003O branch's commits; PR #19's TASK-003K code and artifacts are not present in the local object database.

## Added end-to-end diagnostic runner

`vnext/analyse_task003o_age30_lead5.py` is a diagnostic-only runner for the requested analysis once PR #19's actual current/candidate prediction artifacts are available in the checkout. It does not fit models, tune parameters, change folds, change targets, change calibration, or write production artifacts.

Expected use after rebasing onto `agent/task003k-event-logistic` or otherwise materialising PR #19 artifacts:

```bash
python vnext/analyse_task003o_age30_lead5.py \
  --current <pr19-current-predictions.csv> \
  --candidate <pr19-candidate-predictions.csv> \
  --annual vnext/output/annual_rows.csv \
  --out reports/task-003o-age30-lead5/generated
```

The runner writes:

- `summary.csv`: age-30+ lead-5 and lead-4 current-versus-candidate metrics, row counts, unique-player counts, prevalence, calibrated probability bias and percentage deltas;
- `by_origin.csv`: the same metrics by historical origin/fold;
- `row_deltas.csv`: row-level paired error deltas;
- `influential_players.csv`: player-block contributions to candidate-minus-current error;
- `leave_one_origin_out.csv`: leave-one-origin-out sensitivity;
- `player_block_bootstrap.csv`: player-block bootstrap intervals and probability the candidate is better.

If PR #19 prediction files include `raw_p_meaningful`, the raw columns are preserved by the loader for extension, but the local pre-PR #19 artifact does not contain raw event probabilities.

## Prior evidence inspected

- `reports/task-003f/` and `docs/current/TASK-003F-REGRESSION-DIAGNOSIS.md` identify the locked material regressions; age-30+ lead-5 is not one of the original 15 locked TASK-003F material regressions.
- `reports/task-003g/` and `docs/current/TASK-003G-COMPONENT-ATTRIBUTION.md` attribute earlier regressions to component-level behaviour, especially event probability versus conditional magnitude.
- `reports/task-003h/` and `docs/current/TASK-003I-EVENT-CALIBRATION-AUDIT.md` preserve TASK-003I raw-versus-isotonic event calibration evidence.
- `reports/task-003j-support-diagnosis/` and `docs/current/TASK-003J-SUPPORT-DIAGNOSIS.md` preserve support-distance evidence for the original problematic cohorts.

## Local smoke/reproducibility check

The runner was smoke-tested with the only local prediction file available (`vnext/output/eval_v3_fast/predictions.csv`) supplied as both current and candidate, joined to `vnext/output/annual_rows.csv`. This confirms the runner executes but also confirms the local artifact is not the PR #19 locked-evidence dataset needed to adjudicate the reported regression: age-30+ lead-5 contains 2,425 rows and 939 unique players, not the reported `n=278`.

Local age-30+ lead-5 current-vNext-only metrics from that artifact:

| metric | value |
|---|---:|
| rows | 2,425 |
| unique players | 939 |
| origins | 2019: 683; 2020: 803; 2021: 939 |
| meaningful prevalence | 0.012371 |
| mean calibrated p(meaningful) | 0.028536 |
| calibrated probability bias | +0.016165 |
| Brier | 0.014270 |
| games MAE | 0.447386 |
| total-points MAE | 32.989242 |

Age-30+ lead-4 in the same local artifact also has 2,425 rows and a Brier score of 0.020685. This comparison is not sufficient for TASK-003O because it lacks the PR #19 TASK-003K candidate and the reported `n=278` population.

## Required analyses still not defensibly completed in this checkout

The following required checks need PR #19's candidate/current evidence tables or a reproducible TASK-003K runner, neither of which exists locally:

- independent reproduction of the reported age-30+ lead-5 candidate-versus-current deltas;
- by-fold candidate/current metrics on the reported `n=278` population;
- raw versus calibrated probability comparison for TASK-003K's evidence rows;
- player/origin influence analysis against candidate-current deltas;
- overlap of the reported failure rows with tenure, prior-games, position and support-distance diagnostics;
- player-block bootstrap, leave-one-origin-out and influential-player-block sensitivity on the actual candidate regression.

## Recommendation

**insufficient evidence**

Under the existing critical-subgroup rule, a candidate should not be accepted or rejected on a critical subgroup claim that cannot be reproduced from committed evidence in the available repository state. The reported age-30+ lead-5 worsening may be a genuine critical subgroup failure, fold noise, representation/support trouble, or an artefact of a different evidence population, but this checkout cannot distinguish those cases until PR #19's exact code/evidence is available. Do not invent or change acceptance thresholds retrospectively.
