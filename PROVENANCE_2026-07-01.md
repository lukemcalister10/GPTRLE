# PROVENANCE — GATE-1 disposition + SITOUT_RETAIN tail (from the record, not recall)
2026-07-01 · engine 8aed420a · answers pulled from CHANGELOG / UNRESOLVED / the nogames notepads

## (a) GATE-1 disposition — ACTUALLY PASSED (not superseded; not owed)
**What it checked:** whether the pole's PEDIGREE read is a genuine predictive signal rather than leakage or
survivorship. Redesigned from the early "flatness" framing to a **leakage-guarded within-player** test: cohort
held out, held-out cond_prior, so in-sample ~= walk-forward (leakage ~0 -> the read is genuine prediction);
and it must cleanly SEPARATE good players from busts EARLY (GOOD 34-84% of par vs BUST ~0-1%), with the pole
pricing pedigree before a player is proven (high-pick good 53%@draft -> 84%@T5; late-pick good 34% ->
production-driven).

**Disposition: PASSED** on 2026-06-29 at engine md5 **7f7d7f76** (CHANGELOG "GATE 1 PASSED (leakage-guarded
within-player)"; UNRESOLVED L20 "LAST engine gate DONE"; UNRESOLVED L1102 the older 'flatness to re-measure'
note explicitly marked SUPERSEDED). It was called "the LAST engine gate" and "cleared for book."

**Not superseded by Measure-1 — different test.** M1 is the aggregate cohort value CURVE (per-cohort
trajectory as % of Yr1). GATE-1 is the within-player leakage/separation test on the pole's pedigree read. M1
does not contain GATE-1's leakage guard; GATE-1 is a distinct, already-passed engine gate. It "dropped out of
the docs" because it was DONE, and work moved to the book/curve phase.

**Was the disagreement settled? Yes, by redesign.** The record shows the sequence: the first GATE-1 attempts
FAILED / were confounded (CHANGELOG "GATE 1 (flatness) NOT passed"; "GATE 1 attempt confounded (cross-sectional,
small-n), corr 0.53, STILL OWED") — that was the disagreement window. The **leakage-guarded within-player
redesign** then PASSED (IS~=WF, clean good/bust separation). So the disagreement over "did it pass" was
resolved by fixing the METHOD, not by fiat.

**Residual (open for Luke's EYE, not a gate-fail):** the "GATE-1 84% question / MATURITY-EASING" — good MATURE
players sit ~69-85% of their OWN peak (pole fades faster than production holds at the top). Flagged in the book
FINDINGS and UNRESOLVED L18 as an eyeball item for Luke; it is NOT recorded as a gate failure.

**RE-RUN AT HEAD (2026-07-01): PASSES.** The formal harnesses (`_gate1_wf.py` leakage-guarded IS-vs-WF held-out,
`_gate1_picksplit.py` pole-pedigree) — previously missing from the tarball — are now included and were formally
re-run at head 8aed420a. Result: leakage ~0 (IS~=WF within <=3 pts, tree-matched at 150), clean good/bust
separation (GOOD -> 43-82% of par by T3-5, BUST 0-1%), pole prices pedigree before proven (high-pick 28->80% vs
late-pick 13->44%). No break from the upside fix's T5 zone. Early @draft level more conservative than 7f7d7f76
(28% vs 53%), consistent with the gentler-upside/no-games changes; shape and separation intact. Full numbers:
docs/rationale/GATE1_rerun_at_head_8aed420a_2026-07-01.md. The earlier "passed only at 7f7d7f76, not re-run at
head" caveat is RESOLVED. Known residual (unchanged, for Luke's eye, not a fail): the maturity-easing / 84% question.

## (b) SITOUT_RETAIN yr3-6 tail — DESIGNED (extrapolated), on a thin measured anchor
**Verdict: the yr3-6 tail is DESIGNED / re-parameterized, not raw-measured.** The measurement only extends to
N5, and the wired array is a smooth plateau-then-decline shape fitted to it.

**What was measured (NOTEPAD_2026-06-30_nogames_basis, LOCKED estimator = daEV WQ6, still-listed-at-N,
busts=0, group/normal-dev baseline):**
```
RUC     N1-5: 0.76 0.97 0.50 0.40 0.44     sample n = 89, 26, 12, 6, 5
KPP     N1-5: 0.59 0.71 0.52 0.14 0.18
nonKPP  N1-5: 0.45 0.47 0.39 0.31 0.45
```
So the measurement stops at **N5**; **N6 was never measured.** The deep-N samples collapse fast (RUC N3=12,
N4=6, N5=5). The notepad explicitly flags: **"Per-position sat4-5 thin (n=4-6) -> pool"** — i.e. the N4-5
slices are too thin to stand alone and were pooled/smoothed (the finest-resolution / thin-slice discipline
applied and stated).

**The measured SHAPE:** hump at N2 (survival signal — washout 44%->1%), then decline to a NON-ZERO floor
(sat3+ has 0% washout -> a still-listed yr2+ sitter SURVIVED THE CULL = a kept project, not a washout; RUC
terminal ~0.40, not 0).

**The wired array is a re-parameterization of that shape (NOTEPAD_2026-06-30_nogames_3issues):**
```
RUC     yr1-6: 0.85 0.85 0.74 0.62 0.51 0.40
KPP     yr1-6: 0.70 0.70 0.60 0.50 0.40 0.30
nonKPP  yr1-6: 0.50 0.50 0.42 0.35 0.28 0.20
```
**Design rule:** "plateau (yr1-2, survived cull) then decline to terminal by ~yr6." The clean regular steps are
the tell of a designed curve. **Anchored to:** (i) the measured hump-then-decline-to-nonzero-floor shape above,
and (ii) the washout-collapse finding (sat1 56% -> sat2 1% -> sat3+ 0%), which justifies the yr1-2 plateau and
the non-zero terminal. Re-expressed on the DRAFTVAL basis (normal-value inverts pick order).

**So, precisely:** yr1-2 = plateau grounded in the strongest-sampled measurement (N1-2, n=89/26 RUC); yr3-5 =
guided by thin, pooled measurement (n=12/6/5 RUC); yr6 = beyond the measured range, a designed extrapolation to
the non-zero terminal. **Levels are DEFERRED to the PVC** ("the SHAPE is the fix"); the yr3-6 tail should be
treated as a provisional designed shape, not a measured quantity, and re-derived/confirmed at the PVC step
(pool deliberately if re-measuring, because still-listed-at-N is a tiny set past N3).

## (c) 1.19x sit-out retention lift — PARKED (do not apply)
The uniform ~1.19x lift on SITOUT_RETAIN (raised earlier as a candidate to bring the anchored sat-out Yr1 level up
to the ~217,573 empirical target) is PARKED, not pending. It is NOT applied at head. Sit-out RETENTION LEVELS are
re-derived at the PVC step on the measured values (the SHAPE is wired; the levels are provisional). Note when
revisited: a uniform x1.19 breaches retention 1.0 for RUC yr1-2 (0.85x1.19=1.01), so it needs a RUC yr1-2 cap
below 1.0; KPP tops 0.83 and nonKPP 0.60, both fine. This is no longer a "say-the-word" hold — it is closed to the
PVC step.

## (d) _pos_now double-switcher fixes (2026-07-01) — store data, engine code UNCHANGED
Two confirmed _pos_now errors (field stuck one switch behind current) corrected in the store (pre_stage0 + stage0):
- Ryan Maric  drafted GFWD -> GDEF(yr2) -> MID(now): _pos_now GDEF -> MID. ev 1427 -> 1409 (pole already MID; only
  the present-position replacement bar shifted).
- Ed Langdon  drafted MID -> GFWD(last yr) -> GDEF(now): _pos_now GFWD -> GDEF; _fut [GDEF 50, MID 50] ->
  [GDEF 70, MID 30] (was landing GDEF only by tiebreak). ev 1122 -> 593 (driven by removing the 50% MID pole
  inflation; now priced as the veteran defender). The 70/30 weight is a "mostly-defender, residual mid" choice —
  tunable if Luke's read differs.
Verified: panel 10/10; a full 2654-player before/after diff shows EXACTLY these two players moved, no others.
Engine code md5 UNCHANGED at 8aed420a (data-only). Store pre_stage0 md5 cf8b3c5e -> 644d1254.

---
## FOLD 2026-07-01 — Langdon causal correction + md5-axes note
- **Langdon (`ed-langdon`) −529 drop CAUSE = the present-position BAR (GFWD → GDEF), NOT the `_fut` pole.** Earlier framing attributed it to the `_fut` pole; that is wrong. The move to GDEF replacement pricing is what drops him. **MID is DEFLATIONARY, not inflationary** here. Value at head = 593 (verified this checkpoint).
- **md5-axes clarity**: the three identity axes are code→head (`_merged_recover.py`=8aed420a), data→store (`rl_model_data.json`/`.pre_stage0`=644d1254), band (`cm_400.pkl`=34faa865); the bundle checksum is the file→bundle axis (CHECKPOINT_MANIFEST.md). See START_HERE §1.

---
## FOLD 2026-07-01(b) — current-season-drop mechanism PINNED (supersedes reliability-shrink AND "correct aging")
- The uniform-looking current-season (2026) drop is the EXPOSURE-FEATURE / recency-decay channel: the prior season decays to 0.72 while the in-progress season is ~60% elapsed + thin, so `_exposure` (a forward-model input) drops → model lowers value. Cohort-VARYING (young −48% ≫ old −26%; INVERTED vs aging). NOT `_lvl_wt` (thin 2026 is games-size-discounted to ~10% weight; level move ≈0), NOT the reliability-shrink multiplier (saturated for 90% of thin players), NOT aging.
- Rozee (Luke read: underpriced): −31% = −21% exposure/decay/age channel + −9% thin-2026 level pull; `_lvl_wt` 96.6→96.0.
