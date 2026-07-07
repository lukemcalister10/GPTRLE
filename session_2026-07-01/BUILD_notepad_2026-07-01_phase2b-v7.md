## BUILD — PHASE 2b: v6 mechanics + refined two-variable ceiling model (v7) vs simple baseline (v3)
head 8aed420a / store 644d1254. Measure/prototype only, nothing baked, no re-cut, LEVEL HELD FIXED throughout.
Re-pricing validated exact vs price6 (Parish 3356, Jeffrey 1857, Bruhn 863).

================================================================================
v6 EXACT MECHANICS (as I actually coded it)
================================================================================
q90 (w[4]) and q97 (w[5]) decayed EQUALLY by (1-k); freed weight k*(w90+w97) split 50/50 into q30 & q50.
k(T)=0.5*clip((T-1)/4,0,1). Weight vectors on [q10,q30,q50,q70,q90,q97]:
   k=0.00: [0.18, 0.18,  0.18,  0.18, 0.18,  0.10]
   k=0.25: [0.18, 0.215, 0.215, 0.18, 0.135, 0.075]
   k=0.50: [0.18, 0.25,  0.25,  0.18, 0.09,  0.05]

================================================================================
DERIVED CONSTANTS (from walk-forward data, 6685 player-season records; era-adjusted)
================================================================================
(A) BREAKOUT BASE RATE (q97 fair weight):  among proven-mediocre records (T>=4, dem in [67,81], n=1849),
    P(forward-best-season reaches the model q97) = 318/1849 = 17.2%.  P(jump>=+15)=33%, P(jump>=+20)=22%.
    => REFUTES the "~2-5% breakout, cut the q97 weight" premise. Breakouts are COMMON for proven-mediocre (partly
       survivor-selection, but real). The current q97 weight 0.10 is NOT too high vs the base rate (17% cumulative;
       quantile-mass fair weight ~0.065). CONCLUSION: DO NOT cut the tail weight. The tail is preserved.
(B) BODY WIDTH is justified by EVIDENCE (seasons), not tightness: forward-peak spread by cohort:
       1-2 seasons  : mean jump +18.9, p90 +42.7   (WIDE)
       n>=4 volatile: mean +6.2, p90 +24.5
       n>=4 stable  : mean +5.1, p90 +22.5          (tight; ~0.53x the 1-2 season p90)
    => high-evidence forward peaks cluster ~half as wide. DERIVED body compression cB = 0.47*clip((n-1)/3,0,1)
       [n1:0.00 n2:0.16 n3:0.31 n4+:0.47]. (Dispersion barely separates stable vs volatile -> SEASONS dominate,
       matching "evidence resolution", NOT age/tenure.)
(C) TAIL HEADROOM shrinks with AGE: p90 forward jump by age: 19-21 -> 49.9 ; 21-23 -> 37.9 ; 23-25 -> 28.8 ;
    25+ -> 20.0.  DERIVED tail age-scale aSc = interp(age,[20,22,24,27],[1.00,0.76,0.58,0.40]) on the q97 WIDTH
    (q97-median). Young keeps full breakout headroom; old gets a modest tail.

VARIANTS (level fixed):
- v3  = plain drop-q90: bands [q10,q30,q50,q70,q97], weights [.18,.18,.18,.18,.10]. (SIMPLE baseline; BLANKET, no gate.)
- v6  = tenure-gated tail weight-decay (above).
- v7  = TWO-VARIABLE: compress q70,q90 toward median by cB(n) [BODY <- evidence]; scale q97 width by aSc(age)
        [TAIL <- age headroom]; KEEP the weights (tail preserved, per (A)). q10/q30/q50 untouched (level-anchored).

================================================================================
HEAD-TO-HEAD (Δ% vs current, re-anchored to Serong)
================================================================================
 case                  tier                  v3      v6      v7     (age/n)
 bookParish-yr3        PUREBAND             -8.3    -1.6    -1.5    (21/3)
 bookParish-yr5        PUREBAND             -4.6    -5.5    -3.8    (23/5)
 Jeffrey               MIDOV               -15.4   -13.9   -13.4    (24/4)
 Bruhn                 MIDOV(plateau)      -30.5   -27.8   -37.1    (24/5)
 O'Driscoll            MIDOV(plateau)      -37.7   -33.8   -42.9    (24/4)
 Serong                FAIR/anchor          +0.0    +0.0    +0.0    (25/7)
 Butters               ELITE                +1.4    +3.3    +3.7    (26/8)
 Bontempelli           ELITE                +4.3    +5.6    +5.5    (31/13)
 ClaytonOliver         ELITE-decl           +3.2    +3.9    +2.0    (29/11)
 -- VALIDATION --
 DaviesUniacke@21      BREAKOUT(pre,rising) -9.8    -6.8    -8.8    (22/4)
 EdRichards@21         BREAKOUT(pre,FLAT)  -31.6   -27.8   -31.8    (22/3)
 Parish@20             BREAKOUT(pre,rising) -4.6    -5.5    -3.8    (23/5)
 MatureAge:McCarthy    MATURE(old,1seas)    +4.5    +5.3    +4.9    (25/1)  pk1
 (MatureAge:Watkins near-zero value cur=17 -> % is noise; excluded)
 -- TRUE YEAR-1 FLIERS (genuine first season, the decisive first-year test) --  Δ% vs current (NOT anchored):
 Willem Duursma  pk1 a19 n1: cur 4179  v3 -7.1%   v7 +0.0%
 Zeke Uwland     pk2 a19 n1: cur 1639  v3 -20.3%  v7 +0.0%
 Harry Dean      pk3 a19 n1: cur 1874  v3 -22.7%  v7 +0.0%
 CooperDuffTytler pk4 a19 n1: cur 1426 v3 -33.8%  v7 +0.0%
 Sam Cumming     pk7 a19 n1: cur 1987  v3 -20.2%  v7 +0.0%

================================================================================
VERDICT
================================================================================
YES - v7 CLEARLY beats v3, but for ONE specific, decisive reason: FIRST-YEAR SAFETY.
- On the TARGETS (MIDOV/PUREBAND) and ELITE and mature-age and the rising breakout cases, v3 ~= v6 ~= v7 (all within a
  few %). The blunt drop-q90 already gets the tier differential (posval geometry does the work, as Phase 2 showed).
- BUT v3 is BLANKET and CRATERS genuine first-year fliers: Duursma -7%, Uwland -20%, Dean -23%, Duff-Tytler -34%,
  Cumming -20%. That violates first-year protection (Duursma pk1 4179 is a Harley-Reid-class value). v6 (tenure gate)
  half-helps but tenure~=age is unsound. v7's EVIDENCE-GATE (n=1 -> cB=0 -> body untouched) leaves EVERY true first-year
  EXACTLY unchanged (+0.0%). That is the whole ballgame - the simple baseline is NOT first-year-safe; v7 is.
- The DECISIVE ingredient is the EVIDENCE-GATED BODY compression (cB keyed on seasons). v7's age-scaled tail is
  data-supported (C) but SMALL in effect (tail weight only 0.10) - a minor refinement, not the winner.
- The q97-WEIGHT-CUT premise is REFUTED (base rate 17%, not 2-5%): the tail must be PRESERVED, which v7 does.

Does the two-variable split hold on the hard cases?
- MATURE-AGE (McCarthy pk1, old, n=1): v7 gives cB=0 (WIDE body, no evidence) + aSc~0.5 (MODEST tail, old) -> ~unchanged,
  correct BY DESIGN. Exactly the case single-variable framings failed; the split handles it. (v3 spares him only by
  band-shape luck.)
- BREAKOUT set: v7 preserves the RISING breakouts well (Davies-Uniacke -8.8%, Parish -3.8%). The FLAT one (Ed Richards,
  49-60 = sub-replacement pre-breakout) is shaved -31.8% - UNAVOIDABLE and arguably CORRECT: ex-ante he is observationally
  identical to a never-breakout plateau, so no scheme can spare him without sparing all plateaus; his realized breakout was
  a ~17% tail event, priced by the (preserved) tail. The relay's "don't crater the three" is achievable for the rising two,
  not the flat one - and shaving the flat sub-replacement plateau is the right call.

RECOMMENDED DIRECTION (one line, diagnosis only): adopt the EVIDENCE-GATED body compression (v7's BODY half: compress
q70/q90 toward the median by cB=0.47*clip((n_seasons-1)/3,0,1)); KEEP the q97 tail weight (base rate 17% refutes cutting it)
and OPTIONALLY age-scale the tail width (minor); this matches the simple drop-q90 on the targets while being the only
variant that is genuinely first-year-safe.

Scratch (workspace only): _p2b_derive.py, _p2b_headtohead.py. No re-cut (no state change). HOLDING for Luke's fix decision.
