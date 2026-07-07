# SESSION SUMMARY — 2026-06-23 (cont.22): SOURCE-OF-TRUTH UNIFICATION + DOB LOAD + peak_est CACHE FIX

## DONE & VERIFIED (Python / source level)
1. **SOURCE OF TRUTH UNIFIED.** `afl_master_db.xlsx` was stale/incomplete (compiler input, last edited Jun 17);
   the live JSON had diverged (2003 cohort, Bramble fix, positions — JSON-only). Rebuilt the master FROM the
   live JSON so it is now a faithful complete superset. PROVEN: `compile(master) == live JSON` for 2654/2656
   records exactly; the only diffs are INTENDED (844 DOBs folded in; Tenace + Lovett-Murray duplicate-year rows
   merged; Monahan key fix).
2. **Compiler `rl_build_data.py` extended** to round-trip everything: scoring now starts **2005** (was 2006 — the
   2003 cohort debut season was being dropped); added columns **dob, phantom, double_count, pvc_exclude, eyr**;
   added **PSD** to the pickless set (Betts/Ware were mis-flagged).
3. **DOBs folded into the SOURCE** (844 incl Shane Tuck = 1981-12-24). Previously saved only in side-car files
   (`dob_corrected.json`, `mature_age_dobs.csv`) and never loaded — now in `afl_master_db.xlsx` `birthyear`/`dob`
   columns and flowing through to `_by`/`_bd`. Tuck etc. now read their real age, not the 18-at-draft default.
4. **2003-2005 scoring** now lives IN the master (was JSON-only, one recompile from being lost).
5. **peak_est CACHE BUG FIXED.** `peak_est` was first computed/memoised at SCALE (rl_model.py L436) while pickless
   players still held the placeholder `_eff`; the real pick-equivalent is applied at L726 but the cache was never
   cleared, so the board shipped stale (too-high) values. Added `_pe_clear()` after attribute finalisation, before
   the board build. Sharman **1147 -> 310** (correct). ~53 pickless players corrected. (NB: this OVERTURNS the
   cont.21 finding that blamed the as-of loop — the as-of loop's `_pe_clear()` was *revealing* the correct value.)
6. **Eddie Betts + Elijah Ware -> 2004 RD #1/#2** (were mis-filed as PSD/no-pick). Thursfield -> #3, rest +2.
7. **Monahan** standardised: key `rob-monohan` -> `rob-monahan`.
8. **40 removed players archived** (`outputs/removed_players_archive_2026-06-23.xlsx` + .json) — full data incl
   scoring, so they can be restored. They were intentionally dropped from the pool; JSON is authoritative.
9. Backups: `afl_master_db.xlsx.bak_pre_unify_2026-06-23`, `rl_model_data.json.bak_pre_unify_2026-06-23`.

## DE-DUP
The two master copies (`rl_build/` canonical + `rl_after/` mirror) are now GUARANTEED identical (the unified build
writes both from one source). rl_build is canonical; only ever edit via the build. Physical single-file collapse
(symlink) is a trivial follow-up if wanted.

## ⚠️ OPEN — DO NOT SHIP THE HTML BOARD YET
**JS-engine parity regressed to 192/788** after the board build. This is EXPECTED, not a bug: the DOB ages +
cache fix MOVE the projection for young/high-pedigree players, and per the documented process projection-moving
changes require re-syncing the in-browser engine (`_engine_block_v23.js` carries its own projection math). All 192
mismatches are projection-driven (167 young <50g; the 25 "proven" are recently-drafted high-pedigree). NEXT: sync
the JS projection/age handling to the new peak_est/ages, rebuild, confirm parity back to ~0/N, THEN ship the HTML.

## ALSO STAGED (separate, not in this build)
- **active-17**: the 17 current-list-but-undebuted players still inactive (IRE/UNR/PDN/PDA/MSD + pre-2024 ND/RD).
  Fix = broaden the `extra`/`active()` unplayed rule to honour `force_active`/`last_listed`, set those flags in
  the master for the 17. Kept separate for proper verification.
