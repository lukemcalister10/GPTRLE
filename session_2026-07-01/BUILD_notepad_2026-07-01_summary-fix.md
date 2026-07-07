# BUILD notepad — 2026-07-01 — walk-forward book SUMMARY metric corrected

Corrected ONLY the Summary tab of AFL_RL_WALKFORWARD_book_M1v7-proto.xlsx (re-rendered; matrix unchanged; per-cohort
sheets untouched). Measure-only, nothing baked. head 8aed420a / store pre_stage0.

CHANGE: Summary metric was Sum(VALUE)/Sum(PRODUCTION) (value-per-production, decays from Yr1 — wrong). Now =
cohort VALUE indexed to the year-1 anchor = 100% (SUM-RATIO, not mean-of-ratios): for each career-year N,
pooled Sum(value at N) / pooled Sum(value at Yr1) x 100, across curve-cohort players. Per-cohort rows the same
(each vs its OWN Yr1). Denominator = full-cohort Yr1 total, FIXED (busts included -> contribute 0 once gone).
V/P kept only as one clearly-labelled SECONDARY row.

RESULT — the appreciation curve (pooled 2004-24, value indexed to Yr1):
  Yr1 100%  Yr2 128%  Yr3 129%  Yr4 132% (PEAK)  Yr5 122%  Yr6 110%  Yr7 92%  Yr8 73%  Yr9 54%  Yr10 40%  Yr11 28%  Yr12 20%
  -> builds early, peaks ~Yr4, decays after. (Shape as Luke reads it.)

TWO caveats carried in the header:
- sit-out Yr1 anchor levels are deferred-to-PVC placeholders -> absolute % is PROVISIONAL until the pick-curve step
  (shape is the read, not the exact %). Same as the baseline book.
- This M1+v7 peak ~132% (Yr4) vs the baseline book's ~158% = the v7 peak-career compression showing up in the curve.

Everything else unchanged: walk-forward/leakage-guard, per-cohort value+production adjacent sheets (2003-2025),
the M1+v7 prototype, Pooled sheet. HOLD.
