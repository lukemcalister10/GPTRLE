> ⚠️ SUPERSEDED — NEWEST state is cont.26 (2026-06-25). This file is HISTORY (the cont.25 band-redesign build #2). It is NO
> LONGER the authoritative current-state doc. Read `SESSION_SUMMARY_2026-06-25_cont26_predebut_par_redesign.md` (and START_HERE.md)
> FIRST. Its design journey is useful context, but the current direction is the par-centred production redesign, not this.

# SESSION SUMMARY — cont.25 (2026-06-24) — BAND REDESIGN of the distribution model (build #2)
# THIS IS THE AUTHORITATIVE CURRENT-STATE DOC. Read this first, then KICKOFF_PROMPT.md for bootstrap. cont.24's summary
# is still valid for the OLD dist model + DB/roster context but is SUPERSEDED for "what is the current build".

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
> ### >>> AUTHORITATIVE BUILD SPEC (read this first) <<<
> The consolidated build is in **5i (architecture) + 5k + 5l**, mirrored in the KICKOFF banner. Sections 5c-5j record how we
> GOT there and some items were later REVISED — in particular the **demonstrated floor was proposed in 5i but REMOVED in 5k**
> (the band already covers proven vets, so it would only inflate the board). When earlier and later sections disagree, the
> LATER section and the KICKOFF banner win. Final formula:
> `value = brodie x lens x E[v( games-weighted blend of at-draft & current-level bands, age+position-conditioned )]` at per-group
> REPL (-4 fwd / -2 else). Floor protection calibrated to empirical recovery (KEY-position calibrated separately). +25% cap
> tested-not-adopted. Strip from engine: convexity layer, raw-PVC pedestal, relative-floor, age-gate, spike guards.


## 0. ONE-PARAGRAPH ORIENTATION
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
The valuation engine (`rl_model.py`, imported as MA) prices AFL SuperCoach keeper-league players in "SCAR" currency.
On top of it sits the DISTRIBUTION-PRICING model (`forward_valuation/distribution_pricing.py`) — a STANDALONE repricer
(NOTHING wired into value(); hard rule) that prices each player as E[v(outcome)] over a probabilistic BAND of where their
career peak (forward best-3) will land, run through the convex `v_at_peak` value chain. cont.25's work = **build #2, a
REDESIGN of how that band is constructed**. The redesign is BUILT and validated on key players; it is NOT yet run through
the calibration audit (#1) or the walk-forward (#2), and the 805-player before/after is NOT yet produced. Those three are DONE (see 5a/5b). REPL-3 is now LOCKED (5b: dial REPL_DROP=3.0 in dist_redesign.py, pricing-only) and the
805 before/after is issued. The CURRENT live thread is the PEDIGREE-WEIGHTING gap from Luke board review (5c/5d) and the
APPROVED NEXT BUILD = position-specific REPL_DROP + a gently-stepped position-adjusted pedestal floor (5d). Nothing wired
into value(); JS port untouched.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 1. THE REDESIGN — WHAT IT IS (files + architecture)
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
Two new files in `forward_valuation/`, both STANDALONE (import from distribution_pricing.py for the pricing chain):

**conditional_prior.py** — THE BAND (the heart of the redesign).
  A quantile GradientBoostingRegressor (Q = .1/.3/.5/.7/.9; hyperparams **depth=4, min_samples_leaf=25, n_estimators=400**)
  that predicts the DISTRIBUTION of forward best-3 given features:
     `_feat(p,Y)` = [position one-hot (6), log(effpk), games-through-Y, tenure, _lvl_asof(p,Y)]
  where `_lvl_asof(p,Y)` = mean of the player's last up-to-2 qualifying-season (>=6 games) averages at/before Y, else 0.
  Trained on **RESOLVED careers only** (debut <= 2021) — one row per (player, as-of-year Y) from draft year (games 0)
  through their last season; target = resolved forward best-3 from Y (`fwd_best3_from`), with BUSTS folded in as low/0
  targets so the lower tail is honest. `build_cond_prior(cap=2026, resolved_cut=2021)` -> (models, n_rows). `cond_prior_band
  (p, models, Y=None)` -> sorted [p10..p90] band. ~13,226 training rows.
  WHY level+tenure are features (Luke's key insight, see SECTION 2): the model learns the STAGE-APPROPRIATE peak — a Y1
  average ABOVE the Y1 norm lifts the projected peak; the SAME level at high tenure is a plateau and lowers it. It is a
  FREEHAND, per-player, price-the-range model (NOT a linear pedigree stencil); conditioning on level REWEIGHTS the
  comparables exactly as a Bayesian update would (the "Duursma mechanism" — verified, see SECTION 3).

**dist_redesign.py** — THE REPRICER.
  `redesign_value(p, cmodels, scale=None, lens='bal')`:
     - pre-debut (MA.level_now(p) is None) -> MA.value(p) [pedigree path, unchanged — v_at_peak needs a current level].
     - else: band = cp.cond_prior_band(p, cmodels);  ev = scale * sum(dp.WQ * [dp.v_at_peak(p,L) for L in band]);
       *= 0.5 if MA.brodie_sig(p);  return round(ev * MA.lens_tilt(p)).
  `build(cap=2026, resolved_cut=2021)` -> cmodels (RETRAINABLE capped at any year, for the walk-forward).
  REPL_DROP=3.0 dial (env RL_REPL_DROP): redesign_value lowers MA.REPL by this around the v_at_peak pricing (try/finally),
  so the redesign prices at REPL-3 while engine value() stays at REPL-0. 0 = old behaviour. (Set per Luke; will become a
  PER-GROUP dict in the next build: forwards 4, else 2.)
  ⚠️ The functions `own_band`, `reliability`, and the dial `K_REL` REMAIN in this file but are **UNUSED / SUPERSEDED** —
  they were the own-band/reliability BLEND that Luke's insight made obsolete (see SECTION 2). Leave them or delete; not called.

The pricing chain (UNCHANGED, reused from distribution_pricing.py): `v_at_peak(p,L)` prices p as-if forward-peak = L through
the real-age production chain (proven players == value() at their level; old players decline). `dp.WQ` = the 5 integration
weights. The convex VOR value chain (value ~ (level - replacement)^GAMMA, GAMMA=0.85) is KEPT — it is the correct VOR
baseline (Luke confirmed). The redesign changes ONLY the band construction, not the pricing.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 2. THE ARCHITECTURE JOURNEY (why we are where we are — DO NOT re-walk these dead ends)
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
- **OLD dist model (cont.24):** band = raw_band (GBR on _v4_feats) shrunk-toward-prior(symmetric normal) by evidence, then
  RELOCATED up to `band_anchor = max(peak_est, recent_best2, youth=level_now+age_move)`. Problems found in cont.25:
  (a) over-projected young players (Caminiti 1394 — peak_est read his form DIP as "bounce back AND exceed");
  (b) JUMPY (the max-of-anchors discontinuously switches -> Rowell 5865->2492->6066 in the walk-forward);
  (c) the prior (symmetric normal, built on INCOMPLETE careers) was miscalibrated low with bad tails.
- **Build #2 first attempt:** conditional prior (pedigree+opportunity) + OWN-band (recency level) + reliability BLEND
  (band = w*own + (1-w)*prior). **This was structurally WRONG** — Luke caught it: it blended a YEAR-1 LEVEL (own = ~71)
  against a CAREER-PEAK projection (prior = ~89) as if they were the same quantity, dragging EVERY young player down
  (every young player sits below their eventual peak). "71 for a first-year defender is not thin" — it is neither a weak
  sample nor a weak result. DATA: median Y1 average for a high-pick GEN_DEF = **55**, MID = 63; so 71 in Y1 is ABOVE the
  norm and should push the peak projection UP.
- **THE FIX (current):** condition the prior on recency-weighted LEVEL + tenure (Luke's "career prior responds to how Y1
  performance behaves vs the Y1 expectation"). Then DROP the own-band/blend entirely — the single level-conditioned prior
  IS the projection. Verified: pick-10 GEN_DEF averaging 71 projects peak p50 **97 at tenure 1** but **80 at tenure 5**;
  Y1 averages of 50/71/85 project peaks 80/97/98. It also fixed the over-projectors (Caminiti tenure-4 plateau at 55 ->
  projects 61, the bounce-back gone) WITHOUT re-breaking anyone.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 3. KEY LEARNINGS / DECISIONS (cont.25) — the knowledge a new chat needs
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
- **The reweighting works (the "Duursma mechanism"), VERIFIED:** a pick-1 MID's band as Y1 performance rises — lower tail
  (busts) lifts 62 -> 98 as Y1 goes 55 -> 95, band narrows + shifts up. i.e. the high-pick "mid busts" carry less weight
  and the 85+ comps carry more (borrowing from neighbours via GBR smoothing). Willem Duursma (pick-1 MID, Y1 86) -> peak
  p50 110 -> redesign value 3418, ABOVE his PVC 3000. So an above-norm high pick IS valued above his draft slot.
- **The prior errs low PERVASIVELY (all positions) — ROOT CAUSE = CENSORING.** Out-of-sample, like-for-like, the OLD
  build_prior centre sat 3-11 pts below the realized MEAN for EVERY position, because it trained on the whole pool incl.
  still-rising INCOMPLETE careers (the downweighting fix had been applied to the quantile band but never to build_prior).
  FIXED by training the conditional prior on RESOLVED careers with actual quantiles. (NOTE: my first "GEN_DEF errs low"
  claim was PARTLY cherry-picked — I compared the prior MEAN to the realized MEDIAN on a skewed distribution; the honest
  story is the pervasive censoring bias, not a GEN_DEF quirk. Lesson: compare like-for-like, audit all positions.)
- **COVID-2020 did NOT depress SuperCoach scores** (SuperCoach is scaled/standardised — 3300 points/match; shorter 2020
  quarters hit AFL Fantasy/raw, not SuperCoach). My "COVID artifact" explanation for the 2019-2021 over-projection was
  WRONG. The real reason: TEST-SET CENSORING — 2019-2021 cohorts aren't resolved (a 2021 debutant is ~5 yrs in, pre-peak),
  so their best-3-through-2026 understates their eventual peak. The VALID calibration read is the RESOLVED **2015-2017**
  window (aggregate coverage 11/29/48/65/87 ~ ideal 10/30/50/70/90 -> prior is calibrated + uniform across positions).
- **Farrow (the long worked example):** GEN_DEF pick 10, Y1 average 71 (above the 55 norm). His MEDIAN outcome (95-97) is
  worth ~1631 = pick-9 value, ABOVE his pick-10 PVC (1482). So the model correctly rewards an above-replacement defender.
  His overall E[v] = 1342 (~9% under his pick) is dragged only by his below-replacement DOWNSIDE outcomes (a 70 prices ~82).
  => the "positional haircut" was OVERSTATED by me; at the median it's a good pick-10 return.
- **The VALUE CHAIN is VOR (value ~ (level - replacement)^0.85)** -> near/below replacement prices NEAR-ZERO (a 70-avg and a
  52-avg GEN_DEF both ~80; v_at_peak GEN_DEF: 72->88, 78->182, 82->359, 90->1015, 97->~1700). This is the only genuine
  remaining issue ("Q2"): in a 736-deep keeper league a serviceable 70-avg defender / 72-avg forward is worth more than the
  floor the chain gives. **TWO LEVERS, BOTH PARKED (Luke: "back pocket, use as levers down the line IF NEEDED — do NOT apply
  yet"):** Q1 = is GEN_DEF replacement (78.3) the marginal STARTER vs the marginal ACQUIRABLE player (~60-65) in a 736-deep
  league?  Q2 = should value decay GRADUALLY below replacement (70 > 60 > 52) instead of flooring flat? DO NOT implement
  either without Luke's explicit go.
- **Key forwards are point-inefficient (a real, intended result):** median career best-3 for a top-15 KEY_FWD = **64**
  (n=53). So a high key-fwd pick is a LOTTERY TICKET — Duff-Tytler (pick 4, Y1 50) projects median 72 -> pick-57 value, but
  his upside (p90 99 -> pick-2 value) pulls E[v] to 1014 -> pick-16 value. i.e. blind-to-roster, the model says a top-5
  key-fwd returns ~pick-16 SuperCoach POINTS (correct — key fwds score less); roster need / scouting conviction justify
  taking him earlier. Not a bug.
- **Proven players land ~ value() naturally** (the prior conditions on their high level): Bontempelli EXACT (2961). RESIDUAL:
  Sheezel/Daicos ~8% under value() (prior_p50 113/116 slightly below their peak_est) — minor, tune later if it matters.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 4. CURRENT RESULTS (value() / OLD dist / REDESIGN) — the before/after preview
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
  Sheezel     MID     pk3   6823 / 6881 / 6266     Bontempelli MID  pk4   2961 / 3089 / 2961 (exact)
  Daicos      MID     pk4   6543 / 6517 / 6042     Serong      MID  pk8   3419 / 3725 / 3431
  Rowell      MID     pk1   3045 / 4037 / 2962     Sam Darcy   KFWD pk2   3474 / 3987 / 4397 (breakout read)
  Duursma     MID     pk1    ...  /  ... / 3418 (> PVC 3000)
  Farrow      GEN_DEF pk10  1584 / 1282 / 1342 (was a BROKEN 577 pre-fix — the level-conditioning fixed it)
  Duff-Tytler KFWD    pk4   2076 /  897 / 1014 (LIFTED — was crushed by the old lower-tail)
  Caminiti    KFWD    pk94  1098 / 1394 /  210 (over-projection corrected — tenure-4 plateau)
  Phillipou   MID     pk10  1641 / 2159 /  241 (over-projection corrected)
  Berry       MID     pk29  2741 / 3128 / 2035 (13-game breakout tempered, not extreme)
  Dowling     GENFWD  pk43   145 / 1412 /  403 (stale thin sample no longer over-projected)

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 5a. #1 + #2 DONE (2026-06-24) — RESULTS
**#1 CALIBRATION AUDIT (level-conditioned prior) — PASSED.** Out-of-sample (train debut<=2014, test resolved 2015-2017),
aggregate coverage 13/29/48/68/88 ~ ideal 10/30/50/70/90. By position reasonable (p50 40-56; MID slightly high, GEN_DEF
slightly low, forwards p90 a touch narrow, RUC noisy/small-n). HOT-Y1 OVERSHOOT CHECK: players with above-norm debut seasons
sit at 47% below p50 (vs 49% cool) — conditioning on level does NOT overshoot a strong Y1. Prior is honest.

**#2 WALK-FORWARD (redesign swapped in) — built into build_dist_walkforward.py (cp.build_cond_prior capped + rd.redesign_value;
v4/quantile/relocation dropped; resolved_cut=T-5; output AFL_REDESIGN_walkforward_backtest_2026.xlsx). Ran 2019 + 2021.**
 (a) STABILITY = THE WIN: redesign CALMED the old model's jumpiness. Rowell 3723/2836/2374/3544/3865/4722/3110 (range
     2374-4722) vs OLD 5865/2492/6066 (range 2492-6066); smooth trajectories (Jackson 1364->6438 monotone, Serong clean
     peak-then-decline, McAsey monotone bust). Genuine form moves still move (Ash breakout, Stephens collapse); no whipsaw.
     => level-conditioning did NOT reintroduce reactivity.
 (b) COHORT LEVEL = THE OPEN DECISION: redesign cohort totals are SYSTEMATICALLY ~13-16% BELOW the old model: 2019
     87/82/80/86/95/94/77, 2021 83/86/92/99/96 (yr1 ~83-87% vs old ~98% vs Luke target 103-106%; rises to ~95-99% by yr4-5).
     CAUSE: dropping the peak_est-relocation (which lifted the old model ~15%) + the conditional prior conditioning on
     players' MODEST actual Y1 production. At MATURITY (yr4-5) redesign ~95-99% ~ the cohorts' honest realized value; the
     YEAR-1 gap is the redesign being conservative (honest conditioning) vs the old model's relocation inflation + Luke's
     benefit-of-doubt target. NOTE a global scale would BREAK proven players (push Bont above value()), so any lift must be
     YOUNG-END-SPECIFIC (a gentle controlled benefit-of-doubt term — a tamed version of what the relocation did, WITHOUT the
     individual over-projection that broke Caminiti). DECISION FOR LUKE: keep the honest-conservative level, or add a young-end lift toward target?

## 5. PENDING NEXT STEPS — STRICT ORDER (this is exactly where to resume)
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
**#1 — DONE (passed, see 5a). #2 — DONE (stability win + the cohort-level decision, see 5a).**
**#3 — 805 BEFORE/AFTER DONE.** File AFL_REDESIGN_805_before_after_REPL3.xlsx (Board / By position / Movers tabs, 2593 formulas, recalc 0 errors; data _board805_repl3.json). Board totals: redesign-3 = 108% of PVC (~ old dist 109%; REPL-3 lifted from ~90%), 124% of value(). BY-POSITION STANDOUT: RUC redesign = 254% of PVC and 137% of value() (55 rucks, sumPVC 25k vs sumRedesign 64k) — rucks are late-drafted but high-scoring so they massively out-return draft capital; PRE-EXISTING (old dist rucks 265% PVC, value() 186%), amplified by the redesign. The dubious-rucks review item — flag for Luke (RUCK CONVEXITY may be a separate lever). Other positions red/value 108-137%; red/PVC varies (GEN_FWD 70%, MID 125%) since PVC is position-blind. Top risers vs value(): Tom Green 2129->3955, Nic Martin 1211->3499, Mark Keane, Tom McCarthy (players value() under-rates, often missed-year/peak_est cases).
**#4 (NEXT, if Luke wants): review the 805 — esp. the RUC over-weight + young-breakout bullishness — then value-chain Q2 lower-tail if needed.**
[original #1 detail retained below for reference]
**#1 — CALIBRATION COVERAGE AUDIT on the LEVEL-conditioned prior (DONE).**
  Re-confirm the bands are honest by position now that level is a feature. Method: train on debut<=cut, test on a LATER
  RESOLVED window (e.g. train <=2014, test 2015-2017 — must be RESOLVED, never unresolved cohorts), and for each test
  (player,as-of-year) check what fraction of realized outcomes fall below each predicted quantile; ideal = 10/30/50/70/90,
  BY POSITION. Watch specifically that conditioning on level did NOT make it OVERSHOOT players with a hot Y1 (the thing it
  now rewards). The pedigree-only prior passed this (2015-2017 aggregate 11/29/48/65/87); re-run with the level feature.
  (Code pattern already used in cont.25 — adapt the two-window coverage diagnostic to call the current _feat.)

**#2 — WALK-FORWARD with the REDESIGN swapped in (do SECOND, ~minutes).**
  In `build_dist_walkforward.py`, replace the per-year `dp.build_training`/`fit_quantiles_capped`/`dp.build_prior` +
  `dp.dist_value` with `rd.build(cap=T, resolved_cut=...)` + `rd.redesign_value(p, cmodels)` — KEEP the capped + cohort-
  held-out + records-truncated-to-<=T structure (honest walk-forward; no future leak). Check: (a) cohort yr1 lifts toward
  the 103-106% target (baseline old-model was ~97-98%); (b) PER-PLAYER STABILITY — did level-conditioning CALM the old
  model's jumpiness (old: Rowell 5865->2492->6066, Josh Ward 2047->1032->2395) or REINTRODUCE year-to-year reactivity?
  This is the main risk of the level feature and the walk-forward is exactly where it shows.

**#3 — 805-PLAYER BEFORE/AFTER sheet.** `dist_before_snapshot.json` (already saved: 805 current-dist values keyed by player
  key, with name/pos/pick/pvc/dist_before) = the BEFORE. Compute redesign_value for all 805 = the AFTER. Build an .xlsx
  (xlsx skill: Arial, formulas for totals/ratios, recalc + verify 0 errors) with before/after/delta + movers + by-position.
  Present to Luke. (He wants the FULL pass — #1, #2 — done BEFORE he reviews this; do not show it half-tuned.)

**#4 (only if Luke asks)** — value-chain Q1/Q2 lower-tail (PARKED levers above).
**#5 (only on Luke's EXPLICIT "build/wire")** — wire redesign into value(), then port the out_tilt cut to JS
  `_engine_block_v23.js` ~L79, regenerate the 805, add the by()-guard, re-verify JS/Python parity (was 0/785). HTML board
  is DO-NOT-SHIP until that port. This is a big step and gated on Luke.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════


## 5b. REPL-2 EXPLORATION (2026-06-24) — Luke's structural catch + the fix (DECISION PENDING)
LUKE'S POINT (correct): the redesign cohort total peaking BELOW 100% at maturity (-0 peaked 93%) is illogical — a draft
cohort's stars should make it collectively worth MORE than the draft capital at prime. ROOT = the parked Q1 lever:
replacement (~78 GEN_DEF) is the marginal STARTER, but in a 736-deep league the acquirable replacement is lower, so the
chain under-prices. Lowering REPL is principled (not curve-fitting).
MEASURED (12-cohort true walk-forward, flat REPL drops): -0 peak 93% | -2 yr1 91/97/102/107/107/98 peak 107% | -4 yr1 100
.. peak 124%. => -2 is the sweet spot: real peak >100% at yr4-5, sensible yr1<100% (unproven), gentle decline; -4 overshoots
(yr1 100%, and young players' redesign exceeds their own pedigree). NOT zero-sum (widens level-repl for all; % lift biggest
near replacement, ABSOLUTE lift biggest for stars — Sheezel +318 vs Caminiti +80 at -2, so cohort total lift is star-driven).
ANCHOR PRESERVED: value() uses REPL too, so both move together — Bont redesign stays == value() exactly (2961->3096 at -2).
Mechanism for young players: lowering REPL doesn't touch their (sub-replacement) production, but their PROJECTED PEAK band
clears replacement by more -> redesign lifts (Farrow 1342->1556 at -2, still under his 1584 pedigree => clean).
FULL-HISTORY SHAPE (2003-2025, FIXED-prior maturation view under -2, file AFL_REDESIGN_maturation_REPL2_2003-2025.xlsx):
mean arc 102/110/115/119(peak yr4)/117/109/97/84/69/57/43/35 — logical rise-peak-decline across 23 cohorts. CAVEAT: fixed-prior
is in-sample for <=2021 so levels run ~10pts hot; HONEST levels = the OOS walk-forward (yr1 91 / peak 107). 2003 starts yr2
(yr1=2004 predates SC scoring); missing yr1 = minor games-count understatement for that one cohort, no bug.
*** LUKE LOCKED REPL-3. *** Dial REPL_DROP=3.0 (env RL_REPL_DROP) in dist_redesign.py, applied to MA.REPL around the
v_at_peak pricing in redesign_value ONLY (engine value() + Sharman/board anchors UNTOUCHED; -3 moves to the engine when the
redesign is wired in at #5). REPL-3 OOS true walk-forward (2009-2025): yr1 94 / PEAK 113% (yr5) / decline (logical arc).
PER-PLAYER CHECKS @ -3 PASSED: anchor holds (Bont redesign==value@-3 EXACT 3163; Serong tight 3845~3836); the cont.25
over-projection fixes SURVIVE (Caminiti 337, Phillipou 362 — still firmly low vs the old 1394/2159); top guns Sheezel/Daicos
~7-8% under value@-3 (pre-existing prior-p50 residual, NOT introduced by -3). TWO THINGS TO WATCH at -3: (1) above-norm young
players tip just ABOVE their pedigree floor (Farrow redesign 1673 > pedigree 1584, +6% — the wrinkle, milder than -4);
(2) the redesign is BULLISH on young breakouts vs value() (Sam Darcy 4922 vs value@-3 3998; Dowling 613) — the prior peak
projection running ahead of value(). Books: AFL_REDESIGN_truewalkforward_REPL2/3/4_2009-2025.xlsx + maturation_REPL2_2003-2025.xlsx.



## 5c. LUKE BOARD REVIEW (2026-06-24) — the PEDIGREE-WEIGHTING gap (next design step)
Luke flagged ~20 too-high + ~25 too-low players on the 805 sheet. Pulling gfut/pick/age/level/value/redesign reveals ONE
dominant commonality: the redesign ties value to PROJECTED PRODUCTION and UNDER-WEIGHTS DRAFT PEDIGREE relative to value().
 - TOO HIGH = almost all LATE picks producing decently (Nic Martin pk94 lvl97 red 3499 x2.9; Tylar Young pk69 x7.4; Ryan
   Maric pk60 x6.3; Tom Blamires pk94 x3.8; + the developing RUCKS — McAndrew/Madden/Conway/Emmett — high-scoring late picks).
   value() floors them low on their weak pedigree; the redesign floats them up on production.
 - TOO LOW = almost all EARLY picks who are YOUNG + low current level, ESP. KEY position (Gibcus pk9 KEY_DEF lvl54 x0.29;
   Faull pk14 KEY_FWD lvl39 x0.30; Tauru pk10 x0.39; Walter pk3 x0.46; Read pk9 x0.41; Uwland pk2 x0.34). The redesign marks
   them to weak current production (and key position scores low in the VOR chain); value() holds them up on pedigree.
 - => the redesign COMPRESSES the pick-value signal (late picks up, early picks down). ROOT: killing the peak_est-relocation
   to stop over-projection ALSO removed the pedigree FLOOR — the conditional prior conditions ON pedigree but nothing FLOORS
   a played player at it.
PLAYED-vs-UNPLAYED INVERSION (confirmed, the sharpest symptom): Cameron Nairn (GEN_FWD pk20, PLAYED a weak yr1 lvl41) -> red
424, BELOW unplayed lower picks Tai Hayes (pk44, red=value=427) and Tobyn Murray (pk40, red 476). The instant a player debuts,
the redesign drops the pedigree anchor (unplayed -> value()/pedigree; played -> production projection), so a poor debut craters
you below an untested lower pick.
PROPOSED FIX (next step, NOT yet built): restore a PEDESTAL FLOOR (the cont.21 concept) -> redesign = max(production-projection,
beta * pedigree), beta~0.85. Lifts the young high-picks + fixes the inversion; does NOT re-inflate late-pick producers (their
production already exceeds pedigree so the floor doesn't bind) and is STABLE (a floor, not the jumpy relocation). Floor REFERENCE
(beta*PVC vs beta*value() pedigree-component) + beta to be set as dials. RELATED-BUT-SEPARATE threads: rucks over-weighted /
key-position young crushed = the position-VOR (RUCK CONVEXITY lever); aging elite (J.Cameron 33, Gawn 35, Bont 31) age-discounted
= the dynasty win-now delta (separate). DARCY is already high (red 4922) yet Luke wants higher — a strong personal read, not the pattern.
NOTE: redesign keys position on MA.gfut (future group) for the prior one-hot AND v_at_peak pricing; bnow (current) + effpk (draft) also used.

## 6. FILES & ARTIFACTS
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
  forward_valuation/conditional_prior.py    — component 1, the level-conditioned band (run it standalone to see VALIDATION 1/2).
  forward_valuation/dist_redesign.py        — redesign_value + build(); run standalone for the value()/old_dist/REDESIGN table.
  forward_valuation/distribution_pricing.py — the OLD dist model (import as dp): provides v_at_peak, WQ, recent_best2, build().
  forward_valuation/build_dist_walkforward.py — walk-forward harness (currently runs OLD dist; swap redesign in for #2).
  forward_valuation/build_cohort_book.py    — cohort backtest book builder (groups by DRAFT year; cohort-def fix = group by
                                              DEBUT year (cohort C = first eligible to play C+1) still pending on next edit).
  forward_valuation/dist_harness.py         — cohort-RETENTION walk-forward (totals, not per-player). build_dist_walkforward is the per-player one.
  dist_before_snapshot.json                 — 805 current-dist "before" values (for the #3 before/after).
  /mnt/user-data/outputs/AFL_distribution_pricing_board_2026.xlsx  — 805 OLD-dist board.
  /mnt/user-data/outputs/AFL_cohort_backtest_book_2026.xlsx        — cohort book (value()-as-of, walk-forward).
  /mnt/user-data/outputs/AFL_dist_walkforward_backtest_2026.xlsx   — OLD-dist per-player walk-forward (2017/2019/2021).
  /mnt/user-data/outputs/afl_rl_engine_cont25_CHECKPOINT_2026-06-24.tar.gz — LATEST checkpoint (this IS rl_workspace).

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 7. ENGINE INTERNALS CHEAT-SHEET (rl_model.py = MA) — what the redesign calls
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
  MA.players (805 active board, deduped — USE THIS, not MA.data which gives 746) · MA.data (full historical pool) ·
  MA.GRP[pos] (position->group) · MA.gfut(p) (future position group) · MA.effpk(p) (effective pick) · MA.PVC[pick]
  (pick-value curve, pick1=3000) · MA.level_now(p) (current production level; None pre-debut) · MA.value(p,lens) (shipped
  engine value) · MA.REPL[group] (replacement levels; GEN_DEF=78.3) · MA.age(p) · MA.brodie_sig(p) · MA.lens_tilt(p) ·
  MA.BASE_REF / MA.AGE_REF (the "as-of" year; set both then MA._pe_clear() after ANY scoring mutation or BASE_REF change —
  peak_est cache MUST be cleared) · debut(p) = p['year'] if MSD else p['year']+1.
  Env: GAMMA=0.85 (RL_GAMMA), PICK1=3000 (RL_PICK1), PYTHONHASHSEED=0. Sharman peak sanity = 310. Run from /home/claude/rl_after.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 8. LUKE'S WORKING PREFERENCES (LOCKED — do not drift)
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
  - Player READS + realized outcomes are GROUND TRUTH. Engine VALUES are NOT. Validate PER-PLAYER on absolute values, not
    just cohort averages (the per-player view has caught every structural bug).
  - VERIFY before asserting — run the diagnostic, don't claim a mechanism. Luke has correctly caught: the future leak, the
    cherry-picked prior, the COVID error, the broken own-band blend. Compare like-for-like; audit ALL positions, not the one
    you happened to look at. Own mistakes plainly.
  - SURFACE dials (module header), do NOT bake them. Don't bail after one failed approach. Push back / challenge when the
    data supports it. Hold off building until you've absorbed the WHOLE message.
  - Communication: direct, casual, concise; dislikes verbosity / walls of text / over-formatting.
  - HANDOVER DISCIPLINE (critical): proactively keep handover/kickoff/UNRESOLVED/CHANGELOG/session-summary updated AND SEND
    them (present_files / a checkpoint tarball) in the SAME turn — an update kept only in the working dir is lost if the chat
    ends. Re-verify driver output first thing each session. Checkpoint before a long chat risks timing out.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
## 9. DO-NOT-RE-LITIGATE / STILL-TRUE CARRY-OVERS
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
  - The v_at_peak VOR value chain (GAMMA=0.85) is the agreed baseline — KEEP. The redesign changes only the BAND.
  - Nothing is wired into value() (hard rule until Luke's explicit go). HTML board DO-NOT-SHIP until the out_tilt JS port.
  - establishment-P frozen (P baked at real draft-cohort position; do NOT recompute on SuperCoach position toggle).
  - Roster = 805, manually maintained (MA.players). §9 contamination resolved (0/788 proven). Sharman 310.
  - The value-chain Q1/Q2 levers are PARKED (Luke's explicit "not yet").

## 5d. MORE board-review findings + the FLOOR design (2026-06-24)
- KEANE>BATTLE = NOT a code bug, it's UNCERTAINTY-CONVEXITY. Keane (KEY_DEF lvl77 ~56gms) band p90=96 (v_at_peak 4018);
  Battle (lvl86 ~122gms) band p90=89 (2473). Battle better+more-proven but LOWER ceiling, because the prior conditions on
  GAMES -> Keane (fewer games, same tenure) gets a WIDER band -> convex v_at_peak rewards the fat upper tail -> Keane red 2838
  > Battle 2160. Root: games-vs-tenure mismatch (26yo 6yr but low-games journeyman read as breakout upside). SEPARATE lever
  from pedigree (floor won't fix it) -> candidate: temper the upper tail when recent production is STABLE. LUKE ADD: AGE must
  bound the band as much as games — a 26yo has less growth-runway after 50 games than a 20yo, so the breakout upper tail
  should shrink with absolute age, not just games (the games-only width is weakly evidenced). Fold age into the temper.
- Luke refined position read: GEN_DEF a touch HIGH (Luke Ryan 30yo lvl95 red 1549; aging non-elite over), forwards a touch
  LOW (Jeremy Cameron KFWD under). PROPOSAL (Luke): position-specific REPL_DROP -> base -2, but KEY_FWD+GEN_FWD -4 (lower repl
  lifts forwards; higher repl vs -3 lowers G-Def). Note aging FLAT v_at_peak: Luke Ryan band [82..99] all price ~1283 (age
  dominates, peak-insensitive) -> "elite-aging under / non-elite-aging over" is the age-discount not distinguishing eliteness.
- UWLAND (pk2 GEN_DEF, 1 season lvl44.7 10gms) band [53,74,87,94,102] v_at_peak [0,38,652,1371,2300] -> red 1095, dragged by
  the below-replacement LOW tail; value() 3268 (pk2 pedigree). The young-high-pick-crushed case the floor must fix.
- PEDESTAL FLOOR design (Luke's calls): (1) floor reference = POSITION-ADJUSTED pedigree (the Duff-Tytler KPF-at-pk4 nerf),
  NOT raw PVC[pick] — use effpk-through-position / the pedigree component of value(). (2) GENTLY STEPPED — protection decays
  with the EVIDENCE against pedigree (depth of underperformance x SAMPLE SIZE), so Uwland (drastic but 10 games = weak evidence)
  keeps protection while a 50-game underperformer at the same level gets less. NOT a hard max(production, beta*pedigree).
- NEXT BUILD (proposed, awaiting go): (a) position-specific REPL_DROP dict (fwd -4, else -2); (b) gently-stepped position-
  adjusted pedestal floor; then re-run 805 + spot-check Uwland/Keane/Battle/L.Ryan/J.Cameron/Duff-Tytler. Keane upper-tail temper = later/separate.

## 5e. STRESS-TEST FIND: "value()" = _vpt (point), the board is _v (convex) — and the engine ALREADY caps convexity (2026-06-24)
- Stress test pass: NO REPL leak into value() (value(Bont) pre==post==2961), REPL dict fully restored, deterministic
  (redesign(Bont) twice=3163), edge cases (145 pre-debut + 1 brodie) no crash, full 805 no errors/None/negative,
  build_dist_walkforward.py has NO manual REPL mutation (no double-apply), conditional_prior.py standalone clean. CLEAN except:
- THE FIND: rl_model.py L813 sets p['_vpt']=value(p,'bal') (POINT value); L851 sets p['_v']=proj_value(0) = the CONVEXITY-
  priced "option value under present-level uncertainty", with p['_cvx']=min(_v/_vpt, CVX_CAP=1.25). So **_v = _vpt x convexity
  (capped +25%)**. Sharman: _vpt=302, _cvx=1.0265, _v=310 (the documented anchor 310 is _v, CORRECT — engine untouched, mtime 06-23).
  MY "value()" EVERYWHERE (all diagnostics + the 805 "value()" column) = _vpt (point), NOT the shipped board _v. Across 805:
  median _v-_vpt = 0 (most players _v==_vpt), but 26 players AT the 1.25 cap and ~122 with a >6% premium — ALL YOUNG (capped
  cohort median age 24, range 19-26). So my "value()" UNDERSTATES the board by up to 25% for young/uncertain players.
- INSIGHT 1 (diagnosis REINFORCED, not changed): the redesign is itself a CONVEX valuation, so the apples-to-apples baseline
  is _v (convex), not _vpt (point). For young high-picks (Uwland _vpt 3268 -> _v ~4085; Gibcus/Faull etc.) the board _v is even
  HIGHER than _vpt, so the redesign's "too low" is even starker -> the pedestal floor is MORE justified. Established late-pick
  producers have _cvx~1.0 (_v==_vpt) so those "too high" flags are unchanged. NO flags flip. (Aggregate barely moves: "124% of
  _vpt" ~= "120% of _v" since median premium is 0.)
- INSIGHT 2 (the Keane lever + a floor principle): the engine's option value is ADDITIVE-ONLY and CAPPED — rl_model.py L841
  `clamp(base, pt, pt*CVX_CAP)`: convexity can only ADD (floor = point value) up to +25%, NEVER subtract. The redesign's
  E[v(band)] is UNCAPPED on the upside (Keane's wide band p90=96 -> unbounded premium = the Keane>Battle runaway) AND can go
  BELOW the point value on the downside (Uwland band low-tail p10=53 -> E[v] 1095 < _vpt 3268). So vs the engine the redesign
  (a) over-rewards uncertain veterans' upper tail and (b) over-penalises young players' lower tail. The engine already solved
  BOTH with additive-only + CVX_CAP=1.25. => Keane upper-tail temper should CAP the convex premium like CVX_CAP; and the
  pedestal floor is the redesign's missing "floor at a sensible baseline" (the engine floors option value at _vpt; the redesign
  needs a pedigree floor). These are the SAME structural gap from two sides.
- ACTIONS: (i) documented here + KICKOFF (my "value()" = _vpt; board = _v; compare to _v). (ii) the NEXT 805 regeneration
  (post position-REPL + floor build) will ADD a _v (board) column so Luke reviews against his actual board, not _vpt.
  (iii) folded the CVX_CAP insight into the Keane temper + floor design above. NO code bug; engine untouched.

## 5f. ENGINE-vs-REDESIGN LAYER AUDIT (2026-06-24) — what the engine adds on top of value(), and the double-count risks
WHY THE SPLIT: value() (= p['_vpt']) is the deterministic POINT value. The engine then bolts on a "Phase-2 variance layer"
(rl_model.py L815-852, proj_value) that prices CONVEXITY/option value as a SEPARATE stage -> p['_v']. The redesign has been
built as a replacement for value()'s production model, but it ALSO does the convexity job (E[v(band)]), so the two OVERLAP.

WHAT value() (=_vpt) APPLIES (L644-674): production projection (v4, via player_raw) OR a demonstrated floor, whichever higher;
pedigree PEDESTAL = PVC[ep]*relative*decay as a floor (res=max(production,pedestal)); a young-key-pos RELATIVE-FLOOR
(RUC/KFWD/KDEF, age<=22, year-scaled); BRODIE cut x0.5 (L673); lens tilt. NO survival (removed cont.20), NO out_tilt (removed
cont.21), NO P-gating (P_HOOK=None + PROD_GATE='off' -> establishment-P DEACTIVATED cont.20; the README glossary calling it
"SHIPPED & LIVE" is STALE — fixed). Captaincy + REPL live inside the VOR chain (player_raw/posval), applied once.

WHAT THE ENGINE ADDS ON TOP (the only substantive layer): proj_value(0) -> _v, the option value of PRESENT-LEVEL uncertainty,
with THREE disciplines: (1) CAPPED at CVX_CAP=1.25 (+25% max); (2) ADDITIVE-ONLY (L841/843 clamp(base, pt, pt*1.25) + max(r,pt)
-> never below the point value); (3) AGE-GATED via _upside_w=clamp((31-age)/12,0,1) -> 0.92@20, 0.58@24, 0.42@26, 0.08@30,
0.00@31+ (the upside option fades to zero by ~31). The slider states _vP1/_vP2 (forward) + _vM1/_vM2 (backward) are UI
"board as of year +-N", NOT modifications to the present value.

SCRUTINY (Luke's question — helpful / contradicts / double-counts):
1. CONVEXITY = DOUBLE-COUNT if wired naively (the redesign already prices convexity via the career-peak band; the engine's
   proj_value(0) would stack present-level convexity on top -> uncertain/young players double-charged the option). BUT the
   engine's three disciplines ARE EXACTLY the redesign's two open fixes: cap+age-gate solve the KEANE runaway (uncapped, no
   age bound); additive-only solves the UWLAND crater (band low-tail prices BELOW point; the engine never does). So do NOT
   simply keep both: when wiring in, the redesign's band convexity should INHERIT cap+additive-only+age-gate, and the engine's
   separate proj_value(0) layer is REMOVED for redesigned players (no stacking).
2. BRODIE x0.5 = DOUBLE-COUNT (applied in BOTH value() L673 AND redesign_value). Must fire exactly once when wired in.
3. PEDIGREE PEDESTAL + young-key-pos RELATIVE-FLOOR = OVERLAP with the approved position-adjusted pedestal floor. The redesign's
   floor (position-adjusted, stepped) is the better version and should REPLACE value()'s raw-PVC pedestal + relative-floor, not
   stack on them. (Reconcile the floors: pedigree floor + the additive-only point floor are two flooring ideas to unify.)
4. CAPTAINCY / REPL / VOR base = CONSISTENT (shared chain; applied once). Caveat: redesign prices at REPL-3, value() at REPL-0
   -> when wired in the REPL level must be made consistent (REPL-3 propagates to value(), the documented intent).
5. SPIKE guards (SPIKE_CAP KEY_DEF 0.60, v4_spike_guard) = DIFFERENT handling, not a double-count (the band is trained on
   resolved careers so spike-reversion is implicit; the engine guards it explicitly on the v4 projection).
WIRING CHECKLIST (when Luke says go): redesign convexity adopts cap+additive-only+age-gate; engine proj_value(0) off for
redesigned players; brodie once; redesign pedestal floor replaces value()'s pedestal/relative-floor; REPL level unified.

## 5g. ENGINE-MECHANISM DISPOSITION (2026-06-24) — Luke: band stays the base, incorporate engine parts only where value-adding
FRAMING (Luke): do NOT redesign the band around the engine; incorporate engine mechanisms as ADDITIONS where they add value.
UWLAND calibration (Luke): he IS a touch low now (1095) but must NOT triple. His position-adjusted pedigree floor is high
(~2500+, genuine pk2 GEN_DEF) so full protection ~2.3x him = too much. The gently-stepped floor resolves it by weighing thin
sample (10 games -> weak evidence -> MORE protection) AGAINST depth (44 vs ~55 expectation -> large gap -> LESS protection);
for Uwland these oppose, landing him ~1700-1900 (lifted, not tripled). The dial sets exactly where (tune on the spot-check).
AGE-GATE explained: _upside_w=clamp((31-age)/12,0,1) multiplies the level-uncertainty SPREAD that the option value integrates
over. ~1.0@19-20, 0.58@24, 0.42@26, 0.08@30, 0@31+. Wider spread -> bigger convex premium; at 31+ spread=0 -> no premium.
Logic: young output understates potential (upside option); old output is what it is. This is the Keane age-bounding, already built.

DISPOSITION TABLE (each engine value-mechanism -> fully incorporate / partial / strip; band remains the base):
THE CONVEXITY LAYER (literally on top of value()):
1. Convex premium itself (E[value] over level spread)        -> STRIP engine's version (band already does it; running both
   stacks two convexity prices); keep ours, adopt the 3 guardrails below.
2. +25% cap (CVX_CAP)                                        -> INCORPORATE (partial): bound how far the band E[v] sits above
   its own p50 central estimate -> stops the Keane runaway.
3. Additive-only (floor at point)                            -> INCORPORATE via the pedestal floor: the band's bad low tail
   must not price below a sensible floor -> the Uwland crater fix. Our position-adjusted pedestal floor is this principle.
4. Age-gate (_upside_w, fades to 0 by 31)                    -> INCORPORATE: shrink the band's upside contribution by
   (31-age)/12 -> the Keane fix Luke flagged.
INSIDE value() (what the band replaces):
5. Pedigree pedestal floor (raw PVC x mult)                  -> INCORPORATE improved: our position-adjusted + stepped floor
   replaces the raw-PVC one (raw over-floors a KPF at pk4; Luke prefers position-adjusted).
6. Young key-pos relative-floor                              -> STRIP (subsumed): our pedestal floor covers all positions.
7. Brodie x0.5 cut                                           -> FULLY (already in redesign_value); ensure fires ONCE on wiring.
8. Captaincy premium + REPL (in VOR chain)                   -> FULLY (already in via v_at_peak); only unify the REPL level (-3 vs -0).
9. Demonstrated-level floor (prod_floor)                     -> PARTIAL/monitor: band conditions on level so mostly self-handles;
   check no proven player is under-priced.
10. KEY_DEF spike guards (SPIKE_CAP 0.60, v4_spike_guard)    -> STRIP (band trained on resolved careers captures spike-reversion);
   sanity-check a KEY_DEF off one big year isn't over-projected.
DEACTIVATED (nothing to do): establishment-P (off cont.20), survival (removed), out_tilt (removed).
NET BUILD: keep band as-is + bolt on 4 guardrails (cap, additive-only-via-floor, age-gate, position-adjusted stepped floor),
strip 3 redundancies (engine convex layer, relative-floor, spike guard), inherit the rest. Plus the position-specific REPL_DROP.

## 5h. CORRECTION + STANCE (2026-06-24) — Luke caught me anchoring to the positionless PVC and deferring to the engine
ERROR: I quoted Uwland's floor as ~2500 = raw positionless PVC[2] (=2496), NOT the position-adjusted reference Luke asked for.
CORRECT numbers (our OWN at-draft band, priced at REPL-3):
- Uwland (GEN_DEF pk2): raw PVC[2]=2496, engine value()=3268, but POSITION-ADJUSTED at-draft E[v] = **1849** (band [64,92,94,101,106]);
  beta(0.85)x = 1571. So floored he lifts 1095 -> ~1400-1571 = MODEST, NOT a triple. The tripling fear was the wrong anchor.
- Duff-Tytler (KFWD pk4): raw PVC[4]=2076=engine value(), but POSITION-ADJUSTED at-draft E[v] = **1324** (beta x = 1125) which is
  BELOW his current redesign 1241 -> the floor DOESN'T BIND. Correct: a KFWD at pk4 gets a low floor. Validates position-adjustment.
STANCE CORRECTION (Luke's meta-point, accepted): I was being deferential to the OLD engine — importing its positionless PVC
framing and presenting its convexity guardrails (cap, additive-only, age-gate formula) as "the fix" without scrutiny. The
redesign is the principled base and already does some of this BETTER (it prices the full distribution; it position-conditions).
REVISED approach — implement the IDEAS natively, do NOT copy the engine's crude post-hoc patches; TEST whether each is even needed:
- AGE: add age to the conditional-prior features so the BAND itself narrows with age (Keane: 26yo+few-games gets a narrower band
  than a 20yo) — the redesign-native fix, more principled than bolting on the engine's (31-age)/12 multiplier. Retrain + re-validate.
- FLOOR: position-adjusted (Uwland 1849, not 2496/3268), gently stepped — the numbers show it lifts modestly without over-anchoring.
- CAP / ADDITIVE-ONLY: do NOT adopt wholesale. Additive-only is the engine's LIMITATION (it can't price downside); our band CAN,
  and the stepped floor is the better downside protection. RE-TEST whether a cap is needed AFTER age-conditioning the band — Keane
  may be fixed by age-conditioning alone, making the +25% cap an unnecessary blunt patch. Only borrow if a residual gap remains.
NET: keep the band as the base; fix Keane by AGE-CONDITIONING the band (native) + Uwland by the POSITION-ADJUSTED stepped floor
(native); the engine's guardrails are CONFIRMATION the ideas are sound, not templates to copy. Position-specific REPL_DROP still stands.

## 5i. CONSOLIDATED PLAN + "ONE PLACE" ARCHITECTURE (2026-06-24) — the agreed build, after all of cont.25's discussion
ARCHITECTURE (Luke: as little engine-side as possible, all formulas in ONE place — AGREED, with one caveat):
- The redesign module becomes the SINGLE valuation model: band + floors + age-conditioning + brodie + the VOR pricing it calls.
- rl_model.py reduces to: data load, the shared VOR primitives (v_at_peak / REPL / captaincy chain) the band calls, lens defs,
  and the board/HTML/JS/UI. value() becomes a thin call to the redesign (or is replaced).
- CAVEAT (the one real obstacle): the HTML board's JS recomputes value() live for position toggles. To keep modelling Python-only
  we PRE-COMPUTE the position-toggle states and bake them into the export so the JS just looks up (no JS re-implementation =
  no second copy of the formulas). Decide this when we wire in.

WHAT WE DO (the band stays the base; everything below lives in the redesign module):
1. AGE-CONDITION THE BAND — add age to the conditional-prior features; retrain + re-validate. Native Keane fix (26yo+few-games
   gets a narrower band than a 20yo). Makes the engine's age-gate redundant.
2. POSITION-SPECIFIC REPL_DROP — per-group dict: KEY_FWD + GEN_FWD = -4, ALL ELSE = -2 (confirmed w/ Luke; replaces the locked
   global -3; aggregate will re-shift -> re-check cohort level after).
3. POSITION-ADJUSTED, GENTLY-STEPPED PEDESTAL FLOOR — floor = beta(~0.85) x position-adjusted at-draft E[v] (Uwland 1849 NOT raw
   PVC 2496; KFWD-at-pk4 floors low, e.g. Duff-Tytler 1324 doesn't bind). PROTECTION DECAYS with evidence (qualifying-seasons x
   depth): young high-picks lift (Faull +440, Jed Walter +660) but older underperformers DON'T (Max King 26 must NOT get +1429,
   Lukosius 26 not +1108). Stepping is essential — verified on the KPF cohort. Replaces engine raw-PVC pedestal + relative-floor.
4. DEMONSTRATED-LEVEL FLOOR — value = max(band E[v], demonstrated SCAR). This is the "elite-aging stars under" fix: value()'s
   demo-floor binds for 224 players (Petracca +948, Merrett +883, Dawson +793) because the band/projection regresses a 30yo below
   what he's still scoring. Graduated from "monitor" to INCORPORATE (verify proven vets aren't under-valued without it).
5. BRODIE x0.5 — keep (already in redesign_value), fire ONCE; EXTEND the flag to role-risk thin-sample players like Billy Dowling
   (10 games, redesign 613, brodie currently False) per Luke's read. (Player reads = ground truth; flag the set with Luke.)
6. CAPTAINCY + REPL + LENS — already in the band's VOR chain (ours, kept).
7. +25% CAP — do NOT adopt up front; TEST after age-conditioning whether any runaway remains (likely none -> no cap).

WHAT WE STRIP FROM THE ENGINE (move toward one place):
- proj_value convexity layer (_v) -> band does convexity natively. STRIP.
- value() pedestal (PVC x relative x decay) -> replaced by the position-adjusted stepped floor. STRIP.
- young-key-pos relative-floor -> subsumed by the floor. STRIP.
- age-gate _upside_w -> band age-conditioned natively (and it lives in proj_value, which is removed). STRIP.
- spike guards (SPIKE_CAP, v4_spike_guard) -> band trained on resolved careers handles it; Mac Andrew sanity-checked OK. STRIP.
- already off: establishment-P, survival, out_tilt.
KEEP engine-side (or move into the redesign module): data load, VOR primitives (v_at_peak/REPL/captaincy), lens defs, board/UI.

CONSOLIDATED VALUE FORMULA (one place): value = brodie x lens x max( band E[v(age-conditioned, position-conditioned)],
   stepped position-adjusted pedigree floor, demonstrated-level floor ), priced through the VOR chain at the per-group REPL.

INVESTIGATION EVIDENCE (this session): #2 cap binds at +25% for 26 young players (Josh Lindsay 824->1030 etc.). #4 age-gate:
Duursma +13%@19, Daicos +3%@23, B.Smith +0%@26, Grundy +0%@32. #9 demo-floor binds 224 players. #5 KPF floor lifts the young
high-picks but over-lifts 24-26yo without stepping. #7 Dowling thin-sample over-valued. #10 only Mac Andrew spike, OK at 23.

## 5j. DEMONSTRATED FLOOR — mechanism + correction (2026-06-24)
prod_floor (rl_model.py L323) = value the player at CURRENT level (level_now, ~2-season mean w/ best-2 haircut) THIS season,
then age-decline from there; value()=max(projection, prod_floor). So it stops the model regressing a player BELOW current
output (regression applies next year+). Confirmed: Bontempelli (31, recent 131/119) v4 projection=2477 (already regressed)
but floor holds 2961; Petracca proj 1936 -> floor 2884. Does NOT bind for young ASCENDERS whose projection exceeds current
(Daicos 23: proj 6543 > floor 2993 -> no bind; Gulden no bind). So it only lifts players the projection regresses below current
= mostly proven vets = the legit "elite-aging under" cases.
CORRECTION to 5i: the "224 binds" is OVER-BROAD — it's "recent scoring > v4 projection", legit for PROVEN/stable producers but
would also floor a one-year SPIKE where regression is correct. So in the redesign the demonstrated floor must be EVIDENCE-WEIGHTED
(full hold when the level is backed by multiple qualifying seasons; fades for a one-year spike) — same stepping logic as the
pedestal floor. Not all 224 are under-valued; Luke's "some do, some don't" is correct.

## 5k. BUILD REVISIONS from Luke's scrutiny (2026-06-24) — demo-floor KILLED, scientific floor, capped-player cause
1. DEMONSTRATED FLOOR = REMOVED from the build. Verified the redesign ALREADY holds every proven vet at/above their demo_floor:
   Bont 3163>2961, Petracca 3087>2884, Merrett 2460>2249, Dawson 3013>2667, J.Cameron 1132>939, Sinclair 2788>2543,
   Sicily 1874>1652, Touk Miller 2188>1890, R.Marshall 1784>1294, Gulden 4522>2145. The band's level-conditioning does the job
   the old v4 projection couldn't (it regressed vets; the band doesn't). Incorporating the demo floor would help NONE of these
   (already covered) and only ADD undeserved points to mediocre players = board inflation (Luke's concern, confirmed). The
   "elite KPF feels under" (J.Cameron 1132) is a POSITION issue -> the -4 forward REPL, NOT a demo floor.
2. WHY THE 7 WERE CAPPED: thin-sample high level-uncertainty. Josh Lindsay 1 qual season/12 games -> _cov 0.334 -> wide level
   dist -> premium > +25% clipped. Same for Retschko/Gothard/Conway (1 or 0 seasons, ~10 games). The cap bounds thin-sample
   premiums (= the Keane mechanism).
3. SCIENTIFIC YOUNG-PLAYER PROTECTION (replaces arbitrary beta + stepping): EMPIRICAL recovery. Resolved high-picks (pick<=20)
   weak (<=58 avg) in first 2 seasons: n=87, 38% reached best-3>=78 (Davies-Uniacke 52->111, Callan Ward 51->109, Ed Richards
   54->105; busts Bonar 49->45). => protection level = that empirical recovery rate. IMPLEMENTATION: a GAMES-WEIGHTED BLEND of
   the at-draft (pedigree) band and the current-level band, weight calibrated so the blend reproduces the empirical recovery.
   Self-steps (pedigree weight decays with games, no hand schedule), lives in the band (one place), testable vs resolved
   outcomes. Cuts both ways: thin-sample HIGH-pick (Uwland) pulled UP to pedigree; thin-sample LOW-pick (Dowling) pulled DOWN.
   NOTE: this is a blend of two PEAK-bands (coherent), NOT the earlier incoherent Y1-level-vs-career-peak blend.
4. UWLAND mechanics: ~1849 at draft (position-adjusted), then smooth decay as games accumulate (heavily pedigree-weighted in
   season 1, easing toward production) — NOT a hard lock-until-season-2. Season-1 level = the calibration knob vs the 38% curve.
5. ROLE-RISK cut (#7): the games-weighting handles systematic thin-sample inflation (Dowling 613 comes down via his low pedigree).
   A SEPARATE explicit cut is only for solid-sample/fragile-role players = a player-read (Luke's call). Offer: surface a candidate
   list to flag from, don't infer names from stats.
REVISED CONSOLIDATED FORMULA: value = brodie x lens x E[v( games-weighted blend of at-draft band & current-level band, both
   age+position-conditioned )], priced through the VOR chain at per-group REPL. (No separate pedestal-max, no demo floor — the
   blend IS the floor, calibrated to empirical recovery.) +25% cap tested-not-adopted. Position-specific REPL (-4 fwd/-2 else) stands.

## 5l. KPP-SPECIFIC calibration, Petracca eligibility, Uwland trajectory, candidate list (2026-06-24)
PETRACCA eligibility (Luke right): pos=MID but bnow(current group)=GEN_FWD (forward-eligible THIS season); prod_floor prices off
bnow -> GEN_FWD replacement 70.9 vs MID 80.1, so the forward eligibility LOWERS replacement and props up 2884. MID-only he
compresses. NOTE the redesign uses gfut (=MID for Petracca) not bnow, so redesign and the old prod_floor differ on his position
basis. Position eligibility (DPP) materially moves valuations; the redesign consistently uses gfut.
KPP PROTECTION must be calibrated on KPP DATA with a KPP SUCCESS BAR (Luke right — success looks different for KPPs):
- weak-debut KPP high-picks (pick<=20, <=58 avg first 2 seasons), n=30: reach best-3 >=78 only 23% BUT that's a MID bar
  (a successful KPF peaks ~72-80: Riewoldt 49->92, Henderson 45->80). At a KPP-appropriate bar: >=68 -> 47%, >=72 -> 30%, >=76 -> 27%.
- => calibrate the young-KPP protection on KPP realized VALUE outcomes (VOR, which auto-handles the lower scoring), NOT the
  blended 38% or a mid threshold. Key-position gets its OWN recovery curve in the blend calibration.
UWLAND TRAJECTORY (GEN_DEF pk2, drafted last yr, this season 14/24 @45) under the games-weighted blend (illustrative w=1-games/30):
  draft 1849 -> 2g 1804 -> 6g 1696 -> 10g 1596 -> 14g 1481. The RAW band would crater to ~1085 at 6 games; the blend eases him
  ~20% instead. Demonstrates the mechanic. (Real w from the position-specific recovery curve, not this placeholder.)
CANDIDATE LIST (Dowling-like, band inflates thin-sample/modest-pedigree; redesign>=1.8x value, <=30 games, pick>20): 39 players,
  RUCKS DOMINANT — Nick Bryan RUC pk38 29g value17->redesign762 (44.8x), Samson Ryan 14.4x, Max Heath 13.1x, Oscar Steene,
  Dante Visentini, Liam Reidy, Oliver Hayes-Brown (all RUC), Sandy Brock KDEF 9.5x, ... Billy Dowling GEN_FWD pk43 4.2x (mid-list),
  several KFWD pk94. The games-weighted blend tempers ALL (toward low pedigree); the explicit role-risk cut is Luke's per-player
  call on top (rucks are partly genuine binary-role upside, so don't blanket-cut). Ties to RUC=254%-of-PVC structural over-value.

## 5m. MSD/partial-season mechanism + ruck read (2026-06-24)
NEW BAND FIX (Luke found it): _lvl_asof (the level feature) = mean of qualifying-season (>=6g) avgs with NO games-within-season
weighting; "qualifying" is just >=6 games. So an MSD/partial-first-season pick who plays 8 games @65 gets level=65 at FULL FACE
VALUE (identical to 23 games @65), and their low games-count adds a thin-sample uncertainty premium -> inflated. FIX: games-weight
the level (a 6-8 game season counts less than a full one). Band-internal, one place. ADD to the consolidated build.
THE 3 EXCEPTIONS explained by the two band fixes (nothing new): Anderson (8g@56, band p90=97) + Retschko (8g@66, p90=101) =
the partial-season face-value mechanism -> the games-weighted-level fix. Bice (26, jumped to 82, band 89-101) = age over-projection
(Keane) -> the age-conditioning fix.
RUCK read (Luke: some development premium is legit; can't cherry-pick): NO single clean OK-vs-backup signal. Backups cluster as
OLDER (~26) + STALLED (Hayes-Brown 26, Samson Ryan 26 declining 14->3, Reidy 26 - years in, no role, no high season). OK = young
w/ runway (Edwards 21, Steene 23) OR a flashed ceiling (Moyle 86, McAndrew 87). Cleanest model-usable separator = AGE x TENURE
(long apprenticeship POSITIVE when young, NEGATIVE when 26+ still backup). Age-conditioning captures most (old stalled -> narrower
band). Genuine ambiguities need the eye: Conway (23 injured, model can't tell hurt vs can't-play), McAndrew (27 real breakout).
PRINCIPLE: do NOT have the model pick OK-vs-backup rucks (Luke's read); the fixes cut across-the-board EXCESS (thin-sample face-
value) while TENURE preserves a development premium for long-apprenticeship rucks. Individual role-risk cuts = Luke's per-player call.
UPDATED build add-on: games-weight _lvl_asof (the MSD fix) joins age-conditioning + games-weighted blend + per-group REPL.

## 5n. CLIFF-AVOIDANCE + recency signal (Conway) + ruck grace phase-out (2026-06-24)
CLIFF PRINCIPLE (Luke): avoid thresholds where one extra game jumps value; smooth/stage everywhere possible (1-3 game samples
exempt). VERIFIED cliffs in the band for a flat-60 GEN_DEF pk20: +200 JUMP at game 6 (level flips 0->60 as the first season
crosses the >=6g "qualifying" threshold); smaller ~-60 step at the season boundary (tenure 1->2). FIX: the games-weighted level
(phase the level in continuously from g=1, ramped by games-in-season) ELIMINATES the +200 cliff — SAME fix as the MSD over-weight.
General rule: weight every evidence input by games-in-season AND recency on a smooth ramp; nothing flips at a threshold.
CONWAY: blend does NOT catch him — 6 career games, 0 qualifying seasons, 0 games in last 2 seasons, level_asof=0, but pk24 RUC
at-draft pedigree E[v]=2067 > his current redesign 1369, so the blend pulls him UP. The Dowling fix is the wrong tool. What
catches him = RECENCY-WEIGHTING the evidence (recent games count, old games decay): cumulative games/tenure treat a game 5 yrs
ago == last week; recency-weighting makes "0 games in 2 years" read as ~no recent exposure -> value drops. Same mechanism as the
games-weighted level (weight by how much + how recently earned) -> unifies, doesn't add a bolt-on. CAVEAT: can't distinguish
injury from decline (discounts a returning injured player too) — Luke accepts ("no games for so long has to mean something").
RUCK GRACE PHASE-OUT (Luke confirmed): development benefit-of-doubt should fade past a certain age without production. Falls out
of POSITION-AWARE age-conditioning for free — the band conditions on position+age, learns a position-specific age curve (young
ruck keeps upside; 26yo never-produced -> narrow band). Rucks phase out LATER than mids (data shows later development). No separate rule.
BUILD add-ons (all band-internal, one place, smooth): games+recency-weighted evidence (MSD + 6g-cliff + Conway/gap, unified),
position-aware age-conditioning (Keane/Bice + ruck grace), games-weighted blend (young protection), per-group REPL. Demo floor still out.

## 5o. PRIOR REBUILT (features+shrinkage IN) — validation state + 2 open forks (2026-06-24)
DONE & ON DISK (conditional_prior.py): new _feat = [pos one-hot, log(effpk), _exposure, tenure, _lvl_eff, _age_asof].
 - _exposure = recency-weighted reliable game-count (decay RL_RECENCY_DECAY=0.72); replaces raw cumulative games.
 - _lvl_wt = games x recency weighted level (smooth, no >=6g cliff); _lvl_eff = _lvl_wt x min(1, exposure/RL_LEVEL_RAMP=14) (reliability shrinkage).
 - _age_asof = age at year Y (fallback 18+yrs). prior_q_at updated (age=18.5 at draft). _lvl_asof kept LEGACY.
RESULTS: IN-DISTRIBUTION calibration EXCELLENT = {10:11,30:30,50:49,70:70,90:90} n=10886. Conway FIXED 1369->1293 (down,
 shrinkage kills the 5g@80 over-read). Keane 2838->2349, Bice 1747->786, Dowling 288, vets preserved (Bont 3163/Petracca
 3087/J.Cameron 1132 bit-identical -> a band-independent floor in dist_redesign is binding for proven vets; verify when demo
 floor removed). Daicos 7089, Duff-Tytler 1412.
OPEN FORK A — SMOOTHNESS (the cliff rule vs GBR): the LEVEL is now smooth, but the VALUE-vs-games is still JAGGED because the
 quantile GBR is piecewise-constant and the convex v_at_peak chain amplifies upper-quantile steps. Proper synthetic test
 (GEN_DEF pk20, flat 60 every game): +123 jump at game 8, bounces +-50..120 across games 2-23 (~10-25% on a 400-600 base).
 This VIOLATES Luke's no-cliff rule and must be fixed before wire-in. FIX OPTIONS (regularization test TIMED OUT batched, run
 1-at-a-time next): (a) regularize GBR (min_samples_leaf 150-800, max_depth 2-3) -> smoother but risks flattening level/age
 response (undo Keane/Conway); (b) switch quantiles to a quantile FOREST (averages many trees -> inherently smoother);
 (c) post-hoc smooth the band over the exposure dim (local average +-a few games). LEAN: test (a) first, fall back to (b).
OPEN FORK B — AT-DRAFT PEDIGREE INFLATION: at-draft band E[v] for GEN_DEF pk2 ~3335-3413 across ages 18-22 (old design ~1849),
 NOT mainly age (age sweep 18.5->3335, 22->3413, 26->2772). CAUSE: shrinkage makes low-games rows lean on pedigree (pick),
 which is high for top picks. Matters for the BLEND/FLOOR step (would over-lift thin-sample high-picks like Uwland). DECIDE at
 blend step: clamp the at-draft floor ref to a calibrated pedigree anchor (position-adj PVC) OR calibrate blend weight to
 empirical recovery so the inflated ref doesn't bind. Backup: conditional_prior.py.pre_rebuild_bak.
NEXT: resolve Fork A (smooth), then build pricing (games-weighted blend w/ Fork B handling, per-group REPL -4 fwd/-2 else,
 test +25% cap), re-run 805 + _v column, apply Luke role-risk flags, re-establish anchors.

## 5p. RUCK UNREALISED-PRODUCTION TAX — wired in (2026-06-24, Luke approved tau=0.25 rucks-only)
Luke's framing (NOT a scale-fit; he retracted the 1400 ruck anchor and is happy with how production is priced): rucks peak
late = a list spot tied up for years, so DISCOUNT the part of a ruck's value NOT justified by reliable production. Mechanism in
dist_redesign.py: RUCK_TAX=float(RL_RUCK_TAX, default 0.25). In redesign_value, for RUC only: ev -= round(TAX * max(0, ev -
_realised(p))). _realised = redesign_value of a PROVEN CLONE at the player's _lvl_eff (8 seasons x22g at level_eff, high
exposure -> narrow band centred at reliable level = production-only floor); called with _tax=False (recursion guard). Earlier
v_at_peak(level_eff) attempt was CONTAMINATED (v_at_peak carries a demonstrated-production floor -> gave Madden realis 1514 on
level 31, and a POSITIVE tax for Marshall); the proven-clone is the clean baseline. Formula ev-tau*max(0,ev-realis) (NOT
realis+(1-tau)un) so tax never raises value.
SELF-TARGETING (verified): un% tracks reliability. Proven rucks ~untouched (Gawn -2%, Grundy -2%, Jackson -4%, English/Marshall
0%). Production-priced thin rucks barely move (McAndrew 25% un -> 1834->1719; Bryan 8% un -> 735->720). Pure-speculation rucks
take the hit (Madden 92% -> 1960->1508; Heath 89% -> 318->248; Conway 75% -> 1293->1051; Emmett 60% -> 1482->1260). Non-rucks
UNCHANGED (McCarthy 2666, Bice 786, Petracca 3087, Bont 3163). Catches Conway structurally = the principled version of his
manual flag. TRADEOFF: moves some players Luke vibed 'fair'/'too low' DOWN (Heath, M.Edwards, Steene) because it's principled
not vibe-fitted; any per-player override is separate. GENERALISES: same mechanism extends to other positions with per-position
tau by development timeline (KEY next, MID least) -- NOT done, Luke chose rucks-only.
WIRE-IN NOTE: when the redesign ports to the engine value()/JS, the ruck tax + _realised (proven-clone) must port too for parity.

## OPEN ITEMS before engine wire-in (the next step)
1. PER-GROUP REPL_DROP (-4 KEY_FWD+GEN_FWD / -2 else) -- planned+locked earlier (fwd eligibility props up fwd values), but
   currently REPL_DROP is GLOBAL -3. DECISION pending + re-verify aggregate calibration post-rebuild.
2. +25% CONVEXITY CAP -- was 'test after age-conditioning, adopt only if runaway remains'. Age-conditioning + ruck tax now cover
   the runaways; RECOMMEND SKIP unless a non-ruck case (Anderson/Trembath/McCarthy) bothers Luke.
3. 805 BEFORE/AFTER re-run (+ _v board column) = the validation deliverable. NOT done.
4. RE-ESTABLISH VERIFY ANCHORS -- retrain moved them (Bont no longer 3163-as-_vpt etc.); KICKOFF/START_HERE/README verify values stale.
5. Update handover docs + checkpoint (this section banked; docs not yet refreshed to the rebuilt+taxed state).

## 5q. CORRECTIONS (2026-06-24 LATEST) — the dropped blend + Fork B is VOID (supersede earlier cont.25 notes on these)
1. THE GAMES-WEIGHTED PEDIGREE BLEND (5k/5l) WAS WRONGLY DROPPED during the rebuild on an unflagged "prior subsumes
   the blend" judgment call. It is REQUIRED and is being re-wired (see UNRESOLVED U25-A + the KICKOFF correction
   banner). The dist_redesign.py "No own-band blend" reasoning was an ERROR: it over-applied the OLD Y1-level
   own-band removal (correct) to the 5k peak-band blend (which must stay). Do NOT conflate the two blends.
2. FORK B ("at-draft band inflation ~3187-3413") IS A PHANTOM / VOID. That number came from a CONTAMINATED
   diagnostic — it priced the GEN_DEF pk2 at-draft band through a player (Bodhi Uwland, ~62 games) whose v_at_peak
   carries a DEMONSTRATED-PRODUCTION floor, which inflated the result. Priced CLEANLY (through a thin-sample player's
   own v_at_peak), the at-draft band [61,90,93,99,106] -> ~1715 @-3 (~= the spec's 1849) / ~1610 @-2. The pedigree
   pole is NOT inflated and needs NO repair. Do not attempt to "deflate" the at-draft band.
3. The pole drift 1849 (spec, @-3) -> ~1610 (@-2) is purely the global-(-3) -> per-group-(-2 for GEN_DEF) REPL change.
