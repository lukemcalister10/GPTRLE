# TASK-003F — Material subgroup regression diagnosis

## Scope

This is a diagnostic-only continuation of TASK-003E. It does not change model fitting, the locked validation protocol, production forecasts, current values, keeper utility or the UI. It does not use named-player tuning.

The analysis was regenerated from the accepted TASK-003E evidence package:

- workflow run: `28858912803`
- workflow artifact: `8134823849`
- artifact archive SHA-256: `fd66faf3a20a73991e49129b4beceb285e31ad8b0a00d09e8c9e90992a945fe3`
- material threshold: vNext total-points MAE more than 3% worse than `baseline_recent_scoring`

## Ranked material regressions

`Excess MAE` is vNext total-points MAE minus baseline total-points MAE. `Burden rank` ranks excess MAE multiplied by the qualifying row count. Slice burdens overlap and must not be added together.

| Severity | Lead | Slice | n | Baseline MAE | vNext MAE | Worse | Excess MAE | Burden rank |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 1 | position: RUC | 413 | 358.59 | 412.40 | 15.01% | 53.81 | 5 |
| 2 | 4 | prior games: zero prior games | 418 | 211.70 | 232.81 | 9.97% | 21.11 | 11 |
| 3 | 3 | prior games: zero prior games | 515 | 189.89 | 205.93 | 8.45% | 16.05 | 12 |
| 4 | 4 | tenure: 4-5 | 588 | 529.15 | 572.73 | 8.24% | 43.58 | 3 |
| 5 | 1 | pick: 61+ / undrafted | 890 | 309.52 | 334.83 | 8.18% | 25.31 | 4 |
| 6 | 3 | age: 24-26 | 862 | 522.28 | 563.27 | 7.85% | 40.99 | 1 |
| 7 | 1 | prior games: zero prior games | 719 | 93.46 | 99.22 | 6.17% | 5.76 | 14 |
| 8 | 2 | prior games: zero prior games | 615 | 159.91 | 169.00 | 5.68% | 9.09 | 13 |
| 9 | 2 | age: 24-26 | 1,047 | 472.81 | 498.93 | 5.53% | 26.12 | 2 |
| 10 | 4 | age: 24-26 | 680 | 564.31 | 593.21 | 5.12% | 28.90 | 7 |
| 11 | 1 | age: 27-29 | 930 | 468.29 | 491.46 | 4.95% | 23.17 | 6 |
| 12 | 5 | prior games: zero prior games | 327 | 273.35 | 285.63 | 4.49% | 12.28 | 15 |
| 13 | 3 | tenure: 4-5 | 734 | 526.93 | 547.68 | 3.94% | 20.75 | 9 |
| 14 | 4 | age: 21-23 | 924 | 514.72 | 530.88 | 3.14% | 16.15 | 10 |
| 15 | 1 | age: 24-26 | 1,225 | 437.89 | 451.46 | 3.10% | 13.56 | 8 |

## Fold repeatability

The pooled regressions are not isolated named-player effects.

| Slice/lead | Legal origins worse for vNext | Available origins |
|---|---:|---:|
| RUC, lead 1 | 6 | 7 |
| Zero prior games, lead 1 | 7 | 7 |
| Zero prior games, lead 2 | 6 | 6 |
| Zero prior games, lead 3 | 5 | 5 |
| Zero prior games, lead 4 | 4 | 4 |
| Zero prior games, lead 5 | 3 | 3 |
| Tenure 4-5, lead 3 | 4 | 5 |
| Tenure 4-5, lead 4 | 4 | 4 |
| Pick 61+ / undrafted, lead 1 | 6 | 7 |
| Age 24-26, lead 1 | 4 | 7 |
| Age 24-26, lead 2 | 5 | 6 |
| Age 24-26, lead 3 | 4 | 5 |
| Age 24-26, lead 4 | 3 | 4 |
| Age 27-29, lead 1 | 6 | 7 |
| Age 21-23, lead 4 | 4 | 4 |

The zero-prior-games pattern is the most temporally stable. Ruck lead 1, late/undrafted lead 1, and the longer-lead career-stage regressions also repeat broadly enough to justify general investigation.

## Component diagnosis

### 1. Expected-games shrinkage is the dominant shared mechanism

Most high-burden regressions have materially negative expected-games bias. The problem is not primarily an inflated conditional scoring average.

Representative examples:

| Slice/lead | Actual games | Baseline expected games | vNext expected games | vNext points bias |
|---|---:|---:|---:|---:|
| RUC, lead 1 | 8.21 | 7.56 | 5.54 | -319 |
| Age 24-26, lead 3 | 11.70 | 13.00 | 8.00 | -333 |
| Age 24-26, lead 4 | 10.72 | 12.60 | 6.73 | -377 |
| Tenure 4-5, lead 4 | 11.00 | 11.15 | 7.54 | -292 |
| Pick 61+ / undrafted, lead 1 | 7.84 | 7.28 | 4.53 | -245 |
| Age 27-29, lead 1 | 13.32 | 14.46 | 10.80 | -232 |

This points first to the opportunity pathway: meaningful-season probability, conditional games, or their multiplication into expected games.

### 2. Better meaningful-season classification does not guarantee better points MAE

Several regressing slices have improved meaningful-season Brier scores while games and total-points MAE worsen. The binary incidence model is therefore learning useful information, but the expected-games magnitude is too compressed for these groups.

A model hypothesis should not target the classifier alone without decomposing:

- meaningful-season probability;
- conditional games given a meaningful season;
- expected games;
- conditional average;
- expected points.

### 3. Zero-prior-games is a separate zero-inflated problem

The baseline predicts zero for players with no prior AFL games. vNext correctly assigns non-zero opportunity and reduces signed underprediction for players who later play, but this can still worsen MAE because many members of the cohort remain at zero.

This is a distribution and objective issue, not evidence that all such players should be projected at zero. The next diagnostic must separate:

- players who remain at zero games;
- players who later play at least one game;
- conditional error among eventual players;
- mean, median and probability-weighted forecast behaviour.

### 4. Age and tenure findings likely share one career-stage mechanism

Age 24-26 and tenure 4-5 overlap strongly. Their similar negative games and points bias should be treated as one candidate career-stage mechanism until a controlled experiment demonstrates otherwise.

### 5. Position and draft-status findings remain general, not player-specific

Ruck lead 1 and late/undrafted lead 1 repeat across six of seven legal origins. They warrant independent feature and calibration review, but no named-player adjustments or position-specific hard-coded overrides are justified.

## Reproduction

After obtaining the accepted TASK-003E artifact and locating its `comparison` directory:

```bash
python vnext/analyse_task003e_regressions.py \
  --comparison-dir build/task-003e/comparison \
  --out build/task-003f
```

The command writes:

- `material_regressions.csv`
- `component_diagnostics.csv`
- `fold_stability.csv`

## Decision

The 15 regressions reduce to two primary diagnostic tracks:

1. excessive future-opportunity shrinkage for established early/mid-career players, rucks and late/undrafted players;
2. a zero-inflated forecast/loss interaction for players with no prior AFL games.

The next model-changing work must test one general hypothesis at a time against the unchanged rolling-origin protocol. No production replacement or production-layer change is authorised by this diagnosis.
