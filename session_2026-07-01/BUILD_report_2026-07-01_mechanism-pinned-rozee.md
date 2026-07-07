# BUILD — current-season drop: MECHANISM PINNED (Rozee anchor) — NOTHING BAKED
Head `8aed420a` unchanged. Diagnostic only. No fix design (per directive).

## PINNED MECHANISM (overturns BOTH prior diagnoses)
The dominant driver is the **exposure-feature / recency-decay channel**, NOT the level and NOT aging:
- When the clock advances to as-of-2026, the strong prior season (2025) **recency-decays** (weight 1 → 0.72) and the **exposure feature** (`_exposure` = recency-weighted reliable game-count, a direct input to the forward model) **drops** — with no *completed* current season to replace it. The model turns that lower exposure feature (+1 tenure/age) into a lower forward valuation.
- It is **largest for YOUNG players** (−48% vs −26% old) — **inverted vs aging** — because their exposure feature collapses proportionally most (least cumulative buffer). This kills the "correct aging" diagnosis.
- It is **NOT the level** (`_lvl_wt` barely moves; the thin 2026 is size-discounted to ~10% weight) and **NOT the reliability-shrink multiplier** (saturated for 90%, overturned last turn).
- Root: the **decay asymmetry** (2025 fully one-year-decayed while 2026 is only ~60% elapsed) — but it bites through the **exposure FEATURE + the model's response**, not the shrink multiplier or the weighted level. That is why the whole-`_swt` proration under-corrected.

## PART 1 — ROZEE (`connor-rozee`, Luke: underpriced) channel breakdown
Trajectory: 2021 21g/73, 2022 22g/93, 2023 25g/106, 2024 23g/97, 2025 21g/105, **2026 2g/80**. Baseline `ev` 2025=**3874** → 2026=**2679** (−31%).
| channel | Δ | share |
|---|---|---|
| (a) age/tenure + prior-decay + exposure-feature drop | **−827 (−21%)** | dominant |
| (b) level pull of the 2g/80 2026 | −368 (−9%) | secondary |
| (c) reliability-shrink | **0** (exposure 71→53, both ≫ `LEVEL_RAMP`=14; shrink stays 1.00) | none |
| (d) residual | 0 (a+b = total by construction) | — |
- `_lvl_wt` 2025=**96.6** → 2026=**96.0** — the level barely moves; the 2-game 2026 gets only **4%** of the recency-weighted level weight. So the drop is NOT the thin sample redefining his level.
- **Counterfactual** (2 games don't redefine his 105 level → drop the 2026 level pull) = **3047** → candidate artifact from the thin season = **+368**. But his larger loss is the (a) channel (−827): a proven peak player shedding 21% simply because a year advanced (2025 decayed, exposure feature 71→53) with a thin current season.

## PART 2 — cross-cohort channel decomposition (the decisive uniform-vs-varying test)
g<6 population (2025 ≥10g, 2026 1–5g), bucketed by years-since-debut:
| bucket | n | d_age% | d_level% | total% |
|---|---|---|---|---|
| young (2–4) | 14 | **−48** | +5 | −43 |
| mid (5–7) | 12 | **−31** | +1 | −30 |
| old (8+) | 36 | **−26** | +5 | −21 |
- **d_age is cohort-VARYING and INVERTED vs aging** — young players (−48%) drop most, old (−26%) least. Aging would do the opposite. So the dominant channel is the recency-decay/exposure-feature dynamics + tenure, NOT aging.
- **d_level is UNIFORM but tiny and slightly POSITIVE (+1 to +5%)** — the level channel is not the driver in any cohort.
- The total drop is a **young > old gradient** (−43% → −21%), not strictly uniform; it *affects* every cohort (hence "uniform-looking"), but magnitude scales with how thin the player's cumulative exposure is.

## PART 3 — hypothesis test (thin-below-par level drag): FALSIFIED
- (a) `avg_2026 − avg_2025` for the g<6 pop: mean **−4.7**, median **−1.4**, %below = 56% (near coin-flip). Thin 2026 rates are NOT strongly below the prior level.
- (b) 2026 weight-fraction in `_lvl_wt`: mean **12%**, median **9%** — the thin 2026 is ALREADY size-discounted (games×recency weighting). It does NOT over-weight a 2-game season.
→ A thin, below-par recent sample redefining the level is **not** the mechanism.

## PART 4 — M1+v7 × Rozee (bake safety)
M1+v7: 2025 3874→**3831** (barely compresses his 2025 — it's an earned established level, not a speculative riser peak), 2026 2679→**2460** (**−8%**). So M1+v7 **slightly compounds** Rozee's underpricing at 2026 (does not help it). Small but worth noting: baking M1+v7 nudges an already-underpriced proven star down ~8% further at the current season.

## WHY THE PRIOR (whole-`_swt`) PRORATION UNDER-CORRECTED (reconciliation)
The proration raised the exposure feature (2025 weight 0.72→0.82), which is the right target — but (i) it only partially restored exposure (Rozee 53→~60, still below the as-of-2025 71), (ii) for high-exposure established players the exposure feature sits in a **flat model region** (so raising it did ~nothing — Liberatore +0%), (iii) it also perturbed `_lvl_wt`, causing the on-pace side-effects, and (iv) it can't undo +1 age/tenure. Right target (decay asymmetry), wrong lever.

## IMPLICATION (pointing only — NO design per directive)
The lever should act on the **`_exposure` decay clock for the in-progress season** (don't fully decay the prior season while the current one is incomplete), scoped to where the model is actually sensitive (younger / lower-exposure players), and **kept out of `_lvl_wt`** (that channel is not the problem and moving it caused the on-pace collateral). Whether Rozee's (a)-channel loss is fully an artifact vs partly correct is a read call — but the young > old, inverted-vs-aging gradient is strong evidence the exposure/decay dynamics over-penalise. Your reads + this pinned mechanism decide the lever. Nothing baked.
