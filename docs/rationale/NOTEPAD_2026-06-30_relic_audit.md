# Notepad — turn response, 2026-06-30 (relic audit: B1 / delete-candidates / CHANGELOG)

Reconcile + confirm + doc-hygiene. Defects FLAGGED not fixed. Engine e0ac9c377d1e, nothing baked.

1. B1 — STEP-3 DIALS ARE NOT WIRED (clean not-wired answer; price-moving FLAG).
The live ev() path reads the line-26 PROVISIONAL scalars (L31-32/35/41-42/74). The calibrated step-3 values were
never applied to code — confirmed by the CHANGELOG's own "STEP 3 — CLOSED" entry saying "engine UNCHANGED" (only
the 3-B pole re-level was applied, the e0ac9c37 bump). Per dial:
  LDECAY  : live 0.40 single  | calibrated KEY 0.40 / GEN 0.35 / MID+RUC 0.225   (GEN+MID+RUC decaying too slow)
  FLAT_TOL: live 3.0 single   | calibrated KEY 10.3 / GEN 12.0 / MID+RUC 14.0    (3-4x gap; proven-flat hold rarely fires -> levels track current)
  PROVEN_N: live 4 + c=n/4     | calibrated per-branch SURFACE (above~0/near~2.8/below-young) which ALSO replaces the c=n/4 shrinkage — unwired
  POLE_RAMP: live 22 == 22 (OK).
The calibrated numbers (0.225/10.3/12.0/14.0/2.8) are absent from engine code; no per-group dict, no 2nd path.
CONSEQUENCE: all of step 4 (book/backtest/no-games/ruck) was validated on PROVISIONAL step-1 dials, not the
calibrated step-3 surface -> wiring them (Luke's go) shifts step-4 numbers and needs re-validation. NOT fixed.

2. DELETE-CANDIDATES — all confirmed NO live caller (audit INERT tags all correct).
Live ev = raw_ev*iso_corr + staleness; _merged_recover touches rd only for REPL_DROP (L56), never the value fns.
Dead: B8 KAPPA/SCONV/LOWBASE + comp() (no-op `return v`); B13 out_tilt ("CUT cont.21") / track_slip / SLIP_*;
survival() ("REMOVED cont.20", surv=1.0); MA.value pedestal + dist_value + redesign_value + reliability/own_band
blend + par_redesign forks (superseded par-router). NONE had a live caller. -> delete-candidates for a later
BATCHED cleanup (Luke sign-off; not deleted now). Minor: SHRINK_K is in par_build:25 (+print :199), not the cited
dist_redesign :122-123.

3. CHANGELOG — exists (769 lines) but was NOT shipped in the step-4 checkpoint tarball (why the audit found none).
Added a 2026-06-30 relic-audit entry (merged, not forked); adopted the forward convention (every constant change/
derivation -> what, value, derivation-or-"Luke choice + date"). Must be included in every checkpoint henceforth.
Also: the CHANGELOG's "STEP 3 CLOSED" header is the doc-divergence itself — closed on measurement, never wired.

Engine e0ac9c377d1e, nothing baked. No price changes. All defects flagged for Luke's go.
