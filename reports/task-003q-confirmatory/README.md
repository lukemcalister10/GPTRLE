# TASK-003Q confirmatory hybrid

The frozen age-and-horizon blend passed its confirmatory evaluation on the unchanged 20,094-row, 25-fold benchmark.

## Frozen policy

- Leads 1-4: TASK-003K weight 1.00 through age 28, then 0.75 at 29, 0.50 at 30, 0.25 at 31, and 0.00 from age 32.
- Lead 5: TASK-003K weight 1.00 through age 26, 0.50 at 27, and 0.00 from age 28.

## Pooled result versus current vNext

- meaningful-season Brier: 0.322% better;
- meaningful-season log loss: 0.372% better;
- games MAE: 0.239% better;
- total-points MAE: 0.180% better.

## Key gates

- ages 28-29 improved all four pooled metrics;
- age 30+ lead 5 is exactly unchanged from current vNext;
- the frozen policy passed without post-run tuning;
- full vNext tests passed;
- workflow run 28902778706 succeeded;
- artifact digest: `sha256:2aca7538725bdefdc56602b23ee5ae35334985a45a81b211a627c352627750cb`.

TASK-003Q should replace the all-age TASK-003K candidate. It preserves most of the useful event-logistic signal while reverting to current vNext where the long-horizon older-player evidence was harmful.
