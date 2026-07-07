# D10 ASK 3 — ANCHOR CHECKS (three-column, state-labelled)

**STATES: CONTROL = canonical `8aed420a` (pinned matrix `data/s4_matrix_control_8aed420a.json`) · PREVIOUS = CANDIDATE v2 `4a134d05` (pinned matrix `data/s4_matrix_v2_4a134d05.json`) · CURRENT = CANDIDATE v2.1 games-ramp `c8051893` (this branch; scratch deploy p6 + official gates run in the ASK-4 file). Nothing baked.**

| player (ID key: name\|cohort\|pick) | g26 | prod | CONTROL | PREVIOUS v2 | CURRENT v2.1 | Δ vs v2 | note |
|---|---|---|---|---|---|---|---|
| Daniel Annable\|2025\|6 (MID) | 1 | 40.0 | 936 | 936 | **1326** | +390 | V0 1859 held pre-season, decayed R(0.58)=0.667 → 1240 anchor + λ(1 game at pace)=0.40 credit toward his production-priced path — his 1g@40 is finally information, not ignored |
| Dylan Patterson\|2025\|5 (GEN_DEF) | 0 | — | 982 | 982 | **884** | −98 | anchor 0.667·V0(1136)=758, lifted by the **Luke-signed B5 floor** 0.45·dv=884; his V0 is a GEN_DEF start value (0.58×PVC — the position adjustment the old rule erased); no longer punished as a full no-play year — the decay has only accrued 58% of season 1 |
| Xavier Taylor\|2025\|11 (GEN_DEF) | 2 | 42.0 | 690 | 690 | **662** | −28 | Luke's book "Taylor 690" (=0.50×1380 flat); now 0.453·(0.667·860) + 0.547·e_full — GEN_DEF V0 0.62×PVC |
| Oskar Taylor\|2025\|15 (GEN_DEF) | 0 | — | 537 | 537 | **572** | +35 | the OTHER 2025 Taylor (name guard: keyed by ID/pick/cohort) |
| Sam Cumming\|2025\|7 (MID) | 7 | 61.3 | 2002 | 1982 | **1948** | −34 | straddle partner: qualified at v2 already; small net from prorated ramps + first-season fractional level credit |
| Louis Emmett\|2025\|27 (RUC) | 5 | 32.8 | 518 | 518 | **1338** | +820 | RELEASED at pace (5 g ≥ prorated bar 3.5) → live production path. **EYEBALL FLAG:** the size is the engine's own RUC start-value scarcity prior (V0=1536 = 2.5×PVC[27] — ASK-1 table) flowing through par/band; nothing in D10 sets RUC levels |
| Jack Ison\|2025\|47 (GEN_FWD) | 4 | 53.2 | 212 | 212 | **538** | +326 | released at pace; DIAG-A's +257 under-credit estimate, direction confirmed |
| Cooper Lord\|2024\|9-MSD (MID) | 3 | 76.7 | 77 (D8 head table) | 394 (DIAG-A v2 decomp) | **414** | +20 | see attribution one-liner below |
| Tobie Travaglia\|2024\|8 (GEN_DEF) | 0 | — | 601 | 712 | **712** | 0 | untouched by D10 (ns=1, no 2026 games) — see ASK-6a decomposition |
| Angus Clarke\|2024\|39 (GEN_DEF) | 0 | — | 575 | 675 | **675** | 0 | untouched |
| Jacob Farrow\|2025\|10 (GEN_DEF) | 12 | 71.0 | 1641 | 1642 | **1644** | +2 | pole-recovery term is inert for him (pole < band price) |
| Sullivan Robey\|2025\|9 (MID) | 10 | 58.8 | 2219 | 2207 | **2255** | +48 | prorated POLE/LEVEL ramps (judged vs 12.8 playable, not 22) |
| Harry Dean\|2025\|3 (KEY_DEF) | 11 | — | 1872 | 1878 | **1840** | −38 | first-season fractional level credit nets slightly down |

**LORD ATTRIBUTION (the pending one-liner):** CONFIRMED with a correction — his CANDIDATE-v2 394 was **NOT floor×draftval** (floor = 0.35×308 = **108, not binding**); it was the stalled-cap crush (77-level) recovered by the **M3 value-space blend** to 394 (D8's own decomp: "M3 blend recovers to 394", floor column "N (108)"); at v2.1 the cap re-anchors dv→V0 (308→420) lifting him 394→**414**; the real cap-crush release is the Luke-endorsed graded dial, deferred to v3 (dial confirmed absent from this engine by grep).

**Aggregates (three-column):**

> **[D12 ASK 3 / audit R-a correction]** The AUTHORITATIVE 2025-cohort figures are the pinned walk-forward **matrix** numbers (incurve n=64) — the book and board read the matrix, so it is the source of truth. The earlier headline `37,103 / 43,703` was the **n=58 store scratch census** and is superseded. RULE (now stated in the doc): where a store-census number and a pinned-matrix number disagree, the **pinned matrix is authoritative**. The store-census sub-aggregate rows are kept, labelled non-authoritative, because their per-family decomposition is internally consistent on the n=58 census.

| aggregate | CONTROL | PREVIOUS v2 | CURRENT v2.1 | Δ vs v2 |
|---|---|---|---|---|
| **2025 cohort — pinned matrix (incurve n=64, AUTHORITATIVE)** | **37,901** | **37,875** | **43,967** | **+6,092** |
| 2025 cohort — store scratch census (active n=58, non-authoritative) | 37,901 | 37,103 | 43,703 | +6,600 |
| under-seam (never-qualified, 1–5 g26; n=31, census) | — | 10,689 | **16,048** | **+5,359** |
| zero-game sit-outs (n=77, census) | — | — | — | +198 net |
| whole old sit-out family (old-ns==0, n=108, census) | — | 33,733 | **39,290** | **+5,557** |

DIAG-B's what-if said ≈ +3,871 (CF6, full-season-equivalent games, M3 off). Actual matrix Δ **+6,092** (census +6,600): same direction, larger — CF6 never modelled the λ evidence-credit blend for 1–5-game players (the biggest channel: +5,359 on 31 players), the V0 re-anchor, or the prorated POLE/LEVEL ramps for played rookies. DIAG-A's "54 players ≈ +4,096" maps to my census as the 31 active under-seam (+5,359) plus zero-game/depth-2+ family members (whole family +5,557 across 108).

**Directional acceptance — no player's value drops for playing more or scoring more:** proven structurally (λ monotone in games; e_full monotone in output — spot checks: B6 ramp avg-85 monotone 0..14; avg-40 seam ramp monotone post-smoothing; g=2 output ramp avg 30→100 strictly rising — ASK-2 file §3). Players who FELL vs v2 (X.Taylor −28, Leake 407→278, McCabe 507→380, Cootee −25, …) fell because the derived treatment prices their profile below the old flat placeholder — not because they played/scored more; each is ≥floor and position-consistent.

**Position preservation (Dean/Robey-style on penalised players):** same-pick (12) zero-evidence synths at v2.1 price differently by position through the sit-out treatment — the position basis survives the penalty end-to-end; nothing collapses to a flat PVC fraction. **[D12 ASK 3 / audit R-b correction]** the earlier claim "V0 identical 1524 pre-season" is WRONG: **V0 DIFFERS by position** — that difference IS the mechanism preserving position. Cold-audit verified per-position V0 at pick 12: MID **1458** / KEY_DEF **883** / GEN_DEF **863** / RUC **1085** (and class retention differs on top). The conclusion (position preserved, no flat-fraction collapse) stands; only the "identical 1524" support number was a scratch error.
