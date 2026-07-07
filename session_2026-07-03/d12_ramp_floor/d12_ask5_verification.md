# D12 ASK 5 — VERIFICATION at CANDIDATE v2.2

**STATE STAMP: CONTROL = canonical `8aed420a` (byte-verified pre+post: engine 8aed420a · store 644d1254 · band 34faa865) · PREVIOUS = v2.1 `c8051893` · CURRENT = v2.2 `af1fc6aa`.** Sequential engine loads only; canonical workspace restored + md5-verified.

## Full gates board — three-column (CONTROL · v2.1 · v2.2)
Report: `session_2026-07-02/ship_gates_report_af1fc6aa.md`. **VERDICT: PASS=11 · FAIL=4 · FEATURE=1 · NOT-RUN→PASS(B2 below)=1 · PENDING=5 · STRUCK=1 (132s).**

| gate | CONTROL | v2.1 | v2.2 | note |
|---|---|---|---|---|
| A1 Duursma>Uwland | PASS | PASS | PASS | 4160 vs 1976 |
| A2 Curtis≥0.9×Ward | FAIL | FAIL | FAIL | Luke-ruled red (0.822; "look at Curtis down the line") |
| A3 Rozee [DC] | FAIL | FAIL | FAIL | 0.73 (bar 0.75; Luke-amended, out-for-2026) |
| A4 Reid top-40 | PASS | PASS | PASS | rank 29 |
| A5 improvers | FAIL | PASS | PASS | Ginnivan/Bowey/Blakey above SCAR floors |
| A6 early rucks | PASS | PASS | PASS | yr1-3 RUC 449 ≤ MID 558 |
| A7 pos fixes | PASS | PASS | PASS | Maric MID / Langdon GDEF |
| **A8 Berry≥2×Tsatas** | PASS | PASS | **PASS** | **2421 / 1140 = 2.12× (Tsatas byte-unmoved)** |
| A9 Ginnivan>Ward | FAIL | PASS | PASS | 1799 vs 1653 |
| A10 Curnow [DC] | PASS | PASS | PASS | 0.51 (bar 0.50) |
| A11 play>sit [DC] | PASS | PASS | PASS | Farrow 1644>Patterson 849; Cumming 1948>Annable 1414 |
| A12 sit-not-punished [DC] | FAIL | FAIL | FAIL | Travaglia 712<Moraes 887 — **pre-existing** (D10 6a); Smillie 779>Retschko 730 passes |
| B1 growth law | PASS | PASS | **PASS** | see below |
| B2 leakage | PASS | PASS | **PASS** | see below |
| B4 export parity | FAIL | FAIL | FAIL | vs orphaned bundle — expected red at any candidate |
| B5 floor feature | FAIL | FEATURE | **FEATURE** | 52 saves +1330; lowered=0, non-ND moved=0 |
| B6 games ramp | FAIL | PASS | **PASS** | see below |

**The 4 reds (A2/A3/A12/B4) are all Luke-ruled or pre-existing/expected — identical set to v2.1. NO new engine-caused red from D12.** The only v2.1→v2.2 board moves: **B5** (58→52 saves, the floor re-anchor) and **B2** (re-run below).

## B6 — games-ramp green re-proof (all clauses, numbers)
`ramp(0..14g) = [1139, 1469, 1785, 2482, 3103, 3190, 3238, 3291, 3305, 3314, 3367, 3435, 3523, 3563, 3592]`
- dips (more games worth less): **none**
- 0→6 rise T = **+2099**; single 0→6 step > 50%T: **none** (max first-6 step 697 ≤ 1050)
- rise-by-3g = **+1343** (≥ 25%T = 525)
**PASS.** The concave ramp lifts only the sit-out segment (g0–3); g≥4 (production path) byte-identical to v2.1; continuity preserved at the graduation bar (λ→1 kills R·V0). Seam re-proven for KEY_FWD too (ASK 1 artifact).

## B1 — cross-cohort average peak, yrs 4–6 (2025 ref-only; same-builder control)
**v2.2 (matrix `s4_matrix_v22_af1fc6aa.json`): peak N=4 @ 140.1, path_ok=True** → PASS. avg row: d1 100 · d2 128 · d3 133 · **d4 140 (peak)** · d5 135 · d6 128 · d7 113. Cohorts n=17.
- **Same-builder control (isolates engine from builder):** v2.1 rebuilt with the identical `s4_matrix_M1v7.py` = peak N4 @ **138.5**; v2.2 = **140.1** — my changes nudge B1 **+1.6** (up, not down); both peak yr4, both path_ok.
- The v2.1 docs' "151" is the **pinned v21 matrix** (a different builder) — the R-c label class; not comparable to same-builder 138.5. The apples-to-apples number is 138.5→140.1.
- Cell attribution: 1,279 of the 2004–2020 incurve cells move v2.1→v2.2 — these are the **floor re-anchor** touching floored cells across all cohorts (e.g. McCartin's floored yr-cell 1350→851 as his V0<draftval); the concave ramp is a no-op for completed-season cells (fE=1 ⟹ 1^1.5=1). B1 average barely moves.
- Per-cohort curves printed on every board run (Luke eyeball channel); 2020 "shocking draft" peaks N3 (ungated, visible).

## B2 — walk-forward leakage (IS vs WF, tree-matched @150)
`_gate1_wf.py` → GOOD priced near/above par early & flat, BUST at 0–1 every position; **IS−WF gap ≤ 3 pts, median 0.0** → leakage ≈ 0.00. GOOD>BUST separation intact all positions (MID 53/15 … KEY_FWD 22/5). **PASS.**

## Restore-verify + panel — BOTH sides evidenced (candidate-pinned instruments)
- **CONTROL side:** canonical engine byte-identical (8aed420a / 644d1254 / 34faa865) → the fixed panel reproduces **10/10 at canonical** (Daicos 7059 · Bontempelli 3101 · Sheezel 7287 · Gawn 2126 · Reid 3523 · Ward 1782 · Moore 177 · Goad 545 · Smillie 896 · Green 741).
- **CANDIDATE side (v2.2):** **7 of 10 byte-unmoved v2.1→v2.2** (Daicos 7069 · Bontempelli 3109 · Sheezel 7207 · Gawn 2137 · Reid 3565 · Ward 1653 · Moore 201); **3 of 10 move — exactly the sit-out family under the ramp**: Goad 846→850 · Smillie 773→779 · Green 545→552. This is the R-d standard: both-sides evidenced, not just the restored side.

## Anchors — three-column (CONTROL · v2.1 · v2.2)
| anchor | pos | g26 | CONTROL | v2.1 | v2.2 | Δ v2.1→v2.2 |
|---|---|---|---|---|---|---|
| Annable | MID | 1 | 936 | 1326 | **1414** | +88 (concave ramp) |
| Patterson | GEN_DEF | 0 | 982 | 884 | **849** | −35 (floor freed + ramp) |
| X.Taylor | GEN_DEF | 2 | 690 | 662 | **693** | +31 (ramp) |
| Cumming | MID | 7 | 2002 | 1948 | **1948** | 0 |
| Emmett ⚠ | RUC | 5 | 518 | 1338 | **1338** | 0 (⚠ RUC V0 hot, carried) |
| Ison | GEN_FWD | 4 | 212 | 538 | **538** | 0 |
| Lord | MID | 3 | 77 | 414 | **414** | 0 (floor never binds) |
| **Berry (A8)** | MID | 13 | 3473 | 2421 | **2421** | **0** |
| **Tsatas (A8)** | MID | 6 | 1083 | 1140 | **1140** | **0 (byte-unmoved, A8 2.12×)** |
| Ison/Farrow etc | — | — | — | — | — | played players all unmoved |
| **2025 cohort (pinned matrix, incurve n=64)** | — | — | 37,901 | 43,967 | **45,051** | +1,084 |
| **floor-saves** | — | — | n/a | 58 (+2117) | **52 (+1330)** | −6 saves |

**Only sit-out players moved v2.1→v2.2** (Annable/Patterson/Taylor/Smillie/Goad/Green); every played anchor byte-unmoved. **Tsatas 1140→1140 unmoved (A8 2.12× held).**

## Grep-absence + CONTROL byte-verify
- **dial `d66291a` (graded staleness cap): grep-ABSENT** from the live engine (no graded/dial/gradedfix reference).
- **CONTROL byte-verified pre+post:** origin/main engine `8aed420a` · store `644d1254` · band `34faa865` — canonical untouched.
- v2.2 engine md5 `af1fc6aa`; doc_lint 0 FAIL.
