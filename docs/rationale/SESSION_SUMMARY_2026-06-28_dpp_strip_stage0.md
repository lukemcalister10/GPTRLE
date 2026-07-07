# SESSION 2026-06-28 — DPP STRIP / POSITION SPLIT — STAGE 0 EXECUTED (BUILD chat)

State: **PRE-BAKE.** Model store (`rl_model_data.json`) reclassified + `_fut` stripped + assert-gated.
**Board (`rl_app_data.json`) / HTML UNTOUCHED.** cm_400 unchanged (md5 34faa8659cc8f19794f5cb9584fa19b2).
This is the BUILD chat. Stage 0 of the 8-stage sequence is DONE; **STOP before Stage 1** — Stage 1 (P-freeze
reconciliation) is a TEMPORAL question that is Luke's call, not the build's.

## ENV (authoritative for this session — used on every command)
`PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22`
plus `PYTHONPATH=/home/claude/rl_after`. REPL_DROP uniform −3 via `RL_REPL_DROP` (default 3); the old
`RL_REPL_DROP_FWD/OTHER` are INERT this session. Code default `PAR_RAMPS=14` is WRONG — must set 22.

## BOOTSTRAP + GATE — PASSED
- Extracted the cont28d bootstrap tarball; cm_400.pkl md5 verified at both locations; deps match pins
  (sklearn 1.8.0 etc.); installed unidecode 1.4.0; recreated `rl_after`/`rl_build` symlinks.
- `verify_anchors.py` gate: **14/14 OK**, 805 players, CALIB 11/30/49/70/90, deterministic ×2.
- NOTE the gate is PAR_RAMPS-INSENSITIVE (anchors identical at 14 vs 22) — it validates cm_400 / REPL=−3 /
  untouched engine, NOT par-centred pricing. PAR_RAMPS=22 governs Stages 2–7, which these anchors don't touch.

## STAGE-0 STRIP-ONLY CONTAINMENT (pre-execution diagnostic — strip ISOLATED from reclassification)
Harness `rl_after/_stage0_containment.py` (mutates nothing on disk; fidelity-checked base == wire()'s `_v` for all
805). Stripping `_fut` ALONE: **111 movers (|Δ|>0.5); 105 in the expected DPP set (multi-`_fut` ∪ position-overriding
single-`_fut`); total +4102 SCAR.** Top movers all DPP (Ginbey −1098, Sheezel +1082, Sanders +933, Grlj −805,
Holmes +733, Horne-Francis +583, Wanganeen-Milera +574, Robey −568…). **6 non-DPP movers ("leaks"), all small, all
negative:** Will Green −11.71, Taylor Goad −9.97, Harry Barnett −9.12, Max Knobel −2.43, Jacob Molier −0.70,
Lachlan Smith −0.51.

### The 6 leaks — DIAGNOSED, BENIGN (carrier measured, not asserted)
Isolation test (`_stage0_leakdiag.py`): for ALL 6, `iso_self = +0.00` exactly (stripping ONLY that player's own
`_fut` moves them by literally zero) and `iso_others = iso_all` (100% of the move comes from OTHER players' `_fut`).
**Zero own-`_fut` leaks** — the dangerous, grep-missable kind does not exist here. All 6 are pre-debut RUC players
priced through the scorer-borrow pool.

Carrier PINNED + MEASURED (`_stage0_synthprobe.py`) at `tail_restore.synth()` (tail_restore.py:140), which grabs the
**first roster player** with `gfut(p)==pos` as a deepcopy template. For Will Green (pk16), the board-wide strip flips
Harry Sheezel's `gfut` MID→GEN_FWD, swapping the MID synth template Sheezel (rval 1149.60) → Daicos (1112.00), which
drops the 3-scorer pool mean by 12.5 × the RUC level ratio = **−11.71 exactly**. The moves are the position re-key
correctly propagating ONE hop through `synth()`'s `gfut`-keyed template selection — tiny (≤1.4% of base), same-signed,
toward correct single-position pricing, and self-correcting at the Stage-7 re-bake.

**Belt-and-suspenders `_fut` re-grep (post-strip):** the three live Python readers are all guarded —
`gfut` (rl_model.py:38 `if not f: return bnow`), `futblend` (L43 `if not f: return [(bnow,1.0)]`), spike-cap dual
premium (L233 `for … in (p.get('_fut') or [])` → empty loop = no premium). `proj_from_peak` yr1+ blend uses
`futblend` (guarded). The JS mirror is Stage-7 (not a Python-runtime concern now). The `_u28d_*` `_fut` references are
a parked Stage-8 prototype (label string + deepcopy), NOT the live board path. **No path returns a `_fut`-dependent
value after strip.**

## STAGE-0 EXECUTION (committed to the model store; board/HTML untouched)
- **Backup (pristine):** `rl_after/rl_model_data.json.pre_stage0`.
- **Reclassification source:** `roster_dpp_reclassification_edits.xlsx`, sheet `Roster`, columns **M = Drafted Pos
  (AMEND)** → `p['pos']`, **N = Current Pos (AMEND)** → `p['_pos_now']`. Codes MID/RUC/GFWD/KFWD/GDEF/KDEF (model
  store uses the SAME short-code vocabulary; GRP maps short→long at runtime — no translation at storage). Zero blanks.
- **Match:** all **805/805** active matched to the xlsx by normalized name (unidecode/lower/alnum). Zero misses, no
  duplicate keys.
- **34 drafted edits** (`pos != AMEND-M`) — the Stage-1 P-freeze population: Sheezel MID→GFWD, Holmes GDEF→MID,
  Curtin MID→KDEF, Blakey GDEF→KFWD, Rozee MID→GFWD, Sicily GDEF→GFWD, Ginbey KDEF→MID, … (full list in CHANGELOG).
- **Strip scope:** `_fut=[]` on **all 2656 records** — VERIFIED board-neutral vs the validated active-805-only strip
  (`_stage0_verify_scope.py`: 0 active values differ; the runtime only reads active `_fut` via `synth()` over
  `MA.players`; `MA.data` `_fut` reads are `__main__`-only). So the all-strip is clean AND faithful to the containment.

### ASSERT GATE (fresh reload, `_stage0_assert.py`) — ALL PASS ✓
- A0 active players == 805 — PASS
- A1 `_fut` empty (all 805 active) — PASS ; A1b `_fut` empty (all 2656) — PASS
- A2 one drafted + one current, both valid codes — PASS
- A3 `gfut == GRP[_pos_now] (== current)` — PASS
- A4 `pos == AMEND-M` & `_pos_now == AMEND-N` — PASS
Spot checks: Sheezel drafted=GFWD/current=MID/gfut=MID; Holmes MID/MID/MID; Uwland (DPP GDEF·MID) → GDEF/GDEF/GEN_DEF;
Blakey KFWD/GDEF/GEN_DEF; Ginbey MID/KDEF/KEY_DEF. All `_fut=[]`.

## WHAT MOVED ON DISK
- `rl_after/rl_model_data.json` — reclassified (active 805 pos/_pos_now) + `_fut` stripped (all 2656). **WRITTEN.**
- `rl_after/rl_model_data.json.pre_stage0` — pristine backup. **NEW.**
- Diagnostics (mutate nothing): `_stage0_containment.py`, `_stage0_leakdiag.py`, `_stage0_synthprobe.py`,
  `_stage0_verify_scope.py`, `_stage0_apply.py`, `_stage0_commit.py`, `_stage0_assert.py`.
- `rl_app_data.json` (baked board, 605,719) and `rl_draft_engine.html` — **UNTOUCHED** (pre-bake; bake is Stage 7).

## NEXT — STOP HERE. STAGE 1 IS LUKE'S CALL.
Stage 1 = P-freeze reconciliation, a TEMPORAL question: were the 34 drafted edits applied to the value P was frozen
on, or does frozen-P PREDATE them? Check frozen-P vs corrected-drafted on the 34. If they agree everywhere → proceed.
If frozen-P ≠ corrected-drafted on ANY of the 34 → STOP; surface for Luke's ruling between (a) re-freeze P onto the
correction vs (b) drafted accepts the divergence. Build does NOT auto-resolve. **Luke must say which field P was frozen
on before Stage 1 runs.**

## CARRIED NOTE (Stage 4, not a Stage-0 blocker)
`tail_restore.synth()` selects the template via `[0]` (first roster player with `gfut==pos`), so the RUC pre-debut
scorer-borrow pool inherits incidental attributes of whichever real player sorts first in each scorer group, and is
sensitive to roster ordering. Pre-existing design smell (VERBATIM from pickcurve_build.py, validated byte-exact
pre-router) — NOT a Stage-0 regression. Worth hardening when Stage 4 re-derives par/bands (e.g. a synthetic template
with scrubbed pos/age rather than a deepcopied real player).

## ADDENDUM (2026-06-28, same day, after the governing frame arrived)
The "NEXT — STOP HERE, STAGE 1 IS LUKE'S CALL" section above is SUPERSEDED. After Stage 0, Luke supplied the governing
frame (`OBJECTIVE_governing_frame.txt`) and three priority directives, all now CLOSED this session:
- **Frame read + held.** Prospect value = option over the full historical outcome distribution; production REPLACES it.
- **Priority measurement DONE** (before Stage 2): `MEASUREMENT_cohort_trajectory_2026-06-28.md`. POOLED yr0 326 → yr5 876
  (draft-day = 0.37× realized), monotone ramp / NO V, year-1 intercept +92.7 (positive). Verdict: low draft-day anchor +
  ramp, not a V — the right diagnostic is the 0.37 ratio. Re-run post-U28-D.
- **Base-verify** green (14/14, Sharman 310, CALIB 11/30/49/70/90, pristine pre_stage0, full env).
- **Stage-1 P-freeze RESOLVED on (a)** (not a STOP after all): frozen-P recomputes live from `p['pos']`, so the Stage-0
  `pos=AMEND-M` already re-freezes it; 29/34 established inert, 5/34 small sensible moves, no bad edits. `_stage1_pfreeze.py`.
- UNRESOLVED updated: rl_build stale (pre-strip) parked reconciliation; synth `[0]` → RUC-reliability (Stage-4 representative
  borrow + Stage-7 verify-the-6).
STILL the gate: **STOP before Stage 2**, awaiting Luke's read on the trajectory curve. Nothing bakes.
