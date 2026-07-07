# DISTRIBUTION PRICING (U21-4) — PROPOSAL (cont.23, 2026-06-23)

**Plain-English anchor (the whole thing in one sentence):** price every player by the *range* of careers that
similar players actually had — let strong early form pull a kid toward the comparables who made it, let sustained
underperformance pull him toward the ones who didn't (more so the longer it persists), and lean on pedigree only
where the data runs thin. Everything below is machinery serving that sentence.
**Starter code (runs today):** `forward_valuation/distribution_pricing_prototype.py` — the working quantile-band core
+ a 6-item TODO list to make it whole. **Calibration infra:** `forward_valuation/walk_forward_harness.py`.


## The problem this fixes (Luke's per-player audit of the β=0.85 floor)
The engine prices a POINT ESTIMATE (`peak_est` = v4's conditional *mean* forward peak) and props it with a FLAT
pedigree floor (`β·PVC[pick]`, tenure-decayed). Neither prices VARIANCE or TRAJECTORY, so:
- **Ceilings compressed.** Willem (pick-1 MID, 86.4 avg as an 18yo — top ~1-2% of debuts) projects only 101.6,
  because a mean regresses a thin sample toward the prior and cannot extrapolate a star. The signal "elite debut +
  top pedigree → star" lives in the *upside tail*, which a mean discards.
- **Floors prop the stalled, uniformly.** Clark (pick-8 MID averaging 41 — *half* of replacement — three years in)
  floored at 800; Zane (pick-4, ~37 avg) at 1372. The floor is pick-based and decays by *seasons elapsed*, never by
  *how far the player is from his mark*. All underperformance is treated as equal.
- **Not-playing protects value.** Unplayed pedigree (Patterson 1821, Annable 1792) is retained in full while
  playing-well caps you, because the floor only engages once you play.

## EMPIRICAL VALIDATION (cont.23 — ran the data)
**The year-1 signal is real (early-pick MIDs, pick≤12, debut 2007-2020, by year-1 avg → eventual best-3 peak):**
- yr1 75-85: n=11, mean peak 109, **0 busts**, 7/11 stars (≥105). A strong debut from a top pick essentially never fails.
- yr1 60-75: n=28, mean peak 102, 15/28 stars. yr1 <60: n=14, mean 81, 9 sub-90 (weak debuts mostly wash, 3 late bloomers).
- yr1 85+ (Willem's bucket): **n=2** — Sam Walsh 86.9→111.8 (star), Rhys Palmer 87.4→78.3 (bust). THE sparsity, concrete:
  at his exact level the data is 1-for-2, so we BORROW from the flawless 75-85 bucket below + the pedigree prior.
- 2020 verification: top-12 year-1 — Thilthorpe 60.5 (highest, a KFWD), everyone else 42-54, five didn't play. A weak draft
  DID show by year-1; cohort duly cratered to 0.54 by yr6. ⇒ year-1 form is signal; condition the band on it, don't standardise.
**Band prototype (quantile GBR, q10/30/50/70/90 of forward peak — SHAPES valid, absolute E[v] NOT yet calibrated):**
- Willem 86·97·102·108·**116** (banked floor + star tail) · Clark 52·57·62·75·85 (collapsed) · Zane 42·53·61·65·80
  (collapsed < Clark; E[v] 248 > Clark 148 — the gap×time ordering falls out of the data) · Sheezel/Daicos/Bont
  narrow elite bands (107-126). PROVEN = narrow band ⇒ E[v] ≈ production automatically.
**Implications locked:** (a) #2 cohorts take their own path off year-1 form, no standardising. (b) #4 build WHOLE —
narrow bands make proven players ≈ production for free, so whole≡young-only for them; the crux/risk is SCALE
CALIBRATION (pin proven stars to their real values, e.g. Sheezel→6823 not the uncalibrated 4367). (c) #1 the pedigree
prior is ONE dial doing two jobs: fatten the thin right tail for confirmed young top picks (lift Willem→pedigree) AND
set the residual floor for stallers (keep Clark at ~mid-30s-pick, not the raw 148). Luke's "elite debuts almost always
hit" read is a valid input to how hard it leans. (d) #3 read the BANDS, calibrate the absolute E[v] via the harness.

**Band WIDTH by age (ran the data — refines the intuition):** forward move & SD-of-move by age: 18-20 +22.6/SD16.8 ·
21-23 +10.7/14.8 · 24-26 −0.7/12.2 · 27-29 −10.6/11.4 · 30+ −21.1/13.8. Star-level (105+): young star (20-23)
mean +5 / SD **8.9** (narrow, drifts up — elite-young almost never collapse, the MOST predictable players); old star
(29+) mean −25 / SD **15.1** (WIDE — decline cliff is a lottery). ⇒ (i) old players' LEVEL must fall with age (the
quick prototype failed this — left Bont at 117; should be ~92); (ii) band width is NON-MONOTONIC in age (narrow young-
star, widening into the decline) — which is why FREEHAND quantiles beat a fixed stencil, with guardrails (no quantile
crossing; width-by-age must resemble this table). Sheezel narrow+high = right; Bont wide = right; Bont high = the bug.

**PRIOR FAIRNESS across the pick spectrum (Luke: don't disadvantage a high pick for thin data; don't cherry-pick):**
ONE uniform rule, not a top-of-draft special case. Shrink every player's band toward a pedigree-graded prior IN
PROPORTION TO HOW THIN THAT PLAYER'S OWN LOCAL DATA IS. (a) The quantile model already borrows strength from
neighbours — a thin pick-1 cell is informed by the rich pool of strong-year-1 EARLY picks broadly, same mechanism for
all. (b) A light explicit shrink whose weight is a function of LOCAL DATA COUNT, NOT of pick — a pick-13 with thin
data shrinks exactly as much as a pick-1 with thin data. Pick enters ONLY by setting the prior's LEVEL (pick-1 prior
high, pick-13 lower) = pedigree doing its honest job. ⇒ high pick not disadvantaged (borrows + shrinks to a high
prior), not cherry-picked (uniform rule; pick-dependence is only the legitimate pedigree level).

**TOP-OF-DRAFT BOUNDARY (Luke — picks 1-4 must not be dragged down by only having worse neighbours).** Gradient-
boosted quantile trees DON'T extrapolate: at the top of the draft they can only split on data below pick 1, so they
flatten the top picks toward the worse pool — the same truncation the PVC hit (pick 1's ±4 window has no picks
above it). Reuse the PVC fix: build the pedigree-prior CENTRE and WIDTH for the top picks by TREND extrapolation,
not truncated neighbour-average — `loclin` (weighted local-LINEAR, slope-extrapolated to the boundary) and/or the
parametric `a·k^-b` top (pick 1 = intercept `a`; parametric ≤6, blend to local-linear by ~12). The uniform shrinkage
rule then pulls thin top-pick band estimates toward this trend-extrapolated prior, so picks 1-4 anchor to where the
trend heads, not where the trees flatten them. Effect fades by pick ~5-6 (as in the PVC blend). See pvc_smoother_viz.py.

## The principle (Luke's "distance from the mark", formalised)
**Pedigree is a PRIOR distribution over career outcomes. Demonstrated performance UPDATES that distribution toward
the demonstrated reality, and the size of the update is driven by TWO levers: (1) the MAGNITUDE of the gap from the
prior's expectation, and (2) the PERSISTENCE of that gap — how many seasons of evidence have accumulated against
the prior. Value = E[ v(outcome) ] over the resulting posterior, on the existing convex SCAR scale.**
- Confirming evidence (Willem) keeps the distribution high → with the convex scale, E[v] sits AT or ABOVE the
  pedigree anchor (the upside tail is now paid for).
- Contradicting evidence collapses the distribution toward the bust end — but BY BOTH LEVERS, not just the gap:
  one bad year (a slow starter) barely dents the prior; two flat years (Zane) erode it; three-to-four flat years
  (Clark) let the evidence outweigh the prior almost entirely → concentrate near demonstrated level + a residual
  pedigree floor. So Clark < Zane on BOTH counts (bigger gap AND one more season of contradiction); the prior
  yields to accumulating evidence over time, exactly like a Bayesian posterior sharpening.
- The SCALE of the gap and the TIME it has persisted both drive the update — the two things the flat floor (which
  decays only by raw seasons-elapsed, regardless of whether those seasons confirmed or contradicted) ignores.
Convexity does the asymmetry automatically (a fat right tail is worth more than its mean; a collapsed tail less),
so the SAME quantity delivers both the young-gun premium AND the staller discount — no separate floor, no cvx.
Implementation: tenure T + slope/trajectory + demonstrated level are all features, so the quantile model learns
empirically that a year-3 staller recovers far less than a year-2 one (top-pick stallers are data-thin, so the very
top leans partly on the explicit prior-decay logic above).

## Mechanism
1. **Conditional outcome distribution per player.** Train quantile models (HistGBR / GBR quantile loss) at
   q ∈ {.1,.25,.5,.75,.9} on the SAME forward-peak target + features as v4 (effpk/pedigree, position, tenure T,
   games, demonstrated b1/b2/recent, **slope/trajectory**, age). The data itself then encodes each intersection:
   "pick≤5 MID with an 85+ year-1" → high median, fat right tail; "pick-8 MID at 41 in yr3" → low median, closed
   right tail; proven mature → narrow band. The q.5 model ≈ today's v4; the q.1↔q.9 spread IS the uncertainty.
2. **Value over the distribution.** Discretise the quantiles, map each level through the existing convex
   `proj_from_peak → val`, take the expectation: `value = Σ wᵢ · v(levelᵢ)`. This single number REPLACES
   peak_est-point-value, the β·PVC floor, AND cvx.
3. **Pedigree-prior blend for sparse intersections (the Willem guard).** Elite young top picks are rare, so the
   empirical quantiles are thin and noisy there. Blend the empirical conditional distribution with a pedigree-prior
   distribution (pick/position based), weight scaling with sample support. This stops the model under-projecting a
   confirmed young star just because there are few historical comparables — pedigree carries weight precisely while
   performance is *confirming* it, and yields when performance *contradicts* it.
4. **Tenure/age handled by the band, not a gate.** The distribution NARROWS as evidence accrues (tenure is a
   feature; quantile spread shrinks). This SUBSUMES the runway gate and the tenure-decay — a 29yo proven producer
   (Mannagh) gets a narrow band at his level (no phantom option, but no harsh floor cut either), automatically.
5. **Double-count recenter (known ~10% hot risk).** PVC already bakes in average upside; an absolute Jensen
   premium on top double-counts it. Recenter the premium around the COHORT-AVERAGE uncertainty (premium is
   *relative* dispersion vs the cohort, not absolute), and use ceiling-aware (asymmetric) bands. Calibrate so the
   cohort total is conserved.

## What it RETIRES (big simplification)
`peak_est` point-valuation · `β·PVC` floor · `cvx` · runway gate · tenure `decay`. One principled E[v] quantity
replaces five hand-tuned placeholders. (The young-key-pos relative-floor was already slated for removal.)

## Predicted repricing of the audit names (TO VALIDATE once built — not promises)
- **Willem** ↑ back to/above pedigree — confirmed-prior distribution + priced right tail.
- **Clark** ↓ toward a mid-late-30s-pick value — distribution collapsed by the *magnitude* of the gap, prior keeps a residual floor.
- **Zane** ↓ similarly (smaller gap than Clark, so less collapse — the "scale matters" property).
- **Patterson/Annable** hold pedigree as the PRIOR (no contradicting evidence yet) — now principled, not a quirk; updates the moment they play and underperform.
- **Mannagh** priced at his narrow band (~his level), no harsh floor cut; **Bice** rewarded for the improving slope.

## Calibration & build
- Extend the walk-forward harness (already built) to retrain the quantile models per test year (target-window
  capped) → calibrate scale/shrinkage to ≥90% out-of-sample cohort retention, the SAME target. Infra is ready.
- Re-validate per-player (these exact names) AND cohort, every iteration. Then wire into `value()`, rebuild, parity.

## Honest risks / open questions for Luke
1. **Data sparsity at the very top.** Few elite young top picks exist; the conditional tail there leans on the
   pedigree prior (§3). That's defensible (pedigree IS the prior) but means Willem-class values are prior-driven,
   not richly data-driven. Acceptable?
2. **Quantile crossing / stability** on thin slices — may need monotone constraints or a parametric mean+spread
   (band_sd(ρ)) fallback instead of free quantiles. Decide empirically.
3. **Recenter target** — conserve cohort total exactly, or allow a defined prime peak (~110%) per the cont.16
   target language? Your call on the aggregate shape.
   **ANSWERED (Luke, cont.24):** NOT exact conservation — a TRAJECTORY. ~100% in YEAR 1 (a little under OK, but NO
   heavy post-draft drop or picks lose meaning vs selling them pre-draft), rising to 110-115% by YEAR 4-5 as the
   elite few earn convex value and the busts get written down. Calibrate SCALE_DIST on the year-1 number; validate
   the climb with a year-4/5 retention check. (Aggregate shape; per-player hotness like Bont is a separate call.)
4. Scope: full E[v] replacement vs a first cut that prices only the young-player band (where it matters most) and
   leaves proven players on production. Recommend full — "make it whole" — but flag the staged option.
