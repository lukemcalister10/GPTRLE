# DIRECTIVE 1 notes — 2026-07-02 — head 8aed420a store 644d1254 — suite 764a0d91

## Predicted vs actual (prediction on record in the directive)
| gate | predicted | actual | note |
|---|---|---|---|
| A3 [DC] | RED | RED | ratio 0.69 vs >=0.80 |
| A10 [DC] | RED | RED | ratio 0.51 vs >=0.70 |
| B6 | LIKELY RED | RED | 1-5g flat at 745 then +2518 step at 6g; also dips at 9->10g (-220) and 13->14g (-5) |
| A13/A14 | PENDING | PENDING | advisory: all lineball vs stand-in PVC except Burgoyne (2191 vs PVC[8]=1704) |
| A8 [DC] | unknown | PASS | Berry 3473 > 2x Tsatas 2166 |
| A11 [DC] | unknown | PASS | Farrow 1641>982; Cumming 2002>936 |
| A12 [DC] | unknown | RED (half) | Travaglia 601 < Moraes 876; Smillie 896 > Retschko 730 |

## SURPRISES — observations accepted, cause UNKNOWN (not decomposed; no cause labels)
1. **A2 RED**: Josh Ward 1782 ABOVE Paul Curtis 1162 AND Joshua Weddle 1628 (Luke read: Ward below both).
2. **A9 RED**: Ginnivan 1578 < Ward 1782 (same Ward-high / Ginnivan-low pattern as A2/A5).
3. **A5 RED (narrow)**: Ginnivan 1578 vs floor 1600 (-22); Bowey 2585 and Blakey 3053 clear their floors.
4. **B4 RED**: regenerated `rl_app_data.json` = `1898ead7`, shipped board = `b8f9e998`; regeneration IS
   deterministic here (same md5 across two runs). Ranked hypotheses: (h1) shipped board was exported from the
   pre-reconciliation LIVE store, not the pre_stage0-reconciled store bootstrap installs; (h2) original-container
   env drift (board cut pre-dates the pins); (h3) export-path code moved after the board was cut. Status: UNKNOWN.
5. **B5 RED (DECLARED floor)**: 9 yr1-2 picked players below 0.25x draftval (worst Jack Watkins ev=18 vs dv 308);
   floor is a DECLARED proxy needing ratification — offender list in the report file.

## DECLARED thresholds needing supervisor/Luke ratification (all marked in-script)
B2 leakage tol 5.0 %-pts · B5 floor 0.25x draftval · B6 seam tol 10% & 3x median step ·
B1 rule = per-cohort rise (yr4-6 peak > yr1) + POOLED peak position in 4-6 · A6 kernel bw 0.6 on log-pick.

## doc_lint warn-allowlist — current spec (STEP 4, for supervisor review)
- FAIL rules (unchanged): banned status words `\b(closed|done)\b` case-insens. in LIVE docs; superseded hashes
  {8c6d5582, 55e3c3a9, 7147b824} claimed current/latest/head.
- WARN rule: `\b(LATEST|pending|not yet|TODO)\b` (case-sensitive) in LIVE docs.
- WARN allowlist (suppresses WARN only, never FAIL): case-insensitive substring match on the LINE for any of:
  `not yet created` · `pending luke` · `decision pending`  (added 2026-07-02, commit 06e3ddd — covers legitimate
  gap/gate statements).
- Line-level exemption (pre-existing, applies to FAIL+WARN): line contains any of
  `supersede/lineage/banned/five-state/reconciliation`.
- LIVE list changes: +SHIP_GATES.md (06e3ddd, pre-directive) · +BAKE_CHECKLIST.md (this commit). No new allowlist
  terms needed this directive: current board = 0 FAIL 0 WARN (live=7).

## C1/C2 + B3
Definition proposals live in `session_2026-07-02/ship_gates_report_8aed420a.md` (written by the check script);
each needs its own directive to build the baseline/V1 books; B3 needs the book-gate set enumerated.
