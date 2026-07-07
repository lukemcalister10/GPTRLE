# TASK-003O — adjudicate age-30+ lead-5 regression

Draft PR state: diagnostic only. References issue #22.

## GitHub state verification

Attempted to verify the private GitHub state before analysis by adding `https://github.com/lukemcalister10/GPTRLE.git` as `origin` and fetching `vnext` plus PR #19. The environment had no GitHub credentials and no `gh` CLI, so the fetch failed with:

```text
fatal: could not read Username for 'https://github.com': No such device or address
```

Therefore this report cannot independently inspect issue #22 or PR #19's committed candidate evidence. The local checkout is at `e5f90c4` (`TASK-003J: diagnose conditional-regressor feature support (#15)`), before the reported TASK-003K PR #19 evidence.

## Prior evidence inspected

- `reports/task-003f/` and `docs/current/TASK-003F-REGRESSION-DIAGNOSIS.md` identify the locked material regressions; age-30+ lead-5 is not one of the original 15 locked TASK-003F material regressions.
- `reports/task-003g/` and `docs/current/TASK-003G-COMPONENT-ATTRIBUTION.md` attribute earlier regressions to component-level behaviour, especially event probability versus conditional magnitude.
- `reports/task-003h/` and `docs/current/TASK-003I-EVENT-CALIBRATION-AUDIT.md` preserve TASK-003I raw-versus-isotonic event calibration evidence.
- `reports/task-003j-support-diagnosis/` and `docs/current/TASK-003J-SUPPORT-DIAGNOSIS.md` preserve support-distance evidence for the original problematic cohorts.

## Local reproducibility check

Using the only local prediction file available (`vnext/output/eval_v3_fast/predictions.csv`) joined to `vnext/output/annual_rows.csv`, age-30+ lead-5 does not match the PR #19 reported `n=278`; it contains 2,425 rows and 939 unique players, all from origins 2019–2021. This confirms the local artifact is not the PR #19 locked-evidence dataset needed to adjudicate the reported regression.

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

## Required analyses not defensibly completed

The following required checks need the PR #19 candidate/current evidence tables or a reproducible TASK-003K runner, neither of which exists in this checkout:

- independent reproduction of the reported age-30+ lead-5 candidate-versus-current deltas;
- by-fold candidate/current metrics on the reported `n=278` population;
- raw versus calibrated probability comparison for TASK-003K's evidence rows;
- player/origin influence analysis against candidate-current deltas;
- overlap of the reported failure rows with tenure, prior-games, position and support-distance diagnostics;
- player-block bootstrap, leave-one-origin-out and influential-player-block sensitivity on the candidate regression.

## Recommendation

**insufficient evidence**

Under the existing critical-subgroup rule, a candidate should not be accepted or rejected on a critical subgroup claim that cannot be reproduced from committed evidence in the available repository state. The reported age-30+ lead-5 worsening may be a genuine critical subgroup failure, fold noise, representation/support trouble, or an artefact of a different evidence population, but the local checkout cannot distinguish those cases. Do not invent or change acceptance thresholds retrospectively; require PR #19's exact evidence artifacts or runner before adjudicating TASK-003K.
