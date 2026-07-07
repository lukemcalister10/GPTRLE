# BUILD notepad — 2026-07-01 — decay-proration (Phase 2) prototype: INERT holds, fix NOT viable → HOLD

Head 8aed420a unchanged, nothing baked. Built exactly as specified: _swt=0.72^max(0,(Y-yr)-(1-f)),
f=14/24 for Y=2026, f=1 else; rebound at INFERENCE only (models never retrained).

BOTTOM LINE: the safety property holds (byte-exact no-op historically), but the prototype FALSIFIES the
mechanism it was built on and causes large uncontrolled side-effects -> not viable as-is. HOLD + re-diagnose.

1. INERT at f=1 — PASS. 60 established players x historical Y 2022-2025: max|Δ|=0, #changed=0. Book
historical columns + M1+v7 curve untouched by construction. Bake stays separable.

2. Thin-2026 lift — FAILS for 90%. liberatore 1455->1455 (+0%), o-brien 692->692 (+0%), nankervis -1%,
rozee +7%. MECHANISM: liberatore exposure 55->62.5 but reliability-shrunk level UNCHANGED 106.4->106.4 —
exposure already >> LEVEL_RAMP=14, so min(1,exp/14) saturated at 1.0. Only 6/62 thin-2026 players (10%) are
in the shrink regime (exp<14); median thin-player exposure = 35. Diagnosis assumed thin-2026 => low
exposure, but exposure is CUMULATIVE recency-wtd games; a thin 2026 on full prior seasons still totals ~35.
The intended channel is inactive for 90%. Only a secondary _lvl_wt reweight fires (on avg-gap, not
thinness) -> rozee lifts, liberatore doesn't.

3. On-pace — FAILS <2% badly. 42/121 (35%) move >2%. jack-ross +22%, james-jordon -21.5% (DEAD-FLAT
63->63!), hardwick -13%, rayner -9.8%, rowbottom -9.1%. Median |move| 0.9% but tail severe + bidirectional.
james-jordon flat-rate -21.5% proves it's NOT a toward-2025 shift — proration reweights the WHOLE season
history and propagates nonlinearly through the trained models. Each move depends on full trajectory shape.

ROOT CAUSE: (1) diagnosis over-attributed the g<6 drop to reliability-shrink — only ~10% shrunk; the rest
is forward-model age/tenure (correct aging). (2) _swt is a GLOBAL recency lever, not a thin-season lever;
prorating it perturbs every prior season for every Y=2026 valuation -> large bidirectional trajectory-
dependent moves.

RECOMMENDATION (HOLD): (A) re-diagnose FIRST — decompose the g<6 drop into age/tenure vs level vs
exposure/shrink channels; likely most of the established-thin drop is correct aging (smaller real artifact
than assumed); target specific players Luke flags. (B) if a genuine artifact remains it's the ~10% true-
thin-CAREER cases (exp<14: rookies/long-absence) — a controlled lever prorates decay ONLY in the
exposure/shrink term and ONLY when exp<LEVEL_RAMP, leaving _lvl_wt on original _swt (kills the on-pace
over-correction); small reach, doesn't explain the broad drop, so (A) first.

SEPARABILITY: M1+v7 bake fully separable + unaffected; inert-at-f=1 confirmed. Can proceed on read-merits.
