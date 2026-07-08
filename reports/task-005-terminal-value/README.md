# TASK-005 terminal remaining-career value

## Result

The trained terminal model failed the frozen acceptance gates and must not be adopted.

Across 12,483 rolling-origin boundary observations, the model's MAE was 51.46 versus 42.47 for the monotone empirical decay baseline, a 21.16% regression. For players aged 30+ at the boundary, the model was 34.00% worse than decay.

The terminal addition also did not solve the current-board capital concentration. Top-100 share remained 85.27% and bottom-half share remained 0.047%, effectively identical to the five-year TASK-003Q surplus board. The empirical decay alternative was similarly concentrated.

## Interpretation

The principal problem is not the absence of years 6-10. It is the direct surplus-pricing layer used by the TASK-004 adapter, which assigns almost no value to below-replacement or low-probability players. Adding a statistically estimated tail cannot repair that structural compression.

The evidence does not support treating Claude as the year-6+ forecaster, nor does it support the tested terminal model. The next decision is therefore about keeper-utility architecture rather than forecast horizon.

## Evidence

Workflow run `28909455423` succeeded. Artifact digest: `sha256:5f6c378e9618b16ec4b72ee90d19253656b0e29ee66eaf6803560080e75d4977`.
