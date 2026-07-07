# D13 ASK 4 — CARRIED ACCEPTANCE QUERIES

**STATE:** CONTROL = canonical `8aed420a` · PREVIOUS = v2.2 `af1fc6aa` · CURRENT = v2.3.

## (a) The gate that "left PASS" between v2.1 (12P/4F) and v2.2 (11P/4F)

**B2 (leakage).** It did NOT fail. The v2.1 gates board scored **12 PASS / 4 FAIL / 1 FEATURE** (`ship_gates_report` at c8051893; audit A6). The automated v2.2 board scored **11 PASS / 4 FAIL / 1 FEATURE / 1 NOT-RUN→PASS**: B2 came up **NOT-RUN in the automated pass** at v2.2 (dropping the automated PASS count 12→11), and was **re-run manually and confirmed PASS (leakage ≈ 0.00)** in the D12 ASK 5 write-up (`session_2026-07-03/d12_ramp_floor/d12_ask5_verification.md`, B2 block). The **four reds were unchanged and identical to v2.1** — A2 (Curtis, Luke-ruled), A3 (Rozee, Luke-amended out-for-2026), A12 (Travaglia<Moraes, pre-existing D10 6a), B4 (export parity vs orphaned bundle). No new engine-caused red from D12; the only board moves were B5 (58→52 floor-saves) and B2 (NOT-RUN→re-run PASS).

## (b) The four audit write-up fixes (R-a..R-d) — doc + commit each landed in

All four "reporting-hygiene reds" the D11 cold audit named (`docs/AUDIT_COLD_v21_c8051893.md`, R-a..R-d) landed **docs-only in one commit — `c1893b0` (D12 ASK 3, "four audit-named write-up fixes, no engine effect")** — which edited `docs/CHANGELOG.md` (D12 entry) plus the three D10 write-up docs it corrected (`d10_ask2_derivation.md`, `d10_ask3_anchor_checks.md`, `d10_ask4_verification.md`):

| red | the drift | the fix | landed in |
|---|---|---|---|
| **R-a** (43,967 cohort) | PR #14 anchor-table 2025-cohort v2/v2.1 = 37,103 / 43,703 was a stale n=58 store scratch census | quote the authoritative **pinned matrices: 37,875 / 43,967** (incurve n=64; book/board read these) — rule stated: matrix is authoritative | commit `c1893b0` · CHANGELOG D12 |
| **R-b** ("V0 identical 1524") | build's ASK 3 claim "V0 identical 1524 pre-season" is false — V0 **differs by position** | corrected: V0 by position at pk12 (MID 1458 / KEY_DEF 883 / GEN_DEF 863 / RUC 1085); the *conclusion* (V0 basis survives end-to-end, no flat-PVC collapse) stands | commit `c1893b0` · CHANGELOG D12 |
| **R-c** (B1 labels) | scripted B1 "151 vs 161" label mix-up | labelled: **151 = v2.1 matrix, 161 = nogames/control matrix**; both peak yr4, both green | commit `c1893b0` · CHANGELOG D12 |
| **R-d** (panel claim) | "panel 10/10 at candidate" overclaimed | corrected: 10/10 is the **CONTROL-side restore**; the candidate side has 3 legit ramp movers; **both-sides** evidence is the standard | commit `c1893b0` · CHANGELOG D12 |
