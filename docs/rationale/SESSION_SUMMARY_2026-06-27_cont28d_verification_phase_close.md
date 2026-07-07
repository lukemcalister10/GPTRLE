# SESSION SUMMARY — cont.28b/c/d (2026-06-27): VERIFICATION PHASE CLOSE

> **This is the LIVE FRONTIER.** It closes the verification phase that ran AFTER the cont.28 valuation audit and the
> GEN_DEF pre-debut ship. For the audit narrative see `SESSION_SUMMARY_2026-06-27_cont28_valuation_audit.md`; for the
> full live queue + every parked item see `UNRESOLVED.md` (reprioritised, audit/verification items on top).
> **Nothing was built in this phase — it was verification + doc consolidation only.** ONE decision remains OPEN (Luke's
> call): the U28-D design-go. Sooner-vs-fold for the live deep-pick magnitudes was RESOLVED 2026-06-27 (cont.28d) = FOLD
> (see §7) — the live magnitudes stay as-is and the correction folds into U28-D; NOT a separate prospect-side pass.

---

## 1. SHIPPED / LIVE STATE (baked, in the HTML)
- **Architecture = par-centred redesign, ROUTER option B.** Value flows through `tail_restore.production_value(p,cm)`
  (the router): PRE-DEBUT (level_now None) → `rval` (restored band) / RUC scorer-borrow; ESTABLISHED (≥3 games) →
  `dist_redesign.redesign_value`. The router is the entry point — NOT a `redesign_value` edit. `wire_redesign.wire()`
  calls `production_value` per player; `build()` loads cached `/home/claude/cm_400.pkl` deterministically.
- **Board baked STATIC @ 400 trees** into `rl_after/rl_app_data.json` + `rl_after/rl_draft_engine.html` (data inlined,
  no server). Two-part parity gate passed byte-exact at ship.
- **Live board total = 605,719** (805 active players; Sheezel 7264, Daicos 6942). This is POST the GEN_DEF ship
  (pre-ship was 603,839 — superseded).
- **GEN_DEF pre-debut tail-restore fix SHIPPED + re-baked** (cont.28): `HIGH_TAIL` += `GEN_DEF` (tail_restore.py).
  Board **603,839 → 605,719 (+0.31%)**, **8 movers ALL pre-debut GEN_DEF**. Cohort book: **GEN_DEF draft/cost
  0.44 → 0.53** (genuine under-valuation recovered; yr4 1.02 unchanged; MID 0.99 / KEY_DEF 0.62 / KEY_FWD 0.66 /
  RUC 1.04 unmoved). SCOPE = PROSPECTS only (established young defenders unreachable: established path uses a level=0
  dead pole + doesn't restore). Temporary pre/just-debuted inconsistency, closed by U28-D.
- **TWO DISTINCT CURVES — do not conflate:**
  - **Pre-debut player BLEND** (what a freshly-drafted player at pk1/5/10/20/40 is worth, position-mix blended):
    **2086 / 1473 / 1126 / 635 / 396** @ 400 trees = SHIPPED. The **200-tree 2176 / 1505 / 1131 / 647 / 392 is a
    SUPERSEDED derivation MOCK** — it appears throughout `MILESTONE…` and older summaries; it is NOT the shipped curve.
  - **Pick-ASSET curve** (tradeable pick values, the `picks` list in rl_app_data.json): **3000 / 1957 / 1482 / 748 /
    620 / 556 / 453 / 388** @ pk1/5/10/20/28/37/45/50. Richer than the blend (pick optionality). Distinct artifact.
- **FOUR no-move guards (held at the GEN_DEF ship):** pk1-6 GEN_DEF untouched; KEY_DEF / KEY_FWD / MID unmoved.
- **Per-position MONOTONICITY GUARD** (`_monotonicity_guard.py`, PASSES): synth value non-increasing in pick at equal
  **{games, tenure, age, position, pick, dual-position eligibility}** (the held-equal set — see §4 for the 6th input).
  Validation check, no valuation change; run before every bake.

## 2. REPRODUCTION ENV (cold-start MUST use this, or numbers diverge silently)
**REDESIGN / AUDIT env** — authoritative for the par-centred chain, the curves, and every `_*` diagnostic:
```
PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_REPL_DROP_FWD=4 RL_REPL_DROP_OTHER=2 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22
```
- `RL_PRIOR_TREES=400` = the SHIPPED tree count (also code default). `PAR_RAMPS=22` — **code default is 14, which is
  WRONG**; must be set or the level feature differs. `PYTHONHASHSEED=0` for determinism.
- `RL_LEVEL_RAMP` is INERT in the par-centred chain (a legacy floor-model knob); ignore it. The 805-board `verify_anchors`
  GATE env uses `RL_LEVEL_RAMP=14` and NO `PAR_RAMPS`/trees — that env is for the gate ONLY, do not use it for diagnostics.
- ⚠️ NEVER lift an env string from a historical summary (cont24/25/26 headers carry `PAR_RAMPS=14` / 200-tree strings).
- `bootstrap.sh` recreates the rl_after/rl_build symlinks, pins deps (scikit-learn==1.8.0), and **copies cm_400.pkl to
  `/home/claude/cm_400.pkl`** (the absolute path the diagnostics/build load from — see §9).

## 3. U28-D — THE HELD ACTIVE THREAD  [SIZED, HOLD-do-not-build]
**Framing:** ONE unified elapsed-opportunity mechanism on BOTH sides of the 3-game line (established flips at 3 games via
`level_demo` gm≥3). NOT two patches.
**The bug (cont.28 cliff test):** the established pedigree pole `_adraft_band` is built at **level=0 → DEAD**
(pole << prod: Kyle 73 vs 381, Zeke 139 vs 660), so `max(0, pole−prod)=0` gives ZERO pedigree upside. The
exposure-graded upside weight `_floor_w`/gw ALREADY EXISTS (0.90@3g → 0@30g) but grades toward a corpse → value flat
across games. The crater hits below-par early performers (Kyle).
**THE CUT (decided, code-grounded):** give `_adraft_band` a **LIVE pole** = par-path level (not 0) + the **p97** tail
restoration; the existing `_floor_w` grading then delivers the smooth prospect→established transition for free, and the
pole carries the tail (subsuming the separate p97 thread). ONE mechanism. **Kyle: 465 now → ~740 after** (live pole ≈ his
prospect value ~690 vs prod 381 → 0.90×(690−381) ≈ +280 → ~740, fading to pure production by 30g).
**p97 sizing (done, `_tail_sizing.py`):** tail above p90 = +11 MID / +8 GEN_DEF / +5 KEY_DEF. Two methods agree through
p97, diverge at p99 → **p97 is the defensible ceiling**; odds at p97 = observable ~3% realized rate (survivorship-clean).
**THE FULL 7-CONSTRAINT SET** (locked for design, recorded verbatim in `UNRESOLVED.md` U28-D CONSTRAINT SET):
1. UNIFIED elapsed-opportunity decay across both sides of the 3-game line — live pole + p97 tail (established) +
   position-calibrated staleness decay (prospect), CONTINUOUS handoff at the boundary, one curve not two patches.
2. POSITION-CALIBRATED — MID worst, KEY_FWD already roughly right. BOTH the decay AND the p97 tail anchored to each
   position's OWN realized elite (no position-blind lever).
3. MAGNITUDE — discount reaching ~50-60% of fresh-slot value for a 3-4yr non-producer.
4. SMOOTH/MONOTONIC IN TENURE — no George(99)/Oscar(487) 5x flips.
5. PRODUCTION-GATED MATURATION — the age/`v_at_peak` credit earned ∝ GAMES PLAYED, not raw tenure. SEPARATE lever from
   the staleness decay. Do NOT remove the age term (correct for players who play) — gate it on production. (Anchored on
   real players — see §4.)
6. SURVIVORSHIP-CLEAN odds — realized ~3% rate, busts retained as zeros, censored cohorts excluded.
7. CONTINUITY at the 3-game boundary — pole ≈ prospect value, no jump at debut.

## 4. VERIFICATION BLOCK (cont.28b/c/d) — NEWEST STATE, the easiest to lose
All scripts in `forward_valuation/`, all banked. Everything below is VERIFIED, not designed.

**(a) #5 production-gating ANCHORED ON REAL PLAYERS.**
- Isolating experiment (synthetic): MID pk10 tenure-1 0-game prospect = 1515 @ age18 vs 1960 @ age22 → **+445 from AGE
  ALONE** (older never-played prospect valued HIGHER → the maturation term has no games-check).
- Real-roster anchors (`_real_anchor_check.py`): **Tai Hayes** (GEN_FWD pk44, 0 games, drafted at 21) prices **673 vs
  381** if drafted-at-18 = **+293** pure maturation credit; **Tobyn Murray** (GEN_FWD pk40, 0 games, drafted at 20) =
  **+262** (681 vs 418). On-manifold (normalized against a tenure-1 18-draftee).
- **No HIGH-pick mature recruit exists** — mature recruits cluster at deep picks (pk40+); the high picks are all 18yo.
  So the inflation reaches real entries only at deep picks.
- **Tobyn Murray = the cont.28c monotonicity "violation"** (pk40 t1 681 beating stale earlier picks) — now EXPLAINED as
  age-inflation, NOT a pick-curve break.

**(b) STALENESS POSITION-CALIBRATION MEASURED ON REAL PLAYERS (not ceiling-height inference).**
- Each player's OWN staleness discount = actual tenure vs forced-fresh, age/pick/games held:
  **Charlie Edwards** (MID pk21, stale) keeps 95% → **−5%**; **Luker Kentfield** (KEY_FWD pk60, stale) loses **−42%**.
- ⇒ **MID worst (over-valued), KEY_FWD already near-right.** CONSEQUENCE for sooner-vs-fold: any sooner correction MUST
  be the position-calibrated cross-position pass — a global staleness factor would crush already-correct KEY_FWD.

**(c) MSD CAVEAT on the forced-fresh harness.** `debutyr = p['year'] if type=='MSD' else p['year']+1`. The `force_fresh`
harness sets `year=2025`, so non-MSD players land tenure-1 but MSD players land tenure-2. **Kentfield is the only MSD
player in the measured set** → his forced-fresh baseline resolved tenure-2 not tenure-1, **understating his −42%** (the
true KEY_FWD discount is LARGER → the MID-worst/KEY_FWD-fine read is strengthened, not weakened). Every other baseline
(the MID anchor, the GEN_FWD anchors, the deep-pick prospects) is verified clean tenure-1.

**(d) SIXTH VALUE INPUT FOUND — multi-position eligibility.** For a 0-game prospect the chain is
`rval → priceband → _price_repl(p,b,SCALE_DIST,'bal')` (lens hardcoded 'bal' → no lens-tilt; brodie/ruck-tax are
established-only). Yet at identical {games,tenure,age,pos,pick}, a dual-eligible prospect prices differently:
**Holmes** (dual MID/GDEF, `_fut` MID70/GDEF30) **1061** vs **Daicos** (pure MID) **1022** (+39); **Duff-Tytler** dual
**−81 below** pure key forwards (733 vs 814). Same band → the difference enters at the PRICING step (effective replacement
uses the multi-position eligibility). Added to the guard's held-equal set → **{games, tenure, age, position, pick,
dual-position eligibility}**. The guard is NOT compromised (single-base synths hold it implicitly) but it must be pinned
the moment the guard is extended to compare across real players. (The pricing rule itself is parked as U28-MULTIPOS, §6.)

## 5. LIVE-BUT-ACCEPTED — deep-pick over-valuation magnitudes  [DELIBERATE, not a bug]
The GEN_DEF ship moved some deep-pick low-games prospects large: **Jakob Ryan pk28 g1 = 515**, **Tew Jiath pk37 g1 =
443**, **Oscar Ryan pk27 g0 = 487 (above Carmichael pk21 g0 = 455)**. This is a CONTAINED sub-population — the deep-pick
fringe (stale non-producers + mature recruits) — **~2x over Luke's eyeball target (~200-250), NOT board-wide.** It is the
flat-realized-ceiling property interacting with the weak staleness discount + un-gated age term. **ACCEPTED pending
U28-D** — a resuming chat must read this as deliberate, not re-flag it as a regression. Correcting it sooner vs folding
into U28-D was the sooner-vs-fold decision — RESOLVED 2026-06-27 (cont.28d) = FOLD (§7); the correction folds into U28-D,
no separate pass.

## 6. U28-MULTIPOS — PARKED  [independent of U28-D, do-NOT-fold]
The multi-position pricing rule (the 6th input, §4d). Holmes priced UP (dual MID/GDEF, the expected direction —
flexibility is worth more in a keeper league), but **Duff-Tytler priced −81 DOWN** vs pure key forwards — the OPPOSITE
direction. So the rule is NOT uniformly "dual = bonus"; it can penalise. **TASK (not actioned):** characterise exactly
how effective replacement is computed for dual-eligible players (which positions' REPL — blend / min / max across the
`_fut` set) and sanity-check the SIGN; Duff-Tytler going the wrong way suggests a second position whose replacement drags
him down. INDEPENDENT of U28-D; do not fold in.

## 7. DECISIONS — one OPEN, one RESOLVED (cont.28d)
1. **U28-D design-go — OPEN.** The unified elapsed-opportunity rework is SIZED + constraint-locked but HELD. No build
   until the explicit word. NOTHING in this archive authorizes it.
2. **Sooner-vs-fold for the live deep-pick magnitudes (§5) — RESOLVED 2026-06-27: FOLD (Luke's call).** Do NOT do a
   separate position-calibrated prospect-side pass now. The live magnitudes (Jakob 515 / Tew 443 / Oscar 487 +
   mature-recruit age-inflation) stay LIVE and ACCEPTED; the correction is folded into the U28-D build. The board ships
   as-is until U28-D lands. (The §4b finding still constrains the *how* whenever U28-D is built: the staleness decay must
   be position-calibrated, never a global factor.)

## 8. DEFERRED BACKLOG (still present + current in `UNRESOLVED.md`)
Genuinely-open behind U28-D: U28-B (recency 0.72 lag + muted captaincy, secondary, individual-level); the PVC→realized-floor
migration (separate lever for the board-total residual); best-3 partial-sample shrinkage + aging quality-interaction (two
items that dropped out of the live queue at the board switch — flagged); RUC per-position reliability; U24-F Zane-class
CROSS-position ordering (distinct from the per-position guard); U24-E ruck convexity; v2 HTML interactivity; A1/A2 JS
engine parity. U28-CLOSED block lists verified dead-ends (incl. "calibrate to 1.0") — do NOT reopen.

## 9. MODEL-FILE HANDOVER NOTE (the one artifact a fresh chat can't reproduce)
`cm_400.pkl` (the cached par-centred 400-tree GBM, **4,174,555 bytes**, md5 `34faa8659cc8f19794f5cb9584fa19b2`) is in the
archive at `rl_workspace/cm_400.pkl`. The code loads it from the ABSOLUTE path `/home/claude/cm_400.pkl`. Running
`bootstrap.sh` copies it there automatically; without it, `build()` and every diagnostic will fail to load the model.
`cm_200.pkl` (2,242,567 bytes) is the SUPERSEDED 200-tree derivation mock — present for provenance, NOT the shipped model.

## 10. DOC CONFLICTS FOUND + RESOLVED THIS CHECKPOINT (cont.28d)
- START_HERE "WHERE WE ARE" paragraph called the GEN_DEF fix "specified, not built, awaiting go" — CONTRADICTED its own
  SHIPPED banner. **Resolved:** rewritten to SHIPPED.
- START_HERE "HOW TO OPEN" board total read 603,839 (pre-ship). **Resolved:** corrected to 605,719.
- START_HERE LIVE-FRONTIER pointer + bootstrap tarball ref pointed at the audit summary / `cont28_audit` tarball (both
  predate this phase). **Resolved:** repointed at THIS summary + the newest tarball.
- Checked clean (no conflict): "calibrate to 1.0" appears only as the overturned dead-end everywhere; the architecture is
  correctly described as the `production_value` router, NOT a `redesign_value` edit.
- **(2026-06-28 follow-up — post-cont28d "two open" sweep):** the cont28d pass fixed the three pointers above but MISSED
  three residual "two open decisions" strings that contradicted §7 — the **top banner**, the **§5 cross-reference**, and
  `START_HERE.md`'s **READ-ORDER item 2** (line 58). **Resolved:** all three rewritten to match §7 (ONE open = U28-D
  design-go; sooner-vs-fold RESOLVED 2026-06-27 = FOLD). Whole-doc-set sweep otherwise clean — the remaining "two
  decisions" hits in HANDOVER/KICKOFF/cont25 are the unrelated establishment-P thread (scoring-nudge + basepk shrinkage),
  not this relic.
