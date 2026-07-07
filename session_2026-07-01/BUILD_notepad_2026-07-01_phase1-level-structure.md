# BUILD — PHASE 1: LEVEL + STRUCTURE (measure-only) — head 8aed420a / store 644d1254

Nothing changed, nothing baked, no re-cut. All four sub-tasks measured cold on the current head. Two relay premises are
corrected by the numbers (Parish career-high; "Lc lags") — flagged, evidence-grounded.

================================================================================
1a — DOES THE BAND CONSUME THE LEVEL?  YES — the band is DOWNSTREAM of the level.
================================================================================
b6(p,Y) = cond_prior_band(p,cm,Y) [5 learned quantiles] + q97m ceiling. BOTH take cp._feat(p,Y) as their only input,
and _feat was rebound to _feat_infer, whose feature vector INCLUDES cp._lvl_eff(p,Y) = Leff:
   _feat_infer = onehot(pos) + [log(effpk), exposure, dev_tenure, cp._lvl_eff(p,Y)=LEVEL, age]
So every band value is a learned function of a vector containing the level.
DIRECT SENSITIVITY (Jeffrey): force Leff to base+/-4, remeasure b6:
   Leff 73.5 -> band mid 84.2 ;  Leff 77.5 -> 87.2 ;  Leff 81.5 -> 92.6     (band mid moves ~1:1 with the level)
=> A shift in the level shifts the band ~1:1. The level is genuinely UPSTREAM; a stale/inflated level double-counts into
   the band. Phase 1 (level) before Phase 2 (band) is the correct order.
REFINEMENT (load-bearing for who Phase 1 vs Phase 2 owns): the ~1:1 holds for PROVEN players (band is demonstrated-
   dominated). For THIN-EXPOSURE pedigree players the band FLOATS far above a conservative level on pedigree features
   (see 1c: early Parish level 66-82 but band mid 100-105). So the level's leverage on the band is strong for the
   proven-mediocre cohort (Jeffrey/Ginnivan/Bruhn) and weak for first-year/unproven pedigree (early Parish = a pure-band
   case for Phase 2).

================================================================================
1b — RECENCY COMPOSITION: the lag is real, but it lives in L_old (0.72^k), NOT Lc (0.35^k).
================================================================================
Two weightings: Lc=_lvlcurr uses LDECAY_G (0.35^k GEN / 0.225^k MID / 0.40^k KEY) - STEEP. The engine-USED level
Leff = L_old = lvl_par ~= _lvl_wt uses _swt = 0.72^k - FLAT (carries old seasons). (For these proven players
Leff == L_old == lvl_wt exactly; the hold-band selects L_old, not the fresher Lc.)

 player   pos     bar  seasons(yr:g:avg, recent->old)                 rec1  rec2   Lc  Leff  Leff-rec1  %lvlwt>=2yr
 Powell   GEN_FWD 67.9 26:8:67.6 25:23:84.3 24:23:80.2 (older weak)   67.6  80.0 75.7 73.9   +6.3       50%
 Ginnivan GEN_FWD 67.9 26:13:81.8 25:25:77.4 24:23:72.0 (23-:weak)    81.8  78.9 78.0 71.4  -10.4       44%
 Bruhn    MID     77.1 26:13:76.9 24:17:72.3 23:19:68.8 (21-22 weak)  76.9  74.3 76.4 68.9   -8.0       64%
 Day*     MID     77.1 26:2:102.5 25:6:99.0 24:16:91.2 (thin recent)  102.5 99.9 98.7 89.4  -13.1       79%
 Serong*  MID     77.1 26:10:101.1 25:24:107.5 24:23:115.7 (all high) 101.1 105.6 104.3 104.3 +3.2      54%
 (* = fair-value contrasts Luke reads as correctly tracked)

- IMPROVERS on FULL samples are under-credited: Ginnivan Leff 71.4 vs recent-1 81.8 (-10.4); Bruhn 68.9 vs 76.9 (-8.0).
  Cause: 44-64% of the 0.72^k weight sits on OLD, WEAK seasons (Ginnivan 2022=56@23g; Bruhn 2021=45@13g), so L_old is
  dragged below realised recent form; the hold-band then uses that laggy L_old (rise < FLAT_TOL_G 12.0, so held).
- FAIR contrasts behave correctly: Serong TRACKS (Leff 104.3 ~= recent 101-105; stable career, old seasons ~ recent).
  Day's lag (Leff 89.4 vs recent-1 102.5) is CORRECT - his recent seasons are 2g and 6g; games-weighting properly
  discounts them to his last reliable ~89-91. Same mechanism, right answer, because the signal is thin.
=> The distinction is reliability, not recency: 0.72^k + games-weighting handles thin-recent (Day) correctly; it FAILS
   on full-sample improvement (Ginnivan/Bruhn) because old weak full seasons still carry ~half the weight and the
   hold-band prefers L_old to Lc.

POWELL VERDICT: NOT a clean stale-Lc over-hold. His Leff 73.9 sits BELOW his last two full seasons (80.0) and above only
his 8-game 2026 partial (67.6, down from 2025's 84.3). His "+7.8 above bar" rests on GENUINE 2024-25 (80-84 on full
seasons); the engine level is if anything conservative vs that. LEANS GENUINE. The one lag signal: IF the 8-game 2026 dip
is his true new level, the 0.72^k carries 2024-25 and over-holds - but 8 games is too thin to conclude. His overvaluation,
if Luke still reads one, is the SOFT GEN_FWD bar (67.9) + band/runway (M2/M3), not a stale level.

================================================================================
1c — PARISH BOOK-LEVEL RECONCILE: the LEVEL is conservative; the inflation is 100% BAND x runway.
================================================================================
FACTUAL CORRECTION: Parish raw career-high = 116.5 (2021 breakout), NOT ~86. His 2016-20 PRE-breakout high = 86.7.
Present Lc 93.4 is a recency-weighted blend of recent 89-108 seasons (all <= 116.5) -> LEGAL, no "weighted-avg exceeds
best season" problem, no level inflation today. (The ~86 in the premise is the pre-breakout high, not the career-high.)

BOOK seasons 1-5 (2016-2020, hindsight-free as-of), MID bar 77.1:
   yr  seas g savg lvlwt  par  Leff bandM    EV   EVdem  levShare
   16   1  20 72.2 72.2  64.9 66.7 105.5  3151  3669   -518
   17   2  20 76.2 74.5  69.4 72.4 105.6  3268  3811   -543
   18   3  15 80.3 76.7  73.8 77.7 103.9  3356  3474   -118
   19   4  21 84.8 80.1  78.6 80.1 100.0  3210  3620   -410
   20   5  17 86.7 82.2  83.7 82.2  99.5  3021  3491   -470
   SUM EV(1-5) = 16006 ; SUM at level=demonstrated = 18065 ; LEVEL's share of inflation = -2059 (NEGATIVE)
- The engine's Leff (66.7->82.2) sits BELOW his season averages early (pulled toward par + the exposure ramp). Forcing
  level = that year's actual average RAISES EV every year -> the level is CONSERVATIVE, not inflating.
- The >3000/season sits on a BAND MID of ~100-105 for a player producing 72-87 (pk5 pedigree ceiling), integrated over
  huge runway (age 19-23). That is entirely M2 (ceiling weight) x M3 (runway) -> Phase 2.
=> Of book-Parish's ~16,006 over seasons 1-5, the LEVEL's share is ZERO/negative. The band owns it. Present-day Parish
   is a genuine producer (+16, level legal); the OVERVALUED exemplar is the pre-breakout BOOK Parish, and it is pure band.

================================================================================
1d — DE-SURVIVORED COHORT CURVE (current head): STILL PEAKS LATE (career-year 6).
================================================================================
Reconstructed the 2026-06-28 method faithfully (harness dropped from bundle): full cohort ND-with-pick, draft 2014-2019
(n=437); value_asof = deepcopy + scoring truncated to yr<=D+t + strip _pos_now/_fut (leak-free, drafted-pos) + realised-
bust floor (never-debuted & t>=3 -> 0). Mean SCAR(ev) per player by career-year, current engine 8aed420a:

   t:     0    1    2    3    4    5    6    7    8
   mean:257  471  638  741  821  826  848  787  666      (median flat ~24-28 throughout)
   n:  437  437  437  437  437  437  437  437  372

- PEAK at t=6 (848), then declines (787, 666). Does NOT peak yr4-5. peak/yr0 = 3.30x ; yr6/yr1 = 1.80x.
- Matches the 06-30 book curve (pooled peak cy6; GEN_DEF cy7; RUC cy7-8). The M1/survivorship work did NOT move the peak
  to yr4-5 - the curve still peaks LATE.
- Median flat (~24-28) at every t: the late peak is a MEAN/star phenomenon (survivor-stars keep appreciating to cy6);
  the typical player is flat-low. The low yr0 anchor (257) vs peak (848 = 3.3x) is the same "draft-day option underpriced,
  production additive" pattern the 06-28 doc named (yr0/peak 0.30x here vs 0.37x then).
=> Per the relay's rule: peak yr6 (LATE) -> the runway+variance concern is LIVE. Phase-2 ceiling-weight decay is the
   shared fix; the thread does NOT close on survivorship alone.

================================================================================
PLAIN STATEMENT
================================================================================
- Does the level LAG or INFLATE?  It LAGS (under-credits full-sample improvers: Ginnivan -10.4, Bruhn -8.0), localised to
  L_old's 0.72^k weighting carrying old weak seasons + the hold-band selecting L_old over the fresher Lc. It does NOT
  inflate - where we looked for inflation (Parish book) the level is CONSERVATIVE (below production). "Lc lags" is
  imprecise: Lc (0.35^k) tracks recent form; the LAG is in Leff via L_old.
- Does the band CONSUME the level?  YES - downstream, ~1:1 for proven players (level load-bearing upstream). For thin-
  exposure pedigree the band floats above a conservative level on pedigree features. So Phase 1 (level) is correctly
  upstream of Phase 2 (band) for the proven-mediocre cohort; first-year/unproven overvaluation is band-side.
- Does the cohort curve PEAK LATE?  YES - career-year 6 on the current de-survivored curve, then declines. Survivorship
  alone did not bring it to yr4-5; the runway+variance concern is live for Phase 2.
- POWELL classification: leans GENUINE above the soft GEN_FWD bar; NOT a clean stale-Lc artifact (8-game-2026 caveat).
  Any residual overvaluation is the soft bar + band/runway, not the level.
- PARISH classification: present-day = genuine (+16, level legal, career-high 116.5). Pre-breakout BOOK Parish = the clean
  overvalued exemplar, and it is PURE BAND (ceiling x runway); the level's share is zero/negative. -> Phase 2.

Scratch (workspace only): _p1_recency.py, _p1_parish.py, _p1_cohort.py (+ earlier _ov_*.py). No re-cut (no state change).
HOLDING for Phase 2 (the ceiling-weight sweep). Not starting the sweep, not designing any fix.
