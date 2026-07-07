# BUILD notepad — 2026-07-01 — walk-forward SUMMARY: opportunity-matching fix (Luke's censoring catch)

Luke caught the pooled headline Yr9 (53.5%) sitting BELOW every individual cohort's Yr9 (>=56%) — impossible for a proper
weighted average. Root cause identified + fixed. Re-rendered ONLY (matrix + per-cohort V/P sheets unchanged). Nothing baked.

DIAGNOSIS:
- Busts ARE zero (NO survivor bias): a retired player stays in the Yr1 denominator, contributes 0 to later years -> drags
  the curve down correctly.
- The bug was the OPPOSITE — RIGHT-CENSORING contamination: the old headline denominator carried ALL 21 curve cohorts'
  Yr1 value at every year, but at Yr9 only 14 cohorts could physically have reached Yr9 (2018-24 debuts cannot yet). The 7
  immature cohorts added Yr1 value with no possible Yr9 numerator -> deflated pooled Yr9 to 53.5%.

FIX (opportunity-matching):
- For each career-year N the pool = ONLY cohorts old enough to have reached year N (debut+N <= 2026); immature cohorts
  excluded from BOTH numerator and denominator for that column. Busts within eligible cohorts still count as 0.
- Added a "#cohorts (reached Yr N)" row (21 -> 14 -> 11 as N grows) so the shrinking pool is explicit.
- Each cohort row now BLANKS years not yet reached (e.g. 2022 stops at Yr4, 2015 at Yr11) instead of a false 0%.

CORRECTED headline (value indexed to Yr1=100%, opp-matched, pooled 2004-24):
  Yr1 100  Yr2 128  Yr3 136  Yr4 146(PEAK)  Yr5 142  Yr6 134  Yr7 118  Yr8 98  Yr9 76  Yr10 62  Yr11 47  Yr12 37
  (Yr9 now 76% = inside the cohort range; impossibility resolved. Peak Yr4 146% vs the old contaminated 132%/Yr4.)

Caveat retained: sit-out Yr1 anchor levels are PVC-deferred placeholders -> absolute % provisional until the pick-curve
step (read the shape). Per-cohort value+production sheets, walk-forward/leakage-guard, M1+v7 prototype: all unchanged. HOLD.
