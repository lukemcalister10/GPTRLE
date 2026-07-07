# TASK-003K event-logistic experiment

## Interim decision

**Promising historical result; remain experimental.**

Replacing only the meaningful-season `SGDClassifier` with the predeclared batch logistic-regression candidate improved all three pooled primary outcomes on the locked 20,094-row, 25-fold comparison:

- meaningful-season Brier: **0.47% better**;
- meaningful-season log loss: **0.51% better**;
- games MAE: **0.19% better**;
- total-points MAE: **0.16% better**.

The paired player-block 95% intervals favour the candidate for Brier, games MAE and total-points MAE. Conditional games, conditional average and all threshold probabilities were identical, confirming the declared single change.

## Mechanism

Before isotonic calibration, the logistic candidate improved event Brier, log loss and AUC. After temporal isotonic calibration, the pooled gains remained but were smaller. This supports TASK-003I's finding that the raw event classifier—not calibration alone—was a real source of error.

The gain is not uniform by horizon:

- lead 1 is effectively neutral with slightly better Brier/games/points but slightly worse log loss;
- lead 2 is slightly worse on Brier, log loss, games and points;
- lead 3 improves modestly;
- lead 4 improves materially and drives much of the pooled gain;
- lead 5 improves log loss but slightly worsens Brier, games and points.

## Locked regressions

None of the original 15 TASK-003F regression rows worsened by more than 3% on total-points MAE. Most improved slightly, including age 24–26 lead 3, tenure 4–5 lead 4 and age 21–23 lead 4.

## New material issue

One new qualifying regression appeared:

- age 30+, lead 5, `n=278`: total-points MAE **9.52% worse**, games MAE **11.76% worse**, Brier **8.96% worse**.

The same age band improves at lead 4 by 3.42% on total-points MAE. Fold inspection shows unstable direction: the candidate overpredicts age-30+ lead-5 meaningful-season probability in the 2018 and 2019 origins, while improving the 2020 origin. This must be reviewed before acceptance rather than averaged away.

## Zero-history trade-off

The candidate does not create the broad false-positive explosion seen in TASK-003H. Effects vary by lead:

- lower probability at leads 3 and 5 helps eventual-zero rows but worsens eventual-player rows;
- higher probability at leads 2 and 4 slightly helps eventual players while slightly worsening eventual-zero rows;
- lead 1 is nearly neutral.

The underlying zero-history information problem remains unsolved.

## Remaining gates

The experiment cannot advance yet. It still requires:

1. independent validation of the candidate artifacts and metrics;
2. current 2026 board effects on the authoritative 804-player universe;
3. a decision on whether the age-30+ lead-5 regression is an unacceptable critical subgroup failure;
4. review of the parallel zero-history and production-readiness audits.

No production, values, keeper utility or UI behaviour changed.
