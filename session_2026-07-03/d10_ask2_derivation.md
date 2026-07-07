# D10 ASK 2 — the GAMES-RAMP sit-out treatment: derivation + wiring (CANDIDATE v2.1)

**STATE: CANDIDATE v2.1 (games-ramp) — engine `c8051893` / cp `7c3652da`, branch `claude/games-ramp-engine-change-qt7824`. CONTROL = canonical `8aed420a` · PREVIOUS = candidate v2 `4a134d05`. Nothing baked; cold audit next.**

## 0. What was replaced

The `ns==0` sit-out anchor paid a flat position-classed fraction of OLD-PVC draftval (`SITOUT_RETAIN`, nonKPP yr-1 = 0.50), ignoring scores, games this season, season progress, and the position adjustment. Obituary: BOARD_LAYERS_OBITUARY.md. The flat 50% was the wide-bin artifact the statistics rule names.

## 1. The treatment (wired, `_merged_recover.py`)

For a still-listed player with **no qualifying season through Y** (bar prorated: `nseas_pro`, in-progress season judged at `6·fE`, fE = RL_M3_FE = 0.58 = R14/24 at this cut):

**value = (1−λ)·R(τ)·V0 + λ·e_full**

- **V0 = raw_ev(p, draft-year) × iso** — the engine's LIVE start value (zero-evidence band price, pick+position-adjusted; the Dean-below/Robey-above assignment; ASK-1 file). Cached per player; Y-invariant.
- **R(τ)** — retention of V0, knots at end-of-season depths 1..6, **τ = completed seasons since debut + fE** (linear within-season accrual = the decay itself prorates; **τ=0 → R=1 structural: value HELD through pre-season**, proven by `ev(p, draft-year) == V0` exactly). Flat tail beyond depth 6.
- **λ(g/fE)** — measured evidence-credit blend toward the live production path, games read AT PACE against the prorated bar; **structural endpoints λ(0)=0, λ(6·fE→6)=1 → value CONTINUOUS at graduation** (no cliff, no game-6 jackpot; the old +2551 seam step is gone).
- **e_full** — the production path (raw_ev×iso), which prices actual output: scoring-awareness flows through it (Annable's 1g@40 is information). For the FIRST-EVIDENCE family (all evidence = season Y), e_full is a **3-point moving average on the games axis** (±1 game at the player's own rate) — DECLARED smoothing: the GBR band prior is stepwise on the exposure axis (measured +957 in one game on the B6 synth at a constant level feature) and the designed M3 pin-fade otherwise leaves the ramp locally non-monotone. Centered, unit-mass, level-preserving, family-scoped.

**Prorated bars (Luke 2c, the 6/10/14/22 enumeration):** `nseas` 6 → 6·fE (in-progress only) · `_nqual` 10 → first-qualifying-season fractional credit `f1 = min(1, g/(10·fE))` (smooth; first-evidence players only — see §4 scope note) · `LEVEL_RAMP` 14 and `POLE_RAMP` 22 → capped at full-season-equivalent games PLAYABLE since debut (yr-1 mid-season: 14→8.2, 22→12.8; everyone else unchanged by construction) · `bestlvl` 6-bar prorated. `G_ADQ`=12 deliberately NOT prorated (outside the enumeration).

**Relic purge (ASK 1 actioned):** stalled cap, mediocre cap and delist scrap re-anchored `draftval → V0`. The Luke-signed B5 pricing floor stays dv-based (feature, not penalty — declared exception). Grep proof in the ASK-4 file.

## 2. Derivation (statistics rule: finest supported resolution, smoothed; pooling declared)

**Harvest** (`p1_harvest.py`, one v2 engine load): every (player, end-of-season-Y) cell 2004–2025 with no qualifying season through Y, still listed at Y (LISTED-WINDOW rule, D8 convention) → **2,940 cells, 2,465 complete-outcome-window (Y≤2021)**; depth split 1443/585/256/100/48/18/15+; class split nonKPP 1564 / KPP 631 / RUC 270. Per cell: games gY, era-adjusted output q=avg/REPL, **V0**, and realized outcome **O** = price6-at-Y of the best qualifying era-adjusted level in (Y, Y+4], busts/never-qualified = 0 (the locked estimator's busts=0, still-listed conditioning, WQ6/price6 ruler).

**Retention R:** r=O/V0 (winsor 2.0), kernel-smoothed over depth (Gaussian, bw grown until eff-n≥35 — the D5 rule), **normalized by the same-depth all-draftee norm** E[O/V0 | all still-listed at depth d] (n≈1359..489 nonKPP) — the locked daEV-convention **"0.76 form"** (sit-out realization relative to normal development), which reproduces the 2026-06-30 authoritative measurement almost exactly (nonKPP raw ratios [.446 .377 .416 .429 .453] vs the notepad's [.45 .47 .39 .31 .45]). One 3-point smoothing pass; clip [0.05, 1.0].

| class | d1 | d2 | d3 | d4 | d5 | d6 | pooling declared |
|---|---|---|---|---|---|---|---|
| nonKPP | .429 | .404 | .410 | .432 | .437 | .424 | none (n=711 g0 cells at d1) |
| KPP | .468 | .380 | .325 | .278 | .253 | .266 | kernel pools thin d4-6 (n 10/4/3 raw) |
| RUC | .674 | .547 | .503 | .472 | .435 | .435 | **shape pooled with KPP** (thin bimodal, n=270 cells) × RUC's own measured d1-2 level (×1.065); ratio to RUC's own norm |

Reading: relative to surviving classmates, a kept nonKPP sit-out holds a roughly flat ~0.41–0.44 of start value (the still-listed conditioning does the declining for you — washouts exit via the delist gate at 0.02·V0); KPP declines with depth; RUC starts gentle (late developers) and declines. The old designed placeholders (0.50/0.70/0.85 flat-then-decline on the dv ruler) sat ABOVE measurement for KPP/RUC — same finding as the 2026-06-30 audit, now derived and wired.

**λ (games credit):** depth-1 cells g∈0..5 (n=364 played + 1,079 zero-game) + the just-graduated boundary (6-9 games, n=163): raw m(g) = [.205 .399 .454 .486 .419 .625 .704 …] — playing AT ALL nearly doubles realization; kernel-smoothed + isotonic, normalized (m(g)−m(0))/(m(6)−m(0)):
**λ = [0, 0.160, 0.493, 0.547, 0.547, 0.816, 1.0]** at end-of-season games 0..6; runtime x-axis = games/fE (pace).

**Evidence-axis test (declared):** within played cells tau(r, g)=+0.059 · tau(r, q)=+0.099 · tau(r, g·q)=+0.102; residual q after g-control: tau +0.038, NON-monotone across q bins (+.008/−.119/+.199) — a λ-side quality term is NOT supported at finest resolution and was NOT wired; quality credits through e_full (which the graduated boundary confirms: q-split realization .43/.87/1.40). This satisfies 2d without an invented constant.

**Norm baseline (p3, one v2 load):** from-draft realization b0 = .361/.311/.150 (nonKPP/KPP/RUC) and the per-depth norms above — the denominator that keeps sit-out pricing on the same optionality-priced ruler as every other player.

## 3. B6 at the wired candidate (scratch, gate-identical synth MID pk10 @ avg 85)

ramp(0..14g) = [1019, 1397, 1730, 2464, 3103, 3190, 3238, 3291, 3305, 3314, 3367, 3435, 3523, 3563, 3592]
steps = [378, 333, 734, 639, 87, 48, 53, 14, 9, 53, 68, 88, 40, 29] — **dips: NONE · T=+2219 · max first-6 step 734 ≤ 50%·T=1110 · rise-by-3g +1445 ≥ 25%·T=555.** All three clauses green on the scratch probe (official gate run in the ASK-4 file). Low-rate spot ramp (avg 40) monotone post-smoothing; output-monotone at fixed games verified (g=2, avg 30→100 strictly rising).

## 4. Measured and REJECTED variants (declared)

- **Board-wide prorated 10-bar** (_nqual counts an in-progress ≥5.8-game season for everyone): re-prices Luke-ruled anchors OUTSIDE the games-ramp channel via discontinuous proven-flips — Tsatas (accept-and-track 1140) → 2080 breaking A8; O'Driscoll −525; Cadman −253; Walter −322. REJECTED; the 10-bar prorates only for the first qualifying season (fractional f1, first-evidence players), which is the directive's evidence base (DIAG-B CF4 was cohort-scoped, +150). Extension board-wide = a Luke ruling.
- **Unscoped f1** (par-prior credit for any n==0 partial season): +940 on Tsatas (4 list-years, no 10-game season — 75% par-prior injection mid-career). REJECTED → first-evidence scope.
- **λ-side q multiplier**: unsupported (above) + breaks graduation continuity.
- **/b0-only normalization for R** (draft-time premium constant): retention clips at 1.0 by depth 3 (still-listed selection) — a yr-4 sit-out at full draft value fails every eyeball anchor; the same-depth-norm form is both the locked convention and sane. REJECTED.

## 5. Movement census (scratch, vs v2 matrix `cur`, joined n=579 active)

movers 146 · aggregate +5,966 · **2025 cohort (store scratch census, n=58): 37,103 → 43,703 (+6,600)** [D12 ASK 3 / audit R-a: non-authoritative census; the AUTHORITATIVE pinned-matrix figure is 37,875 → **43,967** (+6,092) — book/board read the matrix] · under-seam (old-ns==0, 1-5 g26): +5,458 across 31 · zero-game sit-outs: +198 net across 77 · stalled released by the prorated 6-bar (ns≤1→≥2): Cleary 285→751, Busslinger 599→677, Z.Johnson 528→599 (+3 unchanged) — the D8 graded dial re-prices this family properly at v3 · movers OUTSIDE the games-ramp family: exactly the stalled/mediocre V0-re-anchor set, n=20, max |Δ|=39 (Gibcus −39, M.Edwards −27, C.Harvey +25, …, Gothard 355→368) · Kako −501 is the KNOWN isolated data-patch artifact (matrix carries his missing 2025 season; the store doesn't) — resolves at the matrix rebuild · Curnow/Berry/Tsatas/Curtis/Ward/Rozee byte-unmoved.

Artifacts: scratchpad p1_harvest.json (md5 493385d4) · p2_curves.json · p3_b0.json · p4_final.json · p5/p6 probe JSONs; scripts committed under `session_2026-07-03/scripts/d10_*`.
