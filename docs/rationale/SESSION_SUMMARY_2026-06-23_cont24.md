> ⚠️ SUPERSEDED — NEWEST state is cont.26 (2026-06-25). This cont.24 doc is HISTORY; its 'CONFIRMED current state' line is stale.
> Read START_HERE.md / `SESSION_SUMMARY_2026-06-25_cont26_predebut_par_redesign.md` FIRST.

# SESSION SUMMARY — 2026-06-23 (cont.24): DISTRIBUTION PRICING BUILT + REFINED + WHOLE-BOARD REPRICED — NOT yet wired

## WHAT THIS SESSION DID
Built the finished distribution-pricing model from the cont.23 starter, wiring all 6 spec TODOs. The model
(`forward_valuation/distribution_pricing.py`) is a STANDALONE repricer — **nothing is wired into `value()`**, per
the hard rule. It prices each player as `E[v(outcome)]` over a conditional outcome BAND, on the existing convex
SCAR scale. Then built a walk-forward harness for it (`forward_valuation/dist_harness.py`).

## THE MODEL — one flow (`distribution_pricing.py`)
1. **BAND** — freehand quantile models (q10/30/50/70/90 of forward best-3) on the engine's own `_v4_feats`. GBR
   quantile loss, prototype config (matches the bands Luke reviewed; HistGBR over-regularised elite medians).
2. **`v_at_peak(p,L)`** (TODO#1+#6) — value p AS IF forward-peak = L, through the REAL production chain at the
   player's REAL age (not PEAK_AGE). KEY RESULT: `v_at_peak(peak_est) == value()` to the dollar for proven players
   (production-dominated), so proven players land on their real numbers FOR FREE; old players decline correctly
   (Bont's 117 band valued at age 31 → ~his real value, not the prototype's 4991 PEAK_AGE bug). This single
   primitive collapsed TODO#1 (age-decline) and TODO#6 (map-through-full-value) into one.
3. **PRIOR** (TODO#3+#4) — pedigree forward-peak prior (centre+width) per position×pick from career-best-3, with
   the TOP OF THE DRAFT (picks 1-6) built by parametric `a·k^-b` + local-linear trend extrapolation (reusing
   pvc_smoother_viz's method), so picks 1-4 anchor to where the trend HEADS, not where neighbour-averaging flattens.
4. **SHRINKAGE** (TODO#3) — blend each player's empirical band toward the prior by `w = evidence/(evidence+K)`,
   where `evidence = own_games + comparable_density` (kernel count of similar training rows in pick/level/tenure
   space). This is the crux insight of the session: pure own-games PROPS stallers ("not-playing protects pedigree"
   — Clark wrongly floored at 1261); comparable-density alone over-WIDENS proven elite (rare archetype → hot Bont).
   The SUM de-priors a player who is EITHER proven (own games) OR a common archetype (Clark), leaving the prior to
   dominate only the genuinely-thin RARE-and-unevidenced cell (Willem: pick-1, elite-young, T=1) — exactly where
   the spec wants pedigree to carry. **K_SHRINK is the SURFACED dial (Luke sets it); default 30.**
5. **RELOCATION** — the freehand quantile median regresses PROVEN elite below v4's calibrated point estimate, so
   the band is relocated up by `max(0, peak_est - median)` (lifts only proven players; stallers/young have
   median≥peak_est → delta 0, untouched). Valuing over the band's ACTUAL levels stays (gives stallers their
   upside-tail residual floor).
6. **dist_value** = `SCALE_DIST · E[v_at_peak over the relocated band]`. SCALE_DIST = global recenter (TODO#5),
   harness-calibrated to conserve the cohort total — **currently 1.0, NOT yet calibrated** (see OPEN).
7. **GUARDRAILS** (TODO#2) — monotone quantiles (sort); width-by-age sanity flag vs the empirical SD table
   (relaxed so correctly-narrow proven players don't false-flag).

## CURRENT PER-PLAYER (K=30, RB_TAPER=0.55, SCALE_DIST=1.0 — REPRODUCIBLE, md5 bc0c77b)
```
                 pos    age cur   band(q10..q90)                  val()  DIST
Willem Duursma   MID    19  86   [87.7 101.1 106.5 114.5 124.6]  3162   3672   (>pedigree 3000)
Jhye Clark       MID    22  41   [52.7 60.3 69.0 81.3 92.7]       409    661
Zane Duursma     GFW    21  39   [48.0 57.3 64.6 71.3 85.7]       991    444   (censoring-lifted 358->444; U24-F)
Shaun Mannagh    GFW    29  74   [66.8 71.6 77.0 81.2 90.1]       502    530   (taper pulled 680->530; U24-E)
Riley Bice       GDE    26  78   [63.5 73.5 76.4 82.5 92.3]       485    600
Harry Sheezel    MID    22 115   [106.7 113.1 118.0 121.6 128.9] 6823   6881
Nick Daicos      MID    23 114   [105.6 114.0 120.5 125.0 131.5] 6543   6517
Marcus Bontempelli MID  31 120   [106.8 118.7 123.4 129.9 134.8] 2961   3089   (taper trimmed 3209->3089)
```
**Status vs Luke's reads:** anchors Sheezel/Daicos nailed (<1%). Willem 3672 > pedigree 3000 (elite pick-1 debut
worth noticeably more). Bont 3089 (+4.3%, taper-trimmed). Mannagh dropped to 530 by the recency taper (his 84 was
last year — same recency as the rucks the taper targets); now < Bice/Clark, a surfaced tension (U24-E). Zane lifted
by the censoring downweight but still < Clark (production-vs-pedigree, U24-F).

## ✅ "INSTABILITY" RESOLVED — was a lost-turn edit (server flakiness), not a model bug
ROOT CAUSE FOUND: a turn that never surfaced in the visible chat (Claude.ai server issues dropping/repeating
turns) upgraded the band relocation anchor from `peak_est` to `band_anchor = max(peak_est, recent_best2, youth)`.
That single change is the entire ~6pt shift — and it is GOOD: the `youth` term delivers the Willem lift (3649) and
`recent_best2` delivers the Mannagh lift (702 > Bice/Clark), both per Luke's feedback. VERIFIED reproducible: two
identical-command runs now byte-identical (md5 `adcb592` AT THAT TIME — has since changed with later edits to bc0c77b;
the reads are the stable anchor). Side effect: Bont +7% (recent_best2 127 > peak_est
118), a surfaced judgment call (U24-E). NOT a blocker. The table below is now the CONFIRMED current state.

## REFINEMENTS LANDED THIS SESSION (after the initial build)
1. **CENSORING FIX via DOWNWEIGHTING** (the young-gun target is right-censored by still-rising actives). EXCLUSION
   was tried both ways and FAILED (hard gate -> survivorship, Clark 588->946; riser-only -> Clark 704, Mannagh<Clark,
   anchors +4%). DOWNWEIGHTING works (Luke's call — I'd wrongly skipped it after one failed idea): keep every row,
   SOFTEN a censored riser's target by how far below peak age it is (`row_weight`, RISE_YEARS=4, sample_weight on the
   GBR). Lifts young projections (Zane 358->444) WITHOUT moving anchors or flipping Mannagh<Clark. `CENSOR_DOWNWEIGHT=True`.
2. **SCALE_DIST=1.0 VALIDATED** — harness (12 cohorts 2013-2024, walk-forward, --fast): dist year-1 retention mean
   98.8% (range 85% [2020 COVID] to 109%). Maturation trajectory (live model, by yrs-since-draft): yr1-2 ~99% ->
   yr3-5 ~109% (convex climb) -> yr6-9 ~85-95% -> yr10+ declines. Matches Luke's full target (NOT flat; ~100% yr1
   rising to 110-115% yr4-5). No scaling needed. Old value() runs year-1 at 105.9% (hotter); dist better-calibrated.
3. **RECENCY TAPER on recent_best2** (RB_TAPER=0.55, SURFACED) — each best-2 season credited RB_TAPER**(years-since-it),
   remainder reverting to current form (level_now). Fixes the board's recent_best2 over-credit: Sholl 967->201,
   De Koning 3333->2321, Meek 3444->2223, Bont 3089; young guns untouched. RB_TAPER=1.0 = old un-tapered behaviour.
4. **WHOLE-BOARD REPRICE** -> `AFL_distribution_pricing_board_2026.xlsx` (805 active: Board/Big movers/By position/
   By cohort/Sanity tabs). Board pool fixed to MA.players (805) — MA.data-filter (746) was missing the `extra`/unplayed rows.

## OPEN ITEMS (waiting on Luke — detail in UNRESOLVED U24-*)
1. **RB_TAPER strength** (U24-E) — and the Mannagh-vs-rucks tension: at 0.55 Mannagh 530 < Bice 600 < Clark 661, because
   his 84 was last year (same recency as De Koning's 97). A 1yr grace protects Mannagh but barely moves the rucks.
2. **RUCK CONVEXITY** (U24-E tail) — rucks read 1.55x old engine; matched-margin position scaling is only ~1.25x, the
   rest is band/ceiling + convexity. A SEPARATE lever (flatten the +1.25x ruck premium, or board-wide GAMMA). Offered to test.
3. **K_SHRINK** strength (U24-D, default 30). **Zane-class** pedigree-vs-production (U24-F).
4. **NEW — Luke's cont.24 board-review batch** (U24-REVIEW): Tom Green missed-year, Sam Darcy, Uwland-vs-Ashcroft/Reid/JHF,
   Sam Berry, dubious rucks (Bailey J Williams/Briggs/Madden/Conway, Sweet>Briggs/Meek), Harvey Thomas positional MID,
   Phillipou/Dowling/Caminiti overvalued, the `yrs` column (Reid yr1 vs Willem — is it draft-year or seasons-played?),
   harsh-on-recent-high-picks (Kyle, Duff-Tytler) + early-career KPP floor (Faull/Walter/Armstrong/Read/Tauru/Croft),
   first-years (Nairn, Kondogiannis), unplayed-prospect pedigree-vs-PVC (positional lens, Patterson not strictly PVC),
   Smillie/Patterson taking LESS haircut than peers who've played. Triage/respond — see UNRESOLVED U24-REVIEW.
5. THEN (Luke's explicit go only): wire into value() (retires beta*PVC floor + cvx + runway + tenure decay) + out_tilt
   JS port (`_engine_block_v23.js` L79) + 805 + by()-guard + re-verify parity. HTML board DO-NOT-SHIP until that port.

## FILES TOUCHED/ADDED THIS SESSION
- `forward_valuation/distribution_pricing.py` — the finished model (NEW; built from the prototype).
- `forward_valuation/dist_harness.py` — walk-forward harness for dist_value (NEW).
- `forward_valuation/distribution_pricing.py` — + downweighting (build_training returns W; fit_models sample_weight),
  + recency taper (recent_best2), + RB_TAPER/RISE_YEARS dials. md5 bc0c77b.
- `forward_valuation/dist_harness.py` — + sample_weight in build_training/fit_quantiles_capped (parity with the model).
- `forward_valuation/build_board.py` — whole-board reprice -> Excel; pool = MA.players (805).
- `AFL_distribution_pricing_board_2026.xlsx` — the repriced board (OUTPUT, sent to Luke).
- Engine `rl_model.py` UNCHANGED (no wiring — hard rule honoured).
