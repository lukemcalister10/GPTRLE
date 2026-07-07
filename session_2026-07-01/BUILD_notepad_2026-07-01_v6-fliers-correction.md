# BUILD notepad — 2026-07-01 — CORRECTION: v6 on the true first-year fliers

Answering Luke's question (I'd only shown v3/v7 for the fliers). Ran v6 on all five. head 8aed420a, level fixed, no bake.

 player             pk  devT  k(v6)   cur    v6    v6Δ%  | v3Δ%   v7Δ%
 Willem Duursma      1   1.0  0.00   4179  4179   +0.0   | -7.1   +0.0
 Zeke Uwland         2   1.0  0.00   1639  1639   +0.0   | -20.3  +0.0
 Harry Dean          3   1.0  0.00   1874  1874   +0.0   | -22.7  +0.0
 Cooper Duff-Tytler  4   1.0  0.00   1426  1426   +0.0   | -33.8  +0.0
 Sam Cumming         7   1.0  0.00   1987  1987   +0.0   | -20.2  +0.0

v6 leaves them ALL unchanged (0.0%) = identical to v7. Their dev_tenure = 1 -> v6's gate k(T)=0.5*clip((T-1)/4,0,1)=0
-> no decay.

CORRECTION to the Phase-2b verdict: I wrote "v6 (tenure gate) half-helps" on first-year safety. THAT IS WRONG. For a
genuine T=1 first-year, v6's gate zeroes out (k=0), so v6 preserves true first-years just as completely as v7. First-year
safety is a v3-vs-{v6,v7} distinction, NOT v6-vs-v7:
  - v3 (blanket drop-q90): CRATERS true first-years -7% to -34%. Fails first-year safety.
  - v6 AND v7: both fully preserve true first-years (0.0%). Any gate fixes v3's failure.

Where v6 and v7 ACTUALLY differ (on tested cases):
  - v7 shaves the proven-mediocre BODY harder (compresses q70/q90 directly): Bruhn -37% / O'Driscoll -43%, vs v6's
    -28% / -34%. v6 only trims tail WEIGHT -> under-targets the body, which is the real over-width.
  - Gate variable: v6 gates on TENURE (~= age for normally-aged players; the conflation the relay flagged as unsound).
    v7 splits it: body <- evidence(seasons), tail <- age(headroom). Diverges only on the MATURE-AGE rookie (old but n=1):
    v6 (T=1 -> k=0) hands him a FULL tail; v7 gives a MODEST age-scaled tail (correct by design). Numerically small on
    McCarthy (both ~unchanged), but v7 is right in principle.

CORRECTED NET VERDICT: the decisive failure is v3's (not first-year-safe); any gate fixes it. Between the gated options,
v7 is preferable because it (a) targets the body (the real over-width) more directly and (b) uses the principled
two-variable gate rather than the conflated tenure gate. (Unchanged from Phase 2b: q97 tail weight preserved - base rate
17% refutes cutting it; the age-scaled tail is a minor, data-backed refinement.)

No re-cut (no state change). HOLDING for Luke's fix decision.
