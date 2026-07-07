# BUILD — PHASE 2: THE BAND (ceiling weighting), level held fixed — head 8aed420a / store 644d1254

Measure-only, nothing baked, no re-cut. LEVEL HELD FIXED throughout (each player's Leff frozen; only the band varied).
Re-pricing validated against engine price6 (exact: Parish 3356, Jeffrey 1857, Bruhn 863).

CARRIED CORRECTION (owning my Phase-1 error): I attributed the ceiling float to "thin exposure." WRONG - book-Parish
played 20/19/15/20/17 (full games). Exposure is NOT the seam; it actually moves the ceiling the WRONG way (more games ->
higher ceiling). Part 1 finds the real seam.

================================================================================
PART 1 — WHAT DRIVES THE CEILING FLOAT (band mid - fixed Leff). Seam = AGE; NOT pedigree.
================================================================================
Base offsets: Parish yr1 +38.8, yr3 +26.2, yr5 +17.3 ; Jeffrey +9.7 ; Reid yr1 +18.6.
Feature sweeps on book-Parish yr3 (Leff FROZEN at 77.7), offset = band_mid - 77.7:
   pick 1->60:        +26 +26 +24 +20 +20 +19   -> NEARLY FLAT. PEDIGREE-LOCKED IS REFUTED (pk60 still +19).
   dev_tenure 1->8:   +34 +30 +26 +24 +23 +23 +19 -> right sign, WEAK (8 mediocre seasons still +19).
   age 19->29:        +29 +26 +17 +11 +8 +2      -> STRONG. Age is the dominant driver of the float.
   exposure 10->120:  +11 +24 +29 +28 +28        -> WRONG WAY (more games -> higher ceiling). Not the seam.
Cross-check (Reid pk1, Jeffrey pk30): both offsets age-driven, pick-inert (Reid pk1->60: +19->+18).

THE SEAM PROBLEM: the float is AGE-LOCKED, not tenure-gated. Age (the strong lever) CANNOT separate proven-mediocre-young
from genuine-young-flier: book-Parish-yr5 (+17.3, FIVE seasons of sub-87) and Reid-yr1 (+18.6, unproven) get NEARLY THE
SAME ceiling. Tenure - the variable that SHOULD gate it (years demonstrating a median, what Luke's slide keys on) - has the
right sign but too little magnitude. => No clean seam exists in the current band. A first-year-safe fix must AMPLIFY
tenure-sensitivity externally (pedigree is inert; exposure is counter-productive).

================================================================================
PART 2 — WEIGHTS + PERCENTILE SWEEP (level fixed)
================================================================================
CURRENT WEIGHTS: WQ6 = [0.18,0.18,0.18,0.18,0.18,0.10] on [q10,q30,q50,q70,q90,q97]. Top two bands (q90+q97) carry 0.28.

SWEEP - Δ% vs current, RE-ANCHORED to Serong (so a reference stays ~0):
 player          tier        2:no_q97   3:no_q90   4:slidup    5:ten-slide(0.16)   6:wt-decay(0.5)
 bookParish-yr3  PUREBAND      -7.3       -8.3       +0.4         -25.5               -7.6
 Jeffrey         MIDOV         -7.0      -15.4       -3.5         -38.2              -19.8
 Bruhn           MIDOV        -14.8      -30.5       -8.8         -59.9              -33.7
 O'Driscoll      MIDOV        -16.9      -37.7      -10.4         -70.5              -39.7
 WillDay         FAIR          -5.1       -5.9       -1.2          --                  --
 Serong          FAIR          0.0        0.0        0.0         -13.3               -5.9
 Butters         ELITE        +2.9       +1.4       -0.2          -9.1               -2.6
 Bontempelli     ELITE        +4.8       +4.3       -1.0          -0.6               -0.3
 ClaytonOliver   ELITE-decl   +3.0       +3.2       -1.0          --                  --
 Reid-yr1        YOUNG(T3)    -1.8       -3.7       -0.4         -16.9               -4.2
 (v5/v6 Δ% are raw vs current, NOT Serong-anchored; v5 at dmax=0.16, v6 at kmax=0.5)

READS:
- TIER DIFFERENTIAL is REAL and LARGELY INTRINSIC to posval's convexity: bands sitting NEAR the replacement bar (mediocre)
  are in the sensitive/convex region and shave hard; bands FAR ABOVE the bar (elite) are in the ~linear region and barely
  move. So ANY tail reduction hits mediocre > elite. (This is why the blanket v2/v3 already spare elite: Butters/Bonti RISE
  relative to Serong.) The differential is a posval-geometry property, not something the scheme has to engineer.
- BLANKET tail-strips (v2/v3) spare elite and (here) Reid - but they separate on band SHAPE (body-vs-tail), NOT tenure. A
  moderate-body young flier would be shaved like a proven mediocre. Not robustly first-year-safe.
- v5 TENURE-SLIDE (slide percentiles down with tenure): strong on MIDOV but SHAVES the elite BODY too (Butters -9%, Serong
  -13%) because it moves every percentile down. Crude.
- v6 TENURE-GATED TAIL WEIGHT-DECAY (move q90/q97 weight to the body, gated on tenure) = THE WINNER:
    @ kmax=0.5, k(T)=0.5*clip((T-1)/4,0,1) [T1:0.00 T3:0.25 T5+:0.50] -> Bruhn -33.7, O'Driscoll -39.7, Jeffrey -19.8
    (MIDOV hit hard); Butters -2.6, Bonti -0.3, Serong -5.9 (ELITE spared); Reid -4.2 (spared).
  Because it only moves TAIL weight to the body: a compact elite band barely moves; a fat-tailed near-bar band collapses;
  and the tenure gate spares the unproven.
- FIRST-YEAR CHECK: Reid's dev_tenure is 3, NOT 1 (drafted 2023). A true T=1 flier is FULLY spared (k=0). At T=3 he takes a
  small -4.2% under v6 (vs -16.9% under the cruder v5). So v6 is first-year-safe ON TENURE (the seam variable from Part 1).
- TAIL-BIAS: confirmed - the propping is the q90/q97 tail (0.28 weight) applied to fat-tailed near-bar bands; decaying it
  hits fat-tailed mid-tier >> compact elite.

================================================================================
PART 3 — COHORT CURVE UNDER v6 (de-survivored, current head). Late mean DOWN; peak DOES NOT move.
================================================================================
   t:        0    1    2    3    4    5    6    7    8   peak
   baseline:257  471  638  741  821  826  848  787  666   t6
   v6 k0.5: 257  469  594  658  718  705  750  711  603   t6   (Δ: t0 +0.0, t1 -0.5, t2 -6.9, t3 -11.1, t4 -12.6,
                                                                   t5 -14.6, t6 -11.5, t7 -9.7, t8 -9.4)
   v6 k0.9 (steep, ramp to t8): ... t6:722 ...              t6   (peak STILL t6 even aggressively)
- The tenure gate WORKS: early years untouched (t0 +0%, t1 -0.5%), late years pulled down 9-15%. So the band lever DOES
  reach the cohort curve's late region and ties the propped-mediocre component to it.
- BUT the PEAK DOES NOT MOVE from cy6 - not at k=0.5, not even at an aggressive k=0.9 growing through t8. Reason (structural):
  the late-cohort MEAN is driven by survivor-STARS (median flat ~24-28 at every t - Phase 1), and v6 CORRECTLY SPARES stars
  (they sit in posval's linear region, far above the bar). So the fix cannot move a star-driven peak.
=> The per-player propping fix (band) and the cohort-curve PEAK POSITION are DECOUPLED. v6 addresses M2 (propped mediocre)
   and pulls the late mean down, but the cy6 peak is survivor-star real-appreciation, which the fix should not and does not
   touch. Relocating the peak would need a DIFFERENT lever (runway/age M3, or the level) and would risk shaving legitimate
   star appreciation. This REFINES the Phase-1 hypothesis: decaying the ceiling weight pulls the late mean down but does
   NOT move the peak earlier.

================================================================================
PLAIN STATEMENT
================================================================================
- WHAT DRIVES THE CEILING FLOAT: AGE (primary; offset +29@19 -> +2@29), tenure (weak, right sign), NOT pedigree/pick
  (refuted; ~7pts across pk1-60), and exposure moves it the WRONG way. The current band has no clean proven-mediocre seam.
- BEST VARIANT: v6 = TENURE-GATED decay of the q90/q97 tail weight (redistributed to the body). It separates over-valued-
  mediocre (fat-tailed, near-bar -> shaved hard) from genuine-elite (compact, far above bar -> spared) and young fliers
  (low tenure -> spared) more cleanly than the percentile-slide or any blanket strip.
- FIRST-YEAR-SAFE: YES, on TENURE (the seam variable) - a true T=1 flier is fully spared; Reid (T=3) takes only -4.2%.
  Must be applied as an EXTERNAL tenure gate because the learned band under-weights tenure (pedigree is inert).
- COHORT CURVE: v6 pulls the late MEAN down (9-15%, early untouched) but does NOT move the cy6 PEAK - the peak is survivor-
  star real appreciation, correctly spared. The two symptoms are only PARTIALLY tied by this lever; the peak position is a
  separate (largely legitimate) phenomenon, not the band's propping.

CANDIDATE FIX (diagnosis only, one line): tenure-gated decay of the q90/q97 tail weight, k(T) ramping 0->~0.5 over T1->5,
redistributed to the body - first-year-safe, collapses propped-mediocre toward the demonstrated median, leaves elite and
young fliers intact; does NOT relocate the star-driven cohort peak (a separate lever).

Scratch (workspace only): _p2_seam.py, _p2_sweep.py, _p2_tenure.py, _p3_cohort_v6.py. No re-cut (no state change).
HOLDING for Luke's fix decision.
