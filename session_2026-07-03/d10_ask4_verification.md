# D10 ASK 4 — VERIFICATION at CANDIDATE v2.1 (engine `c8051893` / cp `7c3652da`)

**STATE: CANDIDATE v2.1 games-ramp @ `c8051893` — CONTROL `8aed420a` · PREVIOUS v2 `4a134d05`. Official board: `session_2026-07-03/ship_gates_report_c8051893.md` (three-column format, candidate-pinned instruments, workspace-paired then restored). Intra-session head lineage: e15bafa9 → db599058 (V0 structural-prior pin) → c8051893 (V0 cache key content-not-id) — **board A-lines byte-identical across all three** (diff-verified); only harness fold-behaviour changed.**

## B6 — GREEN, all three clauses (the binding fix)

```
B6  FAIL | FAIL | PASS   ramp(0..14g)=[1019, 1397, 1730, 2464, 3103, 3190, 3238, 3291, 3305, 3314,
                         3367, 3435, 3523, 3563, 3592]; dips(more games worth less)=none;
                         0->6 rise T=+2219; 0->6 steps>50%T=none; rise by 3g=+1445 (need >=555)  <- MOVED
```
Clause 1 (no dips): **none** (was −3/−226/−5). Clause 2 (no step >50%·T): max step 734 vs cap 1110 (was +2551 at the game-6 seam). Clause 3 (rise by 3g ≥25%·T): **+1445 ≥ 555** (was +0 — the flat-then-step violation). Spot-proofs: low-rate (avg 40) ramp monotone; output ramp at fixed games strictly rising; pre-season hold `ev(draft-yr)==V0` exact.

## Full gates board (three-column; VERDICT: **PASS=12 FAIL=4 FEATURE=1 PENDING=5 STRUCK=1** — one more green than v2's 11/5)

| gate | CONTROL | PREV v2 | CURRENT v2.1 | note |
|---|---|---|---|---|
| A1/A4/A6/A7 | PASS | PASS | PASS | Duursma 4160 > Uwland 1976; Reid rank 29 |
| A2 | FAIL | FAIL | FAIL | Curtis 0.822 — **red by Luke's ruling** (unmoved) |
| A3 [DC] | FAIL | FAIL | FAIL | Rozee 0.73 — **Luke accept-red** (unmoved) |
| A5 | FAIL | PASS | PASS | Ginnivan 1799 (v2's fix holds) |
| A8 [DC] | PASS | PASS | PASS | **Berry 2421 / Tsatas 1140 = 2.12x** (Tsatas accept-and-track value preserved) |
| A9 | FAIL | PASS | PASS | Ginnivan > Ward 1653 |
| A10 [DC] | PASS | PASS | PASS | Curnow 0.51 knife-edge holds (byte-unmoved by D10) |
| A11 [DC] | PASS | PASS | PASS | Farrow 1644 > Patterson 884; Cumming 1948 > Annable 1326 |
| A12 [DC] | FAIL | FAIL | FAIL | Travaglia 712 vs Moraes 887 — pre-existing, diagnosed in ASK-6a; Smillie leg passes |
| B1 | PASS | PASS | PASS | **avg peak N=4 @ 151** on the **v2.1 matrix** (`s4_matrix_v21_c8051893.json`); the scripted gate uses `s4_matrix_nogames.json` → **N4 @ 161** — both peak yr4, gate green ([D12 ASK 3 / audit R-c: 151 and 161 are two DIFFERENT matrices, not a disagreement — labelled]); >100, path_ok, per-cohort table printed; 2025 ref-only display |
| B2 | PASS | PASS | **PASS** | **median leakage 0.0 %-pts** (see §leakage below) |
| B4 | FAIL | FAIL | FAIL | export parity vs orphaned shipped bundle — red-as-expected at any candidate |
| B5 | FAIL | FEATURE | FEATURE | floor feature: **58 saves +2117**, lower-bound re-verify 0 lowered / 0 non-ND moved; saves table printed in report |
| B6 | FAIL | FAIL | **PASS** | above |

## B1 per-cohort (average row; full pipe table in the report)
avg (v2.1 matrix `s4_matrix_v21_c8051893.json`): d1 100 · d2 129 · d3 140 · d4 **151 (peak)** · d5 148 · d6 140 · d7 123 — cross-cohort average peaks yrs 4–6 ✓ (v2: 156.2 peak N4; the yr-1 denominator lift from the games-ramp flattens the index, peak position unchanged). **[D12 ASK 3 / audit R-c]** the scripted ship_gates B1 reads the nogames/control matrix (`s4_matrix_nogames.json`) → peak **N4 @ 161**; the two figures are two matrices (candidate vs control), both peak yr4, both green — neither is wrong, they were mislabelled as one number.

## Walk-forward book + leakage
Matrix rebuilt at the candidate (`data/s4_matrix_v21_c8051893.json`, walk-forward as-of protocol, 2,649 players); book regenerated (`docs/AFL_RL_WALKFORWARD_book_v21_c8051893.xlsx`, 29 sheets incl. the new Measure-2) — 2025 cohort Yr1 anchor sum 43,967. **B2 leakage 0.0** on the gate1 re-run at the final head. TWO HARNESS DEFECTS found and fixed en route (both engine-side hardening, zero value impact — board byte-identical): (1) V0 evaluated under gate1's fold-swapped models read prior-training variance as phantom T0 leakage → V0 pinned to import-time models (the harness's own "pole/ISO stay in-sample structural priors" convention); (2) the V0 cache was id()-keyed — gate1's deepcopied truncations recycle memory addresses, serving stale V0s cross-fold (measured: T0 gaps 5–20 pts, median 1.0) → keyed by stable draft-time content. GOOD>BUST separation intact every position (MID 50/0 … KEY_FWD 62/1).

## Grep proof (acceptance: no old-PVC reference remains in penalty code)
`grep -n "draftval\|PVC" engine/rl_after/_merged_recover.py` → hits ONLY: the `draftval()` definition itself · the **Luke-signed B5 floor** (`floor_frac(yis)*draftval(p)` — pricing feature, declared exception) · post-split demo prints (display). Delist, sit-out, stalled, mediocre: all V0-based. Dial grep: no graded/dial reference in the live engine (still wired nowhere).

## Restore-verify + panel (canonical untouched)
Workspace restored byte-exact: `_merged_recover.py 8aed420a` · `wire_redesign fe325d36` · `conditional_prior 346cffbb` · `par_redesign ef657403` · store `644d1254` · band `34faa865`. **CONTROL-side: panel 10/10 PASS at canonical values** (Daicos 7059 · Ward 1782 · Sheezel 7287 …). **[D12 ASK 3 / audit R-d correction]** the 10/10 is the CONTROL-side restore only. At the **CANDIDATE**, the panel is **NOT** 10/10 — **3 of 10 young players legitimately move under the games-ramp** (they are exactly the sit-out/rookie family the ramp re-prices); the candidate-side is evidenced by byte-match to the pinned v21 matrix (Daicos 7069 · Goad 846 · Smillie 773 · Green 545). BOTH-SIDES evidence (candidate live-run matches the pinned matrix AND control restores to canonical) is the standard — the original wrote up only the restored side. `verify_restore.sh` prints 6 PASS / 4 FAIL — the 4 FAILs are the instrument reading the **repo tree** (which on THIS branch rightly carries the candidate `c8051893`) against canonical expectations + the D8 pair-guard correctly flagging repo≠workspace at rest: **structural on a candidate branch, not a restore defect** (the workspace axes — store, band, panel — are all green; the named-player axes execute repo-engine×workspace-cp mixed pairs by their D7-documented design). Candidate measurements in this session never used that instrument — all ran fully-paired deployments.

## Floor-saves
58 saves, aggregate +2117 (v2: 54/+1684 — composition shifted: sit-outs mostly price above floor now; V0-re-anchored caps add a few). Full table printed in the report (the B5 alarm surface).
