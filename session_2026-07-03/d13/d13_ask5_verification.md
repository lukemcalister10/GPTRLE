# D13 ASK 5 — VERIFICATION at CANDIDATE v2.3

**STATE STAMP (three-column):** CONTROL = canonical `8aed420a` (byte-verified pre+post: engine `8aed420a` · store `644d1254` · band `34faa865`) · PREVIOUS = v2.2 `af1fc6aa` · CURRENT = v2.3 (head `f3e537ba`, store `644d1254`). Sequential engine loads only.

## Full gates board — v2.3 (`session_2026-07-03/d13/gates_v23.txt`)

**VERDICT: PASS=12 · FAIL=4 · FEATURE=1 · PENDING=5 · STRUCK=1.** The **4 reds (A2/A3/A12/B4) are identical to v2.1/v2.2 — all Luke-ruled or pre-existing/expected. NO new engine-caused red from D13.**

| gate | CONTROL | v2.2 | v2.3 | note |
|---|---|---|---|---|
| A2 Curtis≥0.9×Ward | FAIL | FAIL | **FAIL** | 0.822 — Luke-ruled red |
| A3 Rozee [DC] | FAIL | FAIL | **FAIL** | 0.73 (bar 0.75, Luke-amended out-for-2026) |
| A8 Berry≥2×Tsatas | PASS | PASS | **PASS** | **2421 / 1140 = 2.12× (Tsatas byte-unmoved)** |
| A11 play>sit [DC] | PASS | PASS | **PASS** | Farrow 1644>Patterson 908; Cumming 1948>Annable 1485 |
| A12 sit-not-punished [DC] | FAIL | FAIL | **FAIL** | Travaglia 712<Moraes 887 (pre-existing D10 6a); Smillie 993>Retschko 730 passes |
| **B1** growth law | PASS | PASS | **PASS** | see below |
| **B2** leakage | PASS | PASS | **PASS** | see below |
| B4 export parity | FAIL | FAIL | **FAIL** | vs orphaned bundle — expected at any candidate |
| B5 floor feature | FAIL | FEATURE | **FEATURE** | 51 saves +1319; lowered=0, non-ND moved=0 (RUC floor-saves 1, recomputed off capped V0) |
| **B6** games ramp | FAIL | PASS | **PASS** | see below |

## B6 — games-ramp green (all clauses, numbers; τ^1.5 diff-clean)

`ramp(0..14g) = [1287,1557,1852,2504,3103,3190,3238,3291,3305,3314,3367,3435,3523,3563,3592]` · **dips (more games worth less) = none** · 0→6 rise **T=+1951** · **0→6 steps >50%·T = none** · **rise-by-3g = +1217 ≥ 488** (25%·T). All three clauses **GREEN**. The concave proration line `τ'=(fe)^1.5` and `LAM_SIT` are **byte-identical to v2.2** (diff-clean — only the `R=` line changed R_SIT→_R_surf).

## B1 — cross-cohort average peak yrs 4–6 (the gate to watch)

**AVG (gated row) peak N=4 @ 130, path_ok=True** (peak in yrs 4–6, >100, pre-peak dip <5%). avg row: d1 100 · d2 120 · d3 124 · **d4 130 (peak)** · d5 126 · d6 120 · d7 105. Cohorts n=17. **PASS.**

**Three-column note:** v2.2 pinned peak N=4 @ **140.1** → v2.3 **130** — the retention re-derivation lifts young-cohort yr1–2 sit-out values, raising the yr1=100 index base and **compressing the peak ratio** (exactly the young-cohort channel the directive flagged). The gate **HOLDS** (peak still yr4, >100, path_ok); it did NOT break — no tuning applied. Per-cohort curves (UNGATED, Luke eyeball) printed in `gates_v23.txt`; recent cohorts 2017–2020 peak early (truncated windows), older cohorts peak yr4–5.

## B2 — leakage

`_gate1_wf.py` (150 trees, matched): **median |IS−WF| leakage = 0.0 %-pts** (tol 0.5). GOOD>BUST separation intact all positions (MID 50/0 · GEN_FWD 43/1 · KEY_FWD 62/1 · GEN_DEF 46/1 · KEY_DEF 55/1). **PASS.** Walk-forward book reproduces (matrix `s4_matrix_v23.json` md5 `f17a8b60`).

## Panel — BOTH sides (restore-verify)

- **CONTROL side (canonical restore):** the fixed panel reproduces **10/10 at canonical** (Daicos 7059 · Bontempelli 3101 · Sheezel 7287 · Gawn 2126 · Reid 3523 · Ward 1782 · Moore 177 · Goad 545 · Smillie 896 · Green 741).
- **CANDIDATE side (v2.3):** the 3 legit movers are the sit-out/retention rows — **Goad 850→844, Smillie 779→993, Green 552→626** (v2.2→v2.3); the other 7 are byte-identical to v2.2. Both-sides evidence is the standard.

## Unmoved / byte-checks

- **Tsatas = 1140** byte-unmoved (A8 2.12×) · **Berry = 1402** unmoved (2421 board via A8 scripted 2×).
- **dial `d66291a`** (D8 graded staleness cap) — **grep-absent** in the wired engine (WIRED NOWHERE, still).
- **CONTROL byte-verified pre+post:** canonical engine `8aed420a` · store `644d1254` · band `34faa865` — never modified (v2.3 lives on the candidate branch; canonical on main untouched).
- **Floor-saves:** 52→**51** total (board); **RUC floor-saves 1→1** (recomputed off capped V0, ASK 1).
