# TASK-004 Claude integration diagnostic

## Status

The identity-safe three-board diagnostic completed successfully on workflow run `28906995187`.

The run regenerated the unchanged Claude board, trained current-vNext and TASK-003Q artifacts, generated both authoritative 804-player five-lead forecasts, applied the same diagnostic pricing adapter to both forecast sets, ran the full vNext test suite, and packaged the comparison artifact.

## Validation gates

- Claude active rows: 805.
- Authoritative matched players: 804.
- Sole Claude-only row: Taylor Adams.
- Forecast rows: 4,020 for both current-vNext and TASK-003Q.
- Five leads for every authoritative player.
- St Kilda Max King and Hawthorn Maxwell King remain distinct stable-ID records.
- No name-only joins.
- `exp_points = exp_games × cond_avg` within floating-point tolerance.
- No second multiplication by meaningful-season probability.
- Both forecast-fed boards were rescaled to the same total capital as the matched Claude board; this changes neither ranks nor relative allocations.

## Comparison result

| Comparison | Spearman rank correlation | Mean absolute rank change | Top-100 overlap |
| --- | ---: | ---: | ---: |
| Claude vs current-vNext-fed pricing | 0.7420 | 126.4 | 73 |
| Claude vs TASK-003Q-fed pricing | 0.7420 | 126.3 | 72 |
| current-vNext-fed vs TASK-003Q-fed | 0.9999 | 2.15 | 99 |

TASK-003Q itself is not causing the large board movement. Current-vNext and TASK-003Q produce almost the same value board under the adapter. The large difference is between the Claude full-career value architecture and a direct five-year forecast-surplus sum.

## Capital concentration

| Board | Top-10 share | Top-50 share | Top-100 share | Bottom-half share |
| --- | ---: | ---: | ---: | ---: |
| Claude original | 8.7% | 30.3% | 47.3% | 10.3% |
| current-vNext-fed | 20.0% | 63.2% | 85.3% | 0.046% |
| TASK-003Q-fed | 19.9% | 63.2% | 85.3% | 0.047% |

The direct five-year adapter is therefore too concentrated to be a production keeper-value replacement. This is a value-layer/horizon finding, not evidence against TASK-003Q forecasts.

## Important slices: TASK-003Q-fed minus Claude

- age 30+: mean value change `-378`;
- age 21 and under: mean value change `+191`;
- zero-history players: mean value change `-273`;
- defenders: mean value change `-134`;
- forwards: mean value change `+211`;
- midfielders: mean value change `+81`;
- rucks: mean value change `-731`.

The ruck result and near-zero value assigned to much of the lower half show that the adapter does not preserve all keeper-value structure embedded in Claude, including full-career tail value, position scarcity, floors and pedigree protection.

## Decision required

Do not adopt the direct five-year adapter as production value logic.

Recommended next hypothesis: preserve Claude's full-career valuation spine, replace only the first five annual contributions with validated TASK-003Q opportunity and scoring forecasts, and continue the career tail from year six using the existing Claude trajectory anchored continuously at the lead-five state. Claude survival/retirement mechanics must not be reapplied to the first five unconditional forecast years.

This should be a separate, frozen diagnostic candidate. No value-formula tuning or named-player adjustments should occur during its first evaluation.
