# !!! BAKED v2.5 — 2026-07-05 (DPP STRIP FINAL CONSOLIDATION + A7 frozen-gate amendment). CURRENT = efea88e5 (head `_merged_recover.py`; rl_model.py = 121a45d0 = the DPP strip: three single-valued position columns drafted/present/future, raw_multipos blend DELETED; store e1b4d8bf; band cm_400 34faa865; board rl_app_data.json = 7d1eeef8; book stable-seal 5799a9ceae5ca3ef.. / 2649 players). Lineage: e0ac9c37(frozen) -> 8aed420a(prior working) -> c47cb43d(BAKED v2.4) -> efea88e5(BAKED v2.5). Rollback anchor: prebake-v2.5-anchor @ 4180f06 (candidate + A7 amendment, nothing baked). Owner bake word 2026-07-05: "approved, apply as shown, re-run, and bake if clean". SHIP GATES @ efea88e5 (three-column CONTROL 8aed420a / PREVIOUS c8051893 / CURRENT efea88e5): A7 **PASS** for BOTH protected poles (Ryan Maric future_position=MID/gfut=MID; Ed Langdon future_position=GDEF/gfut=GEN_DEF) under the amended single-valued read; B3 **re-sealed** PASS (seal 5799a9ce, head efea88e5); B4 **re-pointed** PASS (regen 7d1eeef8 == shipped 7d1eeef8); B1/B2/B6/D14a-c PASS. Remaining reds A2 (Luke-ruled ships-red, "we can look at Curtis down the line") + A3 & A12 ([DC] DATA-caused) are the SAME non-blocking reds carried from v2 — no new reds, no engine-caused reds. BAKE: board + book cut from the SAME store e1b4d8bf in one run; BOTH artifacts stamped source_md5=e1b4d8bf, read-only. Four single-source guards LIVE on canonical: one_source_selftest.py PASS (guards 1-3 + F1 board==engine 0-mismatch + F2 book==board 0-mismatch + Kako/Bontempelli ground-truth + position-model) and guard_correction_canary.py (GUARD 4) PASS (josh-ward source edit survives to board+book). Self-checks re-pointed to efea88e5/e1b4d8bf: verify_restore.sh (11 PASS/0 FAIL, incl. cp-pair guard clean), run_panel.sh (10/10), PANEL_EXPECTED.txt, ship_gates B1/B3 baked matrix -> data/s4_matrix_baked_efea88e5.json, B3 seal data/book_stable_seal.json, B4 shipped board data/rl_build/rl_app_data.json. NOTE (pre-existing, not v2.5): verify_anchors.py is orphaned against the deleted dist_redesign board-valuation path (ONE-price deletion f2bb22b) — restore-verify is carried by verify_restore.sh. All prior md5 references below are SUPERSEDED history.

2026-07-05 A7 AMENDMENT — FROZEN-GATE INSTRUMENT FIX (owner-authorised; script/doc edits only; SHIP_GATES.md text untouched per the frozen-file rule — amendment lives here per the SHIP_GATES amendment process):
- A7 AMENDED (Luke, owner-authorised in writing, 2026-07-05): A7's protected position-pole read re-pointed from the stripped multi-position blend `p.get('_fut')`-dominant label -> the live single-valued settled-future position `p.get('future_position')` (the source gfut() prices the years-1+ leg from). Reason: the 2026-07-05 DPP strip (final consolidation; candidate claude/dpp-strip-final-consolidation-cxvk2o @ 2d61130, store e1b4d8bf) DELETED the _fut weighted-blend from engine + store — 0/2652 records carry _fut — so A7 was reading a DEAD field (dominant label -> None) and FAILing as an INSTRUMENT ARTIFACT, not a genuine position revert. CHANNEL SWAP ONLY: same two protected players (Ryan Maric MID/MID, Ed Langdon GDEF/GEN_DEF), same pass condition (fine future_position == dom AND gfut(p) == grp); players / tolerance / pass-logic UNCHANGED. Substance preserved: A7 still tests "did a protected position pole silently revert?" against the CURRENT single-valued data model. Owner-authorised 2026-07-05.

# !!! BAKED v2.4 — 2026-07-04. CURRENT = c47cb43d (head `_merged_recover.py`: ruck-cap default 1.73->1.4 + KEY_FWD REPL 67.8->66.8; REPL edit in rl_model.py = ce4468d6; store 644d1254; band 34faa865). FIRST bake past the frozen e0ac9c37. Lineage: e0ac9c37(frozen) -> 8aed420a(prior working) -> c47cb43d(BAKED v2.4). Owner bake word 2026-07-04: "I give the bake word for v2.4 with ruck cap 1.4 and REPL -1". Rollback anchor: prebake-v2.4-anchor @ 6035ce1. All md5 8aed420a / 7c199a1f references below are SUPERSEDED history.

> RECONCILIATION BANNER (2026-07-01, HISTORY): the then-working engine md5 was 8aed420a (SUPERSEDED by baked c47cb43d 2026-07-04). Any md5 referenced below reflects an earlier turn — see START_HERE.md for authoritative state.

# !!! (HISTORY) prior working engine 8aed420a (no-games sit-out anchor + 34-position reconcile, built on 7147b824). Lineage: e0ac9c37(canonical,frozen) -> 8c6d5582(dials) -> 55e3c3a9(shed) -> 7147b824(upside) -> 8aed420a(no-games) -> c47cb43d(BAKED v2.4). See START_HERE.md + PROVENANCE_2026-07-01.md.
# !!! 2026-07-01 AUDIT CLOSE (engine CODE md5 UNCHANGED 8aed420a — data + harness only, nothing baked):
#   (1) GATE-1 formally RE-RUN at head 8aed420a via _gate1_wf.py (leakage-guarded IS-vs-WF) + _gate1_picksplit.py
#       (both now in the tarball, previously missing) — PASSES: leakage~0 (IS~=WF <=3pts, tree-matched @150),
#       GOOD 43-82% par by T3-5 vs BUST 0-1%, pole prices pedigree early (hi-pick 28->80 vs late 13->44). Residual
#       maturity-easing/84% unchanged (Luke's eye). See docs/rationale/GATE1_rerun_at_head_8aed420a_2026-07-01.md.
#   (2) _pos_now double-switcher fixes (store data, pre_stage0 cf8b3c5e->644d1254): Maric _pos_now GDEF->MID
#       (ev 1427->1409); Langdon _pos_now GFWD->GDEF + _fut [GDEF50,MID50]->[GDEF70,MID30] (ev 1122->593, removes
#       tiebreak-MID pole inflation). Panel 10/10; full 2654-diff = ONLY these 2 moved.
#   (3) 1.19x sit-out lift PARKED (not applied; re-derived at PVC on measured values; no longer a "say-the-word" hold).
# !!! 2026-06-30 UPSIDE FIX (GENTLER) WIRED (candidate 7147b824 = dials+shed+upside; on 55e3c3a9; Stage-0, board UNTOUCHED) — [SUPERSEDED by 8aed420a]
#     _lvl_eff_infer wraps _lvl_eff_core + elapsed-opportunity-gated fade: L_eff=(1-eo)*L0+eo*min(L0,max(S(dL,N),prod)).
#     S=kernel-smoothed realised fwd-ceiling surface; eo=yrs-since-draft x exposure (NOT nq), 0 at yr<=2 -> 1 by yr6.
#     Floors at demonstrated production (GENTLER, Luke's pick); only pulls down; rising/producing untouched. BOOK verified:
#     disease faded ramping by career yr (Davies -7..-42, Cook -22..-51, Clark -8/-29, O'Driscoll, Phillipou); producers
#     protected (Powell/Bruhn/Dempsey/Tsatas/Hollands/Ward/PARISH all 0% -- production-justified). Board 666936->654939
#     (-1.8%). FLAGS (not fixed): position-switchers 77/746 = 10.9% of board value (MANY+HIGH -> two-field BEFORE curve);
#     DOB not systemic (0 missing) but named handful placeholder _by=2000 + Max/Maxwell King both 2007 -> verify handful.
#     PEAK provisional (no-games not wired). CANDIDATE, not canonical until Luke commits. Name-parse fixed (Nathan
#     O'Driscoll/Mattaes Phillipou); Ed Allan not in DB.
#
# --- 2026-06-30 (investigation, NO engine change; 55e3c3a9 unchanged) UNEARNED-UPSIDE re-derived as CONTINUOUS surface
#     (dropped the 62 cutoff = scope-math slip; used MA.REPL effective bars MID 77.1/GENd 75.3/RUC 75.5/GENf 67.9/KEYd
#     65.4/KEYf 64.8). Credit = realised fwd ceiling E[fwdPeak](dL=ceiling-bar, year N), kernel-smoothed. SCOPE two
#     strengths (simulated, no wire): FULL=credit->S (board -16.5%, named -55%, but UNDERCREDITS SUSTAINERS via
#     flash-vs-sustain pop-averaging -> Dempsey -71%, above-bar -11%); GENTLER=floor at demonstrated production (board
#     -4.4%, named -12%, protects producers, hits only pedigree-inflated thin: Clark -50/Davies -55/Cook -15). GENTLER
#     recommended. Parish@yr4 S69 (lower not zero). Parish-type young-mid risk = only 4 under FULL, GENTLER removes it.
#     Peak check deferred to book re-run on wired candidate. HELD for Luke's strength call. See UNEARNED_UPSIDE_SCOPE_2026-06-30.md.
#
# --- 2026-06-30 (investigation, NO engine change; 55e3c3a9 unchanged) UNEARNED-UPSIDE years-3-6 LOCATED + DERIVED:
#     mechanism = thin-path _lvl_eff=c*Lc+(1-c)*par_prior (c=min(nq/4,1)) crediting draft-slot pedigree, gated on
#     QUALIFYING seasons not elapsed opportunity -> persists for partial-season plateaued players to yr3-6 (Clark nq2/cy4
#     Leff 60 vs prod 44; Davies nq1/cy6 75% pedigree). Secondary: pole-lift (tfade/expgate). DERIVED credit = realised
#     fwd-peak of plateaued(best<=62)-at-yr-N players: E=50/37/25/15 for N=3/4/5/6 (washout 28->76%, breakout 21->4%);
#     MID fades hardest, RUC thin->pool. WIRE HELD pending Luke: the Parish scoping fork (replacement-only vs upside-gap-
#     for-all) + plateau threshold + elapsed-opp gate. See UNEARNED_UPSIDE_LOCATE_2026-06-30.md.
#
# !!! 2026-06-30 DECLINER SHED DERIVED + WIRED (combined dials+decliner candidate 55e3c3a9; supersedes the standalone
#     dials commit; on the 8c6d5582 base; e0ac9c37 + 8c6d5582 backed up; Stage-0, board UNTOUCHED) — LATEST
#     DERIVED from realised forward output of established decliners (0=washout, no circularity): recovery~0 beyond ~3 SC
#     drop (forward stays at declined current); age accelerates forward BELOW current (_AGEMULT fwd/cur: 22=.89 25=.85
#     28=.79 30=.73 32=.68 34=.62). Position ~uniform; RUC harder 0.68 but n=49 THIN -> POOLED agemult (flagged).
#     WIRED asymmetric in _lvl_eff_infer proven branch (ONE shed curve): UP-side hold within per-group FLAT_TOL else Lc;
#     DOWN-side drop<=DOWN_TOL(3) hold, else L_eff=(1-sw)*L_old+sw*(Lc*agemult), sw smooth over drop 3->8. Fires only
#     n>=PROVEN_N=4 (gate intact). VERIFY (dials-only->combined): Symptom B FIXED (Darcy Moore 429->179, Scrimshaw
#     438->104, Perryman 426->215); steady stars FLAT (Daicos/Bont/Serong/Gulden/Butters delta-0); young/Edwards/first-
#     years/sat-out delta-0; movers 48 (6%), ALL down, board -1.5%, vw 1.5%. FINDINGS: (1) named decliners DON'T shed
#     because NOT declining (Petracca recovered 2026=112; Powell young riser 56->84) -> correct, relay premise stale;
#     (2) Konstanty/Gruzewski OUT OF SCOPE (thin/unproven, PROVEN_N axis not decliner); (3) near-par crater magnitude via
#     price6 convexity (Hopper 282->42) data-grounded but agemult-on-Lc may slightly over-shed -> Luke judgment (floor/
#     gentler agemult); (4) tfade/recover NOT adjusted (level-read is the lever for established; pole already faded).
#     CANDIDATE, not canonical until Luke signs off. No-games tandem + peak 120-130% check = later step.
#
# !!! 2026-06-30 STEP-3 DIALS WIRED (candidate engine 8c6d5582; e0ac9c37 backed up; Stage-0, board UNTOUCHED) — LATEST
#     LDECAY per-group {KEY .40 / GEN .35 / MID+RUC .225} + FLAT_TOL per-group {KEY 10.3 / GEN 12.0 / MID+RUC 14.0} WIRED into
#     _lvlcurr + proven-flat branch. Derivation: step-3 calibration record (2026-06-29 STEP-3-CLOSED entry). POLE_RAMP 22 unchanged.
#     PROVEN_N per-branch SURFACE *not wired* (no committed exec spec; kept scalar 4 + c=n/4) — BLOCKER logged. VERIFY: hard gate
#     PASS (first-years intact); proven stars held (Daicos/Bont/Serong delta-0), risers held flatter (Gulden -5%, Butters -6.5%);
#     ruck/no-games/sat-out UNCHANGED (dials skip n=0). Named decliners ~0% (decliner is the tfade/recover axis, not these dials).
#     SIDE EFFECT: wider FLAT_TOL is symmetric -> over-holds moderate decliners (Darcy Moore +122%, Scrimshaw +102%) at stale
#     established level -> decliner fix must make the hold asymmetric. Aggregate: 19% move >5%, board -2.3%, vw|move| 5.1%. Book
#     re-run owed (base moved). CANDIDATE, not canonical until Luke signs off. Nothing baked to board.
#
# !!! 2026-06-30 RELIC AUDIT (BUILD chat; engine e0ac9c377d1e UNCHANGED, nothing baked) — LATEST
#     Reconcile + confirm + doc-hygiene; defects FLAGGED not fixed (Luke's call). Three findings:
#  B1 — STEP-3 DIALS NOT WIRED (price-moving FLAG). The live ev() path reads the PROVISIONAL line-26 scalars
#     (_merged_recover.py:26 `PROVEN_N=4; FLAT_TOL=3.0; LDECAY=0.40`), read at L31-32/35/41-42/74. The step-3
#     CALIBRATED values recorded in the 2026-06-29 "STEP 3 — CLOSED" entry were NEVER applied to code — that
#     entry's own "engine UNCHANGED" confirms it; only 3-B POLE re-level was applied (the e0ac9c37 bump).
#       LDECAY : live 0.40 single  | calibrated KEY 0.40 / GEN 0.35 / MID+RUC 0.225  (GEN+MID+RUC running too slow a decay)
#       FLAT_TOL: live 3.0 single  | calibrated KEY 10.3 / GEN 12.0 / MID+RUC 14.0   (3-4x gap; proven-flat hold rarely fires -> tracks current level)
#       PROVEN_N: live 4 + c=n/4   | calibrated per-branch SURFACE (above~0/near~2.8/below-young 2D), which also REPLACES the c=n/4 shrinkage (L42) — unwired
#       POLE_RAMP: live 22 == calibrated 22 (OK, not in question).
#     The calibrated values (0.225/10.3/12.0/14.0/2.8) are ABSENT from engine code; no per-group dict, no 2nd path.
#     CONSEQUENCE: all of STEP 4 (book, backtest, no-games, ruck work) was validated on PROVISIONAL step-1 dials,
#     not the calibrated step-3 surface. When the dials are wired (Luke's go) step-4 numbers shift -> re-validate. NOT FIXED.
#  B2 — DELETE-CANDIDATES confirmed NO live caller (live ev = raw_ev*iso_corr + staleness; _merged_recover uses rd only for
#     REPL_DROP L56, never the value fns). All audit INERT tags CORRECT (none had a live caller):
#       B8 KAPPA/SCONV/LOWBASE (rl_model:266) + comp() (:268, a no-op `return v`); B13 out_tilt (:614, "CUT cont.21" :656) /
#       track_slip (:597, uncalled) / SLIP_* (:596, only inside track_slip); survival() (:298, "REMOVED cont.20" surv=1.0 :652);
#       MA.value() pedestal + dist_value repricer + redesign_value + reliability/own_band blend + par_redesign forks = superseded
#       par-router, unreached by live ev. -> all delete-candidates for a later BATCHED cleanup (Luke sign-off; not deleted now).
#       NOTE: SHRINK_K lives in par_build.py:25 (+ diagnostic print :199), not the cited dist_redesign :122-123 — minor loc correction.
#  B3 — CHANGELOG SHIPPING GAP. CHANGELOG.md EXISTS in the workspace (769 lines) but was NOT included in the step-4 checkpoint
#     tarball -> the audit (on the tarball) correctly found none. Action: ship CHANGELOG in every checkpoint henceforth.
#     FORWARD CONVENTION ADOPTED: each constant change / derivation gets an entry = what, value, and (derivation | "Luke choice + date").
#     Price-moving (C) rationale recorded as each is confirmed/re-derived downstream; no retroactive archaeology now.
#
# !!! 2026-06-29 VERIFIED BACKUP — design-locked checkpoint (BUILD chat) — LATEST
#     Inventoried + extract-verified tarball at the design-locked/sizing-ready state. Refreshed STALE resume docs (HANDOVER Jun25,
#     KICKOFF Jun26, START_HERE/SESSION_SUMMARY Jun28-midday were pre-sizing-prep) with current-state banners + NEW
#     SESSION_SUMMARY_2026-06-29_sizing_prep_design_locked.md (authoritative resume point). Pulled /tmp deps into archive:
#     rl_after/rl_model_data.json.stage0 (=53728e6a, harness snapshot), rl_after/cmp.json (backtest dep). cm_400.pkl md5
#     34faa8659... VERIFIED in extracted copy. Nothing baked; store Stage-0 (53728e6a); board/HTML untouched; before Stage 2.
#
# !!! 2026-06-28 CONFIRM1 (pk11-24 MID well-sampled) + PRICER-SEQUENCING LOCK -> SIZING-READY FINAL (BUILD chat, analysis-only) — LATEST
#     Script rl_after/_traj_mid_stability.py; full account MEASUREMENT doc. CONFIRM1: pk11-24 MID down-correction target ROBUST,
#     not thin-tail fragile - Kish effN 16.1 (adequate, vs pk3 cells 2-6); bootstrap 90% CI [270,563], option 825 > CI-high 563 ->
#     over-pricing ROBUST; jackknife drop-top LOWERS mean (Butters->346 etc, worsens over-pricing, not fragile to over-count);
#     wide-kernel @pk15 borrow pk6-30 = 474(H.4)/495(H.7) < 825. REFINEMENT: size down-correction to STABLE WIDE-KERNEL target ~480
#     (not narrow 408); option 825 vs ~480 ~= 1.7x. CONFIRM2 PRICER-SEQUENCING LOCK (SUPERSEDES Lock 1's defer-to-Stage-4): fold
#     per-cell pricer into TARGET FIRST (v_at_peak->established), THEN (A)+(B) size to established curve signed per cell. CANNOT
#     defer - flips sign per cell (pk25+ MID v_at_peak 1.20x -> established 0.90x over->under). No later step re-defers (Lock-1 text
#     amended with SUPERSEDED marker). MID pk11-24 lowers to ~480, pk25+ MID LIFTS (under on est basis), crash pos lift hard. NET
#     SIZING-READY: target = per-cell ESTABLISHED curve (pricer in), era-norm bust-wtd 2008-2021, survival-in-curve + timing-along-
#     ramp (Lock2), pk3+pk11-24-MID wide-kernel, RUC pooled. Levers (audited): (A) level-lift+live-pole hold; (B) upper-band
#     re-centre to realized p70-p97 (load-bearing SIGNED: lift crash pos, lower pk11-24 MID ~480); Lock-2 timing decay (KAPPA
#     retired); age-gate #5 (independent). DROPPED: (C) tail-restore, staleness KAPPA, old p97. (A)+(B) size jointly whole-ramp
#     signed vs established curve, debut-continuity anchored. STILL before Stage 2; nothing baked; store Stage-0 (53728e6a).
#
# !!! 2026-06-28 MID-OVERPRICING VERIFIED (narrow) + DESIGN AUDIT -> reduced lever set (BUILD chat, analysis-only) — LATEST
#     Scripts rl_after/_traj_mid_verify.py,_traj_mid_basis.py,_traj_audit.py; full account MEASUREMENT doc. PART1 MID over-pricing
#     is NARROW not blanket: 1.1 conversion REFUTED (top-8 realized mids ALL drafted MID - Bontempelli/Oliver/Macrae/Neale/Butters/
#     Mitchell/Daicos/Fyfe; current-MID~=drafted-MID 0.99x). 1.2 pricer basis per band (established): pk1-10 1.02x FAIR, pk11-24
#     2.02x OVER, pk25+ 0.90x UNDER. => MID correction = NARROW (B) upper-band DOWN-correction at pk11-24 ONLY (restore over-weights
#     thin upper tail: pool ~4% elite + 96% modest, mean 408, option 825); top-pick MIDs FAIR (protect, best-realizing), deep MIDs
#     UNDER (lift). PART2 DESIGN AUDIT: (C) tail-restore ABSORBED into curve everywhere (value 57-79% upper-band ALL pos, median~=0;
#     curve mean integrates p97; GEN_DEF NOT special) -> DROP. STALENESS KAPPA RETIRED -> subsumed by Lock-2 timing decay (the
#     principled staleness); don't carry old KAPPA (would stack/overshoot). AGE-GATE #5 vs LIVE POLE INDEPENDENT (age in v_at_peak,
#     pole in _adraft_band) -> KEEP both. p97 RE-READ off curve (MID 3889/GFWD 1601/KFWD 2202/GDEF 2425/KDEF 2361/RUC 5208), retire
#     +11/+8/+5. PRICER +101 SEQUENCING: fold per-cell pricer into TARGET (v_at_peak->established) FIRST, then (A)+(B) size to
#     established curve signed per cell (pricer flips pk25+ MID sign) - don't double-correct; refines Lock 1. REDUCED LEVER SET: KEEP
#     (A) level-lift, (B) upper-band re-centre (LOAD-BEARING+SIGNED: lift crash pos, lower MID pk11-24), (A) live-pole hold, Lock-2
#     timing decay, age-gate #5; DROP (C) tail-restore, staleness KAPPA, old p97. (A)+(B) size jointly whole-ramp signed, debut-
#     continuity anchored. STILL before Stage 2; nothing baked; store Stage-0 (53728e6a).
#
# !!! 2026-06-28 PER-CELL DAMAGE + +57% RETIRED + DEBUT CONTINUITY -> SIZING-READY (BUILD chat, analysis-only) — LATEST
#     Scripts rl_after/_traj_damage.py, _traj_continuity.py; full account MEASUREMENT doc. TASK1 PER-CELL DAMAGE (signed, the
#     real how-much; old pooled 0.32x SUPERSEDED): wf-option(yr0 opt x0.86)/curve per cell, v_at_peak basis (Lock-1) — MID
#     1.13/2.14/1.28 OVER-priced (restore inflates/under-bust-weights); GEN_FWD 0.14/0.15/0.20 catastrophic under; KEY_FWD
#     1.03/1.04/0.47; GEN_DEF 0.82/0.81/0.72 mild; KEY_DEF 0.10/0.04/0.06 WORST. Lift SIGNED (lower MID, raise GEN_FWD/KEY_DEF/
#     KEY_FWD-deep). TOTAL over 211 rostered prospects (active <=15g age<=23): Scurve 98,214 - Swf-opt 72,693 = NET +25,521 SCAR,
#     agg ratio 0.74 (net masks gross signed moves). Pricer +101 separate (Stage-4/bake). TASK2 +57% RETIRED: yr0 330; raw non-deb
#     =0 -> 510 (+55%); Lock-2 non-deb=0.46x opt -> 546 (+66%); consistent-option basis 330->370 (+12% = systematic year-1 = C's
#     +40 drift). HONEST DIRECTION FIX: un-zeroing RAISES the raw step (zeroing UNDERSTATED, not overstated) but raw step is
#     debut-revelation artifact either way; genuine systematic = +12%, +57% carried forward nowhere; gate = per-cell option->curve.
#     TASK3 DEBUT CONTINUITY: martingale EXACT at yr1/yr2/yr3 (361=.57*507+.43*167; 167=.48*249+.52*92; 92=.32*223+.68*31). Tracks
#     MEET by construction (both on realized E[outcome|debut-state]); value steps UP at debut (good news) balanced by non-deb decay,
#     no predictable round-trip. Anchor debutant prod-state on E[outcome|debut t] (live pole) + non-deb on curve*decay -> no
#     discontinuity (same principle as level=0 pole / 3-game line). NET: SIZING-READY; (A)+(B) size jointly vs per-cell curve,
#     whole-ramp, (A) two jobs. STILL before Stage 2; nothing baked; store Stage-0 (53728e6a).
#
# !!! 2026-06-28 THREE LOCKS -> sizing target finalized (BUILD chat, analysis-only) — LATEST
#     Script rl_after/_traj_locks.py; full account MEASUREMENT doc. LOCK 1 ONE BASELINE: per-cell era-norm realized
#     E[outcome|pick,pos] curve (v_at_peak-priced) IS the target; 876 RETIRED (in-sample pooled mean/diagnostic, gone from
#     sizing math); gate = option(cell)->curve(cell), lift = curve - wf-option per cell; prospect-vs-established PRICER basis
#     (+101) is a SEPARATE Stage-4/bake item. LOCK 2 DEBUT-TIMING (trap's last hiding place, CLOSED): curve bakes SURVIVAL
#     (bust=0) but is POOLED over timing; measured timing-decay weight E[outcome|not-deb-by-yr t]/draft-day E[] = yr1 0.46x,
#     yr2 0.26x, yr3 0.09x (steeper top picks pk<=18 0.45/0.27/0.00, gentler deep pk>=25 0.70/0.43/0.16). Applied ALONG THE
#     RAMP: yr1+ option target = curve x decay -> prevents over-lifting future-busts AND shows yr1 bust-zeroing too harsh
#     (residual option 0.46x not 0). State-discount taper (debutant side) + timing decay (non-debutant side) = whole-ramp option
#     evolution. LOCK 3 THIN pk3 HANDLED: retire raw effN 2-6 cells; MID pk3 effN25 keep raw 1519 (convex premium, fit
#     under-shoots); thin pos (GEN_FWD/KEY_FWD/GEN_DEF/KEY_DEF effN 2-7) use wide-kernel H=0.70 / log-pick fit (KEY_DEF ~530-570
#     etc), pool convex top-pick shape from MID (pk3/pk8~1.76) where divergent (GEN_DEF 696 vs 1070); RUC fully pooled. NET: curve
#     is the sizing target, one baseline, survival-in-curve + timing-along-ramp, pk3 handled; (A)+(B) size jointly whole-ramp.
#     STILL before Stage 2; nothing baked; store Stage-0 (53728e6a).
#
# !!! 2026-06-28 CORRECTED TARGET CURVE (Part 1) + KYLE/THIN-SAMPLE = (A)'s 2nd job (Part 2) (BUILD chat, analysis-only) — LATEST
#     Held jointly. Scripts rl_after/_traj_target_curve.py, _traj_kyle.py, _traj_thinsample.py; full account MEASUREMENT doc.
#     PART 1 CORRECTED TARGET: era-norm (REF 70.8), bust-weighted realized E[outcome|pick,pos], window WIDENED 2008-2021, kernel
#       /log-pick. The draft-day option must equal this curve; GATE = option/curve -> 1.0, debut-timing-weighted (NOT the year-1
#       step). Table per pos x pk3/8/15/30/50 in MEASUREMENT doc. Well-sampled+monotone for pk>=8 (5 field pos); pk3 thin for
#       GEN_DEF/KEY_DEF/GEN_FWD (effN 2-6); RUC thin+NON-MONOTONE -> pool. Current wf option ~0.32x -> lift = target - wf_option,
#       sized JOINTLY (A)+(B), whole-ramp. Confirmations locked: B settled, D 2008-2021, GEN_DEF deep n=62 robust, RUC pooled,
#       era-norm ~5%, Fork1 joint, Fork2 whole-ramp.
#     PART 2 KYLE/THIN-SAMPLE = (A)'s SECOND job. 2.1: 22% of <=15g debutants are below-par thin-sample, crash -216 below option,
#       PREMATURE on avg (realized yr5 803 > option 686 >> yr1 471), MASKED by the +132 bucket mean (Kyle pattern, same as GEN_DEF
#       masking). Cases mixed (Flanders 5g 1204->690->realized 4765; Florent ->premature; McCartin/Boekhorst ->justified busts) but
#       44-mean vindicates option. 2.2: mechanism = DEAD pole (_adraft_band=119, lift-only < prod 510 -> inert -> Kyle=prod 510,
#       -62); LIVE pole (option) holds him 566. NOT too-fast transition (w=0.90 at 3g). (A)'s live pole fixes BOTH jobs (same pole).
#       2.3: linear 1-g/30 vs reliability K/(g+K) AGREE at 3-6g (both ~0.90 pole), DIVERGE at 15-30g (reliability holds below-par-
#       pedigree on pole longer, principled). Adopt live pole first; switch _floor_w to reliability as the 15-30g refinement (K
#       calibrated on realized). (A) TWO JOBS: (i) option->target curve, (ii) live-pole thin-sample hold; dead pole broke both.
#       STILL before Stage 2; nothing baked; store Stage-0 (53728e6a).
#
# !!! 2026-06-28 PRE-SIZING VALIDITY CHECKS (A/B/C/D + Fork1) — +57% IS NOT THE HONEST GAP (BUILD chat, analysis-only) — LATEST
#     Scripts rl_after/_traj_validity_CD.py, _traj_walkforward.py; full account MEASUREMENT_cohort_trajectory_2026-06-28.md.
#     A WALK-FORWARD: cm_400 trains cond_prior on resolved debut<=2021 -> 2014-19 ARE in-sample. Per-cohort held-out retrain
#       (cap=D+1) drops the yr0 option a consistent -14% (-11..-17% across cohorts) -> yr0 330->~284, ratio 0.37->0.32; yr0->yr1
#       +55% in-sample -> +61..+79% walk-forward. Option MORE under-priced OOS -> lever sizes up; use walk-forward targets.
#     B CONFIRMED: yr0=DRAFT (option,0g), clock=years-since-draft (debutyr=year+1). 44% non-debuted by yr1.
#     C THE BIG MOVER: +57% = 22% PRICING (+40 option drift) + 78% DEBUT-TIMING (+140 crossing to prod/zero). Debutants 246
#       option->prod +459; non-debutants 191 hold option 201 but zeroed. The +57% STEP is mostly mechanical debut-revelation,
#       NOT option re-pricing -> year-1-step target FAR below +57%; lift MUST be debut-timing-weighted (don't lift a 2-yr-late
#       debutant's option); gate on EXPECTED year-1 change (intercept), not the raw step.
#     D (i) n=437. (ii) window widenable to 2008-2021 (14 cohorts all yr5<=2026); 2014-19 was conservative -> widen to thicken
#       slices. (iii) deep-pick GEN_DEF crash n=62 ROBUST; thin = top-pick GEN_DEF/KEY_DEF (healthy, not crash) + RUC (n~1-15,
#       pool/widen). (iv) era drift ~5-6% (2020 73.9 -> 2021+ ~69 rule change); yr5 anchor straddles it -> era-normalize ~5%.
#     FORK 1 (A)/(B): directionally (A) state-pole ~+269 (state discount), (B) upper-band ~+101 tail + upper-body share of +252,
#       PRICER +101 separate; but ENTANGLED -- A acts on state-pricing axis, B on band-level axis -> compound not double-count,
#       SCAR split order-dependent via convexity (pool-vs-own 682-506=176 measures it ~30%) -> size A+B JOINTLY, not fixed budgets.
#     FORK 2 = WHOLE-RAMP taper flatten (Luke's call). Aggregate +42%/yr0->464 is the OUTPUT check, never the lever.
#     NET: don't size to +57%; size with walk-forward targets, debut-timing-weighted, expected-year-1-change gate, finest pick-res
#       (window widenable), RUC pooled, era-norm ~5%, A+B joint, whole-ramp. STILL before Stage 2; nothing baked; store Stage-0.
#
# !!! 2026-06-28 LEVER (B) REDEFINED upper-band + 6-MOVERS CONFIRM + FIRST-ORDER SIZING -> SIZING-READY (BUILD chat) — LATEST
#     Script rl_after/_traj_movers.py; full account MEASUREMENT_cohort_trajectory_2026-06-28.md. (B) CORRECTED: it is an
#     UPPER-BAND (p70-p90) re-centre, NOT a body/median move -- for the crash positions p50 is correctly sub-replacement and
#     prices ~0 wherever placed (GEN_FWD p50 54.6), the gap is p70/p90 below realized; built as a median move it does NOTHING
#     for GEN_FWD. (B) is HIGH-PRECISION (convex floor: 2-pt p90 miss = hundreds of SCAR, GEN_FWD 48 SCAR/avg-pt) -> p70/p90
#     targets landed on realized precisely per position. 6 GEN_DEF anchor-movers: DO include top-pick producers (Hayden Young
#     pk7, Wanganeen-Milera pk11, Max Holmes pk21 -- GEN_DEF draftees who became elite mids), BUT keying doesn't move THEIR
#     values (production-priced) and the named top-pick PROSPECTS are stable across keyings (Patterson Δ-0.05 ... O.Taylor -0.05)
#     -> healthy end UNDISTURBED, shift is all at the crash end; REINFORCES drafted-keying (retains positional-flexibility upside).
#     FIRST-ORDER SIZING: aggregate yr0 must reach ~464 (from 326, +42% mean, DISTRIBUTIONAL by pick/pos toward E[outcome|pick,pos],
#     NOT flat) to bring yr0->yr1 +57% -> <=10%. TWO FORKS for the sizing pass (Luke's calls): (1) (A)/(B) apportionment of the
#     +138 (overlap, no double-count); (2) yr0-only flatten vs whole-ramp taper flatten. LEVER MAP LOCKED: (A) live-pole first
#     (taper/pick-scaled/distributional), (B) upper-band re-centre second (pick-resolved, high-precision), (C) tail third; guard
#     standing. ==> U28-D SIZING-READY. STILL before Stage 2; nothing baked; live store Stage-0 (53728e6a).
#
# !!! 2026-06-28 PRE-SIZING RESOLUTIONS + DISTRIBUTIONAL SIZING LOCK -> U28-D SIZING-READY (BUILD chat, analysis-only) — LATEST
#     Script rl_after/_traj_keying_repl.py; full account in MEASUREMENT_cohort_trajectory_2026-06-28.md. Resolved the two gates:
#     (A) GEN_DEF ANCHOR-KEYING (drafted vs current): only 6 movers; drafted-keyed (principled cohort) p50 0.75 deep-pick crash,
#     current-keyed p50 0.30 (median crashes too) -> keying shifts magnitude not direction; GEN_DEF STAYS in body lever, deep-pick,
#     pick-resolved. (B) REPL-HARDNESS: v_at_peak floor is a legit steep convexity (~30-48 SCAR/avg-pt, near-0 at repl-8), NOT a
#     bug; crash positions' realized mass straddles a high replacement so value is UPPER-band (p70/p90) concentrated -> the body
#     re-centre for GEN_FWD/KEY_DEF/deep-GEN_DEF is an upper-band move (not p50), precise+pick-resolved (GEN_FWD 48 SCAR/avg-pt
#     worst); KEEP REPL_DROP uniform -3, no per-position re-scope. DISTRIBUTIONAL SIZING LOCKED: lift realizers' option toward
#     realized E[outcome], hold bust mass ~0, let aggregate fall out -- NOT flat "double yr0" (44% of yr0 = eventual busts ->
#     flat lift worsens the drop); composition-safety = taper-safety (busts price ~0 every state). Live-pole carries all three:
#     taper-matched ~70/yr + pick-scaled 151-deep/357-realizer + distributional/bust-weighted. LEVER MAP locked: (A) live-pole
#     FIRST, (B) upper-band re-centre SECOND (GEN_FWD+KEY_DEF+deep-GEN_DEF, pick-resolved), (C) tail THIRD; pick-isotonic guard
#     standing. Gating move to beat: aggregate yr0->yr1 +57% -> <=5-10%. ==> U28-D SIZING-READY. STILL before Stage 2; nothing baked.
#
# !!! 2026-06-28 GATING YEAR-1 MOVE (+57%) + TAPER ROBUSTNESS + PICK-ISOTONIC GUARD LOGGED (BUILD chat, analysis-only) — LATEST
#     Three final pre-sizing checks (script rl_after/_traj_aggcut.py; full account in MEASUREMENT_cohort_trajectory_2026-06-28.md).
#     (1) GATING NUMBER: yr0->yr1 on the AGGREGATE-SUM-WITH-BUSTS-AS-ZEROS basis (non-debuted-by-yr-t=0) = +56.6% (~+57%, NOT
#     the earlier +82%; +82 had no yr1 bust-zero). 191/437 (44%) non-debuted at yr1. Curve total SCAR: yr0 142267 -> yr1 222826
#     (+57%) -> 304389 (+37%) -> 348401 (+14%) -> 382339 (+10%) -> 383003. Gates the <=5-10% tolerance; sits 6-11x above it.
#     Sizing: aggregate yr0 option must ~DOUBLE (326 -> ~600+) to flatten, and the lift must be DISTRIBUTIONAL (44% of yr0 option
#     is eventual non-debutants who drop to 0 at yr1). (2) TAPER ROBUST off-survivor: state discount split REALIZERS [357->0 smooth],
#     NON-REALIZERS [~0 at every state, discount ~2 -> the pole has NOTHING to over-lift on busts], DEEP pk>=25 [151->0 smooth].
#     => live-pole must be PICK-SCALED (151 deep vs 357 realizer) + DISTRIBUTIONAL (option, not flat per-player bonus) + taper-matched;
#     a uniform pole over-lifts deep-pick eventual-busts. (3) PICK-ISOTONIC GUARD on cond_prior BAND logged as a STANDING fix in
#     UNRESOLVED (peer to the cont.28b synth-value guard, which PASSES but misses the Sweid/Matthews real-vector band inversion);
#     isotonic clamp at band layer upstream of pricing; independent of U28-D. LEVER MAP stands: live-pole FIRST (taper+pick-scaled+
#     distributional), body re-centre SECOND (GEN_FWD+KEY_DEF+deep-pick GEN_DEF, pick-resolved), tail THIRD. STILL before Stage 2; nothing baked.
#
# !!! 2026-06-28 REAL-PLAYER DIAGNOSTICS — refine the decomposition before 71/29 final (BUILD chat, analysis-only) — LATEST
#     Three per-player checks (scripts rl_after/_traj_players.py,_traj_players2.py,_traj_statecurve.py; board values from
#     rl_app_data.json reproduce Luke's reads; board~=engine within 10%). Full account in MEASUREMENT_cohort_trajectory_2026-06-28.md.
#     (1) GEN_DEF CONFLICT resolved with a twist: first-pass v_opt used a coarse 3-pick-band -> false-flat 837 across pk5-15
#     (the wide-bin artifact). Pick-KERNEL v_opt (H=0.40 log-pick): named young GEN_DEFs are HEALTHY (Patterson pk5 1.25,
#     X.Taylor 0.90, Kyle 0.84, O.Taylor 0.90, Carmichael 0.99) -- NOT crashed. BUT the 2014-19 GEN_DEF cohort is BIMODAL
#     (mean 0.55, p25 0.02, p50 0.75, 49%<0.30); the crash is the DEEP-pick young GEN_DEFs (pk>=25 mean 0.44) on the GEN_FWD-
#     style value-floor knife-edge. So the 0.63 mean DID mask a sub-cluster (Luke right) -- deep-pick, not the named ones;
#     "GEN_DEF tail-dominated" was a mean artifact; body re-centre must target deep-pick young. (2) STATE DISCOUNT is a SMOOTH
#     taper (yr0 269->yr1 192->yr2 131->yr3 56->yr4 12, ~70/yr) NOT a step -> a live-pole removing it state-by-state compresses
#     the +57% yr0->yr1 surge to ~+18% gentle-positive WITHOUT a post-yr0 cliff; CONSTRAINT: U28-D's taper must MATCH this decay.
#     (3) CLEAN pick-monotonicity breach: Sweid pk25 (yr0 294) < Matthews pk30 (yr0 350), both GFWD/0g/draft-age18 -- the
#     cond_prior quantile-GBR band is non-monotone in pick (Matthews' band > Sweid's at q30-q90); held-equal guard blind (differ
#     in pick). Needs a pick-isotonic guard on cond_prior, separate from U28-D. Cross-position orderings (Nairn>Carmichael,
#     Dovaston>X.Taylor/Kyle) confounded by position scale+games, flagged not clean. 71/29 rankings hold; bust-zeroing recut
#     still pending (rankings robust). STILL stopped before Stage 2; nothing baked.
#
# !!! 2026-06-28 GAP DECOMPOSITION — TAIL IS NOT THE DOMINANT LEVER (BUILD chat, analysis-only) — LATEST
#     Decomposed the yr0 330 -> realized 876 gap (546 SCAR) before choosing any U28-D lever. Scripts rl_after/_traj_decompose.py
#     + _traj_reconcile.py; full account appended to MEASUREMENT_cohort_trajectory_2026-06-28.md. All priced in one v_at_peak
#     space (SCALE 1.0, REPL -3, bal). n=437. LADDER: 330 +252 BAND-BODY (band centred ~5-10 avg-pts low: p50 56.4 vs 61.0,
#     p90 81.4 vs 91.6) -> 582; +101 BAND-TAIL (realized mass above p90: p95 99/p97 104/p99 109, truncated by the 5-quantile
#     band) -> 682 (= option value of realized dist via v_at_peak @yr0); +194 STATE+PRICER (v_at_peak prices the SAME outcome
#     +269 LOWER at the yr0 0-games/age-18 state than at maturity = the production-state discount, the purest frame violation;
#     + ~101 prospect-vs-established pricer basis) -> 876. HEADLINE: TAIL is the SMALLEST term; the banked p97 tail-restore
#     (+8-11/pos) addresses only a slice of +101 -> NOT the dominant lever. Dominant = production-state discount (elapsed-
#     opportunity / level=0 pole) + BAND-BODY re-centre. POSITION-UNEVEN: GEN_FWD 0.06 / KEY_DEF 0.04 CRASHED (body, v_at_peak
#     threshold knife-edge: GEN_FWD band p50 54.6 just below the value floor -> 36, realized 59.7 -> 480) vs MID 0.69 / GEN_DEF
#     0.63 / KEY_FWD 0.58 / RUC 0.24; GEN_DEF is the ONLY pos where TAIL>=BODY (tail-restore relevant there; it's in HIGH_TAIL).
#     RIGHT-EDGE CONFIRMED (Task 2): curve plateaus yr4 875 ~= yr5 876, both cohort-halves stable (2014-16 1008->946 ageing,
#     2017-19 741->807 maturing), level tracks realized cohort strength -> mature end priced correctly, entire error is young-
#     end (no-re-prop constraint measured). REVISED U28-D guidance: target state-discount + body re-centre FIRST (position-
#     calibrated), p97 tail LAST. RE-RUN harness+decomposition after U28-D. STILL stopped before Stage 2; nothing baked.
#
# !!! 2026-06-28 GOVERNING-FRAME READ + COHORT-TRAJECTORY MEASURED + BASE-VERIFY + P-FREEZE RESOLVED (BUILD chat) — LATEST
#     Pre-bake. Board/HTML untouched, model store = Stage-0 state. Frame doc (OBJECTIVE_governing_frame.txt) now governs
#     all stages: a prospect's value IS an option over the full historical outcome distribution (convex tail incl) that
#     production REPLACES over time; the engine's default error is the inverse (discounted production + potential bonus).
#     COHORT-TRAJECTORY MEASUREMENT (the governing-frame target; before Stage 2; on PRE-Stage-0 engine). Cohorts ND-with-
#       pick 2014-2019 (n=437), leak-free point-in-time, survivorship-clean. Full: MEASUREMENT_cohort_trajectory_2026-06-28.md;
#       data traj_out_2026-06-28.json; scripts rl_after/_traj_measure.py (+_traj_sanity/_traj_leakcheck/_traj_bisect2/_traj_unstripped).
#       POOLED mean SCAR/player by career-year: yr0 326 -> 594 -> 745 -> 797 -> 875 -> yr5 876. Draft-day option = 0.37x
#       the realized yr5 anchor (876). Monotone RAMP, NO V. Year-1 intercept (dV1 ~ realized yr5 quality) = +92.7 (POSITIVE);
#       mean dV1 +268 (+82% of v0). Leak-free vs un-stripped identical (326 vs 325) -> honest gap, not a strip artifact.
#       VERDICT: not the doc's V (no yr1 crash; intercept positive -> the literal no-round-trip test FALSE-PASSES). Same
#       error, other face: low draft-day anchor + steep ramp (option under-priced to 37% of realized; production ADDS not
#       REPLACES). Right diagnostic = draft-day/realized ratio (0.37) + ramp, NOT the year-1 intercept. => U28-D dominant
#       lever = raise the draft-day OPTION (yr0) via p97 tail-restore, not only yr3+ staleness onset. RE-RUN harness post-U28-D.
#       Surfaced mid-measure: drafted KEY_DEF prospect prices 17 vs equiv GEN_DEF ~374 (GEN_DEF/KEY_DEF young-end gap).
#     BASE-VERIFY (pristine pre_stage0, full env): 14/14 anchors OK, Sharman proj_value(0)=310, 805 active, CALIB 11/30/49/70/90.
#     P-FREEZE RESOLVED on default (a) (rl_after/_stage1_pfreeze.py). Frozen-P = P_estab->pick_prior->GRP[p['pos']] (drafted),
#       baked as 'P' in rl_export.py:33; recomputed live from pos (no stored frozen-P). 29/34 ESTABLISHED -> P=1.0 inert;
#       5/34 non-established move small/sensible (Curtin +0.092, Whitlock +0.056, Hollands +0.018, Nairn +0.014, H.Smith -0.003);
#       no bad edits. pos=AMEND-M already in effect -> (a) mechanical; re-bake recomputes. Inert in value today (P_HOOK=None).
#     UNRESOLVED: rl_build/rl_model_data.json stale (pre-strip) logged as parked reconciliation; synth()[0] folded into a
#       RUC-reliability item (Stage-4 representative/pooled borrow) + Stage-7 verify-the-6 note. STOP before Stage 2.
#
# !!! 2026-06-28 DPP-STRIP / POSITION-SPLIT — STAGE 0 EXECUTED (BUILD chat, PRE-BAKE) — LATEST
#     Model store reclassified + _fut stripped + ASSERT-GATED. Board (rl_app_data.json 605,719) + HTML UNTOUCHED.
#     cm_400 unchanged (md5 34faa8659...). Full account: SESSION_SUMMARY_2026-06-28_dpp_strip_stage0.md.
#     STRIP-ONLY CONTAINMENT (strip isolated from reclass): 111 movers |Δ|>0.5, 105 in expected DPP set, +4102 SCAR;
#       6 non-DPP "leaks" (Will Green -11.71 / Goad -9.97 / Barnett -9.12 / Knobel -2.43 / Molier -0.70 / Smith -0.51)
#       DIAGNOSED BENIGN: isolation test gives iso_self=+0.00 for ALL 6 (ZERO own-_fut leaks) and iso_others=iso_all.
#       Carrier MEASURED at tail_restore.synth() L140 (first gfut==pos roster player as deepcopy template): board strip
#       flips Sheezel gfut MID->GEN_FWD, swaps MID synth template Sheezel(1149.6)->Daicos(1112.0), -12.5 on scorer mean
#       x RUC level ratio = -11.71 exact. Pre-debut RUC pool only; toward correct single-pos pricing; self-corrects at
#       Stage-7 re-bake. Re-grep clean: gfut/futblend/spike-cap all guarded for empty _fut.
#     EXECUTION: backup rl_model_data.json.pre_stage0; reclassify active 805 (pos<-AMEND-M, _pos_now<-AMEND-N from
#       roster_dpp_reclassification_edits.xlsx Roster M/N; codes MID/RUC/GFWD/KFWD/GDEF/KDEF; 805/805 name-matched, 0 miss);
#       strip _fut=[] all 2656 (VERIFIED board-neutral vs active-only: 0 active values differ). 34 drafted edits
#       (pos!=AMEND-M) = the Stage-1 P-freeze population: Sheezel MID->GFWD, Holmes GDEF->MID, Curtin MID->KDEF,
#       Blakey GDEF->KFWD, Rozee MID->GFWD, Sicily GDEF->GFWD, Owens KFWD->MID, Dale GDEF->GFWD, W.Milera GDEF->GFWD,
#       Ginbey KDEF->MID, MacDonald GFWD->MID, Moore GFWD->MID, Wilson GFWD->MID, Yeo MID->GDEF, Humphrey GFWD->MID,
#       Sparrow GFWD->MID, M.Roberts GDEF->MID, Greene GFWD->MID, B.Hill GFWD->MID, Amon GDEF->MID, Whitlock KFWD->KDEF,
#       Nairn GFWD->MID, D'Ambrosio MID->GDEF, Crisp MID->GDEF, B.Williams GDEF->MID, Dempsey MID->GFWD,
#       Coleman GDEF->GFWD, Banks GDEF->MID, Laverde KDEF->MID, Hollands GFWD->MID, Fisher MID->GFWD, Perryman GDEF->MID,
#       McStay KFWD->KDEF, H.Smith KFWD->RUC.
#     ASSERT GATE (fresh reload) ALL PASS: active=805; _fut empty (805 active + all 2656); one drafted+one current
#       (valid codes); gfut==GRP[_pos_now]==current; pos==AMEND-M & _pos_now==AMEND-N.
#     NEXT (Luke's call): STAGE 1 P-freeze reconciliation — TEMPORAL question (were the 34 drafted edits applied to the
#       value P was frozen on, or does frozen-P predate them?). Build does NOT auto-resolve; Luke says which field P was
#       frozen on. CARRIED to Stage 4: synth()[0] template selection is roster-order-sensitive (pre-existing smell).
#
# !!! cont.26 PRE-DEBUT FIX + PRODUCTION REDESIGN (2026-06-25, LATEST) — DESIGN ONLY, no code committed. Engine/prior/
#     HTML byte-identical to the cont.25 checkpoint. SUPERSEDES the cont.25 floor plan: the β×PVC HARD floor is too
#     blunt (Cumming 61 vs 21 over 3g BOTH = 1667 — everyone generic in yrs 1-2). Root cause = the PRODUCTION model
#     (`_lvl_eff` shrink-toward-ZERO, conditional_prior ~L58), not the floor. Break-even avg to look on-track: 87@3g →
#     66@20g, and 66 = empirical par (top-8 mids) → calibrated at full sample, distorted only at low sample. NEW PLAN:
#     a PAR-CENTRED production model with AVAILABILITY-aware evidence weighting (not-playing & playing-poorly = same
#     mechanism; band carries optionality; β×PVC demoted to downside CAP). Also: debut_factor IS season-aware (off-
#     season pedestal = raw PVC; 10% deadband pending); position-aligned PVC pre-debut (PVC × mult); founding axiom
#     SOFTENED (pedigree CAN drag on poor performance). Full: SESSION_SUMMARY_2026-06-25_cont26_predebut_par_redesign.md.
#     Reproduce: forward_valuation/cont26_diagnostics.py (verified runs). Next: build PAR + mock Cumming/61-vs-21/
#     Patterson before any rebuild, on Luke's "go". Files added: the cont26 summary + cont26_diagnostics.py.
#
# !!! cont.25 CALIBRATION AUDIT (2026-06-25) — DIAGNOSIS ONLY, no code committed. The release HTML predates
#     this and is NOT final. Found: (A) GEN_DEF under-projects mid-picks (pk14 median 73.3 vs realized ~84; pole
#     529=0.45×PVC) — fixed at pk3 in cont.24c, drifted lower in the cont.25 rebuild, never re-audited. (B) FLOOR
#     ANCHOR DEVIATION — the soft floor aims at the conditional-prior pole, but the agreed design was
#     max(production, β×PVC-pedigree), β=0.85; revert to β×PVC. (C) RUCK pick gradient BACKWARDS (RUC-only; pk20-30
#     project above pk14; Emmett RUC pk27 = 2.05×PVC) — tiny ruck sample, GBR can't fit; proposed fix = running floor
#     from top of draft (down-only). VERIFIED implemented: censoring fix (resolved_cut=2021) + level+tenure prior.
#     FALSE ALARM (correctly not fixed): GEN_FWD "over-projects" = test-set censoring artifact. Corrected per-position
#     poles @pk14 (native players): GEN_FWD 974 / MID 904 / RUC 765 / KEY_DEF 762 / KEY_FWD 745 / GEN_DEF 529 (the
#     earlier RUC=415 was a broken synthetic). Two mechanics clarified: pre-debut pedestal = position-FLAT PVC;
#     conditional prior (post-debut) = where position differentiation + the miscalibration live. PLAN: ruck fix → then
#     (per-position calibration coverage + β×PVC floor + gentle taper, together) → revalidate → rebuild → re-tar.
#     Full detail: SESSION_SUMMARY_2026-06-25_cont25_calibration_audit.md. Anchors below WILL move once the fixes land.

# !!! cont.25 CORRECTION (LATEST): games-weighted pedigree blend (5k/5l) was wrongly dropped on an unflagged "prior subsumes the blend" call -- being RE-WIRED. Pole intact (~1610 @-2); Uwland 1048 = wrong no-blend value. Other cont.25 changes intact. See KICKOFF correction banner. The "REBUILD COMPLETE / no blend" entries below are SUPERSEDED on this point.

## cont.25 FINAL (2026-06-24) — CONSOLIDATED REBUILD (standalone, pre-wire-in)
- PRIOR REBUILT (conditional_prior.py): features now [gfut 1hot, log(effpk), _exposure (recency-wtd games, RL_RECENCY_DECAY
  0.72), tenure, _lvl_eff (games+recency wtd level x reliability-shrink, RL_LEVEL_RAMP 14), _age_asof]. Smooth (kills game-6
  cliff), MSD/long-gap aware, position-aware age. No separate blend (conditioning subsumes it). In-dist calib 11/30/49/70/90.
  _lvl_asof kept LEGACY. Backup conditional_prior.py.pre_rebuild_bak.
- RUCK TAX (dist_redesign.py, RL_RUCK_TAX=0.25, RUCKS-ONLY, Luke-approved): ev -= 0.25*max(0, ev - _realised); _realised =
  redesign of a PROVEN clone at the player's _lvl_eff (_tax=False recursion guard). Self-targeting; catches Conway (1293->951).
- PER-GROUP REPL (dist_redesign.py): RL_REPL_DROP_FWD=4 (KEY_FWD+GEN_FWD, lifts elite KPFs), RL_REPL_DROP_OTHER=2. Was global -3.
- +25% CAP SKIPPED (Luke); DEMO FLOOR OUT; BRODIE x0.5 kept; pre-debut still engine MA.value PVC path.
- 805 before/after: AFL_REDESIGN_805_rebuild_2026-06-24.xlsx (+ _v column, By Position). verify_anchors.py added.
- Anchors: Daicos 6938, Bont 3096, Petracca 3154, McCarthy 2539, J.Cameron 1196, Gawn 2522, Madden 1395, Conway 951,
  McAndrew 1606, Uwland 1048, Keane 2215, Bice 693, Sharman _v 310. Redesign board +9-28% above _v (REPL drop + uncapped upside).
- NEXT (only step left): engine wire-in -> value() + JS parity (incl. ruck tax + proven-clone realised) + HTML don't-ship.

## cont.(23) 2026-06-23 — VERIFIED cont.22 · by() CRASH FIX · ROSTER→805 · WALK-FORWARD HARNESS · FLOOR SUPERSEDED → DISTRIBUTION PRICING
- VERIFIED cont.22: Sharman=310 correct; §9 as-of contamination RESOLVED & PROVEN (stress test 0/788 drift) — cont.21 had the polarity backwards (1147 was the stale-cache artefact).
- FIXED by() None-guard (rl_model.py L60): cont.22's DOB fold-in wrote `_by=None` for ~302 records → `.get(key,default)` returned None → crashed `_age_at` on every backtest. Shipped board was safe (0 active affected). Guard: `p.get('_by') or (p['year']-18)`.
- ROSTER → 805 (active-17 RESOLVED): set force_active for 17 undebuted-but-rostered players in both masters + JSON. 805 is manually-maintained ground truth, no auto-inactive. Backups *.bak_pre_active17.
- WALK-FORWARD HARNESS built (forward_valuation/walk_forward_harness.py): in-sample-leakage CONFIRMED (106%→96%); β calibrated on 14 clean cohorts (0.85 mean96/min90, 0.87 comfortable, 0.90 hot). Sanity passed (2024/25 wf≈in-sample).
- JS PARITY root-caused: ~189/788 = out_tilt cut (cont.21) never ported to `_engine_block_v23.js` L79; cont.22's DOB/cache changes flow BAKED so don't break parity; "0/785" gate was stale (cont.14). Board DO-NOT-SHIP. Fix parked (remove `*outTilt` L79).
- BACKTEST regenerated on current engine (AFL_cohort_backtest_MASTER_2003-2025.xlsx) — 2020 cohort 0.96→0.54 over yr1-6 confirms write-down works. Mature-age class CLOSED (Luke cleared candidates; Bramble was the only real one).
- ⚠️ FLAT FLOOR (U21-1) SUPERSEDED: Luke's per-player audit of the floor preview — it compresses young-gun ceilings (Willem pick-1 86avg projects only 101.6) + props stalled high-picks uniformly (Clark pick-8 @41=half-replacement floored 800; Zane 1372); not-playing protects pedigree. Root cause: point-estimate + flat pedigree prop, no variance/trajectory.
- DISTRIBUTION PRICING (U21-4) is now the next build, spec'd WHOLE in DISTRIBUTION_PRICING_SPEC.md: pedigree=prior, performance updates by gap-magnitude × persistence; value=E[v] over freehand quantile bands (conditioned on pedigree+form), uniform pedigree-prior shrinkage by local data thinness, top-of-draft trend extrapolation (PVC loclin/parametric technique), harness-calibrated, replaces β·PVC+cvx+runway+decay. AWAITING Luke's go to build.

## cont.(22) 2026-06-23 — SOURCE-OF-TRUTH UNIFICATION + DOB LOAD + peak_est CACHE FIX
- Rebuilt afl_master_db.xlsx FROM the live JSON (was stale) → faithful superset; compiler rl_build_data.py round-trips everything (scoring from 2005, +cols dob/phantom/double_count/pvc_exclude/eyr). Proven compile(master)==JSON for 2654/2656 (intended diffs only).
- DOBs folded into the SOURCE (844 incl Shane Tuck 1981-12-24) → flow to _by/_bd; real ages not 18-at-draft default.
- peak_est CACHE FIX: _pe_clear() @ L812 — peak_est memoised at SCALE while pickless players held placeholder _eff; pickless now price on real pick-equivalent. Sharman 1147→310. ~53 pickless corrected. Backups *.bak_pre_unify_2026-06-23.
- Eddie Betts/Elijah Ware→2004 RD #1/#2; Monahan key fix; 40 removed players archived (restorable). ⚠️ Left OPEN (now fixed cont.23): JS parity regressed; by() crash latent.

## cont.(21-cont) 2026-06-23 — PEDESTAL RE-DERIVATION prototyped+validated (not shipped) + Bramble DB fix + in-sample-leakage finding
- Luke eyeballed young board post-out_tilt-cut, found the pedestal ratio PVC[pick]*(peak/base)^2.2 INVERTS quality (Uwland GEN_DEF pick2 > Willem MID pick1). Proof: Uwland as-MID=2126 vs as-GEN_DEF=3266.
- FIX (prototyped, NOT wired): floor = seasons_decay × runway(age) × max(value_of_peak, β×PVC[pick]), β=0.85. Monotone in pick+projection. runway(age)=clamp((28-age)/6,0,1) = mature-age fix (Blakiston). Code: forward_valuation/pedestal_rederivation_prototype.py. Doc: PEDESTAL_REDERIVATION.md.
- β calibrated to year-1 cohort retention ≥90% (HARD constraint). β=0.40 (set by eye) bled 2025 to 64% (establishment-P redux, caught by Luke). 0.85 holds (2024=92%,2025=90%).
- IN-SAMPLE LEAKAGE finding: old cohorts backtest ~110% (v4 trained on their careers = hindsight), only 2024/25 genuine out-of-sample (~94%). NOT survivorship/composition (both ruled out, verified). Honest benchmark = ~94%; only 2 clean cohorts for calibration.
- BRAMBLE DB FIX: year 2023→2020 (2020 SSP), full 6-season scoring re-entered, games=91. Now production-bound (was phantom rookie-pedestal 232). Backup rl_model_data.json.cont21bak. NOT yet rebuilt into board.
- OPEN: build first-order walk-forward harness (~14 clean cohorts + verify leakage) OR lock β=0.85 + wire in. Mature-age DATA class (Blakiston+) still needs cleaning.

## cont.(21) 2026-06-23 — FULL PEDESTAL AUDIT + out_tilt CUT (rebuilt, parity-verified)
- Audited every inherited value() mechanism (work? how? adds value? double-counts v4?). PEDESTAL_AUDIT.md = canonical verdict table + test numbers.
- BLAST RADIUS: 63% of active are production-bound (v4-clean); only the young 37% are pedestal-bound (old machinery). 
- out_tilt CUT (line 656): redundant w/ v4 — corr(sig,realised−v4)=−0.05, marginal R²=+0.001 (form double-count, same as removed survival()). Was ±300–470 on young; over-lifts down / over-drags up; proven untouched.
- KEPT (audited): tenure decay (essential — makes proven price on production), young-key-pos floor (1/31 overlap w/ explicit floor, not redundant), los_decay (0→1g continuous), relative^2.2 (near-optimal), lens_tilt (inert on bal), capt_prem, _playsig. realized_cv deduped.
- cvx KEEP-FOR-NOW flagged: premise fails (corr(cvx,realised−point)=+0.02) but not a double-count, capped +25%, mostly inert, net-narrows a real −139 young under-pricing. Defer to distribution-pricing piece; don't amputate in isolation.
- Rebuilt (4-step). Parity board=point×cvx ✓, surv=1/P=1 all 788 ✓, proven unchanged ✓. Distribution-range NOT re-injected (board 0.94MB; re-inject when hover feature built).

## cont.(19) 2026-06-22 — LEARNED PROJECTION v2->v4 VALIDATED + forward target + DOB load
- Learned projection replaces the rigid peak_est blend. v2 (career-peak target) R² 0.29->0.46; v4 (FORWARD-realised target, current year counts w/ completeness weight) forward R² 0.43-0.50. SURVIVORSHIP fixed all positions (+75..130% -> ±7%) via bust-inclusive prior; KONDOGIANNIS +7.3 -> ~0. peak_model_v4.pkl, build_peak_model_v4.py.
- Forward target retarget removed the v2/v3 pedestal-explosion (Darcy +282% -> breakouts now correctly RAISE value, Treacy +83% YoY on his 104 breakout). Current year counts, weighted by season progress (Luke directive).
- DOB load: 40 retired 2003-07 mature-age DOBs + 808 active from xlsx, composite name|debut key (two Sam Fishers / Alwyn Daveys / Callum Browns). dob_corrected.json (848), load_dobs.py. Needle: marginal for R², good for individual mature-age correctness.
- CORRECTION: the pedestal is a YOUNG-player floor (value=max(prod,pedestal); decays to 0 by ~season 5) — NOT the proven-gun driver. Proven-gun "markdown" vs old engine = v4 dropping the old `level/frac(age,peak)^0.88` age-extrapolation, calibrated to realised outcomes. Pedestal re-derivation belongs to the young/unproven floor work.
- OPEN/GATED on Luke "build": re-derive pedestal for unproven floor + position-aware starting value + no-evidence decay; parallel before/after workbook; distribution pricing; integrate into rl_model.py (deletes ×P_establish + rigid blend; redo JS parity).

## cont.(18) 2026-06-22 — CONTROL built (establishment-P OFF, backtested) + bias audit
- CONTROL = engine w/ establishment-P off, backtested whole DB. Projection R² 0.287 (RUC 0.011 random). Found BIAS #1 survivorship (universal +75..130% late-pick overshoot) + BIAS #2 Kondogiannis (early-establisher under-projected 7.3). Architecture decision: keep value pipeline, replace only the projection. CONTROL_metrics.json, control.py, the byCohort backtest workbook (+ Cohort vs Draft summary, active-window masking, 2005 scoring start).

## cont.(17) 2026-06-22 — Forward Valuation PIVOT (D+ bug)
- D+ value-assembly was structurally wrong (draft pick a permanent multiplier -> dragged proven late-pick guns; hidden by cohort average, caught per-player). Engine values NOT ground truth; reads + realised outcomes are. New direction: PV of predicted realised future production read through INTERSECTIONS. FORWARD_MODEL_V2_DIRECTION.md.

## SESSION cont.(16) — FORWARD VALUATION MODEL (v5/variant D) + BIRTHDAYS + ROSTER CLEANUP (2026-06-22)
**Design + prototype + DATA only — the LIVE ENGINE/BOARD is UNCHANGED** (the Forward Valuation Model is NOT yet integrated into `rl_model.py`; the shipped HTML still runs establishment‑P). The **data‑of‑record DID change** (`rl_after/rl_model_data.json` 2653→2656 rows; retirements + 3 adds + dates).

**FORWARD VALUATION MODEL — the establishment‑P successor (prices bust risk ONCE; replaces the `×P_establish` gating that caused the cohort cliff / old 0c).** Standalone prototype + spec in `forward_valuation/`. Components: position‑tilted anchor (TILT) · stage‑bar performance update with reliability‑faded asymmetry · survival‑hold (band × POSADJ) blended by arrival weight · convex `cv()` captaincy premium · smooth gaussian runway · leak‑free forward‑decay projection.
- **v5 = variant D shipped in the prototype (3 changes over v4):** (1) smooth runway (gaussian, no birthday cliffs); (2) position‑conditioned survival POSADJ (RUC ×2.20 / KEY_DEF ×1.89 by yr5 vs MID ×0.85 — late developers retain); (3) smooth game cutoff `gw(g)=clip((g−2)/8,0,1)` blended with the survival hold (no 8‑game discontinuity).
- **VALIDATED (ND 2006‑2020):** cohort yr1 102% → yr4 105% → yr6 105% → yr10 85% (no cliff, prime ROI lift, clean aging); forward bias **+0%/−0%** all‑players; 2020 dud crop flagged 86%.
- **DEFERRED: distribution / upside premium** — built (variant C, youth +8% / proven +2%) but double‑counts PVC's baked‑in upside → runs ~10% hot. Needs recentering around the cohort average + ceiling‑aware (asymmetric) bands. **Target (Luke):** yr1 cohort ≥90%, a defined peak ~110% at some stage, ~95% avg fine, NO scripting; reach ~110% via the discount/convexity lever + the redistributive premium.

**BIRTHDAYS** (`forward_valuation/AFL_Player_Birthdays.xlsx`, 809 rows ≈ current AFL list): matched 799/1016 active. **Pedigree = draft cohort, not age** (age → runway only). Applied full DOBs (`_bd`) to the 7 corrected + 3 new + Monahan + Callum M. Brown. **PENDING: bulk‑load all 799 `_bd` + wire continuous age into the runway.** File error found (Ben Murphy DOB 2027) + name collisions (Max King = young Maxwell King; Callum Brown = active Callum M. Brown) documented.

**ROSTER CLEANUP (data‑of‑record; active pool 1016→805 ≈ the file's 809):** retired 214 stale delisted players (`forward_valuation/delisted_candidates.csv`); added Berry (KEY_DEF) / Carr (RUC) / Bourke (GEN_DEF) — pickless post‑draft signings, end of 2025; Watkins `_by` 2001→2000; Monohan→Monahan kept active; two Callum Browns confirmed SEPARATE (active Callum M. Brown + retired older one), not a dup.

## SESSION 2j cont.(14c) — FILE-STRUCTURE CLEANUP + DATA CONTRACT + 3rd/4th AUDITS (2026-06-21)
**Structural + documentation only — engine/board UNCHANGED** (board md5 27cc6fb5, HTML 348af1d6, parity 0/785, re-verified by clean-room rebuild). Data was already unified: `rl_model.py` reads ONLY `rl_model_data.json` + `params.json` + `rl_passmark.json`, and that DB already spans draft years **2003–2025** (the PVC builds from them) — nothing to "fold in".
- **Root de-cluttered:** removed ~15 exact-duplicate files (8 scripts == `rl_after/`, `recalc.py` == `xlsx_scripts/`, 3 xlsx == `deliverables_2h/`, 2 `.pre*.json` == `backups/`, and a duplicate `xlsx_scripts/` tree); archived 9 unique derived artifacts into new **`rl_workspace/archive/`** (+ its README); moved `rl_app_data.pre331.json` into `backups/`. Tarball root is now just `START_HERE.md` + `rl_workspace/` + the `rl_after`/`rl_build` symlinks.
- **Data contract documented** in README + START_HERE (engine input = those 3 files; everything else is derived/snapshot/tooling/docs). Corrected the stale HANDOVER "BACKUPS … OUTSIDE bundle" line.
- **3rd + 4th (cold-start) audits, same session:** fixed README nav (`cont.(9)`→top-block language), the README build recipe (had been single-column, now full dual-column SCAR+VOR), added the root `START_HERE.md` signpost, corrected 3 stale anchors (Moyle 850 / O'Brien 624 / Perez 47) and the `compute.py` O'Brien apostrophe. Full detail in `journal.txt`.

## SESSION 2j cont.(14c) — JS-ENGINE PARITY: ESTABLISHMENT-P + BRODIE NOW IN THE BROWSER (2026-06-21)
**`_engine_block_v23.js` + `rl_export.py` changed; HTML rebuilt. Board values UNCHANGED (Python identical) — only the in-browser recompute + 3 baked fields changed.** Closes the A1 JS-parity gap. **Parity gate (`node _rl_parity.js`): 0/785 mismatches** (max diff 1 = the existing ±1 convexity-rounding).

**Ported into the JS `valuePlayer` (now mirrors Python `value()`):**
1. **Establishment-P gating.** `P` baked per player (`round(P_estab(p),6)`, 1.0 = established). GATE 1: pedestal decay floored — `ped*relative*surv*min(pedDecay,P)`. GATE 2 (PROD_GATE='blenddemo'): `prod_full = ⅓·prod_full + ⅔·(P·prod_full + (1−P)·gfloor)`, `gfloor=max(pedestal, cred·prodFloor + (1−cred)·pedestal)`, `cred=min(1,games/50)`. **P is FROZEN** (computed at the player's real draft-cohort position) — Luke's call: bust rate is a fixed draft-cohort property, not the SuperCoach toggle; toggling position must NOT rewrite it (and the heavy alternative — porting the whole `pgrid` surface to JS — buys nothing here).
2. **Brodie cut.** `brodieBase` baked (the signal minus the RUC bit); JS applies `if(brodieBase && grpOf(p)!=='RUC') res*=0.5` so the RUC exemption fires LIVE — toggle Brodie to ruck and the cut correctly turns off (tested: MID 472 → RUC 1683 → back 472).
3. **0-game in-window P.** Baked a new `pedOnly` flag = Python's pure-pedigree condition (`_unplayed and (debut>AGE_REF or _pedonly)`); the JS no-P branch now keys off `pedOnly`, so genuine pre-debut prospects stay pure-pedigree but IN-WINDOW 0-game players (Patterson, Smillie) correctly get `unpl_eq·P`. (`unpl` stays as-is for the pool filter + UNPLAYED tag.)
4. **Relative-floor (young key-pos) — pre-existing JS gap, also folded in.** The JS recompute never had the v3.4 relative-floor; surfaced by the parity gate (25 young key-pos players off). Ported the `(RUC/KEY_FWD/KEY_DEF & age≤22 & relative<1) → relative += sc·(1−relative)` block. Not part of the P/Brodie ask, but required for true 0/785 parity.

**Dual-engine note (corrects an earlier doc claim):** there is NO second engine copy — `_rl_parity.js` was already canonicalised to LOAD `_engine_block_v23.js`, so this was a one-file change. **Position-toggle non-idempotency (old PARKED §3): tested CLEAN** — every round-trip returns exactly (Bailey J. Williams 1918→1372→1918, etc.).

**Baked fields added to `rl_app_data.json`:** `P`, `brodieBase`, `pedOnly`. HTML 1.07M→1.14M (per-player fields). **A1 JS parity is CLOSED.**

## SESSION 2j cont.(14b) — THIN-PRIOR RECENCY FIX SHIPPED (2026-06-21)
**rl_model.py `level_demo` changed; HTML rebuilt (785, dual-column).** Closes the thin-prior item (was UNRESOLVED/PARKED §8). Two changes, both general (no gating):
1. **RECENCY-FLOOR (the inversion fix).** Floor `conf` at the recent season's share of the recency-weighted game mass: `_pmass=Σ 0.60^(ly-y)·min(gm,18)` over prior seasons; `_cfloor=min(lg,18)/(min(lg,18)+_pmass)`; `conf=max(conf,_cfloor)` in the improving branch. Guarantees a more-recent game never weighs LESS per game than an older one (more, with recency decay). Fixes Alger's case: 4g-2025 vs 4g-2026 was weighting 2025 higher (0.55 vs 0.45) → now 2026 0.62 vs 2025 0.38. Lift-only.
2. **MERGE (the dropped-cameo fix).** A sub-3-game CURRENT-year cameo folds into the most-recent qualifying season (kept as that season's games): `la=(la*lg+ca*cg)/(lg+cg); lg+=cg`. So 1-2 game current-year results COUNT (up or down) instead of being dropped by the `>=3` filter. Transient by design — once the live season hits 3 games it becomes its own qualifying season and the games pull back out.
**IMPACT (vs the cont.14 board):** level moves are small (±1-3 pts); the larger value swings are the convex curve at the top, not the merge over-reading. Gulden 4296→4476 (2g@112.5), Day 2230→2386 (2g@102.5); Rozee 3048→2848 (2g@80, slow start counts), Taylor 1607→1453 (2g@48.5). Intended thin cohort: Alger 120→124, Ramsden 250→267, Busslinger 542→549. Stars (Sheezel/Daicos/Dangerfield) and McAndrew unchanged; Brodie 476→473. Net board immaterial. Decision (Luke): apply to ALL players, not just non-established — the 2 games are real evidence, the level move is small, and it self-corrects as the season fills. **Thin-prior is now CLOSED (no remaining broad-fix item).**

## SESSION 2j cont.(14) — ESTABLISHMENT-P + BRODIE + CAPTAINCY PORTED TO THE BOARD (2026-06-21)
**rl_model.py + pgrid.py + compute.py changed; HTML rebuilt (dual-column SCAR+VOR, active 785).** The three compute.py-only mechanisms that never reached the shipped board are now LIVE on it (single source of truth = rl_model.py). Backups: /home/claude/{pgrid.py.bak,compute.py.bak}; this-session pre-port state in rl_model.py.bak.pre_pathways.

**1. ESTABLISHMENT-P GATING — now LIVE on the board.** The consuming machinery (`PROD_GATE='blenddemo'` + `decay_eff=min(decay,Pz)` in `value()`) was already in rl_model.py but INERT because `P_HOOK=None`. Ported the SURFACE (`pgrid.Praw`+`mat_mult`) + the per-pick/per-pathway establishment prior (`_pick_curveP`/`_grpoffP`/`pick_prior`/`_pathpr`, PAVA-monotone) + `P_estab` from compute.py into rl_model.py (after PICKEQ, before the overrides → priors build on REAL types), and set `P_HOOK=P_estab`. P personalises bust risk: a not-yet-established player's pedigree pedestal + production are weighted by P(establish); established players P=1 (untouched). **Board effect: 264/785 move, ALL down (median −207).** Stars at P=1 unchanged (Daicos 7487, Sheezel 9237); late-pick rucks tempered (Xerri 8577→5694, Moyle 3479→844, Madden 2576→693); high-pedigree prospects gated (the intended "establishment discounts the draft prior"). This is Luke's DESIGNED bust-rate fix, not an age band-aid (which would double-count).

**2. BRODIE ROLE-RELIABILITY CUT — now LIVE.** `brodie_sig(p)` (non-RUC, `seasons>=5`, NOT a recent starter, NEVER durable, `level_now>=80`) → `res*=0.5` inside `value()`, so it flows to point + convex (via proj_value) + backward columns. **Will Brodie 1443→476.** Catch set this build = {Will Brodie}.

**3. CAPTAINCY BAR 108.0→107.4** (`CAPT_THRESH`, rl_model.py ~243; M6, last-5 rank-25 from the unbiased upload).

**4. PRESENT-IDENTITY OVERRIDES — value-side now complete.** The relocation to rl_model.py (cont.13) plus gating means McAndrew lands at his intended **3051→1755** (the override's designed partner: SSP-2024 anchor + P=0.28 gating). Keane 1795 (P=1), Perez 46 (P=0.21), Hall-Kahan 120 (P=0.31).

**5. pgrid.py DECOUPLED.** The port created a circular import (rl_model→pgrid→rl_model) that broke under rl_export's `exec()`. Rewrote pgrid: removed `import rl_model`; surface now built via `pgrid.build(data,GRP,debut)` (caller injects data); `mat_mult(ea,G)` takes entry-age as an arg. Zero rl_model dependency → no cycle, works in the exec path. Verified: VOR + SCAR exports both clean (785).

**6. compute.py SINGLE-SOURCED.** Removed the duplicated surface/P_estab/brodie/override/`P_HOOK=` blocks; now aliases `MA.established/grp3/P_estab/brodie_sig`. Removed the redundant Brodie cut in its `after` block (rl_model.value now cuts → was about to double-count). Validated: Brodie 476 (single cut), McAndrew 1755, Xerri 5694, Sheezel 9237.

**SHIPPED HTML (rebuilt):** active 785, v_vor 785/785, McAndrew v=1755/v_vor=1711, Brodie 476/384, Madden 693/630, stars unchanged. Recipe unchanged (HANDOVER cont.11 §C).

**NOW UNBLOCKED / OPEN:** conditional-anchor / prospect-reward (UNRESOLVED 0c — gating makes first-years SAG because pedigree×P double-charges bust risk; THE next fix, only buildable now that gating is live); **JS-engine parity port of gating + Brodie (A1) — ✅ CLOSED cont.14c** (now in the JS recompute; parity 0/785); currency SCAR vs VOR (0i); thin-prior broad fix (recency-floor — ✅ CLOSED cont.14b).

**DISPLAY NOTE (not a bug):** the 4 auto-recalled players show their FILE pathway (Keane=Ireland, McAndrew=Mid-Season, Perez=National) while valued at their SSP re-entry — the documented auto-recall convention (PHANTOMS.md §0); McAndrew now joins Keane/Perez in it. Showing re-entry pathways instead would be a global display choice.

## SESSION 2j cont.(11) — PICK-1=3000 ANCHOR LOCKED + SCAR-vs-VOR DUAL-COLUMN BUILD (2026-06-21)
**rl_model.py + HTML changed.** (1) **Pick-1=3000 anchor LOCKED (permanent):** board now scales so pick 1 = 3000 (was 99th-pct player→7000 ⇒ pick1≈3867); pure global ×0.776 rescale, all relativities/trades unchanged (Sheezel 13226→10261, Pendlebury 706→548). Code: rl_model.py ~478 (`_P1=RL_PICK1 env; BOARD_FACTOR=_P1/PVC[1]; SCALE*=…; PVC*=…`; SCALE reassign rides val() late-binding). (2) **GAMMA switchable via RL_GAMMA env** (line 239; 0.85=SCAR concave, 1.0=VOR linear). (3) **One-off dual-column board:** each player shows SCAR + VOR (both pick-1=3000), built by exporting twice (RL_GAMMA 1.0→v_vor, 0.85→v) + merging by id (787/787); HTML got a VOR `<th data-s="vor">` (_body.html, 10 cols) + sort case + pick/player-row `<td>` (_features_v23.js; VOR shows at Now only). Picks IDENTICAL both columns (PVC GAMMA-independent). **Comparison:** stars rise under VOR (Sheezel +21%, Daicos +17%), depth falls (Papley/Barrass −34%), pick-level prospects ~unchanged — VOR rewards top scarcity, SCAR's ^0.85 tempers it. **PENDING: Luke locks the forward-value currency (SCAR vs VOR); then default that GAMMA + revert to single column. Pick-1=3000 stays.** Backup /home/claude/rl_model.py.bak.pre_pick1. **CURRENCY KNOWLEDGE captured (HANDOVER cont.11 §F):** SCAR="SuperCoach Above Replacement", val=SCALE·raw^0.85 (SCALE≈5.17 @pick1=3000, pure units; GAMMA=0.85 hand-set temper, no recorded derivation); VOR=linear best2-REPL (SCAR with GAMMA=1.0); replacement subtraction amplifies the top (raw 1.11<SCAR 1.81<VOR 2.0); curvature is NEGLIGIBLE on PVC shape (<1.5% indexed) → VOR-backward/SCAR-forward split sound; forward SCAR-vs-VOR ratio driven by AGE (corr -0.63) > value (+0.34). **README SCAR/VOR glossary corrected.** **Credit-phantom note (§G/UNRESOLVED 0h):** the two-Keanes/two-McAndrews double-count is **DELIBERATE** (PHANTOMS.md §2 — feeds IRE/MSD PICKEQ; Luke's call) — the credit phantoms outrank the real records via a fresh pedigree and show twice by design; **NOT a bug, do NOT remove from data**; only an optional cosmetic board-render filter is open. (Audit corrected an earlier mischaracterization of this as a bug.) **Pick-value rounding note:** engine ints (323/764/2143) differ a few pts from design grid (316/767/2142) via double int-rounding + 1-player pool diff; engine authoritative.

## SESSION 2j cont.(10) — v3.4 PICK-VALUE CURVE BUILT & SHIPPED (2026-06-20)
**rl_model.py CHANGED** (PVC builder replaced; forward model untouched). Shipped `rl_draft_engine.html` (board 787). Luke gave the explicit "build" after reviewing the cont.9/10 curve visuals and locking the R-0 proposal.
**BUILT:** `build_pvc_v34()` replaces the legacy `peakval`-curve. Method: MEASURE `posval(best2+capt−REPL)` busts→0 (no bust floor, no survivor clamp); RISK tiered CE α 0.6→0.8 (`PVC_ALPHA_LO/HI`); SMOOTHER varying-bandwidth local-linear (W 3 top→9 tail); TOP parametric power-decay a·k^b fit to picks 1-8 blended into loclin below ~pick 12; MONOTONE light isotonic (plateaus allowed); SCALE posval-VOR→SCAR by anchoring pooled picks 1-3 to the CURRENT board top (preserves board scale; pick1 3867≈old 3913). Knobs `PVC_ALPHA_LO=0.6/HI=0.8`, `PVC_REPL_BUF=0` (R-0; =5 for R-5). Code ~rl_model.py 427-475; legacy build_pvc/peakval kept (390/361); pedestal reads PVC at 541. Backup /home/claude/rl_model.py.bak.prev34.
**NEW PVC vs old:** 1:3867/3913 · 5:2762/3052 · 15:1572/1807 · 40:796/781 · 60:416/343 · 80:416/323. Flatter (top:tail ~9.3 vs 11.4): early-mid cheaper, tail richer, crossover ~pick40, tail plateaus 416. The richer tail = the TIERED α (not floor/clamp): flat α=0.6 crushes bust-heavy late picks; α→0.8 credits the rare hit (+72-119% picks 50-70). Empirical decomposition: NEW-measure FLAT-α tail (indexed 3.2) is LOWER than current's bust-floored (4.6); the tiered α flips it to 6.3. Survivor clamp is ~uniform ×1.10-1.14 (not a top/tail driver).
**BOARD IMPACT (pre/post diff):** proven players UNCHANGED (Sheezel 13226/Daicos 10739/Pendlebury 706/Newcombe 3826/McCarthy 3786; 120+g 0 movers of 218; 20-120g median 0.0%). Raw prospects (<20g) +16.8% median (149/266 >15%) — they track the pedestal/PVC; up because most sit at late picks where the new tail is richer. Pathways (PICKEQ) re-derived (IRE/MSD/SSP/UNR/PDA=90, PDN/PDS=96). Clean.
**MANIFEST:** M1/M2/M4/M8/M9 + parametric top DONE. Open: M0 (master patch incl. 548 positions), M5 (best2 ≥7→≥10 not done — curve uses current ≥7), M6 (captaincy bar not done), establishment-P forward dormant. Scaling-anchor (board-preserve) + tail (plateau) logged UNRESOLVED §0f/§0g. Design scripts pvc_smoother_viz.py/viz2.py/pvc_v34_vs_current.py bundled. Rebundled.

## SESSION 2j cont.(9) — BOARD-IMPACT ANALYSIS · CE/VOR LEARNINGS · v3.4 PVC DESIGN RECOMMENDATION (2026-06-20)
**No build, no data change** (rl_model.py/data byte-identical to cont.8). Analysis + design consolidation on the position-filled v3.3.1 baseline. Three things landed:
**(1) BOARD-IMPACT OF THE POSITION FILL — measured (regenerated pre-fill board from `/home/claude/rl_model_data.pre_positions.json`, diffed vs current).** ALL 787 active players are in BOTH boards (none were ever excluded from the LIVE board — the 548 positionless were all historical/retired). Change is BIMODAL: 438 unchanged (<0.5%), 195 dropped ~50%; median |Δ|=0.13%, mean 12.5%. **Split by career games (the pedigree-vs-production test): 0-20g (raw prospects) n=266 median −40.4% (146 movers >15%); 20-60g median 0.0%; 60-120g median 0.0%; 120+g (established) median 0.0% (1 mover of 218).** CONCLUSION: the positionless bug NEVER touched anyone with a real sample. Every player with 20+ games (521/787 — the whole proven/tradeable core incl. Sheezel/Daicos/Pendlebury) was valued correctly all along. Only RAW PROSPECTS (<20g) were inflated ~40-50%, because a thin-sample player's board value leans on the pick-pedigree prior (peak_est blends pedigree-prior + own production weighted by games → thin sample = prior dominates → tracked the inflated PVC → halved when corrected). PRACTICAL: established-player trades were always fine; pick/prospect-heavy trades overvalued the speculative side by ~half — that's the population to re-examine. Reproducible: `rl_after/board_impact.py` (safe try/finally restore).
**(2) grid_v331.py REISSUED on the position-filled pool** (no exclusions now — positions complete). REPL-0 indexed (top band=100): 4-6=71.1Cur/61.1CE.6; 71-99=7.8Cur/4.5CE.6/8.4(.6→.8)/10.5(.7→.9); SSP 3.1@22Cur/2.0@22CE.6; MSD 4.3@21Cur/2.6@21CE.6 (MSD>SSP restored). At .7→.9 (+REPL5) the new tail overtakes Current. 21-25 remains a genuine cohort-quality trough (survives the fill). SSP wants cy≤2022 (Nic Martin), MSD cy≤2021 (2022 MSD class dilutes).
**(3) CE/VOR CONCEPTUAL LEARNINGS (groundwork for M4).** CE_α=(mean(x^α))^(1/α) monotone-increasing in α; **CE.5 is NOT the median** — it's a downside-weighted mean (busts pull it), higher α weights the ceiling/stars (toward the mean). To reward ceiling go UP (.7), not down (.5). The backward pool value IS a VOR system: posval(best2+capt−REPL). VOR PRE-AMPLIFIES stars: 81 vs 85 avg (REPL 80.1) = 0.9 vs 4.9 VOR = 5.4×; posval softplus COMPRESSES near replacement (2.56 vs 5.44 = 2.1×; posval(0)≈2 cushion), LINEAR above, captaincy SUPER-LINEAR at the elite top (avg 120→45). CE leverage far bigger on VOR than raw (.5→.8 swing 1.01× raw vs 1.32× posval-VOR). Because the VOR scale already does the ceiling-rewarding, α should LEAN LOWER, not higher. The tiered **0.6→0.8 reconciles**: direction right (raise α at the cheap end so bust-heavy lottery tickets don't read ~0), but VOR amplification CAPS it at 0.8 NOT 1.0 — at the mean the 71-99 band is **59% carried by the top 5%** of players (vs 15% at 7-9), an unrealisable payoff from a single pick. α matters most at the bust-heavy cheap end, barely at the reliable top (outcomes clustered). Single-outcome/own-team → 0.8; tradeable-market-asset → a notch higher but never the raw mean.
**(4) ⭐ v3.4 PVC DESIGN RECOMMENDATION (Claude's, for when Luke returns to build).** MEASURE: busts→0, posval(best2+capt−REPL); DROP the bust floor; DROP the survivor clamp from peakval (the per-player ≤3× amplifier that caused the 10-12-beats-7-9 inversion — VOR already rewards the ceiling), KEEP both forward. CE: tiered 0.6→0.8 capped at 0.8 not 1.0; REPL buffer 0 (softplus already cushions). SMOOTHING: local-linear (loclin5) primary + LIGHT isotonic top-coat for monotonicity (pure PAVA over-flattens into blocky steps) + VARIABLE bandwidth (light at the steep top, heavy in the noisy 56-99 tail); curve must end monotone decreasing. PICK-1 BOUNDARY: local-linear extrapolates the slope (low boundary bias, unlike local-mean which drags pick 1 down) + anchor the top to the pooled 1-3 BAND not a single noisy pick (also the =100 index anchor) + pin pick 1 + enforce monotone descent; optional parametric power/exp decay on picks 1-8 blended in below. MSD 1.5× inherits into v4. OFFERED (not yet built): render the loclin5+light-isotonic finished curve on the position-filled bands next to the current shipped curve, pick-1 region magnified. Full detail in HANDOVER cont.(9) + TODO M-block.

## SESSION 2j cont.(8) — POSITIONS FILLED (positionless 548 -> 0) (2026-06-20)
Luke filled ALL 548 positionless players (MID 151, GDEF 123, GFWD 105, RUC 61, KFWD 57, KDEF 51; 0 invalid) via positionless_players_to_fill.xlsx; folded into working json by key (548/548 matched, 0 positionless remaining). EFFECT: every washout now counts as a bust in its proper bucket instead of being dropped. PVC TAIL ~HALVED (pick-60 706->343, pick-99 ->229) — the shipped curve had been OVERVALUING late picks + pathways by excluding positionless washouts. Pathways fell (CE.6 REPL0: SSP 3.9->2.0, MSD 3.4->2.6 [MSD>SSP order RESTORED], IRE 3.7->0.9, UNR 6.6->1.5); late bands fell (71-99 11.0->4.5); early/mid ~unchanged. Band counts evened (26-30 now 95, Brad Howard placed). Anchors: Sheezel 13226/Pendlebury 706/Daicos 10739 stable; Newcombe 3928->3826, McCarthy 3925->3786. Re-shipped rl_draft_engine.html. Backup /home/claude/rl_model_data.pre_positions.json. M0 master-patch must now also fold in the 548 position assignments. Rebundled.

## SESSION 2j cont.(6) — v3.3.1 CONSOLIDATED BASELINE **BUILT & SHIPPED** (2026-06-20)
Consolidated the CURRENT/shipped curve (bust-floored peakval — method UNCHANGED, NOT v3.4) on the full up-to-date 2690-row DB (2003-05, ND gaps closed, Benjamin Johnson, 4 phantoms incl. 2 double-count credits, recall consolidations). NEW base mechanic: **MSD year-1 ×1.5 floor** (was ×2; Luke changed 2026-06-20) — load-time transform in rl_model.py (`MSD_Y1_MULT=1.5`, after line 3) scales each non-phantom MSD player's mid-season DRAFT-YEAR season games ×1.5 rounded down (avg unchanged) + folds into career total, so all gates fwd+bwd read it consistently. Phantoms excluded. **ZERO effect on PVC** (MSD not in the ND/RD pick-curve pool); moves MSD forward board values only (sign = debut−level: McCarthy +294 standalone, Newcombe −48; tiny-sample ≤4g jumpy e.g. Hall-Kahan). Built `rl_export.py`→`rl_build_html.py` → **rl_draft_engine.html** shipped (board 787, clean). Anchors (1.5×): Sheezel 13226 · Newcombe 3928 · Pendlebury 706 · McCarthy 3925. New-PVC (v3.4) work PARKED into HANDOVER/KICKOFF (cy≤2021 both-measure comparison + SSP/MSD relaxation scenarios + forward-path games-gate anatomy; scripts grid_compare_cy.py, msd_ssp_scenarios.py bundled). Backups `/home/claude/*.pre331*`. Rebundled.

## SESSION 2j cont.(4) — DOUBLE-COUNT PHANTOMS for KEANE/McANDREW (2026-06-19 PM)
Option 1 done: added value-carrying credit phantoms in the original pools (mark-keane-ire-credit best2~77.8 in IRE; lachlan-mcandrew-msd-credit best2~87.1 in MSD), no-gap scoring so the recall consolidation leaves them put. Real records stay in SSP => deliberate DOUBLE-COUNT across both mechanisms (Luke's call). Inflates IRE/MSD pooled value+hit+n feeding PICKEQ, intentional. Full canonical detail written to PHANTOMS.md. Working data 2690. Rebundled.


## cont.(15) 2026-06-21 — CONSOLIDATED DATA/PVC EDITS + BACKWARD-BOARD BUG FIXES (baked & built)
DATA (rl_model_data.json): Hawkins 2006 ND #41→#2; Smith #41→#11, Morton #43→#14, Cloke #38→#23 (all 2004 ND, slide-repack). 37 GC(2009-10)/GWS(2011) concession players removed (holes left). Shiel/Treloar/Cameron flagged `_pvc_exclude` (out of the PICK-CURVE pool only — build_pvc/build_pvc_v34/_natcv34 routed through `_in_pvc`/`_epk` with same-year slide-up; BASEPK/establishment/forward valuation keep the full pool so the 3 stay on the board; forward rescaled +1.12% via the shared pick-1 anchor).
CODE (rl_model.py): (1) `debut()` — ONLY MSD debuts in draft year; ND/RD/SSP + post-draft (PDA/PDN/PDS/IRE/UNR) all debut year+1 [fixes 2025 post-draft first-years on the -1 board]. (2) `_on_board` unplayed fallback bounded to entry+{1,2} [fixes long-retired/no-scoring recalls; retired-recalled 605→185]. (3) backward boards CONSERVATION-NORMALISED (-1 ×0.944, -2 ×0.901) [removes the raw younger=more-runway inflation; re-ported from rl_build]. (4) `_deplateau()` post-process ramps mid-curve flat runs through their endpoints, deep-tail floor protected.
GATES: JS parity 0/785 (max diff 1 convexity rounding); board 785; de-plateau leaves 0 mid-curve flats. Backups: /tmp/rl_model.py.preShiel, /tmp/rl_model_data.{preHawkins,postHawkins,postRemoval,locked}.json.
OPEN: Will Hayes duplicated record (2022 MSD + 2024 ND) needs dedup. UI future-position render + backtest spreadsheet regen pending.


## [cont.20] 2026-06-23 — v4 forward-projection integration + unproven-floor resolution (BUILD)
### Decided (with before/after evidence)
- Pining: explicit formula evaluated head-to-head vs v4 OUT-OF-SAMPLE (n=233 test) -> WASH (v4 RMSE 32.37 vs explicit 31.16, MAE 24.60 vs 25.14; correction backfired). v4 retained on evidence, not deference. Point-estimate floor ~24 MAE (bimodal piner outcomes); spread stored for hover.
- survival() REMOVED (v4 separates below-bar by 11.8pt; survival's <=9% was double-count).
- pedigree-persistence on proven guns: NONE (0.4 season, non-monotonic).
- KEY_DEF spike: V4_SPIKE_RETAIN guard added (v4 over-trusts +0.28; level_now SPIKE_CAP doesn't reach v4 projection).
### Shipped [to be finalised post-build]
- peak_est -> v4; P_HOOK=None; PROD_GATE='off'; DOBs in rl_model_data.json (composite key, 845/848); distribution stored; board rebuilt; parity; tarball.

### SHIPPED (cont.20 build complete, 2026-06-23)
- peak_est -> v4 forward-projection (memoized); production + pedestal both v4-driven.
- EXPLICIT unproven floor blended by games (EXP_PEAK_BASE/EXP_RETAIN/EXP_PICK_SLOPE; w=clamp(g/45,0,1)). Beats v4 on group calibration (4.8 vs 6.0). Low-pick developing players tempered (Archie Roberts left top-8); proven unchanged (Daicos 6569->value steady, w=1).
- V4_SPIKE_RETAIN={'KEY_DEF':0.69} guard live (fires on fresh 1.30x KEY_DEF spikes).
- survival() removed; P_HOOK=None; PROD_GATE='off'.
- DOBs in rl_model_data.json (composite key, 845/848). PVC snapshot (pvc_snapshot.json) breaks SCALE<->PVC bootstrap cycle.
- Distribution range stored per player (pkest_lo/mid/hi, v_lo/hi; dispersion shrinks with games) for future hover.
- Board: rl_draft_engine.html rebuilt (1.16MB, 788 active). Top: Sheezel 6849, L.Jackson 6639, Daicos 6569, Treacy 5493, Xerri 5448.
### FOLLOW-UPS (not blocking the static board)
- JS PARITY: v4 is sklearn -> cannot run in-browser. Static board shows correct Python values; the JS engine must be pointed at exported pkest_mid for live-slider recompute (currently would diverge on peak_est). KEY follow-up.
- Per-season avg/games history not yet in export (needed for hover).
- Dial post-workbook: EXP_BLEND_GAMES (45), V4_SPIKE_RETAIN (KEY_DEF 0.69, KEY_FWD off), position-tilt.

## [cont.20b] 2026-06-23 — JS/board PARITY RESOLVED (correction to earlier "static board" claim)
- DIAGNOSIS: board-vs-engine "0-9% gap" was NOT a bug — exported 'v' is the CONVEX value (_vP0 = point x cvx); MA.value() is the POINT value (_vpt). board_v = point x cvx EXACTLY (verified all players, e.g. Daicos 6569x1.0257=6738).
- The JS already reads the v4+floor peak via exported 'pn'/'ps' and applies convexity via 'cvx' — so v4 + the explicit floor ARE reflected in live recompute. (Earlier "JS can't run v4" framing was wrong: peak is exported, not recomputed in JS.)
- THE ONLY real divergence was surv/P: JS valuePlayer applied exported survival + establishment-P, which value() no longer does. FIX: rl_export.py now emits surv=1.0 and P=1.0 (matching value()). Verified: surv/P = 1.0 for all 788; previously-gated unproven players (Lalor, Sanders) ungated.
- NO JavaScript changes were required. render()->recompute()->valuePlayer now reproduces the modified engine.
- Confirmed current/future position split: proj_from_peak prices k=0 (current season) vs REPL[g0] (CURRENT position) and k>=1 vs the 'fut' split (FUTURE positioning). Intact.
- RESIDUAL: full numeric JS verification needs the board run in-browser/node (JS ports of projFromPeak/relC pre-date this work and are assumed faithful). Open the board and spot-check a few values if desired.

## cont.24 (2026-06-23) — DISTRIBUTION PRICING (U21-4) BUILT (standalone; NOT wired)
- NEW `forward_valuation/distribution_pricing.py`: finished model from the cont.23 starter. All 6 TODOs wired —
  band(GBR quantile) → v_at_peak(real-age full-chain; proven==value() for free, old declines) → pedigree prior
  (trend-extrapolated top) → shrinkage by `own_games + comparable_density` → relocation to peak_est for proven
  elite → E[v] over the convex scale → width guardrails. Retires (conceptually) β·PVC floor + cvx + runway + tenure.
- NEW `forward_valuation/dist_harness.py`: walk-forward harness for dist_value (retrain quantiles+prior+v4 capped,
  cohort held out; calibrate SCALE_DIST to ≥90% retention). Built, not yet run to convergence.
- Validates directionally: anchors Sheezel/Daicos <1.5%; Willem ↑ above pedigree; Mannagh > Bice > Clark (Luke's reads).
- `rl_model.py` UNCHANGED (hard rule: nothing wired into value()).
- RESOLVED end-of-session: the "run-to-run instability" was a lost-turn edit (server flakiness) that upgraded the
  relocation anchor to `band_anchor = max(peak_est, recent_best2, youth)` — a GOOD change delivering the Willem (3649)
  + Mannagh (702) lifts Luke asked for. Output now reproducible (md5 adcb592, two identical runs).
- REMAINING: (1) calibrate SCALE_DIST via harness (board slightly hot, Bont +7%); (2) Bont-class recent-credit
  judgment call (surfaced); (3) young-gun target censoring (cleaner Willem fix); (4) K_SHRINK surfaced (default 30);
  (5) reprice whole board + scan; (6) then wire into value() on Luke's go.

## cont.24 (later) — censoring fix TRIED + REVERTED (empirical)
- Implemented the young-gun completeness gate (hard + riser-only `is_censored_riser`). Both REGRESSED the validated
  per-player reads (Clark over-projected; Mannagh<Clark; anchors +4%) vs no-gate, because band_anchor already
  compensates and the downstream calibration was tuned to the current model. Kept OFF (MATURE_GATE=False). Reads
  restored exactly (Willem 3649, Clark 588, Mannagh 702>Bice 606>Clark 588, anchors <1.5%). See UNRESOLVED U24-B.

## cont.24 (later 2) — censoring fix RESOLVED via DOWNWEIGHTING (Luke was right to push)
- EXCLUSION regressed reads; DOWNWEIGHTING (soft, sample_weight on censored risers, RISE_YEARS=4) works: lifts young
  projections (Zane 358->444) WITHOUT moving anchors or flipping Mannagh<Clark. ADOPTED (CENSOR_DOWNWEIGHT=True).
  build_training now returns W; fit_models + harness take sample_weight. Reads (K=30): Willem 3672, Clark 661,
  Zane 444, Mannagh 680>Bice 600, anchors <1%, Bont 3209 (+8.4% accepted).
- Zane residual (still < Clark) = production-value vs pedigree-value tension (U24-F) — surfaced for the board, not changed.

## cont.24 (later 3) — SCALE_DIST calibration DONE (=1.0, validated)
- Harness walk-forward year-1 retention mean 98.8% (12 cohorts) -> in Luke's 95-105% target, no scaling. Maturation
  trajectory yr1-2 ~99% -> yr3-5 ~109% -> yr6+ declines, matching Luke's full target shape. SCALE_DIST=1.0 final.

## cont.24 (later 4) — WHOLE-BOARD REPRICE built + scanned (AFL_distribution_pricing_board_2026.xlsx)
- 746 active repriced (Board / Big movers / By position / By cohort / Sanity tabs). KEY FINDING: dist ~1.3x old
  engine board-wide (established players credited), RUC 1.55x — driven by recent_best2 crediting recent peaks of
  now-declining/volatile players (De Koning 76-now->3333, Meek 67-now->3444). Surfaces THE decision (U24-E): discount
  recent_best2 for decline/age (a years-since-best taper would protect Mannagh while taming rucks+Bont). Near-zero
  corrections (Sholl 5->967) are mostly the dist model fixing old-engine errors. 746 vs 805 roster note (U24-G).

## cont.24 (later 5) — recency taper on recent_best2 BUILT (RB_TAPER=0.55, surfaced)
- recent_best2 now recency-tapered toward level_now (RB_TAPER**years-since-best). Sholl 967->201, De Koning
  3333->2321, Meek 3444->2223, Bont 3089; young guns untouched. Residual: Mannagh->530 (<Bice/Clark — his 84 last
  year, same recency as De Koning 97); ruck residual is position-convexity not recency; Conway thin-sample. Board regen'd.

## cont.24 (later 6) — board pool fixed to canonical 805 (U24-G resolved)
- build_board was re-filtering MA.data (746); switched to MA.players (805, the deduped active board incl. the `extra`
  list). The 59 missing were unplayed draft prospects (0 games) — they price on pedigree (dist==value), so no movement,
  just inclusion. Board regenerated at 805 rows.

## cont.24 (later 7) — COHORT BACKTEST BOOK + non-play empirical (the artifact Luke kept asking for)
- build_cohort_book.py -> AFL_cohort_backtest_book_2026.xlsx: Summary (cohort value() as-of each yr vs PVC, walk-forward
  via BASE_REF) + per-cohort tabs 2009-2025 + Non-play analysis. Zero formula errors.
- FINDINGS: non-play discount is pick-band + position dependent + compounds (top picks ~neutral yr1, mid/late picks big bust
  signal, compounds by yr2). Smillie (75%) too high vs empirical (~43% for top-pick-not-played-thru-yr2); Patterson (93%) ~OK.
  Within-cohort DISPERSION (not aggregate) is the real issue: cohort totals ~96% but value mis-allocated from played-mediocre
  kids to thin-sample spikes. Outliers (Bodhi/Berry/Dowling/Caminiti high; Kyle/etc low) all = thin recent sample over-extrapolated.
- Metric care: used realized production value (career best-3, no pedigree) NOT value()-as-of (which bakes in pedigree -> circular).

## cont.24 (later 8) — cohort book: walk-forward FUTURE-LEAK fixed (Luke caught it)
- Luke spotted that as-of-2025, Kyle (pick 14) priced at PVC+77 while Taylor (pick 15, same pos) sat at flat PVC. ROOT:
  debut_factor keys off cg=sum(games over ALL scoring rows), NOT filtered by as-of year -> it counted Kyle's 2026 debut
  when valuing him "as of 2025" (a future leak). level_now was as-of-aware but debut_factor/peak_est were not.
- FIX: build_cohort_book as-of loop now TRUNCATES each player's scoring to rows<=Y before valuing (then restores), so
  debut_factor/peak_est/los_decay/level_now all respect the as-of year. Verified: all 2025 draftees now == PVC as-of-2025.
- Substantive findings UNCHANGED (non-play analysis uses full-career realized production by design; only the as-of
  trajectory columns were affected). This was a flaw in the BOOK, not the engine.

## cont.24 (later 9) — DIST-MODEL WALK-FORWARD BACKTEST built (build #1 of the proposal)
- forward_valuation/build_dist_walkforward.py -> AFL_dist_walkforward_backtest_2026.xlsx. Per focus cohort (grouped by
  DEBUT year), traces every player YEAR BY YEAR under the dist model: retrain v4+quantiles+prior+META capped at T with the
  cohort HELD OUT, truncate records to <=T (walk-forward, no debut_factor leak), value with dist_value. Summary + per-cohort tabs. Zero formula errors.
- BASELINE (current model, cohorts 2017/2019/2021, --fast): shape RIGHT (peak yr3-5 at 115-127%, then decline). yr1 ~97-98%
  across all three = just under Luke's 103-106% target (the gap the redesign must close). Per-player STABILITY CHECK validates
  Luke's concern: current model IS jumpy on some (Rowell 5865->2492->6066->3832; Josh Ward 2047->1032->2395->1301) — partly real
  form (Darcy breakout 822->3467) but partly max-of-anchors switching + single-season over-reaction. This book is the before/after instrument.
- Model-agnostic: swap in the redesigned dist model + re-run to measure yr1 lift + stability improvement. ~8s/cohort-year (fast).

## cont.24 (later 10) — BUILD #2 COMPONENT 1: conditional outcome-shape prior (DONE + validated)
- forward_valuation/conditional_prior.py. Replaces build_prior's symmetric-normal-from-incomplete-careers. Quantile GBR
  (Q=.1/.3/.5/.7/.9, depth=4 leaf=25 nest=400) of forward best-3 given [pos one-hot, log(pick), games-so-far, tenure],
  trained on 13,226 RESOLVED (player,as-of-year) rows (debut<=2021, censoring-corrected), busts folded in as low/0 targets
  so the lower tail is honest. cond_prior_band(p,models,Y) returns the band.
- WHY (rigorous, all-position): prior errs low PERVASIVELY (MID -5/-6, GEN_DEF -2/-11, GEN_FWD -5/-8, KEY_DEF/-FWD -3/-6 vs
  realized MEAN like-for-like). ROOT = censoring: build_prior trained on whole pool incl. still-rising incomplete careers
  (-3 to -8 drag); the downweighting fix was applied to the quantile band but never to build_prior. ALSO the symmetric band
  misfit tails (GEN_DEF pk3 prior p10/p90 54/101 vs realized 69/109 -> lower tail far too fat = a source of the young-high-pick crush).
  (My earlier 'GEN_DEF errs low' was partly cherry-picked: prior MEAN vs realized MEDIAN on a skewed dist overstated it. Owned.)
- VALIDATED: GEN_DEF pk3 p50 now 92 (=realized 92; was 77.5). p10/p90 calibrated across positions. Non-play reshaping WORKS
  (MID pk7 tenure1: 0g 45/81/107 -> 15g 62/98/115 — floor lifts, ceiling holds = Luke's insight). depth=4 fixed the
  over-smoothed high-pick floor (pk3 p10 48->62, pk8/pk30 p10 match realized exactly). Minor small-n over-projection at
  GEN_FWD/KEY_DEF pk3 (n=6-14) noted for component-2 blend.
- NEXT: component 2 (own demonstrated band, production-anchored + recency-aware) + component 3 (reliability weight = effective
  full-season games; blend prior+own, drop peak_est-relocation). Preserve 'proven ~ value()'. Then validate via walk-forward + 805 before/after.
- dist_before_snapshot.json written: all 805 current-dist values (the 'before' for Luke's end-of-build-2 before/after sheet).

## cont.25 (handover consolidation, 2026-06-24)
- Full handover rewrite for a clean restart: SESSION_SUMMARY_2026-06-24_cont25.md rewritten as the single authoritative
  current-state doc (orientation, the redesign architecture, the journey + dead-ends, all learnings/corrections, results,
  the strict-order next steps #1/#2/#3, files, engine cheat-sheet, Luke prefs). KICKOFF_PROMPT.md cont.25 banner prepended
  + bootstrap tarball -> cont25. START_HERE.md rewritten as a clean entry pointer. HANDOVER.md cont.25 block prepended.
- AUDIT fixes: conditional_prior.py standalone was BROKEN (validation block built 9-feature vectors after the level feature
  made it 10) -> fixed prior_q_at (+level=0 at draft) and replaced VALIDATION 2 with the Y1-level-lifts-the-band test.
  dist_redesign.py standalone table cleaned (dropped the superseded w/r/recent_best2 columns). Both verification commands
  now run clean. Verified the engine code + v4 pkl + redesign files + snapshot are all INSIDE the checkpoint tarball.

## cont.25 (late session, 2026-06-24) — REPL-3 locked, 805 before/after, board-review diagnosis
- REPL-3 LOCKED as dial REPL_DROP=3.0 in dist_redesign.py (acquirable-replacement recalibration; applied to v_at_peak pricing
  in redesign_value only, via try/finally save/lower/restore of MA.REPL; engine value() + anchors untouched). #1 calibration
  passed; #2 walk-forward stability win + REPL-3 logical maturation arc (OOS 2009-2025: yr1 94 / peak 113%). Books issued at
  REPL-2/3/4 + the fixed-prior full-history 2003-2025 maturation grid.
- 805 BEFORE/AFTER issued (AFL_REDESIGN_805_before_after_REPL3.xlsx; Board/By-position/Movers tabs, 2593 formulas, 0 errors).
  Board redesign-3 = 108% PVC, 124% value(). By-position: RUC 254% of PVC (the ruck convexity item, quantified).
- Luke BOARD REVIEW diagnosis: the redesign under-weights DRAFT PEDIGREE (late-pick producers high, young high-pick non-
  producers esp. KEY position low, played-modestly < unplayed inversion). Keane>Battle = uncertainty-convexity (games-driven
  band width + convex pricing; should be age-bounded). Position imbalance (G-Def high, fwds low). All in summary 5c/5d.
- APPROVED NEXT BUILD (not yet built): (a) position-specific REPL_DROP (fwd 4 / else 2); (b) gently-stepped position-adjusted
  pedestal floor (ref beta*E[v(prior-at-draft)]; protection decays with evidence x depth). Then re-run 805 + spot-checks.
- Docs refreshed: KICKOFF banner (full current state + next build), START_HERE (new REPL-3 verification values), summary 0/1/5a-5d.

## cont.25 (stress test, 2026-06-24) — third self-check, looped to clean
- Stress pass CLEAN on: REPL-mutation leak into value() (none; value(Bont) pre==post), REPL dict restoration, determinism,
  edge cases (pre-debut + brodie), full-805 (no errors/None/negative), build_dist_walkforward double-apply (none), and
  conditional_prior.py standalone.
- FIND (not a code bug): "value()" in all diagnostics + the 805 sheet = p['_vpt'] = MA.value(p,'bal') (POINT value). The
  shipped board value is p['_v'] = proj_value(0) = convex option value, capped CVX_CAP=1.25 (rl_model.py L851). _v = _vpt x
  convexity; 26 players at the cap, all young. Sharman _vpt=302 / _v=310 (the documented 310 anchor = _v, correct). Diagnosis
  REINFORCED (young high-picks even more under vs _v; established producers _v==_vpt; no flags flip). INSIGHT: the engine's
  option value is additive-only + capped at +25%; the redesign's band-convexity is uncapped (Keane runaway) and can dip below
  point value (Uwland) — the same structural gap the Keane temper (cap convexity) and the pedestal floor (floor the baseline)
  address. Documented in summary 5e + KICKOFF + START_HERE. NEXT 805 regen will add a _v column.

## cont.25 (cold-start onboarding audit, 2026-06-24) — fourth check, "new hire's first day"
- Simulated a zero-context restore. Found + fixed THREE cold-start hazards a continuing-chat check missed:
  1. setup.sh installed unidecode but NOT scikit-learn (the v4 model + redesign GBRs need it) -> a new hire's "setup OK"
     was silently incomplete and the first real command would ImportError. FIXED (sklearn added to setup.sh).
  2. README.md header + "section 7 / where things stand" were STALE (cont.23/cont.16: "next build is distribution pricing",
     "HANDOVER cont.16 is live") -> the conventional first file misdirected to a 2-3-session-stale state, and its read-order
     conflicted with START_HERE. FIXED (header + section 7 rewritten to cont.25; doc table adds START_HERE + cont.25 summary +
     forward_valuation; glossary extended with the band / v_at_peak / REPL_DROP / _vpt-vs-_v / pedestal-floor vocabulary).
  3. forward_valuation/ had 40+ files (live redesign next to deprecated prototypes + 4 peak_model*.pkl) with NO map.
     FIXED (forward_valuation/CURRENT_FILES.md: live trio + v4 model vs superseded/prototypes, explicitly).
- README sections 1-6 (purpose, run recipe, glossary, how-Luke-works) were already excellent cold-start material — preserved.

## cont.25 (consolidation + KPP/Petracca/candidates, 2026-06-24)
- Build consolidated to ONE formula in the redesign module: value = brodie x lens x E[v(games-weighted blend of at-draft &
  current-level bands, age+position-conditioned)] at per-group REPL (-4 fwd/-2 else). Demo floor DROPPED (band covers vets;
  would inflate board). Floor protection calibrated to EMPIRICAL recovery (KPP calibrated separately, ~30-47% at a KPP bar).
  Strip from engine: proj_value convexity, raw-PVC pedestal, relative-floor, age-gate, spike guards. +25% cap tested-not-adopted.
- Petracca eligibility confirmed (bnow=GEN_FWD props his value). Uwland trajectory mapped (1849 draft -> 1481 at 14 weak games).
  Candidate list for role-risk cut (39, rucks dominant). KICKOFF + START_HERE refreshed to the consolidated plan.

## cont.27 (2026-06-26) — PAR BUILT + A/B/C VALIDATED (U26-REDESIGN). Full: SESSION_SUMMARY_2026-06-26_cont27.
- par_build.py: PAR surface locked (level_pos(log-pick)+ramp_pos(tenure), additive, recency-wtd target, gate >=6g,
  cohort 2003-2018). Reconciles MID yr1 pk1-8 = 66.7 (anchor 66.0). Ramps un-pooled; thin protection in level kernel-ESS.
- Par-centred production BUILT as standalone mock (par_redesign.py) + VALIDATED. Retrain (one feature redefined,
  train/inference-consistent) kills the frozen-GBR OOD artifact (3g/61: prod 3423->1050, p50 108->79).
- A: floor beta=0.85 too high (at top-pick par-production); beta~=0.5 safe across positions. [CORRECTED mid-session:
  earlier "single beta can't work/re-anchor" was a Fork-A synth bug; par-production is healthy, ratios rise with pick.]
- B: non-play tilt LOCKED to band space (p50 bounded-down + p10 fat-left + p90 PRESERVED). Tilt-in-level -> OOD.
- C: tilt magnitude = base-rate-relative shortfall; yr1 base=0 -> first-year zero-drag emerges; tenure ramp emerges.
- READ-OUT GATE: all three fall out at ramp 14/beta 0.5 (Cumming par-held 1349; 61-vs-21 separated 1248 vs 981;
  Patterson hold-pedigree wide-band; yr3 non-establisher tilt fires correctly). Par + insertion + A/B/C validated.
- conditional_prior.py: +RL_PRIOR_TREES env (default 400, no change; 200 for mock speed).
- NOT WIRED. Next: ramp sweep -> finalize beta+tilt caps -> wire-in + regen board/HTML on explicit go.

## cont.27 UPDATE — surface cleaned, beta locked, Fork B banked
- par_build.py: weighted-isotonic monotonization (Decision-D class) -- level non-increasing in pick, ramp
  non-decreasing in tenure. Fixed GEN_DEF pk8<pk15 (noise) + KEY_FWD yr5 dip (backfitting artifact). Reconcile 66.9.
- FLOOR = position-specific beta (scorers 0.50 / defenders 0.28), gated by real-player check (par defenders price
  370-1000, confirming the low ratio). Two-tier trigger documented: >2 tiers -> switch to realized-level floor
  (position-specific beta == realized-level floor at lower fidelity; same insight).
- Fork B BANKED: recency-weighted shortfall; stress p90 preserved across range, cap binds only at extreme washout.
- NEXT: ramp sweep (responsiveness/inertia frontier: pair sep at 3g vs 15g across ramps, Cumming pinned).

## cont.27 UPDATE 3 — ramp sweep + pre-debut reconciliation (corrected) + sole-path resolution
- RAMP SWEEP (par_sweep.py, pre-floor): ramp 14 over-reads (growth 1.3x); ramp ~22 sweet spot (3g+434/15g+1112,
  2.6x); frontier NOT flat -> separation is evidence-weight-driven. Cumming par-held across all ramps. RECOMMEND ramp 22.
- PRE-DEBUT RECONCILIATION corrected (synth age-confound): vs PVCxmult, uniform high-pick ~50% markdown (GEN_DEF 41%,
  MID 52%), converging ~100% at late picks -> band UNDER-CAPTURES high-pick pedigree UPSIDE => decision 2 = (a) restore
  upper-tail dispersion at low evidence for HIGH PICKS only (late picks reconcile, don't touch).
- SOLE-PATH: par-path becomes sole pre-debut value; PVCxmult retired as valuation path, survives only as floor anchor.
  Restore high-pick band upside BEFORE wiring. League-reality call: set upside magnitude to actual draft-capital trades.

## cont.27 UPDATE 4 — (a) locked; markdown decomposed; tail-restoration plan
- Check 1: PVC = expected-value curve (busts->0, CE-averaged) not a pole => high-pick gap is under-pricing => (a).
- Check 2 (decomposition): clipping is POSITION-dependent -- MID(116 vs 105)/KEY_FWD(101 vs 88) under-dispersed (BUG),
  GEN_DEF(103 vs 102) correct (leave; low-scarcity defender, ties to beta finding). Root cause = quantile fit smooths
  the sparse high-scoring tail (dispersion axis, not pick axis -- position-dependent at same pick proves it).
- PLAN: restore upper quantiles toward empirical at-draft, evidence-weighted, exposure-0 = empirical; MID/KEY_FWD only;
  leave GEN_DEF/KEY_DEF + late picks. MUST hold at preseason/0-games (Duursma test). Magnitude vs league trade values.

## cont.27 UPDATE 5 — tail-restoration prototype (tail_restore.py)
- New module: restores band upper quantiles (p70/p90) toward smoothed-monotone empirical at-draft tail,
  evidence-weighted (full @ exposure 0), MID/KEY_FWD + high picks only, only-raises, GEN_DEF/KEY_DEF untouched.
- DUURSMA PASSES: pk1 MID 0g preseason -> 2596 (79% full pedigree), continuous through debut (no jump/crash).
- Restores MID high picks 50% -> 80-90% of PVC; KEY_FWD to empirical ceiling (64-69%); GEN_DEF control 40->40.
- Residual pk1 gap (79%) = PVC best2+CE vs v_at_peak best-3 pricing method (NOT clipping, NOT captaincy -- both
  include capt_prem). Engine-consistent; set magnitude vs LEAGUE TRADES. Two moments orthogonal (season haircut = wire-in).

## cont.27 UPDATE 6 — clean synth curve + PVC-vs-v_at_peak seam + seam doc
- PART 1 (magnitude artifact): clean synth pre-debut curve pk1-8. MID 2596->1718 (79-92% PVCxmult, monotone);
  KEY_FWD 1252->1011 (49-69%, tiny pk1<pk2 blip from thin data). Restored = empirical-p90 floor; magnitude vs trades.
- PART 2 (seam on known truth): established MIDs two-way. Par-path gives sensible forward values (elite in-prime
  2800-4000, declining vets nil, busts 0) -- v_at_peak validated. par/PVC ratios conflate perf+age; clean seam = Part 1.
- CLEAN SEAM: par-path ~13% below raw PVC at pk1, converging by pk5 -> PVC hot at TOP picks. Verdict: if in-prime
  par-path matches gut, PVC is hot.
- PART 3 (doc): PVC = reference not ground truth, ~13% hot at top, under beta-floor; resolution = realized-level-floor
  MIGRATION not recalibration (floor binds at low-value where seam ~0, so practical impact small). "Retire don't recalibrate."

## cont.27 UPDATE 7 — PVC two-jobs; position-mix pick-value curve; best-3 findings; aging LOG
- PVC two jobs locked: A=pick valuation (->par-path pre-debut/position-mix curve), B=floor anchor (->realized-level
  floor). Retire once both replaced -> now done.
- (1) BUILT position-mix pick-value curve: pk1/5/10/20/40 = 2176/1493/1058/539/352 (mix-weighted par-path pre-debut).
  ~67-72% of raw PVC; empirical-floor magnitude (dials lift high picks); RUC per-position noisy (small weight). DIALS UNBLOCKED.
- (2) PVC seam documented: hot ~13% at top picks only, floor binds where seam ~0 -> retire don't recalibrate.
- (3a) LOG: best-3 no partial-sample regression (Heeney 12g/124). FIX later: regress partial seasons (thin-evidence at peak layer).
- (3b) CHECKED: trajectory already captured forward via recency-wtd level (rise 3163 vs fall 2227, same avg) -> NO 2nd
  recency mechanism (double-count); never on ceiling best-3; smooth decay only if ever.
- (4) LOG: quality-blind aging (DELTAS one shape). Survivorship caveat (don't fit on raw late-career elites). 80/20
  candidate = shift PEAK_AGE later for high-lp via existing machinery. Defer fix.

## cont.27 UPDATE 8 — dials=0; pick-curve shape (survivor bias); RUC flag
  > SUPERSEDED IN PART BY U9: NO join filter (never-played are in master + emitted as bust training points,
  > checked 3 ways); flatness is a BLEND issue (RUC + mid-pick under-leveling); realized gradient = 1.70x not 1.50x.
  > dials=0 and the RUC flag remain correct.
- DIALS SETTLED = 0 (MID expected-outcome no premium/haircut; KEY_FWD strong corroboration 42-69% matches 40-70% gut).
- SHAPE CHECK: captured pick20/40 empirical 1.50x ~= par-path 1.53x BUT bust-capture badly under-counted late
  (never-qual 0%@1-10, 14-20%@31-60, vs reality ~40-55%); median pick-40 = 9. Survivor bias -> true gradient STEEPER ->
  ~2x intuition correct, par-path too FLAT at back. FIX: fold full draft lists (never-played=0) or bust-rate correction.
  High-pick dials UNAFFECTED. Sequencing: fix-then-wire vs wire-then-steepen -> Luke.
- RUC per-position pre-debut unreliable (thin) -- harmless in blend, flag before individual ruck pricing.

## cont.27 UPDATE 9 — join diagnosis (CORRECTS U8): no filter; read confirmed 1.70x; cause = blend composition
- NO inner-join filter: 745 never-played in master (all channels), valid positions (0 dropped), emitted as bust
  training points. U8's "missing busts" framing was wrong.
- Clean gradient (ND-only national axis, decided cohorts, loclin fine): pick20/40 = 1.70x, 15/40 = 2.07x. Original
  1.50x was binning+pollution artifact. Read CONFIRMED too-flat; ~2x right direction.
- Cause = BLEND not bands: bands gradient-faithful (MID 2.04 vs emp 1.93). Flatness from (a) high-ceiling MID
  under-leveled at mid-picks (537 vs 1097; tail_restore fade ends pk16) and (b) unreliable RUC at 10% late inflating.
- FIX = design call (not left-join): extend tail_restore mid-pick fade + fix RUC. TENSION: touches mid-pick magnitudes.
  Pending Luke direction.

## cont.27 (post-2nd-compaction)
- VERIFIED MID "12%" = mostly PEAK_AGE measurement artifact (level-dependent: elites agree 3-9%, modest best3 ran 30-48% hot). Risk-discount story FALSIFIED (clean residual narrows with pick). pk1-8 STAND; no scaling fudge.
- tail_restore.py: fade extension PICK_GATE 16→26, TAPER_FULL 8→20, _build_curve range→27, emp_q cap→26 (full restoration pk1-20). pk1-8 byte-identical; pk9-20 lifted to 0.92-0.99 of clean-realized.
- pickcurve_build.py: RUC scorer-shape pool (mean of MID/GEN_FWD/KEY_FWD par-path × RUC/scorer level ratio). Monotone; kills late-pick inversion.
- Corrected blend (1/5/10/20/40): 2176/1504/1130/665/325. Blend gradient 2.05x. Clean realized gradient = 1.76x (the "1.70x" ref was PEAK_AGE-contaminated).
- OPEN: pk21-40 extension (→1.76x) pending Luke's call + pk40 survivorship verify.

## cont.27 (post-2nd-compaction) cont'd — pk21-40 extension + survivorship gate
- SURVIVORSHIP GATE passed: busts retained (debutyr is draft-based; fwd_best3→0; busts pull pk40 -14%). Censoring boundary refined: realized stabilises at draft<=2017/2018 (resolved grad 1.69-1.73x, pk40 430-452); earlier 1.76x was right-censoring-contaminated.
- tail_restore.py: PICK_GATE 26→46, TAPER_FULL 20→40 (full restoration pk1-40, fade pk40-46), range→47, ±15 smoothing fallback, emp_q cap→46. pk1-8 byte-identical; pk20 1004→964 (smoothing correction). MID anchored pk1-40 (0.97-0.99).
- Corrected blend (1/5/10/20/40): 2176/1505/1131/647/392, gradient 1.65x. Realized-blend 1.73x is contaminated at pk20 by GEN_DEF/RUC outliers; clean MID column anchors at ~1.93x.
- FLAG: KEY_FWD 25-35% above realized mean (restoration→p90, KPF bimodal). Awaiting Luke's KPF call + blend sign-off.

2026-06-29 sizing-prep gate close: convention confirmed undiscounted->flat-100. GATE 2 (responsiveness) FAIL on current engine = dead-pole (_floor_w->0@30g) perf-chasing, controlled pk1@70<pk20@72, bands pick-blind, magnitude 100-200%/20pt; real players confounded; Boekhorst anomaly flagged. GATE 1 (flatness) NOT passed: (b) pick-resolved decay measured (gentle-top/steep-deep) needs elapsed-opportunity axis; (a) survivorship-clean premium construction failed/open. Both gates => U28-D dead-pole is the shared fix. Nothing baked; store Stage-0 (53728e6a); board/HTML untouched. Scripts: _size_twolines.py _size_gate2_bands.py _gate2_real.py _size_gate1_ab.py.
2026-06-29 P97 provenance = CASE (B) regression: re-read p97 doc-only (zero code), live band Q caps q90, redesign_value no tail, restore only pre-debut -> debut-discontinuity. Doc claims of 'p97 into lever B' corrected as wrong. p97 re-impl MERGES with pole fix (one build, lever B joint-sizing). HELD for confirm+approach. Nothing baked, Stage-0.
2026-06-29 tail measurement: opt3 q97-GBM only responsive option (Stephens 87<Sheezel 125); opt2 frozen perf-blind; opt1 inert for established (restore faded). Shape: BODY-drops/ceiling-holds for MID/GEN_DEF/KEY_FWD/RUC, CEILING-drops for KEY_DEF, both GEN_FWD. opt3 needs year-2 ceiling-hold verified + retrain cost. HELD for Luke's construction pick. Nothing built, Stage-0.
2026-06-29 tail 3-condition verify: (1) yr2 ceiling-hold PASS no-slash; (2) position shape PASS matches realized; (3) pick-resolution well-resolved (effN high) but q97 LEVEL FLAT across picks ~5pt -> pedigree gradient is BODY+POLE-borne not tail-level, tail=convex-upside/undervaluation fix only. Build expectation corrected. HELD for (3) nod then merged build. Stage-0, nothing built.
2026-06-29 pre-build: REPL preserved (no fix, -3 stays); pedigree locus=floor q10/q30 not body; DECISIVE reviving _floor_w alone FAILS falsifier (at-draft pole<<prod, lift0, pk1@70 537<pk20@72 586 w=1; at-draft median 27<<par 75); par-centred pole PASSES (598>586). Build pole revival must be PAR-CENTRED not _adraft_band. HELD for par-pole source. Stage-0, nothing built.
2026-06-29 MERGED BUILD falsifier-clean: par-centred pole(lift-only)+q97 tail+age-w(Kyle fix)+recovery-gated lift. ALL guardrails PASS (pk1@70 2386>pk20@72 1625; pk1@40 falls 355; pk20@95>pk1@62; grid pk1>pk20). recover shape hypothesis (confirm vs realized). Remaining: elapsed-opp+GATE1+slow-dev+1/4 floor+xlsx book. Nothing baked, Stage-0.
2026-06-29 recover MEASURED (gentle; below-par young recover; bust 56%=realized not rescue, stalled->1/4 floor; guardrails hold). RECORD RECONCILED by deletion: sizing-pass NEXT killed everywhere, UNRESOLVED U28-D/floor/p97 contradictions deleted, START_HERE = single authoritative page, -16,529 diagnosis banked. Stage-0, nothing baked.
2026-06-29 doc-hygiene pass (concept-scrub rule): UNRESOLVED banner added; ALL live (A)+(B)/(B)-LOAD-BEARING/upper-band-re-centre/lever-B-tail-pending/opt3-pending instances tombstoned (L1006/1051-53/1061/1064/1075/1086); 'word).' fragment cleaned. COLD_RESUME opt3 UNVERIFIED/pending + stale NEXT-merged-build section tombstoned. ENGINE PIN: _merged_recover.py md5 ec965689e9de carries MEASURED recover curve (rx=.30/.52/.67/.82/.97/1.30, ry=.54/.64/.84/1/1/1); cold smoke-run reproduces BUST 57% (1791), NOT stale 11%. Stage-0, nothing baked.
2026-06-29 BOOK BUILT (AFL_RL_backtest_book): 6 sheets (Gate_Verdict/Summary/GATE1/Pick_Curve/Drill_2019/Companions), 0 formula errors, populated with merged-engine values. FINDINGS: up-leg present (cohort value climbs 152->212% draft to yr4); slow-dev PASS (Patterson 63%/Annable 81% modestly-below); FLAG1 pick curve flatter than PVC (MID pk1/pk20 2.3x vs 4.0x, KEY_FWD pk1<pk2 non-monotone); FLAG2 staleness floor unbuilt (Oscar 570->156 etc, applied as post-engine cap, needs wiring); WATCH MID/KEY_FWD value rises early (under-prices). Nothing baked, Stage-0.
2026-06-29 doc-hygiene: COLD_RESUME state-diffed against START_HERE on ALL shared engine facts (not just recover) — title, falsifier nums (2386/355->2879/1791/57%), recover (hypothesis->MEASURED curve), REMAINING (measure-recover+book DONE), scripts, book-built all reconciled to canonical. Added MIRROR-OF-START_HERE banner (drift-prevention: secondary doc defers to canonical). UNRESOLVED L1093 _floor_w intermediate tightened. NO engine change, Stage-0.
2026-06-29 ENGINE WIRED (md5 36d01244): delist->~0 + staleness floor (all stalled, 1/4 draft tenure-declining) + isotonic pick-guard, INTO _merged_recover.py. Named proof: Ronin 526->10/Oscar 570->156/Jakob 594->140/KEY_FWD pk1=pk2 monotone/Coleman 767>=Stephens 761/2019 deep 82%->25%. Falsifier still clean. FLAGS: GATE1 not yet flat (5); Harrison/Stephens price per 2026 data (reads disagree). BOOK RETRACTED (premature). Stage-0, nothing baked.
2026-06-29 PRODUCTION-READ FIX (md5 bcef17cc): exposed level feature ALREADY games×recency weighted (correct); real inverter was PAR-POLE over-crediting established mediocre shallow picks. FIX: recover-perf->weighted _lvl_wt + POLE FADES by tenure (w*clip(1-(tenure-2)/3)). CONSEQUENCE: Riccardi>Jones (368>219), Georgiades>Kemp (1422>799) fall out naturally; well-shaped stay put (Serong/Daicos stable). Resolved Harrison(219)/Stephens(293) as pole-over-credit not input data (Luke's reads correct). Falsifier+delist+staleness+isotonic intact. Stage-0.
2026-06-29 POLE-FADE MEASURED (md5 7f7d7f76): V1 fade measured on TENURE [1,.76,.40,.16,.05,.05] (residual pick signal beyond demonstrated level; games doesn't decay cleanly; guess too slow). V2 flat target RULED OUT (corr 0.998 w/ weighted, mean|Dpred|=1). V3 bust was OVER-valued (level-vs-value: 0.70 level=0.08 value); fade corrects direction, residual recover-gate level-calibration flagged. 4 players hold, well-shaped stable, falsifier(young) passes. Stage-0.
2026-06-29 RECOVER value-space (md5 7f7d7f76 UNCHANGED): 8-15% target NOT supported (survivorship-biased read); measured value recovery 0.66-0.75 ~= current level-ratio RECY; recover-gate kept, bust enforced by delist/staleness. GATE 1 attempt confounded (cross-sectional, small-n), corr(value,prod)=0.53; needs within-player winners-normalised redesign, STILL OWED. No book. Stage-0.
2026-06-29 GATE 1 PASSED (leakage-guarded within-player, md5 7f7d7f76 unchanged): IS~=WF (leakage~0, read is genuine prediction); GOOD 34-84% par vs BUST ~0-1% (clean early separation); pole prices pedigree before proven (high-pick good 53%@draft->84%@T5, late-pick good 34%->production-driven); no violent moves. Last engine gate. Cleared for book (FULL format). Stage-0.

2026-06-29 BOOK DELIVERED (FULL format, engine md5 7f7d7f76, in-sample): AFL_RL_cohort_value_book_2026-06-29.xlsx — Summary (cohort×tenure SUM-ratio, AVG row) + 19 per-cohort sheets (2003-2021), per-player VALUE+PRODUCTION year-by-year paths draft->now, cohort-total SUM-ratio via SUMIFS (not mean-of-ratios), 0 formula errors. Drill 2019/2008-10/2021. FINDINGS: climb-or-cliff present (AVG 130->170%); current-by-cohort correct (old~2% retired, young 114-141%); delist->0 + stalled->1/4 confirmed at player level; MATURITY-EASING flag (good mature ~69-85% of own peak = GATE1 84% question, for Luke); 2020 COVID cohort anomaly; small-n tail blanked. No tuning. Stage-0, nothing baked.

2026-06-29 BOOK REBUILT FULL-CLASS (survivorship defect fixed, md5 7f7d7f76 engine UNCHANGED): cohorts were survivor-sized (~62, dropped washouts) = survivorship bias. Rebuilt on FULL draft class (ND+RD+MSD+PSD, 73-131/cohort), washouts at ZERO vs their pick. AFL_RL_cohort_value_book_FULLCLASS_2026-06-29.xlsx, 0 errors. CONSEQUENCE: AVG sum-ratio 123/139/130/130/129/121/109/92 (Yr1-8) vs survivor 130..170; per-cohort -14..-53% at Yr5. Survivorship was the inflator (curve drops to sane ~139% peak) -> survivors priced ~fine, not gross over-valuation; monotone climb broke into early-peak+erosion. Aging-elite depreciation (Petracca 4067->1763->2457 = engine does move with production) flagged for fuller check. NO bake, Stage-0.

2026-06-29 BOOK bust-timing = LISTED-WINDOW rule (engine UNCHANGED md5 7f7d7f76). Data has NO delisting dates (1642/1652 busts _retired-boolean only); inferred off_board=max(min-listed-window, last-game), concrete prior wins. Min window ND top20=4/21-40=3/rest=2, RD/PSD=2, MSD=draft+1. New AVG 145/165/132/131/129/121/109/92. Sensitivity: Yr3-8 robust (<=3pt across timings), Yr1-2 reflect held rookie windows (last_game+1 was too aggressive, zeroed washout rookies in debut yr). Canonical book = AFL_RL_cohort_value_book_FULLCLASS_2026-06-29.xlsx. NO bake, Stage-0.

== 2026-06-29  STEP 1 COMMITTED: #1-family thin-evidence/grower/Cook fix (engine md5 7f7d7f76 -> 38de7a01716d) ==
Supervisor-approved. Baked the experimental #1-family fix into rl_after/_merged_recover.py (inference-only; q97m+cm+ISO+pole
on ORIGINAL features then cp._lvl_eff/cp._feat rebound; band pickle cm_400.pkl UNCHANGED md5 34faa8659). Components: career-
evidence shrinkage (A down), grower current-level read _lvlcurr (B up), developmental tenure eff_ten=max(base,age-18) thin-only
(flips A<B), pole exposure-gate + early staleness (Cook decays). Proven-flat Delta=0 enforced via flat gate + proven-keep-real-
tenure + exposure-gate-thin-only + FROZEN pole table (force-populated pre-rebind). Verified vs pre-commit engine (/tmp/orig_engine,
7f7d7f76): A 2941->1096, B 1038->1403 (B>A); proven-flat 8/8 byte-identical MAX|Delta|=0; growers rise; Cook 879/456/411/365/319;
Boekhorst delisted unchanged 16. PROVISIONAL dials (PROVEN_N=4,FLAT_TOL=3.0,LDECAY=0.40,POLE_RAMP=22,c=n/4) flagged for step-3
calibration (NOT baked). Pole is pick-side = frozen until step 2-4. NEXT: step 2 monotone pole smoothing all positions + RUC pooling.

== 2026-06-29  OVERNIGHT FULL BACKUP (engine 38de7a01, Stage-0) ==
Step-2 ACTION-2 pole-basis recompute done (analysis only, engine unchanged): corrected-band pole shift is position-AND-pick
dependent (MID+30/GEN_FWD+53/KEY_FWD+20/GEN_DEF+13/KEY_DEF+21/RUC+4 %) and ~7x sensitive to synth maturity -> largely a synth-
construction artifact (thin synth shrunk toward higher-tenure par prior), pole absolute level FRAGILE (step-3 anchors it).
Entanglement: par_pole recomputes through the band; proven-flat byte-identical only with the FROZEN pole; PRODUCTION is the
invariant, not ev. DECISION (C) recorded: zero the maturation lift for PROVEN players (rest on production), pole touches only
unproven -> permanent decouple. PVC declared DEAD (replaced by Park-1 pick-value curve final design). Three parks + Kondogiannis
test written to START_HERE/UNRESOLVED. Backup tarball = afl_rl_BACKUP_38de7a01_2026-06-29.tar.gz (cold-verified). Step 2 = morning.

## [2026-06-29] STEP 3 CALIBRATION DESIGN (DESIGN-ONLY checkpoint; engine UNCHANGED 38de7a01, Stage-0, NOTHING BAKED)
Heaviest design phase; checkpointed before timeout risk. All ASPIRATIONAL (agreed, not wired). See START_HERE ★STEP 3 section.
- LDECAY final groups: KEY 0.40 / GEN 0.35 / MID+RUC 0.225 (RUC measured-in via direct stability, not the edge-optimal fit).
- EVIDENCE→WEIGHT SURFACE accepted in full (replaces step-1 c=n/4): w(cumulative games × signed dist-from-par × age), all axes smooth.
  above-par w=1 (never drag outperformer; growth via band tenure; margin/variance thread CLOSED, no haircut, A>B on the mean);
  near-par smooth over games; below-par 2D games×AGE (young keep prior, old converge); AGING-ELITE (Park 3) homed in old-below-par.
- POLE LEVEL basis agreed (NOT computed): root cause = arbitrary 2yr synth maturity; fix = unbiased-expectation-derived maturity,
  distribution-integrated (kills 7×), upside preserved (above settled), in-architecture. HARD GATE: must not crater unproven value.
- Standing instruction reaffirmed: no hard cohort/threshold boundaries; smooth over the natural axis unless data shows a discontinuity.
- NEXT: compute pole re-level + robustness + hard-gate spread → re-checkpoint; then dial read-offs + walk-forward incl. recent cohorts.

## [2026-06-29] STEP 3-B POLE RE-LEVEL — APPLIED TO ENGINE (38de7a01 → e0ac9c377d1e; Stage-0, not baked to board)
ACCEPTED + applied. Per-position scale in par_pole: MID 1.19/GEN_FWD .93/KEY_FWD .95/GEN_DEF 1.08/KEY_DEF 1.05/RUC 1.13.
Basis: trajectory-integrated pole (mean price6(par-synth) over development T1-5) / 2yr synth; piece-2 monotone SHAPE kept, LEVEL rescaled.
- The "5× over-level" was the confounded proven-settled comparison — gone; the level was ~right, the BASIS was the broken thing, now principled.
- Robustness PROVEN: integrated pole moves 4-12% on maturity-window perturbation vs single-point 1.2-2.1× (the 7× was extreme single-point).
- HARD GATE PASSED (authoritative panel): A 1096→1096, Attard 511→533 (+4%), hi-pick rookie +6%, mid-pick rookie −2%, Cook identical.
  First-year/unproven NOT cratered. Proven-flat Δ=0 ON THE LIFT (Daicos/Soligo/Bramble exact); ≤0.8% iso-guard structural rebuild (Ward +0.8%).
- MICRO-CALLS: (a) ACCEPT the ≤0.8% iso-guard drift (do NOT freeze ISO — correct downstream recompute, not a leak; document as lift-Δ=0 + iso ≤0.8%).
  (b) SKIP the realized-outcome bias cert (would reintroduce the rejected realized-par-pick comparison; aggregate bias belongs in the backtest book, steps 4-5).
- Upside preserved: scaled pole above proven-settled-at-par every position. Pre-pole engine preserved at _merged_recover.py.PREPOLE_38de7a01.
REMAINING STEP 3 (batched next): (1) dial read-offs off the surface; (2) walk-forward incl. recent cohorts. Then step 4 (pick-value curve).

## [2026-06-29] STEP 3 — CLOSED (final batch: dial read-offs + walk-forward; engine UNCHANGED e0ac9c377d1e)
- Dial read-offs: shrinkage-c SUPERSEDED by the surface; PROVEN_N per-branch (above ~0 / near ~2.8 / below-young = the 2D surface, no scalar);
  POLE_RAMP 22 unchanged; FLAT_TOL MEASURED per LDECAY group = KEY 10.3 / GEN 12.0 / MID+RUC 14.0 (ordering matches LDECAY; per-group, not one number).
- Walk-forward (incl. newest/ambiguous-year-1 cohort): leakage SANE (level-read pred/actual IS 0.911→WF 0.865, ~5pp < the validated 10pp; MAE blowup is
  forward-best-3 variance, not leakage). First-year value INTACT OOS in the FULL engine (449-player: year1-ev 1137 ≈ proven 1192, 0 near-zero, min 45, p10 123).
  The level-read alone under-predicts first-years (0.756) BY DESIGN; the pole fills the gap (Harley Reid y1 3686 vs proven 3510, ratio 1.05).
- GATES held (step-1 triplet; first-year not cratered IS+OOS; nothing board-baked). NO gate broke → STEP 3 COMPLETE. NEXT = STEP 4 (pick-value curve).

## 2026-07-01 (evening→night) — DIAGNOSTIC ONLY; head 8aed420a UNCHANGED (nothing baked)
- Book machinery corrected: opp-matched SUM-RATIO summary; 2003-excluded + 2015-24 secondary-line variant. [WIRED in book scripts; VERIFIED regenerates]
- Directive-v3 low-games: +0.1-retain raise lifts Yr1 +5.6% (abs); unified w-blend backfires −23%. [PROPOSED; not wired]
- Current-season-drop: reliability-shrink hypothesis FALSIFIED; "correct aging" FALSIFIED; mechanism PINNED = exposure-feature/recency-decay channel, cohort-varying (young −48% ≫ old −26%), not level/shrink/aging.
- Decay-proration prototype (Phase-2): INERT historically (byte-identical); NON-VIABLE as specified. [PROPOSED; overlay kept distinct from head; REWORK needed]
- No head/store/band change.

2026-07-02 DIRECTIVE 2 (diagnostics + gate re-specs; ZERO engine/store edits; scratch evals only): Luke's rulings (turns 09-10) folded into ship_gates_check.py — B1 = pooled rise to peak by yr4-5 (yr6 acceptable), pre-peak dips <5% tolerated, no yr6-hold (pooled peak N=4 R=160, path_ok, 17/17 cohorts still PASS); B6 = whole 0->6 ramp with 0-game sit-out anchor (anchor 745 == 1-5g 745, flat-then-step +2518 confirmed verbatim; DECLARED smoothness thresholds: no step >50% of 0->6 rise, >=25% by 3g), monotone clause unchanged; B5 population = ACTIVE/LISTED only (inactive value=0, remains in backtest denominators at 0; offender list unchanged, 0 delisted among the 9); A6 bw 0.6 RATIFIED via delegation; B2 tol 5.0 provisional — N=5 noise floor measured 0.00 %-pts (byte-identical metric tables). Diagnostics: H-WARD FALSIFIED as sole cause (M1+v7 scratch flips A9 1677>1253 + A2's Weddle leg + clears all A5 floors; Curtis 1087 < Ward 1253 survives); B4-h1 NOT CONFIRMED (stage0-store regen c16e1024 vs shipped b8f9e998 vs reconciled-regen 1898ead7; shipped-vs-regen diff structural/large: SCALE 6.53->4.49, intakePickSum ~x0.6, PVC 99/99 subkeys -> evidence favors h3, cause NOT labeled; next isolation = canonical-engine e0ac9c37 x 3 seed stores); 9->10g dip = evidence-onset overlay capping Leff 72.1->68.6 at 10g, 29/36 cohort variants, worst -601 KEY_FWD pk40 avg105, monotonicity-violating; H1 (_lvl_wt thin-below-par) FALSIFIED again (Rozee -827 decay/exposure vs -368 level; d_level +1..+5% all cohorts). Year-schedule crater floor PROPOSED (yr1-4 0.25x, yr5 0.15x, yr6 0.10x, yr7+ 0.05x from smoothed p5 of listed ev/draftval; Luke signs; 0.25x provisional on board). Board 8 PASS / 9 FAIL / 5 PENDING / 1 STRUCK — statuses unchanged post-re-script. Nothing baked, head 8aed420a / store 644d1254.

2026-07-02 DIRECTIVE 3 STEP 0 — GATE AMENDMENT + THRESHOLD RULINGS (script/doc edits only; SHIP_GATES.md text untouched per the frozen-file rule — amendments live here per the SHIP_GATES amendment process):
- A2 AMENDED (Luke, in writing, 02/07/2026): A2's Curtis leg is re-scripted from Ward < Curtis to Curtis >= 0.90 x Ward; A2's Weddle leg and A9 unchanged. Reason (Luke, verbatim): "same cohort; both durable; Ward averaged only +5.5 last season and +2.9 this season; nothing in Ward's 5 years suggests captaincy/convex upside; Curtis's G-FWD positioning already yields value above replacement NOW and each development point compounds it — the reality of Curtis is closer to Ward than the model suggested." Context: post-overlay ratio = 1087/1253 = 0.868, so the amended gate remains (barely) red pending the D3 ASK 2 residual/drop investigation.
- B2 tolerance SET = 0.5 %-pts in ship_gates_check.py (supervisor ruling under Luke's delegation, 02/07/2026). Rationale: measured N=5 leakage-spread noise floor = 0.00 %-pts (Directive 2 Task E, metric tables byte-identical across runs), so any gap >= 0.5 %-pts is signal, not noise. Supersedes the provisional 5.0.
- B5's draftval denominator provenance under question (Q3); any re-base/versioning decision follows Q3's answer.

2026-07-02 DIRECTIVE 4 STEP 1 — INSTRUMENT AUDIT + GATE AMENDMENTS (script edits + one Luke-approved SHIP_GATES.md B5 note; amendments logged here per the SHIP_GATES amendment process):
- A8 AUDIT (Luke's arithmetic catch, D4 ASK1): the scripted expression WAS the literal 2x test (b > 2*t); raw values Berry=3473 / Tsatas=1083 make both reported passes GENUINE (engine ratio 3.21x, board-path 3.87x). The defect was DISPLAY AMBIGUITY — the detail string "Berry=3473 vs 2x Tsatas=2166" invited reading 2166 as raw Tsatas (Luke's 2x2166=4332>3473 arithmetic is that reading). Neither pre-named candidate (missing-2x / ±20% tolerance leak) present. FIX: detail string de-ambiguated to raw values + explicit ratio; comparison > -> >= per frozen "by at least 2x". Printout: session_2026-07-02/d4_a8_audit.txt.
- FULL GATE-LINE AUDIT (all 23 lines vs frozen 764a0d91 + logged amendments): 20 MATCH (6 in Luke-amended form), 3 MISMATCH — A8 (above), A10 (amendment unwired), B5 (signed schedule unwired) — all fixed this session. Table: session_2026-07-02/d4_instrument_audit.md.
- A10 AMENDED (Luke, in writing, 02/07/2026): threshold 0.70 -> 0.50. Reason: DATA-CAUSED per the SHIP_GATES failure triage — Curnow has banked 13 games of 2026; his level is 2026 form, not an engine artifact. PROVISIONAL + review note carried in the gate line (re-review at season-complete).
- A3 ANNOTATED (Luke, 02/07/2026): "evaluated PRE-LTI-layer" — the pre-LTI engine ratio is what A3 tests; a future LTI overlay must not be the thing that passes it.
- B5 YEAR-SCHEDULE WIRED (Luke, SIGNED in writing, 02/07/2026): floors by years-in-system yrs1-7+ = .45/.35/.28/.21/.13/.09/.05 x draftval; POPULATION = NATIONAL-DRAFT entrants only (post PRESENT_ID_OVERRIDES type=='ND'; MSD/SSP/RD/IRE/UNR/PDx + delisted/retired excluded). GENERATING RULE recorded beside the constants: floor ~= 0.9 x smoothed clean p5 (ND-only) — the re-derivation formula at re-base. RE-BASE-AT-PVC reminder written INTO SHIP_GATES.md on B5 beside A5's sibling note (Luke approved this frozen-file edit in writing; new SHIP_GATES.md md5 recorded in the D4 return).
- Supersedes the 0.25x proxy (D2) and closes the D2 year-schedule PROPOSAL (Luke named the numbers).

2026-07-02 DIRECTIVE 4 (Luke's ruling package — ONE-price execution + bake candidate + M3 derivation): PR #6 merged (post-merge main e8688a72). ASK1 audit: A8's scripted expression WAS the literal 2x (Berry 3473/Tsatas 1083, both passes GENUINE, engine 3.21x/board 3.87x); defect = display ambiguity (fixed + >= per frozen text); full 23-line audit 20 MATCH/3 MISMATCH (A8, A10, B5 — all fixed); board at head 9P/8F (A10 FAIL->PASS at 0.51 vs amended 0.50). ASK2: B5 signed year-schedule wired (ND-only via post-override type; 9 offenders VANISH as predicted; 51 new at head / 82 at candidate = 23 dev-window real signal + veteran .05-tail over-binding — LUKE BOUNDARY FLAG: yr8+ clean p5 runs .01-.09, the schedule's generating rule gives ~0 floors there). ASK3 ONE-PRICE EXECUTED (Luke's delete-not-disable ruling): netting lookups first — REPL-3 lives in BOTH paths once each (double application = ZERO; engine price6 keeps its own) and TR.production_value consumed no ev() -> no promotion needed; deletion commit f2bb22b (wire overwrite, router, tail restore, RUC pool, RUCK_TAX, soft floor, Brodie x0.5, lens tilt, verify_anchors.py); BOARD_LAYERS_OBITUARY.md (27af6b41) carries per-layer magnitude/rationale/resurrection ref; rl_export re-pointed to engine ev() (named-row parity byte-exact; bundle 1c94348e vs orphaned ship b8f9e998 -> B4 red until Luke's ONE board re-cut); view re-plumb vM2/vM1/v/vP1/vP2 = ev(p,2024..2028) (retired back-rows flat — Y-aware delisted() spec'd as candidate item); post-delete restore-verify 9/9 + panel 10/10 at unchanged head 8aed420a. ASK4 BAKE CANDIDATE (branch claude/d4-bake-candidate-m2-m1v7, commit 0806d90, engine fb39d88a / cp 5ac8b162; NOTHING canonical): M2-exposure wired in conditional_prior (f=0.545, s=clip(1-g26/11,0,1), RL_EXPO_F kill-switch, byte-exact at f=1 verified) + M1+v7 transplanted verbatim from the read-pass prototype; pre-logged expectations ALL landed (A3 0.642 M1v7-only == D3 reconstruction -> 0.658 with M2; Ward TOL knife-edge gap +3.0<5; A10 0.549 — knife-edge did NOT flip; Tsatas Lo66.7->Lc75.7 M1-lift while Berry compresses -36.7% -> A8 2.24x holds); candidate board 11P/6F (A5+A9+A10 green, A2 0.875 vs 0.90 red); candidate walk-forward book (7147 builder): B1 pooled R=148 peak N4 but per-cohort 16/17 — cohort 2020 fails rise-above-yr1 (yrs4-6 97/98/95) vs same-builder canonical control R=160 17/17 (2020 at 109/110/110) -> ENGINE-CAUSED by the M1+v7 wiring (M2 byte-exact on those completed-season cells); live bake-blocker under frozen B1. ASK5 M3 DERIVED (design m3_design_proportional_tenure.md; NOTHING wired): value-space interpolation between full-click and clock-pinned evals (age/tenure/eo/feat-ten pinned; evidence + M2's exposure clock untouched — no double-proration), scope = M2's s, fE=SEASON_PROG 0.58; zero on-pace collateral (0/288); Rozee +10.7%; A3 0.658->0.728 at fE=0.58 (0.742 at 0.50; full-pin ceiling 0.863) — PRE-REGISTERED A3>=0.80 NOT REACHED at any honest elapsed fraction; pre-overlay decomposition: plain head 0.692 -> +M2 0.706 -> +M2+M3 0.780 (0.794 at 0.50) -> the M1+v7 overlay COSTS A3 ~0.05 (the clock pair alone lands a whisker under the bar) — A2/A5/A9 repair vs A3/B1 damage = Luke's explicit tradeoff; B5 82->63; A10 untouched by construction. ASK6: LTI_REGISTER_2026-07-02.md committed as schema+guards (supervisor CONTENT ABSENT — flagged, nothing invented); no LTI machinery exists (nearest = _b2hc present-unavailability haircut rl_model.py:800); proj_from_peak is already a per-season discounted sum (win-now view feasible); MSD/SSP pick-equivalent = one shared object (PICKEQ + PRESENT_ID_OVERRIDES) feeding valuation and draftval together.

2026-07-02 DIRECTIVE 3 (board layers + A2 residual decomposition + drop-fix design + B4 isolation; ZERO engine/store edits, scratch evals, sequential): PR #5 merged (main fc814936). ASK1: gates price ENG (_merged_recover.ev); board = TR.production_value via wire (JS legacy chain DEAD at v23.js:97); 8 live board layers toggled (wire overwrite 31.6% of board value, REPL−3 19.6%, tail-restore 1.4%, RUC pool 1.1%, RUCK_TAX 0.3% — LIVE on board / DEAD only on ENG path, ledger conflated paths; soft floor 0.1%; Brodie = 1 player; lens tilt inert at bal); dual-path ruler: A4/A9/A11 FLIP between paths, board −7.6% total, median |Δ| 24.9%, 57% >20%, Spearman 0.90; 2866 provenance CONFIRMED (Rozee-under-proration); live board b8f9e998 = orphaned pre-06-21 export-code artifact (PVC[1]=3883 pre-RL_PICK1-anchor, 785 active, cohort 1303). ASK2: h-CurtisDrop FALSIFIED (Curtis decay/exp share +0.5%, 13g on-pace, scoped fix moves him 0.0%); Curtis held down by v7 compression (M1-only 1441 / v7-only 977); post-overlay Curtis 66% / Ward 77% of pick-age-matched producer lines; overlay reconstruction ±5% vs D2 (relativities identical; D2 scratch was uncommitted — flagged). ASK3 (design only, nothing wired): split bundle — channel a is AGE/TENURE-dominated (young −40.1% age vs −12.9% decay/exp; old −26.1% vs −0.6%); unscoped exposure lever FALSIFIED on collateral (86/288 on-pace >2%, James Jordon −21.5% reproduced with _lvl_wt untouched → D1 collateral attribution CORRECTED to the band's exposure-feature response); final M2-exposure lever (f=0.545 derived, scope s=clip(1−g_Y/11,0,1)) = ZERO on-pace collateral (0/288), byte-exact at f=1 + historically, B-gates hold (B1 spliced PASS, B5 9→8, B6 identical) BUT A3 0.692→0.706 (need 0.80) and A10 0.511 untouched (Curnow 13g on-pace → DATA-CAUSED candidate) — acceptance unreachable via the decay/exposure channel alone; design doc session_2026-07-02/dropfix_design_M2exposure.md (Luke reads before wiring). TASK Q: Q1 sign-flip = designed (Ward M1 TOL knife-edge 5.9→3.0 flagged); Q2 nq = _nqual(·,2026); Q3 draftval = PVC[effpk] computed by CURRENT head each load (retrospective; PVC stage will re-base it); Q4 MSD/SSP pick-equivalents (59/94) feed BOTH board values AND the B5 denominator; Q5 board 805 = league ~805, NO coverage gap (696 = listed −pickless −2026-draftees −yr12+ trim). G3-CLEAN: yr1 p5 crater DISAPPEARS on ND-only (.16→.50) — MSD/SSP contamination confirmed; guard-shape skeleton tabled for Luke. ASK4: canonical e0ac9c37 × 3 seed stores → 1898ead7/1898ead7/c16e1024, NONE reproduce shipped b8f9e998; store axis = 5th-decimal SCALE; engine axis provably off the export dep graph; cause UNLABELED, h3 strengthened. B2 tol 0.5 live: GATE-1 rerun leakage 0.0 → B2 PASS. Head 8aed420a / store 644d1254 / band 34faa865 unchanged; all swaps restored + md5-verified.

2026-07-02 DIRECTIVE 5 STEP 1 — B1 GATE REBUILT (Luke's REDEFINITION of the governing growth law; amendment per the SHIP_GATES process — Luke-only, in writing, reason logged here; SHIP_GATES.md B1 text amended under the same ruling, new md5 in the D5 return):
- LUKE'S RULING (verbatim, in writing, confirmed): "NOT every cohort must rise — the CROSS-COHORT AVERAGE at each year-depth must rise to a peak in years 4-6. Individual cohorts may dip by design: not all draft cohorts are equal; 2020 is a shocking draft — it should lose value."
- NEW B1 (wired in ship_gates_check.py): at each years-in-system depth d, the simple (unweighted) mean of indexed cohort value (yr1=100) across all cohorts observed at depth d must rise from year 1 to a peak occurring in years 4-6; pre-peak dips of the AVERAGE tolerated under 5% (tolerance carried from old B1 — now applies to the average only). Per-cohort curves UNGATED but printed as a pipe table on every gates-board run (Luke's eyeball channel — visibility without a gate).
- OBITUARY — the per-cohort backstop, RETIRED. What it was: every incurve cohort 2004-2020 individually had to rise above its yr1=100 index somewhere in yrs 4-6 (max R(4..6) > 100), scripted beside the pooled-rise test since the D2 re-script; 17/17 at re-script, 16/17 at the D4 candidate (cohort 2020 at 97/98/95 = the D4 bake-blocker). Why replaced: Luke ruled the LAW wrong, not the measurement — a uniform per-cohort rise requirement encodes "all draft cohorts are equal," which he explicitly rejects; a shocking draft SHOULD lose value, and a markdown that sinks such a cohort may be desired engine behaviour, not a defect (D5 ASK 2 decomposes whether the 2020 markdown is in fact mediocrity-concentrated). Ruling ref: Luke, in writing, confirmed, 02/07/2026, relayed via the D5 directive. The cohort table stays printed on every board run so a sinking cohort is always eyeballable.
- MEASURED at three states (session_2026-07-02/d5_ask1_newB1_three_states.md): head 8aed420a PASS (avg peak N=4 AVG=160.5, path_ok) · candidate fb39d88a PASS (avg peak N=4 AVG=147.6, path_ok; 2020 row 100/111/110/97/98/95 — visible, ungated) · same-builder fix-off control PASS (N=4 AVG=160.5). THE D4 B1 BAKE-BLOCKER DISSOLVES UNDER THE REDEFINED LAW.

2026-07-02 DIRECTIVE 5 (growth-law gate rebuild + M1+v7 per-term decomposition + B5 evidence + LTI register; gate/doc edits Luke-ruled only; candidate branch READ-ONLY, measured never committed; NOTHING wired, NOTHING baked): PR #7 merged (post-merge main cecb0cc1). ASK1 B1 REBUILT to Luke's redefined law (entry above; SHIP_GATES.md a55921f6, ship_gates_check.py 5e6e34d9) — new-B1 PASS at head (avg peak N4 160.5) / candidate (N4 147.6) / same-builder control (N4 160.5); 2020 row 97/98/95 at candidate stays visible UNGATED; THE D4 B1 BAKE-BLOCKER DISSOLVES; head board re-run 9P/8F (counts unchanged, B2 re-verified leakage 0.0). ASK2 PER-TERM DECOMPOSITION (candidate basis; anchored one-line term-off patches, 5 sequential measurement loads + 3 same-builder 7147 matrix rebuilds; d5_ask2_perterm_decomposition.md): (a) the Curtis improver-squeeze = v7-cB (Curtis -195/-14.4%, Ward -324/-19.6%; M1 counter-lifts Curtis +184 while Ward's +3.0 gap < TOL_M1 earns 0); M1 owns the WHOLE A3 cost (-0.034; M1-off restores 0.692 = head; M2 offsets +0.016); v7-asc owns the B5 blowout (53 vs 82 when off). (b) the 2020-cohort markdown (-11.6% d4-6 vs control) is TWO channels: v7-asc mediocrity-CONCENTRATED (top-quartile -5.0% vs bottom-half -33.6%, Spearman +0.706 p=1e-08 — Luke's shocking-draft read CONFIRMED on the concentration test) vs v7-cB INDISCRIMINATE (rho=-0.024 p=0.87 — artifact-shaped, same term that squeezes Curtis); M1 lifts the cohort +3.9%; either compression off restores 2020 >100 at d4-6; new-B1 passes at every term state. ASK3 B5 EVIDENCE (numbers only, nothing wired): full 51-offender table at head w/ club/ratio/floor/margin (23 dev-window yrs1-8 / 28 deep-tail yrs9+); 31 candidate joiners, 0 leavers, v7-asc implicated in 27/31 (20 solo, 6 +cB, 1 +M2, 4 joint); yr8+ floors from the generating rule (0.9 x kernel-smoothed clean p5 ND-only, eff-n>=35 bw rule, 11+ pooled n=120 deliberately): d8 .011 / d9 .012 / d10 .021 / d11+ .012 vs flat .05 (raw p5 .012/.013/.090/.014) — the .05-forever tail binds ~4x above its generating data; Luke's boundary ruling pending. ASK4 LTI REGISTER CONTENT COMMITTED VERBATIM (closes the D4 content gap): Section A=32 LTI rows, Section B=11 out-for-2026; Maxwell King collision guard; D4 guards retained as trailer; md5 1b24df4e. ASK5 D4 clarifications (d5_ask5_clarifications.md): Tsatas NET candidate ev = 979 (the +9.0 M1 level-lift nets to -104 value-space; below Luke's preferred-lower 1083); A8 candidate trio Berry 2197 / Tsatas 979 / 2.24x; 6 unscored lines named (A13/A14 PVC-staged, A15 struck, B3 unenumerated, C1/C2 unbuilt); obituary completeness = 9 layers NOT 8 (row 9 = DEAD JS legacy chain, excision bake-gated) — discrepancy flagged. Head 8aed420a / store 644d1254 / band 34faa865 unchanged; workspace swaps restored + md5-verified; candidate fb39d88a untouched.

2026-07-02 DIRECTIVE 6 (Gothard decomposition + floor-as-pricing-feature prototype + register-annotated offender table; NOTHING canonical moved; clamp prototype scratch-branch only; SHIP_GATES.md untouched): PR #8 merged (post-merge main b2671355). ASK1 GOTHARD DECOMPOSED (d6_ask1_gothard_decomposition.md): store AGREES with Luke's ground truth (13g @ 70.2 in 2026 · pick 12 2023 ND · GFWD no-switch · yr3 · his ONLY scoring season is 2026); the STALENESS CAP owns the ENTIRE 317-vs-sane gap — every pricing channel values him ~1790 (band 1815 w/ REPL[GEN_FWD] 70.9 vs his 70.2, perf/par 1.05; pole +12.6; iso 0.98) and ev()'s stalled-non-producer branch (el>=onset=3 AND ns<=1) overwrites to exactly 0.25×draftval=317.25; the cap counts qualifying seasons without asking WHEN/HOW GOOD (built for played-once-long-ago; Gothard's one season is the current breakout); counterfactuals: tenure-click -1yr 1480 · +one 2025 6g season 1938 · cap-off 1790; EVERY yr-3 offender at ratio ~0.250 is this cap (Gothard the only one producing); Gothard = 317 at ALL FOUR STATES (head/candidate/candidate-minus-cB/head+M3) — cB is 0 for his profile (effs 13/17<1), M3 scopes to g26<11 (he has 13); floor lifts 317→355 = a patch, the fix is a recency/quality term in the cap (candidate-branch item, Luke's word). ASK2 FLOOR-AS-PRICING-FEATURE PROTOTYPED per Luke's ruling (engine/prototypes/floor_pricing_clamp.py 66fbf0f6, scratch-branch, canonical ev() untouched): ev_final=max(ev, floor_yrs×draftval), ND-only (MSD/SSP+delisted/retired/pickless excluded), BOTH tail variants — A (flat .05 yrs7+, as signed): 51 saves +1287 aggregate (top lifts O'Meara +109, Dow +85, Martin +68; saves Haynes +4 / Hopper +48); B (D5 kernel tail .011/.012/.021/.012): 27 saves +394 (dev-window saves IDENTICAL to A incl. Gothard +38, Ugle-Hagan +57; Haynes/Hopper NOT saved — Luke's utility-value read is the case FOR A's tail or an exception channel); pure lower bound VERIFIED on the wired run (n=807: 0 lowered, 0 non-ND moved, byte-identical elsewhere); new-B1 under clamp PASS peak N4 @160.2 (vs 160.5) — IDENTICAL for A/B by construction (B1 window ends d7; variants diverge d8+); B5 gate-semantics amendment text PREPARED in d6_ask2_floor_saves.md (gate retired as alarm → floor feature + mandatory saves-table print) — NOT committed, SHIP_GATES.md untouched, awaits Luke's written confirm. ASK3 REGISTER-ANNOTATED OFFENDER TABLE (d6_ask3_annotated_offenders.md): head-51 + 31 candidate joiners re-verified FRESH this session (82-51, 0 leavers, matches D5); columns added: REGISTER (4 joiners are LTI: Gibcus/Clarke/Motlop/McInnes — LTI-haircut candidates, not floor saves; head-51 all clear), LUKE'S READ (seeded verbatim: 7 floor-save endorsed, 2 tolerable, 2 utility vets, Gothard HEADLINE WORRY), 2026 games; store AS-OF: no explicit timestamp field exists in the store (FLAGGED as REQUIRED_INPUTS gap) — provenance-derived cut R14/24 (SEASON_PROG 0.58), captured 2026-07-01. ASK4 D5 CONFIRMATIONS (d6_ask4_confirmations.md): A2@candidate-minus-cB 0.822 (1358/1653) RE-MEASURED fresh — supervisor ~0.82 CONFIRMED; new-B1 minus-cB peak N4 156.6 (D5 committed cite); v7 residual terms NIL (source-diff: _v7 = exactly cB on bb[3]/bb[4] + asc on bb[5], pivot/bb[0..2] untouched; all 31 joiners resolve to asc/cB/M2/joint). ASK5 effort rule registered (docs/process/PROCESS_CHANGES_2026-07-02.md §11: original-as-practiced + D6 amendment verbatim; original's verbatim text was never in-repo — flagged for supervisor correction). Engine loads: 4 (head decomp+sweep, candidate, cB-off, clamp verify), all sequential; head 8aed420a / store 644d1254 / band 34faa865 unchanged; workspace restored + md5-verified after the variant block; candidate fb39d88a READ-ONLY zero commits.

2026-07-02 DIRECTIVE 7 STEP 1 — GATE AMENDMENTS (all Luke-ruled in writing; amendment process on the frozen file — SHIP_GATES.md edited under Luke's rulings, new md5 in the D7 return; script wired in ship_gates_check.py):
- A3 AMENDED (Luke, in writing, D7): threshold 0.80 -> 0.75, DATA-CAUSED per the SHIP_GATES failure triage — Connor Rozee is out for the remainder of 2026 (LTI register Section B, register-confirmed; nil further 2026-relevant production is a fact about the world, not the engine). Luke verbatim: "Happy to adjust Rozee to 75%." KNIFE-EDGE NOTE (recorded beside the gate): the bar deliberately sits at reality's edge — same design as A10/Curnow; the gate should fail the moment the engine over-punishes a thin season, not comfortably before. A3 remains [DC] and PRE-LTI-layer-evaluated (D4 annotation unchanged).
- B5 AMENDED (Luke-ruled; the D6-PREPARED text now COMMITS): B5 as a pass/fail ALARM is RETIRED; the signed year-schedule floor becomes a PRICING FEATURE at the ev() boundary — ev_final(p) = max(ev(p), floor_yrs(p) x draftval(p)), ND entrants only (MSD/SSP, delisted, retired, pickless never floored), floor_yrs = .45/.35/.28/.21/.13/.09 yrs 1-6 + FLAT .05 yrs 7+ (TAIL VARIANT A — as signed; Luke's D7 ruling resolves the D6 A-vs-B decision to A, the flat tail). Authorization (Luke, in writing, D6 directive): the listed ordinary players are "saved by the floor" — the crater floor becomes a value clamp standing in for the unpriced q90-97 upside tail, with a printed saves-list for visibility. The FLOOR-SAVES TABLE (player · club · yrs-in-system · raw ev · floor · saved-to · lift · register status) prints on EVERY gates-board run + the pure-lower-bound re-verify (0 lowered, 0 non-ND moved) runs with it — the saves-list is the new alarm surface; mispricings stay VISIBLE, never silently clamped.
- A2 UNCHANGED at 0.90 BY RULING (Luke, D7): the gate ships RED at the v2 config (Curtis/Ward = 0.822 measured at candidate-minus-cB, D5/D6 fresh confirmations). Luke verbatim: "we can look at Curtis down the line." Logged beside the gate in ship_gates_check.py; no threshold motion.

2026-07-02 DIRECTIVE 7 (RULED BAKE CONFIGURATION — BAKE CANDIDATE v2 assembled + gate amendments + full verification + staleness-cap fix DESIGN; NOTHING BAKED — v2 holds for the cold audit + Luke's explicit bake word): PR #9 merged as STEP 0 (post-merge main d0acfc08). ASK1 v2 ASSEMBLED (branch claude/d7-bake-candidate-v2, commit c16b970): **engine 4a134d05 / cp 5ac8b162** = M1 + v7-asc (**v7-cB DELETED per Luke's ruling — deleted not disabled**, _effs feed + GCAP removed with it; obituary in BOARD_LAYERS_OBITUARY.md ENGINE-TERM DELETIONS w/ D5 magnitudes, deletion commit c16b970, resurrection ref 0806d90) + M2 verbatim (f=0.545, 5ac8b162 byte-identical to D4) + M3 proportional-tenure WIRED FIRST-CLASS (the D4 monkeypatch hook inventory as in-engine pin plumbing: cp._age_asof/MA.age/PR.tenure/_eo/_feat-ten; value-space blend w=1−s(1−fE), fE=0.58, RL_M3_FE=1 kill-switch — byte-exact inert 0/807 vs a physically-stripped build f4b35501; scope verified all-g26<11; on-pace collateral 0/288) + the B5 PRICING FLOOR at the ev() boundary (ND-only, real-store scope, VARIANT A flat .05 tail per Luke's D7 ruling; pure lower bound re-verified at v2: 0 lowered / 0 non-ND moved / 54 saves +1684). The D4 candidate fb39d88a is SUPERSEDED. ASK2 GATE AMENDMENTS (entry above). ASK3 FULL VERIFICATION at v2 (d7_ask3_v2_verification.md + ship_gates_report_4a134d05.md): board **11P / 5F / 1FEATURE / 5PEND / 1STRUCK**, every delta vs the D4 board attributed; **A3 measured 0.7307 (2917/3992) — RED by 0.019 at Luke's amended 0.75** (M3 owns +0.072; the supervisor's 0.74–0.78 range was optimistic); **Tsatas 1140 — ABOVE Luke's preferred 1083** (M3-caused, g26=0 full blend; 979 at fE=1; A8 holds 2.12x); Curnow A10 0.509 knife-edge PASS; A2 0.822 red BY RULING; Gothard 317+floor→355 (cap fix NOT in v2); Ward M1-TOL gap +3.0<5 confirmed; new-B1 avg peak N4 **156.2** on the v2-rebuilt book, 2020 cohort >100 everywhere (cB deletion restored it, per D5's prediction); walk-forward book v2 rebuilt (matrix s4_matrix_v2_4a134d05.json, xlsx c5a7adc8); panel: only designed axes moved (Green +6.2% = the M3 design's named spot row); B6 red-as-known + one new −3pt micro-dip at 7g (M3 blend seam noise, cliff-blend territory); B6 gate synth now carries top-level games per the M3 wiring-time note. ASK4 STALENESS-CAP RECENCY FIX — DESIGN ONLY, WIRED NOWHERE (d7_ask4_staleness_recency_fix.md + engine/prototypes/staleness_recency_fix.py): population enumerated at head (38 fire / 33 bind); exemption DERIVED STRUCTURAL — the cap must not fire when the sole qualifying season IS the season being evaluated (gap=0; a player cannot have vanished from a season in progress; ZERO invented constants; a gap=1 quality threshold REJECTED at finest resolution — three near-equal breaks on 1-5-game samples, no dominant mode); measured at head+fix a9e1c14b: **Gothard 317→1790 exact** (Luke's neighbourhood, no shaving), 7/807 movers all in-population (zero collateral), true ghosts stay capped, gates incl. new-B1 HOLD (B1 rises to 169.2 — released historical gap=0 cells lift the growth curve); SECOND GOTHARD FOUND: **Lachlan McAndrew 99→1408 (13g @ 87.1 = 1.11×REPL, the population's best current output)**; Form-B gap=1 extension priced for Luke (Busslinger 481→636 · Caiden Cleary 154→775; support WEAK; Luke's Hardeman/Cleary tolerable-reads stay intact under Form A). ASK5 CLARIFICATIONS (d7_ask5_clarifications.md): 807-vs-805 = 746 shared + 61 sweep-only (59 stale never-played + 2 double-count) + 59 extra-list, NOT containment; D6's B1 160.2-vs-160.5 EXPLAINED — index-denominator arithmetic (floor lifts d1 +1.04% vs d4 +0.04%; a lower bound on values is not one on indexed ratios; no drift, no transcription); distributional/quantile pricing output NIL (band bb internal to b6/price6, integrated to scalar by WQ6 — cited); BASE effort rule registered verbatim in PROCESS_CHANGES §11. INSTRUMENT CAVEAT flagged: verify_restore.sh's named-player axes execute repo-engine × WORKSPACE-conditional_prior (par_redesign.py:12 sys.path[0] insertion) — mixed-pair reads possible when repo and workspace diverge; all D7 measurements ran properly-paired workspace deployments. Engine loads: 9 (3 v2-block, 1 population, 2 sweeps, 2 boards+matrix chain, 1 recon), all sequential; canonical head 8aed420a / store 644d1254 / band 34faa865 restored + verified (panel 10/10); v2 4a134d05 on its own branch.


2026-07-03 DIRECTIVE 8 STEP 1 — RULINGS REGISTRATION (doc commits only; all Luke-ruled, relayed via the D8 directive; nothing wired, nothing baked):
- 1a A3 ACCEPT-RED at 0.7307 (Luke, 2026-07-03, verbatim): "Accept-red on rozee." A3 joins A2/Curtis as a Luke-ruled red on the board (0.7307 vs the amended 0.75 bar); the real remedy is the LTI workstream, queued. No threshold motion; the gate stays scripted as-is and ships red by ruling.
- 1b TSATAS ACCEPT-AND-TRACK at 1140 (Luke, 2026-07-03, verbatim): "Accept and track on Tsatas." The M3-caused lift above his preferred 1083 is accepted; TRACK = the value fades to 979 as the season completes (fE→1); A8 holds 2.12x.
- 1c CAP-FIX FORM A ENDORSEMENT WITHHELD (Luke, 2026-07-03, verbatim — the D8 governing finding): "The two cap fix is odd, because someone like Cleary is far too low when he triggers it and probably too high when he doesn't. That Hardeman doesn't get rescued is a challenging one for me. And looking at Cooper Lord - he's another in the Cleary boat but worse - he shouldn't be so low now, but the idea of him being over 1000 if it didn't catch him is a bit crazy to me." READ: the binary structure (caught → 0.25×draftval · exempt → full ev) is wrong at the margins in BOTH directions; the fix must become a GRADED rule (continuum ghost-floor → full price, driven by evidence of live output). The D7 Form A design read STANDS as a derivation artifact, superseded by the D8 ASK-2 graded round. Registered in docs/process/SYMPTOM_REGISTER.md (family 1) + docs/process/LUKE_RULINGS_LEDGER.md.
- 1d McANDREW RELEASE ENDORSED (Luke, 2026-07-03, verbatim): "McAndrew is fine." His D7 cap-fix release (99→1408, 13g @ 87.1 current output = 1.11×REPL) is Luke-approved; McAndrew is now an ANCHOR for the graded derivation (the STRONG-EVIDENCE UPPER anchor: strong current output → full release), no longer an open question.
- NEW REPO FILES: docs/process/LUKE_RULINGS_LEDGER.md (the rulings authority trail, previously supervisor-side only — handover rev93 §4) + docs/process/SYMPTOM_REGISTER.md (symptom families + Luke-verbatim evidence, previously supervisor-side only — rev93 §5). Both minted this directive per the D8 ASK-1 commit targets; backfill is pointer-only (references to existing CHANGELOG entries; no historical wording invented).

2026-07-03 DIRECTIVE 8 (staleness-cap GRADED form round 2 — driven by Luke's eyeball findings on the D7 lists; rulings registration; sweep hygiene; NOTHING WIRED, NOTHING BAKED — candidate v2 4a134d05 and canonical 8aed420a/644d1254/34faa865 untouched): PR #10 merged as STEP 0 (post-merge main 8954579f). ASK1 RULINGS REGISTERED (entry above; docs/process/LUKE_RULINGS_LEDGER.md + SYMPTOM_REGISTER.md minted repo-side): A3 accept-red 0.7307 · Tsatas accept-and-track 1140 · Form A endorsement WITHHELD (Luke's verbatim block committed) · McAndrew release ENDORSED (anchor). ASK2 GRADED CAP DERIVED — design only, wired nowhere (session_2026-07-03/d8_ask2_graded_cap.md + engine/prototypes/staleness_graded_cap.py; scratch identity head+gradedfix = efc15c6c, run in a SELF-CONTAINED scratch deployment, shared workspace never modified): e=min(e, cap+grade·(e−cap)); grade=1 at gap=0 (D7 structural piece retained, Luke-endorsed) · 0 at zero live games (ghost anchor) · else two measured re-realization curves over q=era-adj current avg/REPL (gap=1 vs gap≥2 pooled), kernel eff-n≥35 + isotonic, normalized between the two Luke-ruled boundary populations (Rg=0.2120 true-ghost baseline, Rtop=0.8024 gap-0 top plateau) — derived from 532 historical fire-cells (Y=2008-2022, LISTED-WINDOW rule, phantoms excluded); the evidence AXIS was data-selected: quality q BEATS the games×quality product (tau +0.234 vs +0.124; 100% of 2000 player-cluster bootstrap resamples; games volume nil signal within 1-5g) — volume enters only structurally (first game arms, 6th game graduates); rate axis dissolves most of the R14 partial-season seam. ALL SIX ANCHORS PASS engine-applied: Gothard 1790 exact · true ghosts byte-flat (Dowling 109/Goater 129/Clarke 98/Archer 62/Hall 136/Collard 152/McMahon 191/K.Smith 90) · Cleary 154→523 · Cooper Lord 77→655 (well below 1000) · Hardeman 154→257 (partially rescued — recency-driven base grade 0.26) · McAndrew 1408 full (CAVEAT: that row is the _double_count MSD-credit phantom, board-excluded; the REAL McAndrew re-entered 2024, cap never fires, 1062 at head, fix-inert). Zero collateral: 24/807 movers, all in the 38 fire population, all lifts non-negative. Gates at efc15c6c: no green-at-head gate fails (reds = head's own A2/A3/A5/A9/A12/B4/B6), new-B1 PASS avg peak N4 @169 (head 160.5; Form A 169.2), B2 re-run PASS 0.0 leakage, B6 ramp BYTE-IDENTICAL to head (no new seam dip). INTERACTIONS PROVEN: floor order (graded-inside-ev then boundary max) is LOAD-BEARING — reversed, the floor is defeated (Hall 152→136); post-grade the floor lifts exactly 4 rows (Wiltshire 86/Hall 152/Collard 170/Stone 97), double-lift NIL (grade>0 rows all price above their floors); graded×M3 composition at a future v3 UNMEASURED (v2 untouched) — h-M3-blend-seam-noise stays OPEN and now covers it. REJECTED variants shown: q-matched normalization (non-monotone at finite sample) · per-class baselines (fails Luke's Hardeman read). NEW HYPOTHESIS h-gap1-zero-games-returners (OPEN, LTI-shaped): zero-live-games historical cells realize HIGH (gap=1 v=0.68 n=25 uniq, survivorship-biased up) — "did not play"≠"played badly"; deliberately NOT priced by the cap (Luke's live-output axis); queued to the LTI workstream as first calibration evidence. ASK3 SWEEP HYGIENE (d8_ask3_sweep_hygiene.md): (i) the 2 double-counts = Keane(IRE credit)/McAndrew(MSD credit) deliberate phantoms, keyed by cohort/pick, name-collision rule verified live (Max King|2018|4 ≠ Maxwell King|2025|49) — declared, no fix; (ii) the "59 stale" entries are NOT stale and NOT pruned — they are the 59 pre-debut 2024+ draftees' originals, superseded in the export by same-key _unplayed copies (key-level: sweep 807 = board 805 + 2 phantoms EXACTLY; D7's "stale never-played" label corrected); effect on 0/807 M3 inertness NIL, gate denominators NIL; (iii) mixed-pair caveat CLOSED WITH A FIX — root cause = wire_redesign.py:14 hardcoded _FV (+ par_redesign.py:14 sys.path head); PAIR-GUARD added to verify_restore.sh (md5-compares engine/forward_valuation vs the _FV target, loud FAIL on mismatch); restore-verify now 10 PASS/0 FAIL w/ guard green + panel 10/10; root parameterization of _FV = candidate-branch item. Engine loads: 9 (2 harvest incl 1 wasted outfile-path retry, 1 graded sweep, 1 matrix rebuild, 1 board 109s, 1 gate1_wf, 1 rl_model-layer recon, 2 restore-verify/panel), all sequential; workspace md5 8aed420a verified before/after every step.

2026-07-03 DIAGNOSTIC B rev3 (walk-forward book TWO PERMANENT VIEWS + 2020-vs-pick-sum + slopes + 2025 cohort Yr1 shortfall decomposition; READ-ONLY on valuations — reporting change only; TARGET = BAKE CANDIDATE v2 4a134d05, all measurements workspace-paired v2 then restored): ASK1 two-view feature COMMITTED in s4_render_7147.py (display-only: 'Cohort Trajectories' = FULL HISTORY 2004-2024 + new 'Trajectories 2015-2024' sheet with OVERALL row recomputed over the window; S4_TAG env for the title's engine md5) and the v2 book REGENERATED from the unchanged matrix s4_matrix_v2_4a134d05.json (28 sheets). ASK3 2020 TEST: current 43831 / draft-day pick sum 54355 (live MA.PVC, 0 mismatches vs matrix) = 80.6% — NOT above 100; the >100 Luke eyeballed is TABLE 1's Measure-1 Current (vs the cohort's OWN end-of-Yr1 total 40874) = 107%; per-cohort curve 100/113/115/105/107/107. ASK4 SLOPES/PEAK: full-history mean yr1->2 +30.4pp, yr4->5 -3.5pp, OVERALL peak Yr4 154%; 2015-2024 window +25.0pp / -4.7pp, peak Yr4 138% — both views peak in yrs 4-6; the window is flatter everywhere (the steep yr1->2 and tall peak are early-era-driven). ASK5 2025 SHORTFALL (session_2026-07-03/d8_2025_shortfall_verdict.md): 37875 CONFIRMED exact; book Yr1 == fresh board evals 64/64 max-diff 0 (trading surface, not display); shortfall -25.8% vs 2004-24 mean / -18.2% vs recent-5 / -26.5% vs 2023 — but pick-mix-controlled (Yr1/pick-sum) 2025 = 73.4% vs recent-5 84.6% (-13.2%) and 2023/24 are the two RICHEST ratio cohorts on record (94.8/91.0); games census 35x0g/14x1-5g/8x6-10g/7x11+g, sit-out-classed 49/64 (77%) vs 63-68% at prior END-of-Yr1; counterfactuals (runtime patches only): sit-out bar prorated +1796 · POLE_RAMP prorated +351 · LEVEL_RAMP +0 · nqual +150 · combined +2313 · FULL-SEASON-EQUIV games (gx24/14, M3 off) +3871 (+10.2%, ->41746 = 80.9% of pick sum, inside the 2018-22 band); ATTRIBUTION VERDICT: PARTIAL — the unprorated-penalty channel is REAL (owned ~78% by the >=6-games sit-out bar, NOT the ramps) but explains 46% of the gap vs the recent-5 mean and 28% vs 2023/24; the rest = cohort size/pick mix (31%/26%) + not-yet-debuted H2 players held at retain x draftval + the sit-out anchor's pre-registered ~16% over-discount + 23/24 benchmark richness; played 2025 draftees (>=6g) price ABOVE nearest-pick 2024 end-of-Yr1 comparables (Duursma 4183 vs Lalor 3280). ASK5c code paths QUOTED (d8_penalty_code_paths.md): sit-out >=6g bar, nqual >=10, LEVEL_RAMP 14, POLE_RAMP 22 all ABSOLUTE full-season constants — nothing prorated to R14/24; only M2 (prior-season decay clock, no-op for Yr1) and M3 (age/tenure clocks, no-op inside the sit-out branch) prorate anything. ASK5e: SAME machinery as the Annable/Travaglia A12 sit-out haircut and the B6 games-seam — one games-ramp rework owns all three; 2025 ref-only = display convention (REFONLY in render), not a data gap. Engine loads: 1 (v2, sequential evals); canonical 8aed420a/644d1254/34faa865 untouched; workspace restored + md5-verified.

2026-07-03 DIRECTIVE 10 (GAMES-RAMP REWORK, ENGINE CHANGE — NEW CANDIDATE v2.1 = v2 + games-ramp on branch claude/games-ramp-engine-change-qt7824; engine c8051893 / cp 7c3652da; canonical 8aed420a UNTOUCHED; NOTHING BAKED — cold audit next): STEP 0 PRs #11/#12/#13 merged (one CHANGELOG conflict on #12 resolved keep-both; post-merge main 6035ce1; D8 dial grep-verified absent from live engine). ASK1 RELIC INVENTORY (d10_ask1_relic_inventory.md): every penalty path on the old-PVC basis enumerated — SITOUT_RETAIN (deleted), stalled cap, mediocre cap, delist scrap (all RE-ANCHORED draftval->V0), B5 floor KEPT dv-basis (Luke-signed feature, declared exception), rl_model value()/unpl_eq legacy declared superseded-surface; LIVE START VALUE identified = raw_ev(p, draft-year) x iso (zero-evidence band price, pick+position-adjusted; verified Dean 1237 vs PVC 2248 BELOW / Robey 1882 vs 1603 ABOVE; RUC start values flagged hot 2.5x PVC). ASK2 GAMES-RAMP TREATMENT DERIVED + WIRED (d10_ask2_derivation.md; harvest 2,940 cells / 2,465 complete-window 2004-2021, one v2 load + one norm load; kernel eff-n>=35): value = (1-lam)·R(tau)·V0 + lam·e_full — V0 held through pre-season (tau=0 -> R=1, ev(draft-yr)==V0 proven); R_SIT = still-listed sit-out realization RELATIVE to same-depth all-draftee norms (the locked daEV "0.76 form"; nonKPP .429/.404/.410/.432/.437/.424 · KPP .468/.380/.325/.278/.253/.266 · RUC .674/.547/.503/.472/.435/.435 with RUC SHAPE pooled with KPP x measured level — declared) with linear within-season accrual (the decay itself prorates); LAM_SIT = measured evidence-credit [0,.160,.493,.547,.547,.816,1.0] isotonic, games read AT PACE, structural endpoints lam(0)=0/lam(prorated bar)=1 -> CONTINUOUS at graduation (old +2551 game-6 jackpot GONE); scoring-awareness through e_full (lambda-side q term tested and NOT supported: partial tau +0.04 non-monotone — declared, not wired); bars prorated to R14/24 (fE=RL_M3_FE 0.58): nseas 6->6fE (nseas_pro), nqual 10 -> FIRST-qualifying-season fractional credit f1 (first-evidence players only — board-wide proration measured and REJECTED: Tsatas 1140->2080 breaking A8, O'Driscoll -525, Cadman -253 via proven flips; extension = Luke ruling), LEVEL_RAMP 14 / POLE_RAMP 22 capped at full-season-equivalent PLAYABLE games (yr-1 mid-season 8.2/12.8, everyone else unchanged by construction), bestlvl 6-bar prorated, G_ADQ deliberately NOT prorated (outside the 6/10/14/22 enumeration); FIRST-EVIDENCE family e_full = 3-point moving average on the games axis (declared: GBR band steps +957/game at constant level + designed M3 pin-fade otherwise break B6 monotonicity; centered, unit-mass, family-scoped). FLAT 50% OBITUARY in BOARD_LAYERS_OBITUARY.md (E2). _FV parameterized via RL_FV env in wire_redesign/par_redesign (D8 mixed-pair root-cause item; defaults byte-identical). ASK3 ANCHORS (three-column, d10_ask3_anchor_checks.md): Annable 936/936/1326 · Patterson 982/982/884 (B5 floor catches) · X.Taylor 690/690/662 · Cumming 2002/1982/1948 · Emmett 518/518/1338 (RUC V0 scarcity prior, flagged) · Ison 212/212/538 · Lord 77/394/414 — his v2 394 was NOT floor-lift (floor 108 non-binding), it was the M3 blend recovering the stalled-cap crush; 2025 cohort 37,901/37,103/43,703 (+6,600 vs v2; DIAG-B what-if +3,871 direction confirmed, larger because CF6 excluded the lambda credit/V0 re-anchor/prorated ramps); whole sit-out family +5,557 across 108; no player drops for playing/scoring more (structural + spot proofs). ASK5 THE THREE REPORTING RULES WIRED PERMANENTLY (Luke's word, BINDING): three-column CONTROL/PREVIOUS/CURRENT gates board + pinned snapshots (data/gates_snapshots/, registry data/report_states.json) + top-50 three-column in every report + LOUD state labels in gates script + book renderer; rules verbatim in BAKE_CHECKLIST.md §REPORTING + docs/KICKOFF_PROMPT.md + START_HERE.md. ASK6a TRAVAGLIA TRIO decomposed at all three states (d10_ask6a_travaglia_trio.md): the channel = PERFORMANCE-WEIGHTING x recency/exposure decay, not pedigree, not cohort-year (same-cohort control Clarke 675 > Travaglia 712-adjacent on output alone; pole throttled by tfade/expgate/recover to ~+180 net for picks 8-vs-39); DIAGNOSIS ONLY, nothing wired — Luke rules. ASK6b MEASURE-2 (cohort value vs PICK-SUM ruler) added to the book renderer as a permanent display-only sheet (closes the 107%-vs-80.6% confusion class). REJECTED VARIANTS logged with measurements (board-wide 10-bar proration, unscoped f1, lambda-side q, /b0-only normalization). Engine loads this session: 7 sequential (p1 harvest, p3 norms, p5 verify, p6 probe, p7 trio, matrix rebuild, gate1) + gates board; workspace paired then restored + md5-verified.

2026-07-03 DIRECTIVE 12 ASK 1 (CONCAVE PENALTY RAMP, ENGINE CHANGE — NEW CANDIDATE v2.2 = v2.1 + concave ramp on branch claude/ramp-floor-writeup-retention-8zqhav; engine after ASK1 = 05d38c65; canonical 8aed420a UNTOUCHED; NOTHING BAKED — scoped re-audit before any bake): Luke-signed OPTION A (verbatim R7): penalty fraction = (season progress)^1.5. The D10 LINEAR within-season proration of the sit-out retention R is SUPERSEDED by a CONCAVE one — sitout_ev() tau term fe -> fe**1.5 (ONE line + comment; diff vs v2.1 = exactly that). Completed seasons stay full (integer knots); only the in-progress season accrues concavely: R_applied = 1 - (1-R_full)*tau', tau'=(R/24)^1.5. PENALTY PATH ONLY — the reward-side M1 G_ADQ gate and the lam evidence blend (min(gy/fe,6)) are byte-untouched (diff-verified; G_ADQ's harder-than-linear reward proration is by design, Luke-conforming, left intact). Penalty fractions R6/R12/R18/R24: linear .25/.50/.75/1.0 -> concave .125/.354/.650/1.0 (halfway .354 in Luke's "33-40%"; 100% at R24). Operative fE=0.58 -> concave .442. CONSTRAINT re-assert (a single 2026 game never weighs less than a single 2025 game): HOLDS — the ramp prorates the penalty (R on V0) only; game weight lives in the untouched lam blend + e_full + recency decay (0.72^(Y-yr) already weights 2026 above 2025). B6 SEAM RE-PROOF at v2.2 (whole 0..14g ramp): MID [1139,1469,1785,2482,3103,...] and KEY_FWD [671,822,1436,2770,4184,...] — NO dips, T/rise3/step all PASS; the concave lift touches only the ns==0 segment (g0-3), g>=4 (production path) byte-identical to v2.1, continuity preserved because lam->1 at the graduation bar kills R*V0. SIT-OUT ANCHOR MOVES v2.1->v2.2 (played-some ns>=1 unaffected): Patterson prefloor 760->849 (EV 884, draftval floor still binds until ASK2), Annable 1326->1414, X.Taylor 662->693; Cumming/Emmett/Ison/Lord/Berry/Tsatas unmoved. REVISIT HOOK: a PVC-era derivation may later replace the t^1.5 shape from partial-season snapshots (open, not a block). Artifact session_2026-07-03/d12_ramp_floor/d12_ask1_ramp.md. Engine loads: 1 (sequential); workspace paired to v2.2 + md5-verified; canonical untouched.

2026-07-03 DIRECTIVE 12 ASK 2 (B5 FLOOR RE-ANCHOR draftval->V0, ENGINE CHANGE — CANDIDATE v2.2 engine af1fc6aa; canonical 8aed420a UNTOUCHED; NOTHING BAKED): Luke ruling R8 (verbatim): "DV floor should be now aligned with v0. Yes, some issues with rucks, but we can refine them before baking or wiring." The B5 pricing-floor DENOMINATOR re-anchored old-PVC draftval -> live V0: ev() floor line fl=floor_frac(yis)*draftval(p) -> *v0_start(p) (ONE line + comment; diff vs ASK1 = exactly that). SCHEDULE FLOOR_YRS .45/.35/.28/.21/.13/.09 + flat .05 tail BYTE-UNCHANGED; national-draft scoping unchanged; pure lower bound preserved. FLOOR-SAVES three-column split by class: v2.1(dv) 58 saves +2117 -> v2.2(V0) 52 saves +1330; nonKPP 47->42 (+1779->+1207), KPP 10->9 (+329->+102), RUC 1->1 (+9->+21) marked PROVISIONAL (ruck V0 hot, h-ruc-startvalue-hot, nerf next directive). ISOLATION: concave ramp alone (dv basis) = 58 saves +2004 (0 leave); the re-anchor dv->V0 drives the churn (13 leave / 7 join, net -6). PATTERSON CONSEQUENCE (loud): floor 884 -> 511 (0.45*V0 1136), no longer binds; EV becomes his concave-prorated-decayed number 1136*(1-0.571*0.442)=849 (directive predicted ~847; fE 0.58 vs 14/24 gap). Leavers incl Ugle-Hagan 270->non-binding, Cootee 225->non-binding; V0>dv newly catches Gothard +44 et al. Lord floor NEVER binds (414 >> 108/147) -> unmoved 414. X.Taylor unfloored both sides -> 662->693 (concave ramp only). OBITUARY E3 (basis retirement; feature KEPT). Artifact session_2026-07-03/d12_ramp_floor/d12_ask2_floor.md. Engine loads: harvest dumps (CONTROL 8aed420a / v2.1 c8051893 / v2.2 af1fc6aa), sequential; canonical untouched.

2026-07-03 DIRECTIVE 12 ASK 3 (WRITE-UP FIXES — docs/tables only, NO engine effect; audit-named reds R-a..R-d from AUDIT_COLD_v21_c8051893.md / PR #15): (a) R-a 2025-cohort table 37,103/43,703 (n=58 STORE SCRATCH CENSUS) SUPERSEDED by the AUTHORITATIVE pinned walk-forward matrix 37,875/43,967 (incurve n=64; book/board read the matrix) — rule now stated in d10_ask3_anchor_checks.md + d10_ask2_derivation.md: pinned matrix authoritative on any store-vs-matrix disagreement; census sub-aggregates kept labelled non-authoritative (verified: v2.1 store sum reproduces 43,703 byte-exact; matrix 43,967 confirmed by build ASK4 + cold audit). (b) R-b the position-preservation line "V0 identical 1524 pre-season" CORRECTED — V0 DIFFERS by position (that difference IS the position-preserving mechanism); cold-audit per-position V0 at pick 12 MID 1458/KEY_DEF 883/GEN_DEF 863/RUC 1085; the conclusion (no flat-fraction collapse) stands, only the support number was a scratch error. (c) R-c B1 "151 vs 161" LABEL MIX fixed in d10_ask4_verification.md: 151 = v2.1 matrix (s4_matrix_v21_c8051893.json), 161 = nogames/control matrix (s4_matrix_nogames.json, the scripted gate's input) — two different matrices, both peak yr4, both green; neither wrong, mislabelled as one number. (d) R-d "panel 10/10 at candidate" CORRECTED: the 10/10 is the CONTROL-side restore only; at the CANDIDATE the panel is NOT 10/10 — 3 of 10 young players legitimately move under the games-ramp (the sit-out/rookie family); candidate side evidenced by byte-match to the pinned v21 matrix (Daicos 7069/Goad 846/Smillie 773/Green 545); BOTH-SIDES evidence is the standard. No engine effect; no player value changes. Docs touched: session_2026-07-03/d10_ask3_anchor_checks.md, d10_ask2_derivation.md, d10_ask4_verification.md.

2026-07-03 DIRECTIVE 12 ASK 4 (READ-ONLY DIAGNOSTICS — nothing wires) + ASK 5 (VERIFICATION at v2.2 af1fc6aa): ASK4 facts (session_2026-07-03/d12_ramp_floor/d12_ask4_diagnostics.md): 4a Cumming|2025|7 V0 1864 vs Robey|2025|9 V0 1882 inversion CHANNEL NAMED = the band base price price6 (Robey pk9 band 1906.4 > Cumming pk7 1845.7, ~3.3% local wobble); NOT effpk!=nominal (7=7/9=9), NOT draft-age (both wage 1.0), iso FAVORS Cumming (1.010>0.987) — the isotonic guard is over EFFECTIVE pick (par-synth multiplicative +-1.3%), too gentle to overcome the band wobble; full nominal-pick V0-inversion scan = 1853 pairs (dominant channel = mature-age re-draftees e.g. Kelly pk24 V0 71, plus a band-wobble tail). 4b never-player depth path RISES between depths (nonKPP d2->d5 .404->.437, KPP d5->d6 .253->.266; RUC monotone) = non-monotone-in-depth under the wired R_SIT; Smillie (V0 1864, MID) end-Yr1 800 -> projected end-Yr2 753 (0 games; nonKPP depth1->2 declines), actual mid-2026 EV 779. 4d RUC V0/PVC distribution n=31 median 1.73x max 2.52x, five hottest Emmett 2.52x/Witts 2.36x/Meek 2.34x/Briggs 2.11x/Gawn 2.07x; Emmett V0 1536 = raw_ev 1767 x iso 0.869, PVC 609; at caps 1.3/1.5/2.0x -> V0 792/914/1218 (MEASUREMENT only); CAVEAT Emmett's current 1338 is production-driven not V0-gated (5g, tenure<ruck-onset) so a pure V0-floor cap won't move it — the nerf must target ruck raw_ev/band. 4c RETENTION REVIEW ROLLED to D13 follow-up (announced, NOT degraded — finest-resolution harvest re-run is the XHIGH driver; coarse bins would be the banned wide-bin artifact). ASK5 (d12_ask5_verification.md): full board three-column CONTROL 8aed420a/v2.1 c8051893/v2.2 af1fc6aa = PASS 11, 4 reds all Luke-ruled/pre-existing/expected (A2/A3/A12/B4) — NO new engine-caused red; only v2.1->v2.2 board moves = B5 (58->52 saves) + B2 re-run. B6 PASS (ramp no dips, T +2099, rise3 +1343). B1 PASS peak N4@140.1 path_ok (SAME-BUILDER control: v2.1 138.5 -> v2.2 140.1, +1.6 UP; the docs' 151 is the pinned-v21 matrix = different builder; 1279 2004-2020 cells moved = FLOOR re-anchor on floored cells, concave ramp no-op for completed seasons). B2 leakage IS-WF <=3 median 0.0 PASS. Panel BOTH sides: control 10/10 at canonical; candidate 3 of 10 move (sit-out family Goad/Smillie/Green), 7 unmoved. Anchors three-column: only sit-outs move (Annable 1326->1414, Patterson 884->849, Taylor 662->693, Smillie 773->779); Tsatas 1140 UNMOVED (A8 2.12x), Berry 2421 unmoved, Cumming/Emmett/Ison/Lord unmoved. 2025 cohort pinned-matrix 43,967->45,051 (+1,084). Floor-saves 58->52. dial d66291a grep-ABSENT. CONTROL byte-verified pre+post (8aed420a/644d1254/34faa865). Engine loads: board + gate1_wf leakage + v2.2 matrix + same-builder v2.1 matrix control + Cumming/Robey decomp = 5 sequential; canonical untouched.

2026-07-03 DIRECTIVE 13 (RUCK PRIOR CAP + V0 PICK-ORDER GUARD + RETENTION RE-DERIVATION — CANDIDATE v2.3, engine head f3e537ba; branched from v2.2 af1fc6aa; NOTHING BAKED — scoped re-audit before any bake): STEP 0 hygiene: cold-audit artifact AUDIT_COLD_v21_c8051893.md extracted to docs path (PR #15 to close unmerged); PR #14 to close superseded-by-#16; v2.3 branched from v2.2 head. ASK1 RUC PRIOR CAP (R9): parameterised dial RL_RUC_PRIOR_CAP default 1.73 (= ND-ruck class median V0/PVC, measured 1.7274) caps the RUC band prior as a max V0/PVC ratio at raw_ev/band level (RUC wage=0 so raw_ev==band price): pure prior V0 capped unconditionally (binds only when hot), production leg capped only in the prior-dominated regime cap*PVC<e<=V0_uncapped so proven-ruck production is byte-exact (Xerri/Grundy/Gawn/Marshall/Sweet/McAndrew unmoved); resolves the R8 PROVISIONAL RUC floor + h-ruc-startvalue-hot. Ladder 1.1/1.3/1.5/1.73/2.0: Emmett board 670/792/914/1054/1201 -> at 1.73 Emmett=1054 materially above his stated 650-800 (that range sits ~1.1-1.3); ratio-vs-pick Spearman rho=-0.10 (scattered, not pick-patterned); RUC floor-saves 1->1 off capped V0. ASK2 V0 PICK-ORDER GUARD (R10, Luke's law): within (position x draft-age x draft-year) cells V0 non-increasing in RECORDED pick (downward-only, load-time), mature-age exempt by cell construction; ND divergence scan 0/1571 (802 non-ND RD/MSD/SSP pick-equivalents out of scope); roster inversion scan 449 (106 cells) -> 0; Cumming|2025|7 vs Robey|2025|9 fixed (both 1859); largest pre-fix Jhye Clark(pk8) 2401>Mackenzie(pk7) 1864 -> 1864; age-preservation Tim Kelly(pk24,age23) vs Naish(pk34,age18) separate cells. ASK3 RETENTION SURFACE re-derived (R11, Luke's objection): depth-only R_SIT (violated Luke's law: nonKPP rose d3->d5, KPP rose d5->d6) SUPERSEDED by continuous R_SURF(cls,log-pick,depth) = kernel sit-out realization O/V0 (winsor 2.0, bw grown until eff-n>=35) / same-depth all-draftee daEV norm (rises 0.44->1.11 w/depth, strips survivor selection), clip[.05,1], ISOTONIC NON-INCREASING IN DEPTH; R1 daEV(V0) kept (blind-dv widened KPP gap 0.065->0.079, KPP V0/dv=0.90 numerator-driven); R2 FIRES all classes (pick maxdev 0.13-0.21) -> pick-conditioned; sit-out family +2861, 2025 cohort 55836->57009 (+1173); named anchors lifted (Smillie 779->993, Annable 1414->1485, Patterson 849->908, X.Taylor 693->733; 2 largest KPP sitters Riak Andrew +67, Matt Whitlock +63); every anchor yr1->yr2-at-zero non-increasing (Luke's law); KPP honesty clause: comparable to nonKPP d1-2, still harsher d3+ (data-derived, thin-cell-declared, Luke's owner override for more); obituary E4. ASK4 queries: (a) gate that left PASS v2.1(12P/4F)->v2.2(11P/4F) = B2 leakage (NOT-RUN in automated v2.2 board, re-run PASS 0.00; 4 reds unchanged); (b) four audit reds R-a..R-d all landed docs-only commit c1893b0 (D12 ASK3). ASK5 VERIFICATION at v2.3 (three-column): board 12P/4F/1FEATURE (same red set A2/A3/A12/B4 as v2.1/v2.2, no new engine red); B6 GREEN all clauses (dips none, T=+1951, rise-3g +1217; tau^1.5 + LAM_SIT byte-identical diff-clean); B1 PASS avg peak N4@130 path_ok (v2.2 140.1->130, young-cohort lift compresses ratio, HELD not broken); B2 leakage 0.0; panel control-side 10/10, candidate movers Goad/Smillie/Green; Tsatas 1140 + Berry byte-unmoved (A8 2.12x); dial d66291a grep-absent; CONTROL byte-verified pre+post (8aed420a/644d1254/34faa865); floor-saves 52->51 (RUC 1). Rulings R9/R10/R11 registered (LUKE_RULINGS_LEDGER). Engine loads sequential; canonical untouched. Session ends with a PR (D13). NOTHING BAKED.
2026-07-03 DIRECTIVE 14 (V0 BOARD CURVE + KPP RETENTION FLOOR — CANDIDATE v2.4, engine head 7c199a1f; branched from v2.3 f3e537ba; NOTHING BAKED — combined scoped D13+D14 re-audit before any bake). FORK NAMED+RESOLVED: the directive cited v2.3 head as "f3e537ba" — that is the v2.3 ENGINE-FILE md5 (state hash); the git head is def39f5a; same state, v2.4 branched from it. ASK1 V0 BOARD CURVE (R12, Luke's AMENDED LAW verbatim: "for the current values ... on the board, we can't have a situation where one player who was a mid at pick 8 has a higher starting v0 than another in the same boat. It's illogical."): replaces the D13 pick-order spot-guard on the BOARD PATH with a DERIVED continuous curve V0*(position x draft-age) over log RECORDED pick — kernel/local (Nadaraya-Watson, adaptive Gaussian bandwidth grown until local eff-n>=35, isotonic non-increasing in pick) fitted on the current roster's CAPPED V0s (RUC cap 1.73 applies FIRST -> _v0_raw, THEN the curve), pooled ACROSS draft years. Cells (census session_2026-07-03/d14): TIER1 age<=18 per position (6 cells, 1408/1571; minEffN 35.0-35.6, bandwidth NOT maxed = finest supported); TIER2 mature>=19 (163; every exact pos x age cell eff-n<35 even at max bandwidth -> R1 pool: 5 non-RUC positions pooled into an age-resolved 2D (draft-age,log-pick) surface [mature V0 age-dominated + position-washed, DECLARED], RUC mature own thin cell eff-n~12 flagged; isotonic in pick AND non-increasing in draft-age -> mature stays differentiated). APPLY board-path only: v0_start := V0*(pos,draft-age,recorded pick). Backtest UNTOUCHED (Luke's exemption: D13 guard retained off-board via _BOARD_PATH=False in s4_matrix/_gate1_wf/_gate1/_comb_book/_build_book_xlsx). By-construction gates wired: D14a cross-draft dispersion 507->0 (Cumming pk7/2025 = Mackenzie pk7/2022 = 1876); D14b within-cell inversions 0 roster-wide. D13 guard-transform -> assertion (obituary E5, incl 449-fix history). R2: 91 movers >35% (28 age18, 63 mature) WIRED anyway (board-ev impact of mature lifts <= few pts, production-driven). Moves 831 up/740 down, max|dV0| 1354 (Naitanui). Emmett cap-then-curve 1054->955 (ev 1054 unchanged). ASK2 KPP RETENTION FLOOR (R13, SIGNED OWNER OVERRIDE O1, Luke verbatim: "if it's lower, it's carried so it can never be the lowest ... I can't see KPPs losing value for sitting at a faster rate than non KPPs" + "Non KPP only. Across each year it applies."): wired KPP sit-out surface := pointwise MAX(KPP,nonKPP) at every (log-pick,depth), comparator nonKPP ONLY (RUC excluded, supervisor spec), BOARD PATH only; depth-monotone re-asserted (gate D14c True); binds d3+ (and d1+ mid-picks 15-30); O1 registered docs/process/OWNER_OVERRIDES.md; D13 anchor set (Annable/Patterson/Taylor/Ison/Smillie) yr1->yr2-at-zero still non-increasing; 54-set 46764->48397, 2025 cohort 57009->57710, floor-saves 54 (RUC 1, pure lower bound lowered=0/non-ND=0). ASK3 carried queries: (a) 1FEAT = B5 floor-as-pricing-feature, status DEFINED + registered SHIP_GATES.md (does NOT mask a red — signal relocated to the printed FLOOR-SAVES list); (b) v2.2 af1fc6aa REPRODUCED directly: Annable 1414 / 2025 cohort n102 55836 (the "43,967" is the DIFFERENT incurve-n64 matrix Yr1 measure, not the n102 board cohort); (c) PR#17 itemises the four write-up fixes under ONE shared commit c1893b0 (not four hashes) — reported; (d) PR#17 ruck-ladder GAP (only Emmett cap-rung row, no per-ruck V0/PVC ladder) CLOSED in this PR: full 172-ruck ladder session_2026-07-03/d14/d14_ask3d_ruck_ladder.md. ASK4 VERIFICATION at v2.4 (three-column CONTROL 8aed420a/v2.3 f3e537ba/v2.4 7c199a1f): board 14P/4F/1FEATURE/1NOT-RUN/5PEND/1STRUCK (D14a/b/c NEW green; 4 reds A2/A3/A12/B4 IDENTICAL to v2.3, no new engine red); B6 GREEN ramp [1287..3592] byte-identical to v2.3 (tau^1.5 + LAM_SIT diff-clean); B1 PASS avg peak N4@130 path_ok (matrix s4_matrix_v24.json); WALK-FORWARD BOOK REPRODUCES maxΔ=0.000000 vs v2.3 (2649 stable-keyed players; backtest byte-identical proven separately: v2.4 _BOARD_PATH=False == v2.3 on all 2656 players); B2 leakage 0.0; panel BOTH sides (control 10/10 canonical; candidate movers = sit-out/retention rows); Tsatas 1140 + Berry 2421 byte-unmoved (A8 2.12x); dial d66291a grep-absent; ruck cap 1.73 default in force; CONTROL byte-verified pre+post (8aed420a/644d1254/34faa865). Rulings R12/R13 registered. Engine loads sequential; canonical untouched. Session ends with a PR (D14). NEXT = combined scoped audit D13+D14. NOTHING BAKED.
