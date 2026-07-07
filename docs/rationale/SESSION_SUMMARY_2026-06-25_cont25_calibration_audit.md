> ⚠️ SUPERSEDED IN PART BY cont.26 (2026-06-25) — read `SESSION_SUMMARY_2026-06-25_cont26_predebut_par_redesign.md` FIRST.
> This file's per-position prior detail (GEN_DEF under-projection, RUC backwards gradient, the mechanics) is STILL ACCURATE
> and useful. BUT its headline conclusion — "the fix is a β×PVC HARD floor, max(production, 0.85×PVC)" — was shown in cont.26
> to be TOO BLUNT (a kid at 61 vs 21 over 3 games both value at 1667; everyone generic in yrs 1-2). The real fix is a
> PAR-CENTRED production model (β×PVC demoted to the downside cap). Do NOT wire the hard floor as "the fix" — build PAR first.

# SESSION SUMMARY — cont.25 CALIBRATION AUDIT (2026-06-25)

**Type: diagnosis + trust-recovery. NO code committed** beyond a default-OFF tenure-taper knob from the
prior segment. The engine release HTML (`rl_draft_engine.html`) **predates every decision below and is NOT final.**
This session found real problems in the redesign's prior and a deviation from an agreed design, and produced a
concrete fix plan. Nothing here is wired in yet — the next session implements, on Luke's explicit go.

> **READ THIS BEFORE TOUCHING ANYTHING.** Two behavioural rules came directly out of this session's failures and
> are now non-negotiable (also in KICKOFF):
> 1. **Keep the handover docs current AND SHARE them with Luke (`present_files` / checkpoint tarball) in the SAME
>    turn** — proactively, without being asked, especially before a long chat risks timing out.
> 2. **Do NOT go off-book.** If you find yourself wanting to implement something that seems sensible but is NOT
>    what was agreed earlier, STOP and ask Luke first, flesh it out, get sign-off + before/after numbers. This
>    session exposed two off-book failures (below) — both would have been caught by this rule.

---

## 0. ERRORS I MADE THIS SESSION (so you don't repeat them)

The throughline: **I trusted synthetic constructions over real players, and asserted before verifying.** Luke
caught all of it. Concretely:

- **Claimed Louis Emmett (RUC) was undebuted / on the pre-debut path.** He has 5 games (avg 32.8), `level_now=32.8`,
  and is on the POST-debut path. Wrong.
- **Reported a per-position pole table with RUC pole @pk14 = 415 (lowest of all positions).** That number came from a
  synthetic built on **Kyle's** record (a GEN_DEF) with the position flag flipped to RUC and **games stripped** —
  so `v_at_peak` priced it with the wrong context. The real RUC pole @pk14 is **765** (mid-pack). The whole table
  was unreliable for non-native positions (KEY_FWD 819→745 too). **Only GEN_DEF 529 was right, because Kyle is a
  real pick-14 defender.**
- **Said rucks "crater" / "over-project, poles highest" earlier in the session** — backwards. Rucks are BOOSTED by
  the prior (Emmett = 2.05× PVC), and GEN_FWD's high pole is the REPL dial, not prior over-projection.

**Lesson for the next session: compute per-position numbers on a NATIVE real player of that position. Do not strip
games to make a "clean" synthetic — for rucks especially that mis-prices badly. Verify against a real player before
quoting any number to Luke.**

---

## 1. WHAT IS ACTUALLY IMPLEMENTED (verified by reading the code, not memory)

- **Censoring fix — IMPLEMENTED.** `conditional_prior.py build_cond_prior(resolved_cut=2021)` with
  `if debutyr(p)>resolved_cut: continue` trains ONLY on resolved careers. This was the root-cause fix for the
  pervasive low-bias (the old `build_prior` trained on the whole pool incl. still-rising/incomplete careers, which
  dragged every position's centre down 3–8 pts — the `censor?` column finding). Genuinely fixed.
- **Level+tenure architecture — IMPLEMENTED.** `_feat(p,Y)` conditions the prior on
  `[gfut one-hot, log(effpk), _exposure, tenure, _lvl_eff, _age_asof]`. `_lvl_eff` is the reliability-shrunk
  recency-weighted level — exactly Luke's "71-at-tenure-1 vs 71-at-tenure-5" fix (own-band blend → single
  level+tenure-conditioned prior). Verified.
- **Asymmetric quantile bands, per-group REPL (fwd −4 / other −2), ruck tax (0.25, rucks-only), brodie ×0.5** — all
  present as documented in the prior cont.25 summary.

## 2. WHAT WAS A FALSE ALARM (correctly NOT implemented)

- **GEN_FWD "over-projects badly (77% fall below p50)" — ARTIFACT, not a real bias.** Traced to **test-set
  censoring** (the 2019–21 test cohorts hadn't peaked, so they only *looked* over-projected; I first wrongly blamed
  COVID-2020, Luke corrected that SuperCoach is scaled). On the clean resolved 2015–17 window GEN_FWD is 55% (fine).
  So there was nothing real to fix. My in-session claim that "GEN_FWD over-projects / poles highest" was **wrong** —
  the high GEN_FWD pole is the deliberate −4 REPL drop, not prior over-projection.

## 3. WHAT GENUINELY SLIPPED — the live problems

### 3a. GEN_DEF UNDER-PROJECTS at mid-picks (REAL, reliable)
- Realized GEN_DEF best-3: **pick 1–10 p50 = 82.7, pick 11–20 p50 = 84.3** (both n_never=0 — top-20 defenders
  essentially always establish), 53–65% above replacement.
- The conditional prior projects a **pick-14 GEN_DEF median of 73.3** — below its own replacement (78.3) and ~11 pts
  below realized. Pole **529** (0.45× PVC), the genuine low outlier.
- History: the cont.24c prior fixed pick-3 (p50 92, exact, vs old 77.5) BUT the same validation showed pick-15 still
  79 vs realized 89 (under by 10 — never fully fixed). The **cont.25 rebuild** (games+recency feature rewrite)
  retrained the prior and drifted GEN_DEF FURTHER down (its own validation flagged "at-draft calibration drift" — it
  wasn't chased). Reliable because Kyle (the test case) is a real pick-14 defender.

### 3b. The PEDESTAL-FLOOR DEVIATION (off-book — my doing)
- **Agreed design (months ago + Luke's quotes): `max(production, β × PVC-pedigree)`, β ≈ 0.85.**
- **What got built instead (this build): a soft floor toward the CONDITIONAL-PRIOR at-draft pole**, not β×PVC. In
  `dist_redesign.py redesign_value`: `value = production + w·max(0, pole − production)`, where
  `pole = _price_repl(p, _adraft_band(p,cm))`. The pole is the conditional-prior's position-specific at-draft band —
  which (a) under-weights pedigree exactly as the original β×PVC fix was meant to prevent, and (b) inherits the
  GEN_DEF under-projection. So a young GEN_DEF is hit twice. Kyle: pole 529, w=0.90 → **519 (0.45× PVC)**.
  Cumming (MID pk7, 7g@61.3): production 961, pole 1236 (=75% of his 1656 PVC pedestal), w=0.77 → **1172**.
- **β×PVC-pedigree is the fix (β=0.85, tunable):** position-blind (matches Luke's PVC axiom), sidesteps the
  per-position calibration for the floor entirely, lifts young high-picks (Kyle→~847, Cumming→~1303, Zeke stays
  ~1669 in the approved 1400–1800), trims over-projected GEN_FWD rookies toward the pick curve, leaves breakout
  producers (production>pedestal) untouched. Production calibration still needs fixing separately (it drives
  established players, w=0).

### 3c. The RUCK pick gradient is BACKWARDS (RUC-only) + rucks are over-valued
- **Why Cumming/Kyle swung and rucks balloon: the two mechanics (see §4).** Emmett (RUC pk27, 5g@32.8): production
  1496, **redesign 1273 = 2.05× his PVC (622)**. The prior ignores his 32.8 (5 games ≈ no evidence), reverts to a
  high ruck peak (~80), the long ruck runway prices it high, ruck tax (0.25) claws 1496→1273. Not "rucks are a
  bargain" working — the model is **broken for rucks**.
- **The pick gradient is non-monotonic for RUC and ONLY for RUC.** At-draft band median by pick (native players):

  ```
            pk1    pk8   pk14   pk20   pk30   pk45   pk60   monotonic?
  MID       99.6   87.3   73.6   70.4   66.4   55.5   48.7    YES
  GEN_DEF   93.4   78.6   73.3   70.5   66.6   55.8   48.5    YES
  KEY_DEF   87.0   75.2   70.6   67.5   64.1   56.9   49.2    YES
  KEY_FWD   78.3   70.2   66.6   64.8   61.1   46.2   38.3    YES
  GEN_FWD   88.6   73.1   70.6   66.6   62.7   51.9   45.2    YES
  RUC      101.7   79.1   73.9 → 82.6 → 81.9   67.3   45.8    NO (hump pk20-30 ABOVE pk14)
  ```

  Same player (Emmett), only the pick changed: pk27 → band 82, pole 1568; forced to pk14 → band 74, pole 765. A
  WORSE pick projecting HIGHER. Cause: the ruck sample is tiny (~43 careers, n=6 in some validation cells) → the GBR
  can't fit a sensible pick curve. The other 5 positions have enough data and are cleanly monotonic on their own.
- **This is NOT in the PVC** (monotonic by construction) **or the pre-debut pedestal** (PVC-based, monotonic). It's
  in the learned conditional prior, which has no monotonicity constraint.

### 3d. CORRECTED per-position poles @pk14 (native players, all age 19) — USE THESE, not the earlier table
```
GEN_FWD 974 | MID 904 | RUC 765 | KEY_DEF 762 | KEY_FWD 745 | GEN_DEF 529
```
GEN_DEF is the genuine low outlier (reliable). RUC's number is untrustworthy at any pick (incoherent fit).

---

## 4. THE TWO VALUATION MECHANICS (corrected, simple — Luke asked for this explicitly)

There are two distinct objects, and they hand off at a player's first game:

1. **Pre-debut pedestal (`MA.value`, engine path).** For an UNDEBUTED draftee (`level_now is None`). It is
   **POSITION-FLAT** — purely the pick's PVC with a ~8% survival haircut. pk2=2329, pk14=1050, pk27=565 for EVERY
   position (verified: Emmett-RUC stripped = 565 = synthetic-anything pk27 = 565). It does NOT adjust by position.
   (Luke's instinct that a pick-2 KPF should be marked down vs a pick-2 MID is reasonable, but the pedestal does not
   do it — that differentiation lives entirely in the prior.)
2. **Conditional prior (post-debut).** The moment a player plays one game, value switches off the pedestal onto a
   projected career peak conditioned on `(position, pick, games, recency-level, tenure)`. **This is where all
   position differentiation lives, and it's the mis-calibrated part.** It projects rucks high and defenders low.

**The hand-off jumps** because the prior is mis-calibrated for some positions: a debuting GEN_DEF craters
(1050 → 519), a debuting RUC balloons (565 → 1273). Rucks carry `w=0` (no pedigree floor — design assumed the prior
projects them high already, so they get the speculation TAX instead). For rucks the at-draft pole is therefore not
even used in `redesign_value`; the **production band** is — and a thin-evidence ruck reverts to the same pedigree, so
any ruck fix must be applied to the band the ruck actually receives, ruck-only.

---

## 5. THE RUCK MONOTONICITY FIX (proposed, awaiting Luke's go to implement)

Luke's constraint: fix the non-monotonicity **without amplifying ruck value** (rucks are already too high; the only
problematic range is pk14→60). Standard isotonic/PAV would average the dip UP toward the hump (raises pk14) — wrong.

**Proposed: a running floor from the top of the draft** — "a later pick may never project above the lowest
projection of any earlier pick" (= Luke's PVC monotonicity axiom as a one-directional, down-only floor). Mechanically
`np.minimum.accumulate` over pick. Result (`RUC_new`):
```
          pk1    pk8   pk14   pk20   pk30   pk45   pk60
RUC raw  101.7   79.1   73.9   82.6   81.9   67.3   45.8
RUC_new  101.7   79.1   73.9   73.9   73.9   67.2   45.8     ← pk15–43 capped at pk14's 73.9; nothing raised
```
- **Pulls down only.** pk1–14 and pk45–60 untouched; the pk15–43 hump comes down to 73.9.
- **Caveat 1 — flat plateau:** pk14–43 all become 73.9 (the raw sample can't tell those picks apart; flattening is
  the conservative read). Alternative if Luke wants a slope: a parametric `a·k^-b` curve, but it re-levels the whole
  ruck line and could nudge pk1–14 — bigger change, less control.
- **Caveat 2 — SHAPE not LEVEL:** this cures the backwards gradient and pulls the mid-range down, but whether
  73.9 / 79.1 / 101.7 themselves are too high is the separate per-position calibration question (needs realized-ruck
  data — deferred, see §6).
- **Implementation:** apply ruck-only to all five quantiles of the band the ruck actually receives, with a
  no-crossing check (p10≤p30≤…≤p90 at every pick); re-decompose Emmett to confirm he comes down. Do NOT touch the
  five monotonic positions.

---

## 6. THE PLAN (agreed order)

1. **NOW (this checkpoint):** detailed handover update + share. ← you are here.
2. **NEXT (on Luke's go): the ruck non-monotonicity fix** (running-floor, ruck-only) per §5.
3. **THEN: the per-position calibration coverage** — the all-positions, fine-band, intersectional band-honesty
   check Luke insisted on the first time (do ~10/30/50/70/90 of resolved careers really fall below their own bands,
   per position). This is the GEN_DEF-under-projection diagnostic done properly on the REBUILT prior, checking for
   over- AND under-projection in both directions. **This is NOT the same as the parked cohort-value calibration**
   (that's aggregate value-conservation over a draft class's lifecycle; this is per-position band honesty).
4. **THEN: the floor-anchor fix** — revert the soft floor from the conditional-prior pole to **β×PVC-pedigree**
   (β=0.85, tunable) per §3b, and wire the GENTLE tenure taper (`RL_FLOOR_TENURE_TAPER=0.25`, grace 2 — built,
   default-off in the prior segment).
5. **THEN: re-validate ALL anchors + 11/30/49/70/90 calibration → rebuild `rl_app_data.json` + `rl_draft_engine.html`
   → re-tar → present.** Luke wants the calibration fix + floor-anchor fix done together, not papering one over the
   other.

Do the per-position calibration fix and the floor-anchor fix TOGETHER (step 3+4), not one over the other.

---

## 7. KEY NUMBERS / STATE (for verification on resume)

- **Run env:** `PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_REPL_DROP_FWD=4
  RL_REPL_DROP_OTHER=2 RL_RECENCY_DECAY=0.72 RL_LEVEL_RAMP=14`. Active board = `MA.players` (805). Container date
  2026-06-25.
- **Anchor gate (`verify_anchors.py`, current build):** Daicos 6938, Bont 3096, Petracca 3154, McCarthy 2539,
  J.Cameron 1196, Gawn 2522, Madden 1395, Conway 951, McAndrew 1606, Keane 2215, Bice 693, Zeke Uwland 1423,
  Jed Walter 1163, Jonty Faull 819 | engine Sharman proj_value(0) = 310. Calib 11/30/49/70/90. **These will MOVE
  once the floor-anchor + calibration fixes land — re-anchor then.**
- **Decomps:** Kyle GEN_DEF pk14 3g@48.7 → prod 434 / pole 529 / w 0.90 / **redesign 519** / pedestal 1050.
  Emmett RUC pk27 5g@32.8 → prod 1496 / pole 1568 / w 0.00 / **redesign 1273 (2.05×PVC)** / pedestal 565.
  Cumming MID pk7 7g@61.3 → prod 961 / pole 1236 / w 0.77 / **redesign 1172** / pedestal 1656.
- **Files:** redesign in `forward_valuation/dist_redesign.py` (soft floor, FLOOR_TAPER default 0, RUCK_TAX,
  per-group REPL) + `conditional_prior.py` (resolved_cut=2021, level+tenure features, the un-monotonic RUC fit).
- **Transcripts:** the raw transcripts live at `/mnt/transcripts/` IN THIS CONVERSATION ONLY — that mount is
  per-conversation, so **a NEW chat will NOT have these files.** To retrieve any past discussion, the next chat uses
  the `conversation_search` / `recent_chats` tools (search terms that work: "defender prior censor", "GEN_FWD
  over-projects", "ruck pole calibration", "running floor monotonic"). Everything load-bearing from those
  transcripts is distilled into this summary, so the raw files shouldn't be needed. (The prior calibration
  discussion was the 2026-06-24 band-redesign session: defender empirical check, censor root-cause, GEN_FWD-artifact
  resolution, level+tenure architecture rebuild.)

---

## 8. SELF-AUDIT — gotchas, open questions, and things the next chat must NOT assume settled

- **RUN THE DIAGNOSTICS SCRIPT FIRST: `forward_valuation/cal_audit_diagnostics.py`.** It reproduces every number in
  this summary (per-position poles, the monotonicity table, the Emmett/Kyle/Cumming decomps, the β×PVC floor values,
  the ruck running-floor) and carries the standard boilerplate (the module loader, `import compute`, `rd.build()`,
  `MA.BASE_REF=2026`, `MA._pe_clear()`). It also hard-codes the NATIVE player per position (MID=Cumming,
  GEN_DEF=Kyle, KEY_DEF=Dean, KEY_FWD=Duff-Tytler, GEN_FWD=Nairn, RUC=Emmett) — use those, don't re-pick. Verified
  to run 2026-06-25.
- **The ruck fix mechanism is an OPEN QUESTION — surface it, don't pick unilaterally (rule 2).** The running-floor
  was demonstrated on the AT-DRAFT band, but rucks carry `w=0`, so the at-draft pole is never used in
  `redesign_value`; the PRODUCTION band (`cond_prior_band`) is what drives a ruck's value, and a thin-evidence ruck
  reverts to the same pedigree. So the fix must reach the production band. Two genuinely different options, undecided:
  (a) post-hoc running-floor on the band a ruck receives (monotonize in pick holding the ruck's games/level — a
  per-player counterfactual), or (b) a monotone-decreasing constraint on the `log(pick)` feature in the model itself
  (cleanest, holds for all feature combinations, but requires switching the quantile learner GBR→HistGBR which
  supports `monotonic_cst`, and re-validating the whole prior). Present both to Luke with numbers; do not assume the
  at-draft demo is the implementation.
- **The β×PVC floor ANCHOR is an OPEN decision (surfaced by the 3rd-pass stress test).** "β × PVC-pedigree" is
  ambiguous: my floor numbers (Kyle 847, Cumming 1303, Zeke 1669) use the pre-debut PEDESTAL `MA.value` (= PVC×~0.928,
  e.g. Cumming pk7 pedestal 1656), NOT the raw PVC (1784) — an ~8% difference. Pedestal is the natural choice (a
  debuting player shouldn't jump off his pre-debut value), but confirm with Luke before wiring; raw-PVC is defensible.
  `cal_audit_diagnostics.py beta_pvc_floor()` documents and uses the pedestal.
- **Ruck-tax interaction:** the ruck tax (`RUCK_TAX=0.25`, applied to ev AFTER the band prices) will move once the
  ruck band changes — re-decompose Emmett end-to-end and re-check the tax self-targeting table after the fix.
- **The calib gate (11/30/49/70/90) spans all positions** — changing the ruck (or any) band shifts the aggregate
  calibration; re-run `verify_anchors.py` after every change.
- **Pre-debut pedestal is POSITION-FLAT — known characteristic, not necessarily a bug.** `MA.value` for an undebuted
  player = pure PVC × ~0.92, identical across positions (verified: real Emmett-RUC stripped = 565 = every position at
  pk27). This is CONSISTENT with the β×PVC floor design (pedigree is position-blind; production differentiates). If
  Luke ever wants position-aware pre-debut pedigree (a pick-2 KPF worth less than a pick-2 MID before debut), that's
  a separate future refinement — not in scope for the current fixes, but logged here so it isn't lost.
- **The gate PASSES NOW (2026-06-25, this checkpoint) but WILL "fail" after the fixes** — the anchors move by design
  once the floor-anchor + calibration fixes land. That is expected; re-anchor `verify_anchors.py` at that point, do
  NOT treat the drift as a regression.
- **`bootstrap.sh` installs the pinned deps (scikit-learn==1.8.0 etc.) AND runs the gate automatically** — a fresh
  container needs nothing else. If imports fail, pip-install the packages listed in bootstrap.sh manually.
- **The prior is REBUILT each session via `rd.build()` (not loaded from a pkl)** — deterministic under
  PYTHONHASHSEED=0. The redesign is wired into the engine export via `rl_export.py` → `wire_redesign` (see U25-E), so
  `p['_v']` on the board IS the redesign value; the release HTML bakes it but PRE-DATES every fix here and must not
  be shipped as-is.
