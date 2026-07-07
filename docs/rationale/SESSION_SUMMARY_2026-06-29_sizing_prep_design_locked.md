> ⚠ SUPERSEDED 2026-06-29 — READ START_HERE.md FIRST. This doc predates the merged build. The '(B) never wired' correction (CASE B) and the par-centred-pole merged engine (falsifier-clean) are NOT fully reflected below; any 'size (A)+(B)/run the sizing pass' instruction here is DEAD. Authoritative current state = START_HERE.md.

# SESSION SUMMARY — U28-D SIZING-PREP → DESIGN LOCKED, SIZING-READY (BUILD chat, 2026-06-28/29)

**STATE: design locked, ready to size. NOTHING BAKED. Before Stage 2.** Live store = Stage-0 edited (md5
`53728e6a77495c91030782c849b3e926`); board `rl_app_data.json` (605,719) + HTML UNTOUCHED; pickle `cm_400.pkl` md5
`34faa8659cc8f19794f5cb9584fa19b2`. THIS doc + `MEASUREMENT_cohort_trajectory_2026-06-28.md` (the frontier detail) are the
[DELETED 2026-06-29: the (A)+(B) sizing pass was RUN and produced -16,529 because it dropped the ASCENSION up-leg (decay down-leg only). The up-leg was then BUILT (cohort maturity passes). DO NOT re-run this pass. Current state: see START_HERE.]

## ENV (authoritative — every command)
`PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22` +
`PYTHONPATH=/home/claude/rl_after`. REPL_DROP uniform −3; SCALE_DIST=1.0. Code default PAR_RAMPS=14 is WRONG → set 22.
HARNESS for pre-Stage-0 work: `cp rl_model_data.json.pre_stage0 rl_model_data.json` → run → `cp rl_model_data.json.stage0
rl_model_data.json` (restore the Stage-0 live store; also mirrored at /tmp/stage0_edited.json during a session).

## THE LOCKED SIZING TARGET
The draft-day option must equal the **per-cell ESTABLISHED curve**: era-normalized (REF era-avg 70.8), bust-weighted realized
E[outcome | pick, pos], window 2008-2021 (14 cohorts), kernel over log-pick. Full table in MEASUREMENT doc (Part 1). Properties:
- **SURVIVAL is in the curve** (busts weighted at 0); **TIMING is applied along the ramp** (Lock 2): a not-yet-debuted player's
  yr-t option target = curve × decay, decay = E[outcome|not-deb-by-yr t]/draft-day E[] = **yr1 0.46×, yr2 0.26×, yr3 0.09×**
  (steeper for top picks, gentler deep). Prevents over-lifting future-busts; closes the composition trap from both ends.
- **PRICER folded into the target FIRST** (LOCKED, supersedes Lock 1's defer-to-Stage-4): per-cell pricer basis (+101/~13%,
  v_at_peak→established) lifts the v_at_peak curve to the established target, THEN (A)+(B) size to it. Cannot defer — it FLIPS
  the signed direction per cell (pk25+ MID v_at_peak 1.20× → established 0.90×). No later step re-defers.
- **Thin cells handled, not caveated:** pk3 (effN 2-6 for GEN_DEF/KEY_DEF/GEN_FWD) and pk11-24 MID use a WIDE kernel; MID pk3
  (effN 25) keeps its raw convex value; **RUC fully POOLED** (thin + non-monotone).
- Gate = option(cell)→curve(cell), lift = curve − walk-forward-option per cell. **876 RETIRED** (in-sample pooled mean).
- Debut-continuity ANCHOR: both ramp tracks derive from the SAME realized E[outcome|debut-state] (debutant production-state on
  E[outcome|debut t] held by the live pole; non-deb option on curve×decay) → martingale holds exactly, no discontinuity at debut.

## THE LEVER SET (audited — reduced)
**KEEP (separate axes), size JOINTLY whole-ramp, signed per cell:**
- **(A) level-lift** — move the option to the established curve. PLUS **(A)'s 2nd job: LIVE POLE thin-sample hold** — the
  `_floor_w` blend onto a LIVE pole (= the option, NOT the dead `_adraft_band`=119) holds thin-sample early-career players at
  ~option until production accumulates. Fixes Kyle (3g, was 510 vs option 572; live pole 572 (566 = 3g held EV)) and the 22% below-par thin-
  sample sub-cluster that crashes −216 below option (realized 803 > option 686 ≫ yr1 471, premature).
- **(B) upper-band re-centre** to the realized p70-p97 — **LOAD-BEARING** (value is 57-79% upper-band concentrated for EVERY
  position; median realized ≈ 0). **SIGNED:** LIFT the crash positions (GEN_FWD ~0.14-0.20×, KEY_DEF ~0.04-0.10× — the worst;
  KEY_FWD-deep 0.47×), LOWER **pk11-24 MID** to its stable wide-kernel target (~480; option 825 ≈ 1.7×, over-pricing verified
  robust: Kish effN 16.1, bootstrap CI-high 563 < 825, conversion refuted). Pick-resolved, high precision.
- **Lock-2 timing decay** (the principled staleness; the in-sample KAPPA is RETIRED).
- **Maturation age-gate #5** — INDEPENDENT surface (age credit in v_at_peak vs pole in `_adraft_band`); keep.

**DROP (subsumed by the curve):** (C) tail-restore (the curve integrates the p97; GEN_DEF not special); the staleness KAPPA
(→ Lock-2 timing decay); the old **+11/+8/+5 p97** (re-read off the curve: MID 3889 / GEN_FWD 1601 / KEY_FWD 2202 / GEN_DEF
2425 / KEY_DEF 2361 / RUC 5208, pick-resolved, folded into (B)).

## KEY MEASUREMENTS (this arc)
- **Signed per-cell damage** (wf-option/curve, the real "how much"): MID 1.13/2.14/1.28 (OVER, pk11-24 only after pricer),
  GEN_FWD 0.14/0.15/0.20, KEY_FWD 1.03/1.04/0.47, GEN_DEF 0.82/0.81/0.72, KEY_DEF 0.10/0.04/0.06 (worst). NOT a uniform 0.32×.
  Net gap over **211 rostered prospects** (active, ≤15g, age≤23) = **+25,521 SCAR**, aggregate ratio 0.74 (masks gross signed).
- **+57% RETIRED** — systematic year-1 = **+12%** (consistent-option basis; = the +40 option-aging drift). Honest note: un-zeroing
  non-debutants RAISES the raw step (+55%→+66%), so the zeroing understated it; raw step is a debut-revelation artifact either way.
- **Debut continuity** — martingale exact at yr1/yr2/yr3 (361=.57·507+.43·167; 167=.48·249+.52·92; 92=.32·223+.68·31).
- **MID verify** — conversion REFUTED (top-8 realized mids all drafted MID: Bontempelli/Oliver/Macrae/Neale/Butters/Mitchell/
  Daicos/Fyfe; current≈drafted); pricer flips signs (pk1-10 fair 1.02×, pk25+ under 0.90×, residual ONLY pk11-24 2.02×).

## NEXT ACTION (Stage 2)
[DELETED 2026-06-29: the (A)+(B) sizing pass was RUN and produced -16,529 because it dropped the ASCENSION up-leg (decay down-leg only). The up-leg was then BUILT (cohort maturity passes). DO NOT re-run this pass. Current state: see START_HERE.]
pk25+ MID; lower pk11-24 MID; live-pole-hold thin-sample), debut-continuity anchored, RUC pooled. Surface the magnitudes for
Luke's read BEFORE any bake. Then (later) Stage 2+ wire/bake. NOTHING bakes without an explicit Luke "go".

## STANDING / PARKED
Pick-isotonic cond_prior guard (Sweid<Matthews monotonicity breach); reliability `_floor_w` `K/(g+K)` as the 15-30g refinement
(K calibrated on realized; agrees with linear at 3-6g); RUC pre-debut reliability (synth, pool/borrow); U28-MULTIPOS (Duff-Tytler
backwards-sign) parked; rl_build stale (pre-strip) parked. Scripts: `rl_after/_traj_*.py` (target_curve, kyle, thinsample, locks,
damage, continuity, mid_verify, mid_basis, mid_stability, audit + decompose/reconcile/players/statecurve/validity_CD/walkforward).

[CORRECTION 2026-06-29] Prior text stating "p97 re-read off curve into lever B" / "old +11/+8/+5 retired into B" is DOC-ONLY and WRONG vs code: lever B never wired, established path has NO q97 (Q caps at q90), tail=zero since the +adds were removed. CASE (B) regression. See MEASUREMENT provenance block.
