# SESSION_SUMMARY 2026-06-26 cont.27 — PAR BUILT + A/B/C VALIDATED (U26-REDESIGN)

**Supersedes the cont.26 "shape only, nothing built" state. Par is now LOCKED; the par-centred production
redesign (A/B/C) is BUILT as a standalone mock and VALIDATED against the three-case read-out. STILL NOT WIRED
into engine value() — no rebuild yet. Next step is the ramp sensitivity sweep, then wire-in on Luke's go.**

## Artifacts created this session (all in forward_valuation/, load-bearing)
- `par_build.py`     — the PAR surface. par(pos,pick,tenure) = level_pos(log-pick) + ramp_pos(tenure), additive,
                       recency-weighted-level target, gate >=6g at tenure, cohort DRAFT 2003-2018. Reconciles:
                       MID yr1 picks 1-8 = 66.7 (cont.26 anchor 66.0). Ramps UN-POOLED (enough per-position data);
                       thin-cell protection lives in the level-curve kernel-ESS. Run via par_build fit().
- `par_centred.py`   — FIRST retrain mock (tilt-in-level). Superseded by par_redesign.py but kept: it is the
                       evidence that tilt-in-LEVEL goes OOD (Patterson band collapse) -> tilt must live in band space.
- `par_redesign.py`  — A/B/C build. THE current mock. Pure par-centred level feature + band-space non-play tilt
                       + per-position beta derivation. Run (⚠️ this command originally used PAR_RAMPS=14, the EARLY
                       A/B/C-build value; it is SUPERSEDED — PAR_RAMPS=14 yields DIFFERENT numbers (blend grad 1.71, pk40
                       376) than the VALIDATED pick-curve deliverable (grad 1.65, pk40 392). The authoritative env is
                       `MILESTONE_VALIDATED_READY_TO_WIRE.md` §B3 — PAR_RAMPS=22):
   cd rl_after && PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_REPL_DROP_FWD=4 \
     RL_REPL_DROP_OTHER=2 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=200 PAR_RAMPS=22 python3 ../forward_valuation/par_redesign.py
- conditional_prior.py: added backward-compatible env knob RL_PRIOR_TREES (default 400, UNCHANGED; lowered to 200
                       only for fast mock sweeps). No behaviour change at default.

## THE DESIGN (locked with Luke across cont.26 + cont.27)
Replace `cp._lvl_eff` (shrink-to-ZERO: lvl_wt*min(1,exposure/14)) with PURE par-centred (shrink-to-PAR):
   eff = par + (lvl_wt - par) * w,   w = min(1, exposure/RAMP)        [the deviation/confidence weight]
- CHANGE-ONE-THING: only the level feature is redefined. Frozen: GBR architecture/hyperparams, target
  (resolved-best3), cohort (2003-2018), all other features, whole downstream chain (peak->VOR->SCAR/REPL/captaincy).
- TRAIN/INFERENCE CONSISTENCY: the par-centred level is one function monkeypatched onto cp._lvl_eff, so
  build_cond_prior (train) and cond_prior_band (inference) call identical code. Mandatory — a frozen GBR scored on
  the redefined feature extrapolates off-manifold (the 3423/peak-108 smoking gun). The retrain IS the reuse.
- NON-PLAY = BAND-SPACE tilt (Fork B), NOT in the level feature (tilt-in-level -> OOD -> band collapse, optionality
  dies). p50 tilt DOWN (bounded: <= TILT_CAP=0.6 of the p50-p10 gap) + p10 widen (fat-left) + p70/p90 PRESERVED.
- TILT MAGNITUDE = base-rate-relative shortfall (Fork C): shortfall = max(0, base_rate(pos,T) - player_rate),
  base_rate = median games/22 over all rostered at pos x tenure. yr1 base = 0.00 everywhere -> first-year
  non-debutant gets ZERO drag automatically; tenure ramp EMERGES; one mechanism (no bolted-on tenure gate).
- player_rate uses the FM#3 denominator: games/available since-first-game (debuted) or since-draft (0-game).
  Cumming's 6 pre-debut rounds are NOT misses -> miss=0 -> holds par.
- FLOOR (Fork A): beta x PVC x mult, as the absolute downside CAP only (production is now primary). beta=0.85
  (cont.25, floor-as-primary) is too high; **beta ~= 0.5** is safe across positions and is the cont.26-aligned value.

## READ-OUT GATE — ALL THREE FALL OUT at ramp 14, beta ~= 0.5 (200-tree mock fidelity)
- Cumming 7g@61: eff 62.9 (par-held), E[v] 1349 > floor 981 -> PAR-HELD (production, not pedigree-floored).
- 61-vs-21 @3g: E[v] 1248 vs 641 -> after floor 1248 vs 981 -> SEPARATED +267 (21 floored as bust, no re-collapse).
- Patterson 0g (yr1): shortfall 0.00 -> no drag, band [45/73/82/86/100] p90=100 -> hold-pedigree/wide-band (correct).
- yr3 non-establisher (8/6/2 g): shortfall 0.15 -> band p50 73->70 (bounded), p10 54->52 (fat-left), p90 97 preserved.
- OOD superstar artifact GONE post-retrain: 3g/61 kid p50 peak 79 (was 108), prod 1050 (was 3423). Manifold moved.
- Anchor sanity: Serong band[101/110/121] prod 4344 (engine value 3419, the documented +9-28% redesign elevation).

## CORRECTION logged (process working)
cont.27 mid-session I claimed "single beta x PVC structurally can't work, the floor wants re-anchoring." That was an
ARTIFACT of a buggy Fork A synth (pos-override failing -> established-par player pricing BELOW a 7-game one). Fixed
(native-position synths). Corrected finding: par-production is healthy, ratios RISE with pick (MID 0.87->2.77), and
the sub-0.5 outliers are PAR-SURFACE artifacts, not constraints. A single beta works; ~0.5 is right. Re-anchoring
the floor to realized-level (not pedigree) stays a GENUINELY PARKED question, not forced by data.

## OPEN ITEMS (carry, not blockers)
1. RAMP SENSITIVITY SWEEP — the next build step. 2-3 ramp values (e.g. 8/14/20), three cases, report (a) Cumming eff
   + does production hold par, (b) pair production separation, (c) Patterson/yr3 band [p10/p50/p90] per ramp. Watch:
   does higher ramp over-separate the 61-vs-21 pair at 3 games (over-reading thin evidence)? Tension responsiveness
   vs inertia lives in the ramp. NOTE: each ramp = a full retrain (slow); run sequentially, not in one timeout.
2. beta precise value — pin after the sweep (and ideally re-fit at full 400 trees, not 200).
3. tilt caps (TILT_CAP, WIDEN_K) — tune on the retrained prior; shortfall is currently career-averaged, consider
   recency-weighting it (a recent cliff-fall reads too mild).
4. PAR-SURFACE WOBBLES — GEN_DEF pk8 non-monotonicity (par(pk8) < par(pk15)); KEY_FWD yr5 dip. Clean the level curve
   (wider bandwidth / monotonicity at thin cells) before the final par lock.
5. PARKED: should the floor re-anchor to realized-floor-level rather than beta x draft-pedigree? Not forced; revisit
   if beta tuning misbehaves.
6. The retrain currently runs at 200 trees for mock speed. The REAL wire-in must use 400 (RL_PRIOR_TREES default) and
   will move the 11/30/49/70/90 gate — that re-anchor is EXPECTED (cont.26 sec.7), not a regression.

## NOT DONE / NEXT
- Ramp sweep (item 1) -> finalize beta + tilt caps -> THEN wire par-centred _lvl_eff + band-tilt + lowered beta into
  the engine, regenerate the 805 board + release HTML (the actual rebuild, on Luke's explicit go). Nothing wired yet.

---
## cont.27 UPDATE (same session, later) — SURFACE CLEANED + beta LOCKED + Fork B BANKED

### Par-surface monotonization (Decision-D class) — DONE, in par_build.py
Both par-surface wobbles were imposed-prior violations, fixed via weighted isotonic (PAVA), sample-size-weighted:
- LEVEL non-increasing in pick (GEN_DEF pk8<pk15 was small-sample noise; high picks 71-74 clearly top, then noisy
  plateau the kernel tracked). Now monotone. RUC pk3 empty cell nan-filled before isotonic.
- RAMP non-decreasing in tenure (KEY_FWD yr5 dip was a backfitting artifact; raw level-by-tenure was already
  monotone 51.6->55.1->58.5->60.4->61.0->64.8; the dip only appeared in the pick-detrended residual via survivorship).
- RECONCILIATION PRESERVED: MID yr1 pk1-8 = 66.9 (anchor 66.0). Both axes monotone for all 6 positions, no nan.
- WHY IT GATED THE SWEEP/FLOOR: the sweep reads band shapes off the par surface; wobbles contaminate the read. And
  the floor's beta is derived from par-production off the surface -> a wobble (GEN_DEF pk8) polluted the beta derivation.

### FLOOR = POSITION-SPECIFIC beta (cont.27 decision, gated by a real-player check)
- The cont.25 single beta=0.85 is too high (over-floors near-par thin-evidence kids -> reinstates genericness).
- Cleaned Fork A ratios (established par): MID/KEY_FWD/RUC all >=0.66 (beta~0.5 safe); GEN_DEF genuinely LOW
  (0.35 at pk8) because par defenders price near the replacement cliff in the convex VOR chain.
- GATING CHECK (a real player decides it, per Luke): real mid-pick par-level defenders price ~370-1000
  (Quaynor 369, Chapman 493, Bergman 504, Florent 719, Hollands 1000) -> the 0.35 ratio is REAL, not a 3rd artifact.
  A beta=0.5 floor would over-floor Quaynor (369 vs ~700 floor). => position-specific beta CONFIRMED.
- LOCKED: BETA_POS = scorers (MID/GEN_FWD/KEY_FWD/RUC) 0.50, defenders (GEN_DEF/KEY_DEF) 0.28. (par_redesign.py)
- *** TWO-TIER TRIGGER (documented, do not re-litigate): position-specific beta IS "re-anchor the floor to
  realized-level" at LOWER FIDELITY -- the floor tracking production-per-position, not pedigree. They are the SAME
  insight, not competing options. If >~2 tiers are needed (watch-item: KPP / KEY_FWD may want a middle tier),
  ABANDON beta x PVC and switch to the realized-level floor. Do not hand-set five betas. ***
- SUBTLETY for sweep tuning: the Fork A ratio table used ESTABLISHED par players, but the floor BINDS on the
  thin-evidence YOUNG par player (lower production). The established ratios rank positions correctly but overstate
  headroom; the real validator is the three-case test (Cumming clears beta_MID=0.5 at E[v] 1249 > 981). Pin exact
  tier values against thin-evidence par production during the sweep.

### Fork B BANKED (recency-weighted shortfall + full stress + cap ceiling)
- Recency-weighted per-season play-rate (recent form governs, as the level feature): a proven player who plays 0
  THIS year reads shortfall 0.14 (mild, level anchors him) where career-averaging gave 0 -> the recent-cliff signal
  is caught but soft (injury-vs-washout decided by observed level, availability only soft-tilts). par_redesign.player_rate.
- Stress across tenure x recent-rate: p90 STRUCTURALLY preserved across the whole range; p50 tilt bounded well under
  the 60% cap; cap binds ONLY at the debut-then-vanish extreme (shortfall 0.76 -> p50 -60% of gap, p90 STILL preserved).
- Three cases hold under position-specific beta: Cumming PAR-HELD (1249>981), 61-vs-21 separated +297 (21 floored as
  bust), Patterson hold-pedigree (852, p90 103 preserved). yr3 decliner floors to 981 (pedigree masks small tilt --
  the FM#3 injury-vs-dropped ambiguity at the floor; defensible but logged as behavior-to-watch).

### STATE: par LOCKED+monotone, A/B/C VALIDATED, beta position-specific LOCKED, Fork B BANKED. Still NOT wired.
### NEXT (the expensive, interruptible step -- checkpoint precedes it): RAMP SWEEP.
- 2-3 ramp values, three cases, Cumming pinned each ramp. Read-out = the RESPONSIVENESS/INERTIA FRONTIER, quantified:
  pair separation at 3g AND at 15g across ramps. Right ramp = 3g separation present but MODEST and GROWS with games.
  A ramp that separates as hard at 3g as 15g is over-reading thin evidence (the failure the redesign exists to prevent).
  If the frontier is flat (no ramp gives modest-at-3g/strong-at-15g), that's a finding: separation isn't coming from
  the evidence weight, look again. Each ramp = a full retrain at 400 trees (RL_PRIOR_TREES default) -> run sequentially.

---
## cont.27 UPDATE 3 — Patterson reconciliation + RAMP SWEEP

### Patterson reconciliation (pre-debut pedestal vs par) — DRIFT CONFIRMED, carried as watch-item
GEN_DEF pk5. [1] current pedestal MA.value=1821 (redesign_value short-circuits pre-debut to this). [2] PVC[5]x1.04=2035.
[3] redesign 0-game production (par+zero-evidence, mock)=852. [4] GEN_DEF floor 0.28xPVCm=570.
- The pedestal does NOT dissolve cleanly: par-production (852) is 53% BELOW the pedestal (1821); the floor (570) is below
  both and doesn't bridge them. The debut discontinuity RELOCATED to draft->pre-debut. Three-way inconsistent: design
  language says dissolve->852; code short-circuits->1821; likely intent (no evidence yet -> hold pedigree) ~1821.
- Root = the floor trend again: at zero evidence shrink-to-PAR gives par-PRODUCTION (852) != hold-pedigree (1821).
  Keeping the short-circuit doesn't fix it (just moves the cliff to debut: 1821 -> ~852 on first game). Clean resolutions
  route through a pedigree-anchored zero-evidence floor that FADES into production as evidence accrues (the old faded
  soft-floor; beta x PVC was trying & failing to be this). CARRIED as a live watch-item tied to realized-level-floor.

### RAMP SWEEP (pre-floor production E[v], beta held out, Cumming pinned, 200-tree, ramps 8/14/20)
  ramp | Cumming(7g) E[v] | sep@3g sep@15g ratio | 21-kid eff@15g
    8  |     1249         |  689    817   1.18   | 21.3 (w=1)
   14  |     1249         |  729    973   1.33   | 21.3 (w=1)
   20  |     1488         |  660   1083   1.64   | 32.1 (w=0.75) <- OVER-HELD (under-trusts a near-full season)
- CONSTRAINT (the real finding, not "max ratio"): w must saturate ~1 by roughly a full season, else a 15-game sample
  stays shrunk (ramp20: 21-kid@15g held at eff 32 not 21). This CAPS ramp at ~15. => RAMP ~= 12-14, 14 the clean pick
  (w=1 at 14g, correct 15g marking-down, 3g inertia retained). Cumming par-held at every ramp (robust).
- RETRAIN-COMPENSATION FINDING (carry): 3g PRODUCTION separation is ~flat across ramps (689->729->660) even though 3g
  EFF separation compresses cleanly (15.0->8.5->6.0). The per-ramp retrain learns a steeper eff->production map to
  compensate. So the ramp is a clean inertia lever in LEVEL space but the retrain NEUTRALIZES it in production space.
  The ratio improves (1.18->1.64) only via the 15g end growing, not the 3g end shrinking. => production-space 3g
  over-reading is NOT ramp-controllable; the lever for that is BAND-WIDENING at low exposure, not the weight curve.

### OPEN DECISIONS / WATCH-ITEMS going forward
1. Pick the ramp (~14 recommended) -- not yet locked.
2. Pin exact beta tiers against THIN-evidence young par production (binding case; established ratios overstate headroom).
3. WATCH: realized-level-floor trigger -- expect KPP to force a 3rd tier; when it does, switch off beta x PVC.
4. WATCH: Patterson / pre-debut pedestal-vs-par drift (above) -- design language vs code vs intent, 53% gap.
5. WATCH: yr3-decliner masking -- needs a real-young-decliner check (FM#3: masking decline vs protecting injury).
6. BAND-SHAPE work (deferred): production-space low-exposure inertia lives here, not in the ramp (sweep finding).
7. THEN wire-in (final retrain 400 trees, gate re-anchors -- expected) + regen 805 board + HTML, on explicit go.

---
## cont.27 UPDATE 3 — RAMP SWEEP (frontier), pre-debut RECONCILIATION (corrected), SOLE-PATH resolution

### RAMP SWEEP — responsiveness/inertia frontier (par_sweep.py, read PRE-FLOOR / production space)
beta held OUT (doesn't enter production). Pre-floor 61-vs-21 pair separation at 3g vs 15g, Cumming pinned:
    ramp 14: 3g +729  15g +973   growth 1.3x   (OVER-READS thin evidence -- 3g already 75% of 15g)
    ramp 22: 3g +434  15g +1112  growth 2.6x   <- SWEET SPOT (3g modest, 15g strongest)
    ramp 30: 3g +362  15g +1027  growth 2.8x   (more 3g modesty but weaker 15g; w too low even at 15g)
- Frontier is NOT flat -> separation IS coming from the evidence weight (the key confirmation). Cumming robustly
  par-held across all ramps (eff 63.0->63.9, prod 1249->1406, always > floor 981). RECOMMEND ramp ~= 22 (20-25 band).
- NOTE: 200-tree mock fidelity; frontier SHAPE robust to tree count; final wire-in re-fits at 400.

### PRE-DEBUT RECONCILIATION (par-path vs PVCxmult) -- CORRECTED, leans (a) restore upside
- SYNTH CONFOUND warning: pk3 synth players inherit the BASE player's age, not a draft age -> their ~90% reconcile
  was an artifact. Use REAL pre-debut players (draft-age) only. (4th time clean real data overturned a synth read.)
- vs PVCxmult (position-aware anchor), REAL pre-debut position medians: GEN_DEF 41%, MID 52%, KEY_FWD 75%(n2), RUC 79%(n2).
- The markdown is NOT position-differentiation (the mult already handles position) -- it is a fairly UNIFORM high-pick
  ~50% markdown, pick-dependent: deep at high picks (GEN_DEF pk5 42%, MID pk6-7 ~52%), converging to ~100%+ at late
  picks (Marsh 99%, Goad 123%). => the par-path band UNDER-CAPTURES pre-debut pedigree UPSIDE at high picks (band
  exposure-0 p90 ~95-105 vs PVC's fatter high-pick tail). "Band carries the optionality" is currently FALSE at high picks.
- DECISION 2 = (a) restore the band's upper-tail DISPERSION at low evidence for HIGH PICKS specifically (late picks
  already reconcile -- DO NOT touch them). NOT uniform blend-to-pole, NOT accept-the-markdown. Confirm-(a) checks:
  (1) PVC construction (expected-value curve [busts averaged] => a, vs pole [establishers only] => b);
  (2) empirical dispersion: historical pk5 90th-pct career peak vs band exposure-0 p90 -- if 110+ vs ~102, bug quantified.
  Root-cause candidates: quantile fit under-disperses the rare high-pick tail, OR evidence weight governs band CENTRE
  not WIDTH. Late-pick reconciliation (Marsh 99% / Goad 123%) is itself evidence PVC is expected-value (a pole would
  sit ABOVE par-path E[v] at late picks due to bust risk; it doesn't).

### SOLE-PATH RESOLUTION (locked + documented -- kills the "which is THE pre-debut number" ambiguity)
- CURRENT CONFLICT (live): dist_redesign.redesign_value L98 routes pre-debut to MA.value (PEDIGREE PEDESTAL,
  "unchanged"); post-debut uses the par-path. The mock layered par-path on pre-debut only for testing.
- RESOLUTION: par-path becomes the SOLE pre-debut value. redesign_value's `if level_now is None: return MA.value`
  becomes the par-path (cond_prior_band -> position-beta floor -> band-tilt). ONE production-anchored path for ALL
  players, continuous at debut (exposure 0 => par + zero-evidence + wide band).
- PVC IS NOT DELETED: retired as a VALUATION PATH (the pedestal), survives ONLY as the beta-FLOOR anchor
  (beta_pos x PVC x mult), and even there trending toward the realized-level floor (see two-tier trigger).
- SEQUENCING: restore high-pick band upside (decision 2a) BEFORE wiring par-path as sole pre-debut path, else the
  sole number under-prices high picks by ~50%. After restore: hold high-pick numbers against ACTUAL league draft-capital
  trades and set the upside magnitude to that (league-reality call, not an abstract target).

---
## cont.27 UPDATE 4 — (a) LOCKED via two checks; markdown DECOMPOSED; tail-restoration plan

### Check 1 — PVC is an EXPECTED-VALUE curve (busts averaged in), NOT a pole => (a)
rl_model build_pvc_v34: _nv_bwd uses "busts -> 0" (posval if b2>0 else 0.0); _ce0 averages over ALL players at each
pick (busts at 0) via risk-adjusted CE (alpha 0.6-0.8). So PVCxmult = expected value incl bust prob. Therefore the
high-pick ~50% gap is the band UNDER-PRICING expected value, not an honest markdown. (Late-pick reconciliation
Marsh 99%/Goad 123% confirms: a pole would sit ABOVE par-path E[v] at late picks due to bust risk; it doesn't.)

### Check 2 — EMPIRICAL DECOMPOSITION (the prize): clipping is POSITION-dependent, not uniform
Empirical at-draft career best-3 (fwd_best3_from, the band's target units), resolved 2003-2018, pk1-8 by position,
vs band exposure-0 p90:
    MID      n=57  emp p50/p90/p95/max = 100/116/126/128   band ~105  -> BADLY CLIPPED (superstar tail smoothed away)
    KEY_FWD  n=21   66/101/101/111                          band ~88   -> CLIPPED
    RUC      n= 5  101/109/111/113                          band ~106  -> ~matched (thin)
    GEN_DEF  n=18   78/103/109/110                          band ~102  -> CORRECT (no high tail to clip)
=> The ~50% markdown SPLITS: MID/KEY_FWD high picks are a genuine UNDER-DISPERSION BUG (fix); GEN_DEF/KEY_DEF are
   CORRECTLY marked down (leave) -- same low-scarcity defender phenomenon as the position-specific beta finding;
   PVC over-values high-pick defenders, the par-path is right there. My earlier "uniform ~50%" read was WRONG.

### ROOT CAUSE = quantile fit under-disperses the rare high-scoring TAIL (not evidence-weight-centre-only)
The band DOES widen at low evidence (exposure-0 width ~55 vs established ~20 -- width responds fine). What fails: few
high-pick MID superstars in 2003-2018 -> the p90 quantile GBR smooths them toward the median. GEN_DEF has no such tail.
PROOF it's the dispersion axis not the pick axis: position-dependent at the SAME pick (MID clips 116->105, GEN_DEF
doesn't 103~102) -- identical pick treatment, opposite result. So fix in the upper quantiles' SPREAD, NOT a pick extension.

### TAIL-RESTORATION PLAN (next; prototype in progress)
- Restore upper quantiles (p70/p90) toward the EMPIRICAL at-draft distribution, evidence-weighted: at exposure 0,
  upper tail = empirical (MID p90 116/p95 126, KEY_FWD ~101); as evidence accrues, -> the GBR band. max() so it only RAISES.
- STRICTLY high-tail positions (MID/KEY_FWD; check RUC). LEAVE GEN_DEF/KEY_DEF and ALL LATE PICKS untouched (already match).
- THREE REQUIREMENTS (Luke):
  (1) Fix lives in the DISPERSION axis (upper-quantile spread at low evidence), NOT the pick curve. Position-dependent
      at same pick is the proof.
  (2) MUST hold at PRESEASON / zero games (SEASON_PROG=0), decoupled from availability -- pure band-clipping bites a
      freshly-drafted gun on draft day. LOAD-BEARING TEST = DUURSMA: pk1 MID, 0 games, preseason -> ~full position-adjusted
      pedigree on draft day, no crash, no jump at debut. If restoration is gated to "season started/evidence accrued",
      he crashes on draft day & recovers at debut = the exact cliff the redesign kills.
  (3) Keep the two pre-debut moments distinct: "just drafted, season not started" = full pedigree (no time passed);
      "season underway, undebuted" = base-rate-relative availability tilt. Tail-restoration sits UNDER the season-aware
      haircut and must not collapse them (restoring the ceiling must not reintroduce a draft-day discount; the
      availability tilt must not touch the ceiling). NOTE: integrating the season-aware haircut into the par-path
      pre-debut path is a WIRE-IN concern; the tail-restoration is orthogonal (evidence-keyed, not season-progress-keyed).
- MAGNITUDE: empirical p90 (MID 116) is the FLOOR of the plausible range, not the target. Final upside set against
  ACTUAL league draft-capital trade values (Luke's call once the reconciled number is shown).
- SEQUENCING: restore MID/KEY_FWD tail -> verify Duursma/preseason -> wire par-path as sole pre-debut (GEN_DEF/KEY_DEF
  wire as-is now; MID/KEY_FWD after the tail fix).

---
## cont.27 UPDATE 5 — TAIL-RESTORATION PROTOTYPE BUILT + VALIDATED (tail_restore.py)

New module forward_valuation/tail_restore.py (importable; bind(PR) then rband/rval). Restores band upper
quantiles (p70/p90) toward the EMPIRICAL at-draft best-3 tail, evidence-weighted; smoothed monotone target
(loclin over log-pick + isotonic); MID/KEY_FWD only, high picks only (pickf fades 1.0@pk1-8 -> 0@pk16); max()
so it only RAISES; full at exposure 0.

Smoothed-monotone empirical p90 target: MID {pk1-7: 115, pk10: 113, pk15: 109}; KEY_FWD {pk1:101,3:100,5:96,8:92}.

DUURSMA TEST (pk1 MID, 0 games, preseason SEASON_PROG=0) -- PASSES:
  raw p90 114 / E[v] 2527  ->  restored p90 115 / E[v] 2596  (= 79% of full pedigree PVCxmult 3300; floor 1650)
  CONTINUITY through debut (no jump): E[v] 2596(e0) 2593(e1) 2587(e3) 2577(e6) 2558(e12) 2527(e22). Smooth.

RECONCILE (restored pk1-8, %PVCxmult raw->restored):
  MID  pk1 77->79 | pk3 68->84 | pk6 54->82 | pk7 52->90      (high-pick MID 50% -> 80-90% of PVC)
  KEY_FWD pk3 51->64 | pk8 56->69                              (restored to KPP empirical ceiling ~100; KPP genuinely lower)
  GEN_DEF pk5 (control) 40->40                                 (UNTOUCHED -- defenders left alone, correct)

KEY FINDINGS / CAVEATS:
- The restoration FIXES THE CLIPPING (MID high picks 50% -> 80-90% of PVC) and leaves GEN_DEF/KEY_DEF untouched.
- RESIDUAL gap at the very top (pk1 79%, not 100%) is NOT clipping (band p90 115 already = empirical) and NOT
  captaincy (verified: BOTH PVC and v_at_peak include capt_prem -- rl_model L317/331). It is PVC's best2+CE
  pick-curve method pricing the same outcome distribution ~10-20% above the engine's v_at_peak best-3 chain.
  => restored numbers are ENGINE-CONSISTENT; do NOT chase PVC to 100%. Set magnitude vs LEAGUE TRADES (Luke's call).
- TWO MOMENTS: par-path gives the SAME value preseason vs mid-season-undebuted (2596) because yr1 base-rate=0 ->
  tilt 0. The season-aware haircut that makes "season-underway-undebuted" < "just-drafted" is a WIRE-IN concern;
  the tail-restoration is ORTHOGONAL to it (evidence-keyed ceiling vs season-keyed centre). Requirement 3 satisfied.
- Real-player Annable(pk6 1675) vs Smillie(pk7 1768) apparent inversion = different real players' feature vectors,
  NOT a restoration bug (synth pk-ordering monotone: pk1 2596 > pk3 2065; smoothed target is monotone). Verify at wire-in.

NEXT: Luke sets high-pick upside magnitude vs league draft-capital trades (restored = empirical-FLOOR baseline) ->
then wire par-path as sole pre-debut value: GEN_DEF/KEY_DEF as-is now; MID/KEY_FWD with tail_restore; carry the
season-aware haircut into the par-path pre-debut branch (separate wire-in step).

---
## cont.27 UPDATE 6 — clean synth pre-debut curve + PVC-vs-v_at_peak seam (established players) + seam doc

### PART 1 — CLEAN SYNTHETIC pre-debut curve (0 games, preseason, restored), %PVCxmult  [the magnitude artifact]
        MID                         KEY_FWD
  pk    E[v]   %PVCxm  (par/PVCraw)   E[v]   %PVCxm
   1    2596    79%    (87%)          1252    49%
   2    2361    86%    (95%)          1279    60%
   3    2065    84%    (92%)          1237    64%
   4    2018    88%    (97%)          1190    67%
   5    1954    91%    (100%)         1143    68%
   6    1847    90%    (99%)          1081    67%
   7    1786    91%    (100%)         1044    68%
   8    1718    92%    (101%)         1011    69%
  (PVC[1]=3000 raw; MID mult 1.10, KEY_FWD mult 0.86. MID curve clean-monotone; KEY_FWD has a tiny pk1<pk2 blip
   from thin n=21 high-pick empirical -- cosmetic.) These are restored to the empirical p90 = the FLOOR of plausible
   upside; final magnitude set vs league draft-capital trades (per position: MID likely at/above; KEY_FWD the hard call).

### PART 2 — established high-pick MIDs priced TWO WAYS (par-path/v_at_peak vs PVCxmult)  [seam check on known truth]
  player            pk seas peak | PVCxmult | par-path | old value() | par/PVC
  Sam Walsh          1   7  112  |  3300 |  2795 |  2275 |  85%    in-prime, solid
  Matt Rowell        1   6  108  |  3300 |  3486 |  3045 | 106%    in-prime, good
  Christian Petracca 2  11  117  |  2746 |  3154 |  2884 | 115%    elite
  Tim Taranto        2   9  106  |  2746 |  2250 |  2161 |  82%    in-prime
  Andrew Brayshaw    2   8  112  |  2746 |  2694 |  2046 |  98%    in-prime
  Noah Anderson      2   6  109  |  2746 |  3985 |  4626 | 145%    elite recent form
  Marcus Bontempelli 4  12  128  |  2284 |  3096 |  2961 | 136%    elite (outperformed pk4)
  Isaac Heeney       4  11  116  |  2284 |  3319 |  3186 | 145%    elite (outperformed pk4)
  Jaeger O'Meara     1  14   96  |  3300 |    31 |    18 |   1%    OLD/declining -> low FORWARD value (correct, not a bug)
  Joshua Kelly       2  12  114  |  2746 |   741 |   598 |  27%    OLD/declining -> low forward value (correct)
  Paddy Dow          3   8   58  |  2465 |     6 |   115 |   0%    bust (peak 58)
- The par-path gives SENSIBLE FORWARD values: elite in-prime ~2800-4000, declining vets ~nil, busts ~0. This is the
  v_at_peak chain validated on known players (Luke checks each vs his read). The par/PVC ratios CONFLATE performance +
  age (PVC = static draft pedigree; par-path = forward, age-discounted) -- DO NOT read the seam from Part 2 ratios.
- THE CLEAN SEAM is Part 1 (same outcome distribution, both methods, no performance/age): par-path ~13% below RAW
  PVC at pk1 (2596 vs 3000), converging to ~par by pk5 (so PVC reads hot at the TOP picks, ~neutral by mid first round).
- VERDICT logic: if Part 2's in-prime par-path values match Luke's gut, the v_at_peak chain is calibrated and PVC reads
  ~13% high at the top -> PVC is the hot curve. (If they ran light, that would flip it; they look reasonable.)

### PART 3 — PVC SEAM, DOCUMENTED: "retire, don't recalibrate"
PVC is a REFERENCE, not ground truth. It reads ~13% above the engine's own value chain (v_at_peak) at the top picks
(converging by ~pk5), because PVC is the more abstract best2+CE pick-curve construction while the par-path is anchored
to the empirical peak distribution and the standard value chain at both ends. PVC currently sits under the beta-FLOOR
(beta_pos x PVC x mult) across the whole board. DO NOT recalibrate PVC: that would move the floor under every player,
re-open conservation, and require anchor re-validation -- a full rebuild for a curve already slated for demotion. The
resolution is the already-planned migration: floor off PVC -> REALIZED-LEVEL floor, at which point PVC stops being used
and its ~13% generosity stops mattering. NOTE: the floor binds at LOW-value players (late picks/busts) where the seam
is ~0 (par/PVC ~100% by pk5), so the hot-PVC effect on the actual floor is small in practice -- another reason
migration (not recalibration) is the right, low-risk path.

---
## cont.27 UPDATE 7 — PVC two-jobs locked; POSITION-MIX PICK-VALUE CURVE built; best-3 findings; aging LOG

### PVC'S TWO JOBS (locked) — retire only once BOTH replaced (they now are)
- Job A = PICK VALUATION ("what is pick N worth as a tradeable asset, pre-use"). FOUNDING deliverable, must survive.
  REPLACEMENT = par-path pre-debut value (reality-anchored, position-aware) -> the position-mix curve below.
- Job B = FLOOR ANCHOR (beta_pos x PVC x mult, internal plumbing). REPLACEMENT = realized-level floor migration.
- PVC retires once BOTH have replacements -> they now do.

### (1) POSITION-MIX PICK-VALUE CURVE [BUILT] — founding deliverable, par-path version
Pick-as-asset = distribution over WHO you draft (PVC approximated this by averaging everyone taken at the slot).
Method: per pick, blend par-path pre-debut values across positions weighted by HISTORICAL position-mix drafted at that
slot (Gaussian over log-pick, bw 0.42).
  pick | mix MID/GDEF/KDEF/GFWD/KFWD/RUC | blended pick-value | raw PVC (ref)
    1  | 56/ 9/ 3/ 8/20/ 4              | 2176               | 3000
    5  | 44/15/ 9/14/14/ 3              | 1493               | 1957
   10  | 33/20/10/18/14/ 4              | 1058               | 1482
   20  | 30/20/11/22/12/ 5              |  539               |  748
   40  | 25/22/12/23/11/ 7              |  352               |  525
Per-position pre-debut par-path (preseason 0g):
  pick    MID  GDEF  KDEF  GFWD  KFWD   RUC
    1    2596  1863  1452  2219  1252  2157
    5    1954   806  1033  1537  1143  1060
   10    1391   534   683  1465   917   544
   20     537   274   509   623   610  1179
   40     263   243   401   408   373   712
CAVEATS: (i) EMPIRICAL-FLOOR magnitude (tail_restore -> empirical p90); MID/KEY_FWD DIALS (Luke vs trades) lift high
picks from here. (ii) RUC per-position NOISY/non-monotone (thin; pk10 544 vs pk20 1179) -- mix weight small (4-7%) so
blend robust, but don't trust RUC per-position alone. (iii) curve ~67-72% of raw PVC -- par-path reality-anchored below
abstract best2+CE PVC. (iv) mix skews MID/KFWD early, spreads late. DIALS now UNBLOCKED (downstream of this curve).

### (2) PVC SEAM [documented; confirms cont27f UPDATE 6 Part 3]
PVC = reference not ground truth; ~13% above v_at_peak chain at TOP picks ONLY (pk1 ~13% -> ~0 by pk5). beta-floor binds
on LOW-value players (late/busts) where seam ~0 -> hot-PVC barely touches the floor. Resolution = realized-level-floor
migration (Job B), NOT recalibration. Problem concentrated where floor doesn't bind -> "retire, don't recalibrate".

### (3) best-3 — TWO ORTHOGONAL FINDINGS (different axes) [LOG]
(a) SAMPLE-SIZE SHRINKAGE [trust / how much seen]: best-3 takes >=6g per-game avg AS-IS, no partial-sample regression
    -> Heeney 12g/124 tops his best-3, transiently inflates peak+forward (strip -> ~107.5). FIX (later): regress a
    partial season toward fuller-season level in proportion to partialness -- same thin-evidence discipline as the level
    feature, applied at the peak/best-3 layer where it currently isn't. Affects in-season career-year-in-progress cases.
(b) RECENCY/TRAJECTORY [timing / when] -- CHECKED -> NO new mechanism. Trajectory ALREADY captured forward via the
    recency-weighted level. DEMO (same career avg 102, opposite trend): rising[90..110] recency-wtd lvl 106.1 -> forward
    par-path 3163; falling[110..90] lvl 93.9 -> 2227 (already separated ~940). A 2nd recency mechanism on forward best-3
    DOUBLE-COUNTS. Recency must NEVER touch CAREER/ceiling best-3 (peak = capability; a genuine 115 three years ago is
    still ceiling evidence; fading it makes it a current-form estimate the level feature already provides). If applied
    anywhere: smooth decay only (~0.72/yr), never a cliff. NET (b): forward side already handled; ceiling side must not.
ORTHOGONAL: (a)=how much seen, (b)=when; opposite for Heeney (recent but small). (a)=real to-build; (b)=resolved no-add.

### (4) QUALITY-BLIND AGING [LOG -- defer fix to after pre-debut/pick thread]
CONFIRMED: DELTAS = one population-average decline shape for all; quality scales HEIGHT (lp), position shifts CENTRE
(PEAK_AGE[g]), nothing bends decline RATE (peak-130 & peak-85 shed same %/yr). Only quality term = young-elite bonus
(age<25, flat <=+25%, not a shape change). => systematically UNDER-VALUES elite late-20s/early-30s (Rowell's ~60%
late-20s window-tightening is the population fall-off applied to an elite). Board-moving; defer.
TWO CAPTURES:
  * SURVIVORSHIP CAVEAT (critical): do NOT fit a quality-decline interaction on raw late-career elite data -- elites
    still playing at 32 are by definition the non-decliners, so that sample OVERSTATES elite aging. Any fix needs a
    SURVIVORSHIP-CORRECTED decline-vs-peak-level estimate. (Logged so a future chat doesn't naively fit it.)
  * LIGHTER 80/20 CANDIDATE (not a commitment): shift PEAK_AGE LATER for high-lp players (elites peak later, well-doc'd)
    via the existing per-position PEAK_AGE / young-elite machinery. Reuses a horizontal shift the model already does by
    position -- far less modelling risk & survivorship exposure; buys a chunk of the same effect.

SEQUENCING: pick-value curve [done -> dials unblocked] -> docs/logs [this] -> dials back to Luke -> wire-in as queued
(par-path sole pre-debut; GEN_DEF/KEY_DEF as-is; MID/KEY_FWD tail_restore; season-aware haircut into pre-debut branch).
(3a)+(4) fixes deferred; (3b) resolved no-action.

---
## cont.27 UPDATE 8 — dials=0 LOGGED; pick-curve SHAPE check -> too flat at back (SURVIVOR BIAS); RUC flag
> ⚠️⚠️ **SUPERSEDED IN PART BY UPDATE 9 (read U9).** The "PICK-CURVE SHAPE CHECK / survivor-bias / missing-bust"
> framing in THIS update is WRONG and was killed in U9: there is NO inner-join filter, the never-played ARE in the
> master + emitted as bust training points (checked 3 ways), and the flatness is a BLEND issue (RUC column +
> mid-pick high-ceiling under-leveling). The realized gradient measured correctly is **1.70x** (pk20/40), not 1.50x.
> The **dials=0** and the **RUC-flag** parts of this update REMAIN CORRECT; only the shape-check diagnosis is superseded.

### DIALS = 0 (both MID and KEY_FWD) -- SETTLED, no adjustment
- MID=0: league trades pick 1 at its EXPECTED outcome (no dream/scarcity premium; deliberately no risk-tax haircut
  either). Par-path restored number already IS the expected-outcome value. Leave high-pick MID as restored.
- KEY_FWD=0: STRONG CORROBORATION. Luke's trade-sense: top KPF ~40-70% of draft value. Model's restored KEY_FWD =
  42%(pk1)/58%(pk5)/69%(pk8) of raw PVC -- every point inside the range, end to end. Two independent methods (market
  gut + reality-anchored empirical-ceiling model) AGREE on the KPF markdown across the whole span. No lift. Talent-ID
  exceptions (Schubert/Walter/Caddy/Lukosius) = managers betting a specific KPF beats base rate -> lives in TRADES on
  top of the honest baseline, NOT in base value.

### PICK-CURVE SHAPE CHECK [⚠️ SUPERSEDED BY U9 below — the survivor-bias / "biased-flat-by-missing-busts" MECHANISM is WRONG (no busts were missing); the curve IS too flat but the real gradient is 1.70x not the 1.50x quoted here, and the cause is a BLEND issue] -> captured gradient FAITHFUL but BIASED FLAT by survivor bias -> TRUE curve is STEEPER
Empirical realized-value-by-pick (2003-2018, priced peak via v_at_peak, busts->0), windowed MEAN:
  pick    1    5   10   15   20   25   30   35   40
  emp   2358 1876 1377 1111  876  792  655  633  583
  par   2176 1493 1058   -   539   -    -    -   352
GRADIENT pick20/40: empirical 1.50x ~= par-path 1.53x -> on CAPTURED data the par-path is faithful & ~2x looks off. BUT:
- BUST CAPTURE badly under-counted at late picks. never-qualified (no >=6g season) by band:
  1-5:0%  6-10:0%  11-20:3%  21-30:6%  31-40:14%  41-60:20%. IMPLAUSIBLY LOW (AFL late/rookie picks bust ~40-55%).
  Valuation data is SURVIVOR-BIASED (never-played draftees largely absent) -> late-pick realized value biased HIGH ->
  the mean gradient is too FLAT.
- MEDIAN realized collapses late: median pick-40 = 9 (~bust), pick-20 = 136, pick-30 = 16. The TYPICAL late pick is a
  bust; the MEAN (583@40) is propped by rare hits + the missing busts.
CONCLUSION: captured 1.50x is biased flat; survivorship-corrected TRUE expected-value gradient is STEEPER -> Luke's ~2x
intuition is the better estimate, and the par-path (trained on the same survivor-biased data) IS too flat at the back
end. REAL FIX to the pick-valuation deliverable.
ROOT CAUSE: survivor bias -- never-played draftees absent/under-counted in the valuation master -> both empirical AND
par-path under-price the late-pick bust rate.
FIX: represent the true late-pick bust rate -- fold in the full national-draft lists (already parsed) with never-played
as 0-value, OR a per-pick bust-rate correction. Steepens the back end. (No precise corrected gradient yet -- needs the
true bust rates; do NOT fabricate.)
WIRE-IN IMPACT: affects LATE-pick pre-debut values (over-valued/too flat). HIGH-pick dials (MID/KEY_FWD pk1-8) UNAFFECTED
(well-captured, 0% bust at picks 1-10). Wire-in correct for high picks; late-pick steepening is the follow-up.
SEQUENCING CALL pending Luke: fix-then-wire (board moves once) vs wire-then-steepen (architecture now, refine late after).

### RUC per-position pre-debut column UNRELIABLE [LOG -- flag, don't fix now]
Thin data -> non-monotone (pk10 544 < pk20 1179 = impossible). HARMLESS for blended pick value (RUC 4-7% of mix,
washes out) but the RUC per-position pre-debut curve NEEDS ATTENTION before rucks are priced INDIVIDUALLY -- the noise
would distort an individual ruck valuation. Not now; don't forget.

---
## cont.27 UPDATE 9 — JOIN DIAGNOSIS: no filter exists; read confirmed (1.70x); cause = BLEND composition (CORRECTS U8)

### CORRECTION to U8: the never-played are NOT filtered out. The survivor-bias-via-missing-busts framing was WRONG.
Verified THREE ways:
- Master HAS 745 never-played records, ALL channels (ND 246/RD 319/MSD 38/SSP 10/IRE 35/UNR 36/PDA 21/PDN 26/PDS 14).
- ALL 745 have VALID GRP positions -> 0 dropped by the `GRP.get(p['pos'])` pool filter (the hypothesised inner-join).
- `build_cond_prior` EMITS them as bust training points: 13226 pts, busts (target<10) present; fwd_best3_from returns
  0.0 for never-played (correct). For a never-played p: scoring empty -> last=d0 -> ONE point at draft year, target 0.
=> No left-join needed. Nothing is being dropped at the join. Luke's hypothesised cause is absent.

### BUT the read is RIGHT: the curve IS too flat. Clean measurement confirms ~2x direction.
DEFINITIVE gradient -- ND-only, NATIONAL-pick axis, DECIDED cohorts (debutyr<=2020), busts->0, loclin-smoothed (bw .42),
fine resolution (Luke's exact spec):
  pick    1    5   10   15   20   25   30   35   40   50   60
  rv    2370 1845 1329 1089 893  757  661  587  525  419  332
  bust%   0%   0%   1%   3%   6%   8%  11%  13%  16%  21%  25%   (smooth, plausible rise)
  GRADIENT pick20/40 = 1.70x ; pick15/40 = 2.07x ; pick10/20 = 1.49x
The original 1.50x (U8) was a WIDE-BINNING + ALL-CHANNEL-pollution artifact. Clean ND-only fine-smoothed = 1.70x. So
par-path (1.53x) IS too flat; ~2x is the right direction. READ CONFIRMED, CAUSE RE-DIAGNOSED.

### CAUSE = the BLEND, not the bands, not a filter.
Per-position bands are GRADIENT-FAITHFUL to their per-position empirical:
  MID: emp 1.93x / band 2.04x (n=338) | KEY_FWD: emp 1.76x / band 1.64x (n=135). Bands fine.
  (other emp 20/40: GEN_DEF 1.65x, KEY_DEF 1.29x, GEN_FWD 2.11x, RUC 1.24x)
The flatness is in the position-mix BLEND, two contributors:
 (a) HIGH-CEILING under-leveling: MID band pk20=537 vs realized 1097 (0.49x); KEY_FWD 610 vs 682 (0.89x). The
     par-centred band under-disperses the high-scoring tail at MID-picks -- the SAME under-dispersion tail_restore
     fixes, but tail_restore's pick-fade ends at pk16 and never reaches pk20+. MID is gradient-steepest (1.93x) and
     weighted heaviest early (32% @ pk11-20), so its under-leveling lets FLATTER positions dominate the blend.
 (b) RUC (Luke-flagged thin/unreliable, n=69, flat 1.24x, suspiciously high 1420@20/1147@40) rises 5%->10% weight by
     pick 31-40 and contributes ~0.10x1147=115 of the 352 pk40 blend (a THIRD) -> inflates+flattens the late blend.
Position MIX shift confirmed: pk11-20 MID 32%; pk51-72 MID 22%, GEN_DEF 26% -> late picks draft more flat-gradient
value-holders, compounding (a)+(b).

### FIX is a DESIGN CALL (not a left-join). Levers + TENSION:
 - Extend tail_restore pick-fade beyond pk16 to mid-picks -> lifts high-ceiling positions toward realized -> steepens
   blend. TENSION: raises mid-pick MID levels (537->~?) which touches MAGNITUDES; Luke's dials validated pk1-8, NOT
   pk20 specifically -- so not strictly a dial violation, but a judgment call.
 - Fix/down-weight RUC column (ties to existing RUC flag) -> drops inflated late blend -> steepens. Cleaner/more certain.
 - Pricing nuance: empirical priced at PEAK (full runway). par-path = pre-debut E[v]. Both are E[peak value] so the
   gradient comparison is valid, but levels differ because the BAND under-projects the high-ceiling tail (above), not a
   pricing-basis difference.
PENDING LUKE: the cause/fix differ from the spec -> get direction before rebuild. Lean: fix RUC + extend tail_restore
mid-pick fade, then re-validate blend gradient toward 1.70x. High picks (1-10) unaffected regardless.

---

## cont.27 (post-2nd-compaction) — MID "12%" verified as artifact, fade extension pk9-20, RUC pool, gradient finding

### MID "12% under-leveling" — VERIFIED as mostly a PEAK_AGE measurement artifact (risk-discount story FALSIFIED)
- The band prices via `dp.v_at_peak` at the synth's DRAFT age (~19, peak ~6yr out, discounted 15%/yr bal lens); my "realized" `rv` priced at PEAK_AGE (25, peak at k=0, undiscounted). NOT the same chain. Artifact is LEVEL-DEPENDENT: elite best3 (~110+) agree 3-9%, modest best3 (~90-96) ran rv 30-48% hot → manufactured a fake systematic gap.
- Re-pricing realized through the band's OWN chain (`v_at_peak` at draft age): gap at validated picks shrinks — pk5 14%→8%, pk8 13%→4%. **pk1-8 STAND** (apparent under-leveling was mostly measurement).
- Gap-shape test: clean residual at validated picks NARROWS with pick (13%@pk3→4%@pk8) = OPPOSITE of a risk discount (which widens w/ uncertainty) → risk-discount story FALSIFIED. Residual = empirical-p90-floor conservatism at the very top where the realized tail is fattest. NO scaling fudge baked in (good — would have been a 12% MID-wide error).

### Fade extension pk9-20 (IMPLEMENTED, tail_restore.py)
- `PICK_GATE` 16→26, `TAPER_FULL` 8→20 (FULL restoration pk1-20, fade pk20-26); `_build_curve` range(1,21)→range(1,27); `emp_q` cap min(pk,20)→min(pk,26). All commented w/ verified-clean-chain rationale.
- Applies to HIGH_TAIL (MID + KEY_FWD); max() guard means it only RAISES where band < empirical-p90 (KEY_FWD already at/above clean-realized → barely moves +2-10%, validated markdown holds).
- RESULT: pk1-8 MID byte-identical (2596/2065/1954/1718). pk9-20 MID lifted to NEW/clean-realized 0.92-0.99 (same standard pk8's 0.96 already met). Grounded, not gradient-chased.

### RUC pool (IMPLEMENTED, pickcurve_build.py per_pos_value)
- n=69 (only 7 at pk1-10) can't support a per-pick ruck curve; band over-fits late-pick outliers (pk20-30 inversion). FIX = scorer-shape borrow: RUC_value(pk) = mean(MID,GEN_FWD,KEY_FWD par-path values) × (RUC level / scorer level), level ratio ~0.95 near-constant + reliable. Monotone; kills inversion; lowers inflated back end. Borrows the EXTENDED-fade scorer shape (so rucks get the restored tail too, scaled).

### CORRECTED BLENDED CURVE (1/5/10/20/40) = 2176 / 1504 / 1130 / 665 / 325
- (was 2176/1493/1058/539/352). Deltas: pk1 +0.0, pk5 +0.8% (RUC), pk10 +6.8% (pk9-10 consistency lift, approved), pk20 +23.4% (mid-pick restoration), pk40 −7.6% (RUC).
- pk1-8 blend movement is ONLY the approved RUC correction (pk1 exact; pk5-8 +0-0.8%); MID fade does not touch pk1-8.

### GRADIENT FINDING (the "1.70x" check was CONTAMINATED; blend over-steep at pk40 only)
- Blend gradient pk20/40 = **2.05x**.
- The cont27_shapecheck "1.70x" reference was PEAK_AGE-contaminated (same artifact; inflates high picks where best3 is lower → flattens measured gradient). CLEAN draft-age realized gradient (all-ND, busts→0, loclin bw0.42) = **1.76x**. [clean realized by pick: pk5 1617, pk10 1102, pk15 888, pk20 723, pk40 411]
- Blend (2.05) steeper than clean (1.76) traces ENTIRELY to pk40: pk5-20 sit on the clean-realized line (0.92-1.03), but pk40 is 0.79 of it (325 vs 411) because the restoration STOPS at pk26 → pk27-40 unrestored (same under-leveling, one zone further out).
- Luke's original 2× intuition was directionally RIGHT (data 1.76x, far from the 1.53x that triggered this); current 2.05x is slightly too steep due to the pk40 end.

### OPEN AT CUT (awaiting Luke's call)
- Whether to FINISH the restoration out to pk40 (pk21-40, same anchor/mechanism) → lifts pk40 toward clean-realized, lands blend gradient ~1.76x (the data, slightly BELOW Luke's 2× gut). Gut-vs-data (2× vs 1.76x) flagged for him.
- PRE-REQ before extending: verify pk40 clean-realized (411) RETAINS never-played busts (best3→0) vs survivor-biased by the `debutyr<=2020` filter. If busts excluded, 411 inflated and pk40's 325 may be correct. [standing note says busts ARE retained in this engine — but verify the nd filter at pk40 specifically.]
- cont27_shapecheck.py header/numbers still say "1.70x" — now known contaminated; update to clean 1.76x once settled (doc hygiene).
- NOT yet wired into engine value() (queued post-sign-off; RUC pool currently only in pickcurve_build, moves into par-path pre-debut routing at wire-in).

---

## cont.27 (post-2nd-compaction) — pk21-40 extension + SURVIVORSHIP GATE + per-position diagnosis

### Survivorship gate (Luke's hard gate before lifting pk40) — PASSED
- Busts ARE retained: `debutyr(p)=p['year']+1` is DRAFT-based not play-based, so `debutyr<=cut` is a COHORT filter that does NOT drop never-played busts; `fwd_best3_from`→0.0 for never-played. 233 busts (best3<10) carry 0. WITH-vs-WITHOUT test: busts pull pk40 down 14% (430 vs 502) → they're genuinely in the anchor; the 411 was never survivor-biased on busts.
- CENSORING boundary matters (Luke flagged): data runs to draft 2025; a 2025 pk5 with 0 games sits as a "bust" — must exclude. Cohort-boundary sensitivity (draft<=cut, busts retained):
    cut 2019: pk20 723 pk40 411 grad 1.76 (UNDER-resolved — 2019 cohort not peaked)
    cut 2018: pk20 744 pk40 430 grad 1.73  ← tail_restore's OWN cohort (2003-2018); the consistent anchor
    cut 2017: pk20 764 pk40 452 grad 1.69  ← stabilises here
    cut 2016: pk20 778 pk40 460 grad 1.69
- The "1.76x" quoted earlier was itself right-censoring-contaminated. Resolved realized gradient = 1.69-1.73x; the consistent anchor (matching tail_restore's 2003-2018 empirical cohort) is pk40~430, grad 1.73.
- tail_restore._atdraft_pts uses `2003<=debutyr-1<=2018` (=draft 2003-2018) + retains busts + anchors to the p90 (busts/un-peaked barely touch the top decile) → already on the resolved bust-retained population. NOT changed (would re-open pk1-8).

### pk21-40 extension (IMPLEMENTED, tail_restore.py)
- PICK_GATE 26→46, TAPER_FULL 20→40 (FULL restoration pk1-40, fade pk40-46); _build_curve range(1,27)→(1,47) + added ±15 smoothing fallback for thin late-pick slices; emp_q cap 26→46.
- pk1-8 byte-identical (2596/1955/1719). pk15-20 shifted slightly (pk20 MID 1004→964): the wider empirical range pulls more declining late-pick points into the pk20 loclin kernel (bw0.45 in log-pick gives pk27 weight 0.80 at pk20) — a SMOOTHING CORRECTION (the old range(1,27) truncation over-stated pk20); still anchored 0.97. pk1-8 far enough (weight ~0.02) to be unaffected.
- MID anchored across pk1-40: model/realized(MID,<=2018) = 0.97-0.99 at pk10/20/40. Clean.

### CORRECTED BLEND (1/5/10/20/40) = 2176 / 1505 / 1131 / 647 / 392 ; gradient 1.65x
- vs cont27m (2176/1504/1130/665/325): pk1-10 stable, pk20 -2.7% (smoothing correction), pk40 +20.6% (the extension lift).
- vs founding (2176/1493/1058/539/352): pk10 +6.9%, pk20 +20.0%, pk40 +11.4%.

### GRADIENT — 1.65x blend vs 1.73x realized-blend: the realized-blend is CONTAMINATED at pk20
- Per-position model/realized(<=2018) at pk10/20/40: MID .98/.97/.99 (clean), KEY_DEF .95/1.01/1.03 (clean), GEN_DEF .97/.54/.74 (realized implausibly FLAT 550→511 pk10→20, small-sample), RUC 1.34/.61/.46 (realized outlier-dominated 1144@pk20>MID — the unreliability we POOLED around), GEN_FWD 1.08/.79/1.13 (noisy), KEY_FWD 1.24/1.32/1.35 (ABOVE realized mean).
- So realized-blend 1.73x is inflated at pk20 by GEN_DEF/RUC outliers. Clean check = MID column (grad ~1.93x, anchored). Blend 1.65x is legitimately flatter via composition (defenders/key-position flatter). Chasing 1.73x = fitting GEN_DEF/RUC outliers. 1.65x = where it landed, defensible.

### OPEN / FLAGGED
- KEY_FWD prices 25-35% ABOVE its realized MEAN. Restoration anchors to p90; KPF bimodal (busts + stars) so p90 >> mean; restoring lifts model above the bust-laden mean (unlike MID, tighter dist, lands at its mean). Plausibly CORRECT (Luke's trade-sense validated KPF at 40-70% draft value, against upside not mean) — but flagged for Luke before wire-in: real optionality vs over-valuing a bust-prone slot?
- Awaiting Luke's gut-check on the blend (2176/1505/1131/647/392, grad 1.65x) for sign-off, + the KEY_FWD question.
- cont27_shapecheck.py "1.70x" header still needs update to clean (PEAK_AGE removed → 1.76x → right-censoring removed → 1.69-1.73x resolved). Doc hygiene, post-sign-off.
- NOT yet wired into engine value() (queued post-sign-off; RUC pool currently in pickcurve_build).
