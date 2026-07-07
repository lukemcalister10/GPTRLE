# TASK-003F — Material subgroup regression diagnosis

## Scope

Diagnostic only. No model fitting, validation protocol, production forecast, current value, keeper utility or UI change. No named-player tuning.

Source evidence:

- TASK-003E workflow run `28858912803`
- artifact `8134823849`
- archive SHA-256 `fd66faf3a20a73991e49129b4beceb285e31ad8b0a00d09e8c9e90992a945fe3`
- material threshold: vNext total-points MAE more than 3% worse than `baseline_recent_scoring`

## Exact result

The accepted evidence contains 15 material slice/lead regressions. The compact ranked table is committed at `reports/task-003f/material_regressions.csv`.

Highest practical burdens:

1. age 24-26, lead 3;
2. age 24-26, lead 2;
3. tenure 4-5, lead 4;
4. pick 61+ / undrafted, lead 1;
5. ruck, lead 1.

## Fold repeatability

The regressions are not isolated named-player effects:

- zero prior games is worse in every available legal origin at leads 1-5;
- ruck lead 1 is worse in 6 of 7 origins;
- pick 61+ / undrafted lead 1 is worse in 6 of 7 origins;
- tenure 4-5 lead 4 is worse in all 4 available origins;
- age 24-26 is worse in 5 of 6 origins at lead 2 and 4 of 5 at lead 3.

The compact fold summary is committed at `reports/task-003f/fold_repeatability.csv`.

## General diagnosis

### Expected-games shrinkage

Most high-burden regressions have materially negative expected-games bias rather than inflated conditional scoring averages. Representative vNext expected-games forecasts are well below realised games for rucks, age 24-26, tenure 4-5, late/undrafted players and age 27-29.

This points first to the opportunity pathway: meaningful-season probability, conditional games, or their multiplication into expected games.

### Meaningful-season classification is not the whole problem

Several regressing slices have improved meaningful-season Brier scores while games and total-points MAE worsen. Binary incidence can therefore improve while expected-games magnitude remains too compressed.

### Zero-prior-games is a distinct zero-inflated problem

The recent-scoring baseline predicts zero for players with no prior AFL games. vNext correctly assigns non-zero opportunity, but MAE can still worsen because many members remain at zero. The next diagnostic must separate eventual zero-game players from eventual players and compare mean, median and conditional forecast behaviour.

### Age and tenure likely share one mechanism

Age 24-26 and tenure 4-5 overlap strongly. They should be treated as one candidate career-stage mechanism until a controlled experiment demonstrates otherwise.

## Reproduction

```bash
python vnext/analyse_task003e_regressions.py \
  --comparison-dir build/task-003e/comparison \
  --out build/task-003f
```

## Decision

The regressions reduce to two primary tracks:

1. excessive future-opportunity shrinkage for established early/mid-career players, rucks and late/undrafted players;
2. a zero-inflated forecast/loss interaction for players with no prior AFL games.

Any model-changing work must test one general hypothesis at a time against the unchanged rolling-origin protocol. No production replacement is authorised.
