# BUILD notepad — 2026-07-01 — v6-vs-v7 unintended consequences (divergence scan)

Answering Luke: "Do you see any unintended consequences with v7 that aren't there with v6 and vice versa?"
Method: scanned 312 real outfield players (>=2 qual seasons, cur>=300), computed cur / v6 / v7, ranked by divergence
(v7Δ% − v6Δ%), profiled the extremes + suspect archetypes. head 8aed420a, level fixed, NOTHING baked.
Script: _p2b_divergence.py.

Both versions hit YOUNG/RISING players wrongly, but through OPPOSITE mechanisms.

================================================================================
v7's UNINTENDED CONSEQUENCES (not in v6)
================================================================================

(1) OVER-COMPRESSES GENUINE IMPROVERS.
    cB keys on SEASON COUNT, blind to trend -> a player who improved over many seasons gets full body-compression
    toward his (lagging) median.
        Jack Graham  MID age28 n8 trend+23.3  cur424:  v6 -35%   v7 -60%
    COMPOUNDS the Phase-1 hold-band suppression: the band is already computed at the improver's HELD (lagging) Leff,
    and v7 then squeezes q70/q90 toward that lagging center. v6 (tail-WEIGHT only, never touches body values) doesn't.
    *** This is the one to flag hardest: v7 applied WITHOUT the Phase-1 level fix double-suppresses improvers. ***
    Aggregate modest (improvers v7 -15.0% vs v6 -13.2%) but worst cases ~25 pts harsher.

(2) OVER-COMPRESSES INJURY-PRONE PLAYERS.
    cB counts SEASONS, not GAMES, so N injury-shortened seasons read as "resolved evidence."
        Alex Davies  MID age24 n5 mg9(!) :  v6 -47%   v7 -68%
    Five 9-game seasons is thin real evidence; v7 treats it as fully resolved. v6's gate is exposure-aware -> gentler.

================================================================================
v6's UNINTENDED CONSEQUENCES (not in v7)
================================================================================

(1) OVER-PENALIZES YOUNG, FEW-SEASON (often rising) PLAYERS — the concrete face of "tenure ~= age" unsoundness.
    v6 gates on dev_tenure, and for a thin career eff_ten = max(base, age-18), so a 23yo with 3 seasons gets
    dev_tenure ~= 5 -> k = 0.5 (full tail-decay), while v7's evidence gate gives only cB(n=3) = 0.31.
        Neil Erasmus  MID age23 n3 trend+22.3:  v6 -41%   v7 -34%
        Elijah Tsatas MID age22 n2 trend+42.2:  v6 -32%   v7 -28%
        Ollie Dempsey MID age23 n3 cur2113:     v6 -24%   v7 -19%
    So v6 shaves age-driven-tenure young risers HARDER than v7 — penalizing exactly the young-upside players beyond
    the literal T=1 first-years.

(2) UNDER-CORRECTS THE ACTUAL PROBLEM.
    v6 only trims tail WEIGHT and leaves body VALUES intact, but Phase 2b showed the over-width is in the BODY
    (q70-q90). So v6 leaves residual over-valuation on proven-mediocre (Bruhn -28% vs v7 -37%). An under-fix, not a
    side-effect.

================================================================================
THROUGH-LINE
================================================================================
  - v7's gate is EVIDENCE (season count) but BLIND to games and trend -> over-hits injury-prone and improvers.
  - v6's gate is TENURE but CONFLATED with age (via age-18) -> over-hits young rising few-season players, and
    under-hits the body.

Profile aggregates (mean Δ%, n=312 scan):
  IMPROVERS (trend>=+8)      n=109  v6 -13.2  v7 -15.0  (v7-v6 -1.8)
  DECLINERS (trend<=-8)      n= 71  v6 -14.1  v7 -19.4  (v7-v6 -5.3)
  INJURY-PRONE (mg<12,n>=4)  n=  2  v6 -43.1  v7 -58.6  (v7-v6 -15.5)
  ALL                        n=312  v6 -13.0  v7 -16.4  (v7-v6 -3.3)

Full extremes tables (v7-v6 = divergence):
  v7 HARSHER than v6 (top): Cox KEY_FWD a24 n4 (-45.6/-73.2/-27.6); Jack Graham MID a28 n8 trend+23.3 (-34.7/-60.2/-25.5);
    Deven Robertson MID a25 n3 trend-17.3 (-46.9/-72.2/-25.2); James O'Donnell KEY_DEF a24 n4 (-27.8/-52.7/-24.9);
    Caminiti KEY_FWD a23 n4 (-29.5/-52.9/-23.4); Hinge GEN_DEF a28 n4 (-26.4/-49.3/-22.9);
    Alex Davies MID a24 n5 mg9 (-46.5/-68.1/-21.7); Worpel MID a27 n9 trend-14.4 (-24.6/-45.6/-21.0).
  v6 HARSHER than v7 (top): Erasmus MID a23 n3 trend+22.3 (-41.0/-33.8/+7.2); Bazzo KEY_DEF a23 n3 (-33.1/-26.9/+6.2);
    Dempsey MID a23 n3 cur2113 (-24.3/-19.0/+5.3); Fonti GEN_DEF a22 n2 trend+18.8 (-26.5/-21.3/+5.1);
    Worner GEN_DEF a24 n2 trend+17.0 (-31.2/-26.3/+4.9); Sheldrick MID a23 n3 (-43.6/-39.4/+4.2);
    Tsatas MID a22 n2 trend+42.2 (-31.9/-28.4/+3.4); Archer Reid KEY_FWD a21 n2 (-18.7/-15.6/+3.1);
    Jaspa Fletcher GEN_DEF a22 n4 cur2071 (-9.8/-7.1/+2.7).

================================================================================
MITIGATIONS (design, not my call)
================================================================================
  - v7 -> make cB exposure-weighted (games, not raw seasons) and/or dampen it for rising trends.
  - v6 -> gate on true evidence rather than age-inflated tenure.
  - SINGLE MOST IMPORTANT CAVEAT: v7 must NOT ship before the Phase-1 improver/level fix, or it compounds
    improver-suppression. v6 is safer on that axis but leaves the body over-width standing.

No re-cut (no state change). HOLDING for Luke's fix decision.
