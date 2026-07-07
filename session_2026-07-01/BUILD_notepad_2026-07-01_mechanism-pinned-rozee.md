# BUILD notepad — 2026-07-01 — current-season drop MECHANISM PINNED (Rozee anchor)

Head 8aed420a unchanged, diagnostic only, no fix design.

PINNED MECHANISM (overturns BOTH prior diagnoses — level-drag AND correct-aging):
The dominant driver is the EXPOSURE-FEATURE / recency-decay channel. As-of-2026 the strong 2025 season
recency-decays (weight 1->0.72) and the exposure feature (_exposure = recency-wtd reliable game-count, a
direct forward-model input) drops, with no completed current season to replace it -> model reads lower
exposure + (+1 tenure/age) -> lower value. LARGEST for YOUNG players (-48% vs -26% old) = INVERTED vs aging
(kills the aging diagnosis). NOT the level (_lvl_wt barely moves; thin 2026 size-discounted ~10% weight),
NOT the shrink multiplier (saturated 90%). Root = decay asymmetry (2025 fully 1yr-decayed while 2026 ~60%
elapsed) biting through the exposure FEATURE + model response.

PART 1 Rozee (underpriced): traj ...2024 23g/97, 2025 21g/105, 2026 2g/80. ev 2025=3874 -> 2026=2679 (-31%).
  (a) age/tenure+prior-decay+exposure-feature: -827 (-21%) DOMINANT
  (b) level pull of 2g/80: -368 (-9%) secondary
  (c) reliability-shrink: 0 (exposure 71->53, both >>14, shrink 1.00)
  _lvl_wt 96.6->96.0 (barely moves); 2026 gets only 4% level weight.
  Counterfactual (discount 2g level) = 3047; artifact from thin season = +368. Bigger loss is (a).

PART 2 cross-cohort (decisive): d_age young -48% / mid -31% / old -26% = COHORT-VARYING + INVERTED vs aging.
  d_level UNIFORM but tiny+POSITIVE (+1 to +5%). Total gradient young -43% -> old -21%, NOT strictly uniform;
  affects every cohort (looks uniform) but magnitude scales with thin cumulative exposure.

PART 3 hypothesis test (thin-below-par level drag): FALSIFIED. avg26-avg25 mean -4.7/median -1.4/56% below
  (near coin-flip). 2026 weight-fraction in _lvl_wt mean 12%/median 9% -> thin 2026 ALREADY size-discounted,
  does NOT over-weight. Level is not the mechanism.

PART 4 M1+v7 x Rozee (bake safety): 2025 3874->3831 (barely compresses earned level), 2026 2679->2460 (-8%).
  M1+v7 slightly COMPOUNDS Rozee underpricing at 2026 (doesn't help). Flag for bake.

WHY the whole-_swt proration under-corrected: right target (exposure/decay asymmetry) wrong lever — (i) only
partially restored exposure (53->60, still < as-of-25 71), (ii) high-exposure players sit in a FLAT model
region for exposure (Liberatore +0%), (iii) also perturbed _lvl_wt (on-pace side-effects), (iv) can't undo
+1 age/tenure.

IMPLICATION (pointing only, no design): lever should act on the _exposure decay clock for the in-progress
season (don't fully decay prior season while current incomplete), scoped to sensitive younger/low-exposure
players, kept OUT of _lvl_wt. Whether Rozee's (a) loss is fully artifact vs partly correct is a read call;
the young>old inverted-vs-aging gradient strongly implies over-penalisation. Reads + pinned mechanism decide
the lever. Nothing baked.
