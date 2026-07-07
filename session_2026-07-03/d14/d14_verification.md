# DIRECTIVE 14 — VERIFICATION at CANDIDATE v2.4 (V0 BOARD CURVE + KPP RETENTION FLOOR)

**STATE STAMP (three-column, binding):** CONTROL = canonical `8aed420a` (byte-verified pre+post: engine `8aed420a` · store `644d1254` · band `34faa865`) · PREVIOUS = v2.3 (engine-file md5 `f3e537ba`, git head `def39f5a`, store `644d1254`) · CURRENT = v2.4 (engine-file md5 `7c199a1f`, store `644d1254`). Sequential engine loads only. **NOTHING BAKED.**

**FORK NAMED + RESOLVED (STEP 0):** the directive cited v2.3 head as `f3e537ba`. `f3e537ba` is not a git object — it is the **md5 of the v2.3 `_merged_recover.py`** (the state hash used in the v2.3 gate-snapshot filenames). The v2.3 git head is `def39f5a` (PR #17, branch `claude/retention-surface-ruck-cap-i1dfft`). Same state; v2.4 branched from it. No other fork taken on the derivation; R1 pooling and the backtest-exemption design (below) are the named pre-specified forks.

---

## ASK 1 — V0 BOARD CURVE (Luke's amended law) — VERDICT: WIRED, gates green

**Curve verdict:** 8 cells fitted. TIER 1 = age≤18 per position (6 cells, 1408/1571 players): adaptive-bandwidth Nadaraya-Watson over log recorded pick, **local eff-n≥35 with bandwidth NOT maxed** (minEffN 35.0–35.6, 0/90 grid points at Hmax) → isotonic non-increasing — the finest resolution the sample supports. TIER 2 = mature draft-age≥19 (163 players): every exact (pos×age) cell is eff-n<35 even at max bandwidth → **R1 pooling**: the 5 non-RUC positions pool into one age-resolved 2-D surface V0*(draft-age, log-pick) [mature V0 is age-dominated and position-washed in-sample; DECLARED], RUC mature kept as its own thin cell (eff-n≈12, flagged); isotonic in pick AND non-increasing in draft-age so mature entrants stay lawfully differentiated by age and from age-18. **Order printed: ruck cap 1.73×PVC applies FIRST (`_v0_raw`), the curve is fitted on the capped V0s.** Full params: `d14_ask1_curve_params.md`.

**Moves:** 831 up · 740 down · 0 unchanged (real-ND curve population n=1571) · max|ΔV0| = **1354** (Naitanui, pk2 RUC 2574→1220 — the top ruck picks smooth down to the RUC age-18 curve).

**Clark/Mackenzie (plain):** Jhye Clark (MID, pk8, 2022) and Cameron Mackenzie (MID, pk7, 2022) both sit on the MID·age-18 curve now — Clark pk8 → V0* 1792, Mackenzie pk7 → V0* 1876 — correctly ordered by pick, no longer the crude both-1864 clamp the D13 guard produced.

**By-construction gates (wired, printed green every gates-board run):**
- **D14a — identical V0* same cell/pick across years:** max cross-draft dispersion = **0.0000 SCAR** (was 507 at v2.3). **Cumming (MID pk7, 2025) V0* = 1876 = Mackenzie (MID pk7, 2022) V0* = 1876** — same boat, identical, cross-draft. GREEN.
- **D14b — within-cell inversions:** **0** roster-wide under V0* (re-run of the D13 scan). GREEN. The D13 guard-transform is retired on the board and converted to this assertion (obituary E5).

**R1 outcome (stated):** age-18 cells fit unpooled at eff-n≥35 (finest supported). Every mature exact (pos×age) cell fired R1 → pooled as above (non-RUC across position, RUC separate); RUC-mature eff-n≈12 flagged as sample-limited.
**R2 outcome (stated):** **91 movers >35%** (28 age-18, 63 mature). **WIRED anyway** (the wobble is the disease). The large-% movers are veterans whose zero-evidence V0 was near-zero (age-crushed) lifted to the mature-pool level; their **board ev is production-driven and moves ≤ a few points** (Tim Kelly V0 71→488, ev 1611→1611; Shaun Mannagh 5→239, ev 529→529). Full list: `d14_r2_movers.tsv`.
**R3:** no fork beyond R1/R2 encountered on the derivation.

**Cross-draft dispersion (one line):** same pos×draft-age×pick across ≥2 draft years (318 groups): BEFORE(v2.3) max spread **507 SCAR** → AFTER(v2.4) **0** (by construction — V0* is a function of pos×age×pick only).

**Emmett (cap 1.73 default + curve interaction, explicit):** ruck cap 1.73×PVC binds his prior FIRST (`_v0_raw` = 1054 at v2.3), then the RUC·age-18 curve at pk27 sets **V0* = 955** (ev **1054 → 1054**, unchanged — his board value is prior/production-blend-fed, not V0-gated).

---

## ASK 2 — KPP RETENTION FLOOR (Owner Override O1) — VERDICT: WIRED, floor binds d3+ (and d1+ mid-picks)

**Floor verdict:** KPP sit-out retention surface := pointwise **MAX(KPP, nonKPP)** at every (log-pick, depth); comparator **nonKPP only** (RUC excluded); **board path only** (`_BOARD_PATH`). Depth monotonicity re-asserted numerically — gate **D14c = True** (max of two isotonic-non-increasing curves is non-increasing). **Where it binds:** predominantly depth ≥3 (KPP decays faster than nonKPP), AND depth ≥1 for the mid-pick band (pick 15–30) where raw KPP d1 retention sits just below nonKPP — exactly the "KPPs losing value faster" case Luke's floor removes. Pick-50 KPP ≥ nonKPP everywhere (no bind). Binding map: `d14_ask2_floor.md`.

**O1 registered:** `docs/process/OWNER_OVERRIDES.md` (owner-set where the floor binds, data-derived elsewhere — so no future audit flags the floor as a derivation error).

**D13 anchor set — end-Yr1 AND projected end-Yr2 at zero games, still NON-INCREASING (v2.4):**
Annable 1122→883 · Patterson 534→435 · X.Taylor 565→401 · Ison 250→176 · Smillie 1118→856 — all non-increasing (Luke's signed law holds post-curve+floor).

**KPP anchors (incl. Riak Andrew and Whitlock) — CONTROL · v2.3 · v2.4 (board ev; V0):**
| player (KPP) | CONTROL | v2.3 | v2.4 |
|---|--:|--:|--:|
| Riak Andrew (KEY_DEF, pk55) | 235 | 330 (v0 614) | 257 (v0 477) |
| Matt Whitlock (KEY_DEF, pk27) | 426 | 327 (v0 616) | 351 (v0 624) |

**Aggregates:** 54-set sit-out aggregate 41139 (control) · 43903 (v2.2) · 46764 (v2.3) · **48397 (v2.4)**. 2025 cohort total (n102) 47416 · 55836 · 57009 · **57710 (v2.4)**. Floor-saves (B5 board) **54 (RUC 1)** at v2.4 (v2.3 51) — pure lower bound preserved (0 lowered, 0 non-ND moved).

---

## ASK 3 — CARRIED VERIFICATION QUERIES

**(a) The 1FEAT = gate B5** (floor-as-pricing-feature). **Defined + registered** in `SHIP_GATES.md` (GATE STATUS VOCABULARY): B5 was AMENDED by Luke (D7) from a pass/fail alarm into a PRICING FEATURE at the ev() boundary. **It does NOT mask a red** — the signal the old alarm carried is relocated to the printed FLOOR-SAVES table (the new alarm surface; a list that grows unexpectedly is the signal), and the pure-lower-bound property (0 lowered, 0 non-ND moved) is re-verified every run. Registered, not retired.

**(b) v2.2 (`af1fc6aa`) PREVIOUS column REPRODUCED directly** (independent re-run of the engine): **Annable board = 1414** (V0 1858.6), **2025 cohort total (n102) = 55,836**, 54-set n137 agg 43903, floor-saves 52 (RUC 1). Confirms the D13 claims. **Note on 43,967:** that figure is the DIFFERENT measure — the incurve-**n64** matrix Yr1 total (PR#16 R-a: 37,875/43,967) — NOT the n102 board cohort (55,836). The v2.1→v2.2 deltas (Annable 1326→1414, cohort 43,703→45,051 pinned-matrix / 47,416→55,836 board) are thereby verified against real engine runs.

**(c) PR #17 write-up fixes:** PR #17 names the four audit fixes (43,967 cohort · "V0 identical 1524" · B1 labels · panel claim) but consolidates them under **ONE shared commit `c1893b0`** (D12 ASK 3, docs-only: CHANGELOG D12 + the three D10 write-up docs) — **not four lines each with its own doc+commit**. The fix-commit hash is `c1893b0` (distinct from the v2.1 engine hash `c8051893` — the confusable pair is resolved here). Reported as the actual state; no doc gap to close for (c).

**(d) PR #17 completeness — one GAP found and CLOSED here.** Present in PR #17: the largest pre-fix inversion (Jhye Clark pk8 2401 > Mackenzie pk7 1864, gap 537 → 1864) and the Luke-facing pipe tables. **GAP:** PR #17 has NO full per-ruck V0/PVC ladder — only a single Emmett cap-rung row (670/792/914/1054/1201). **CLOSED in this PR:** the full ladder for all 172 rucks (V0 + V0/PVC per rung, cap 1.73 in force) is written to `session_2026-07-03/d14/d14_ask3d_ruck_ladder.md`.

---

## ASK 4 — VERIFICATION at v2.4 (three-column CONTROL · v2.3 · v2.4)

**Board scoreboard (v2.4):** **PASS=14 · FAIL=4 · FEATURE=1 · NOT-RUN=1 · PENDING=5 · STRUCK=1.** The 4 reds **{A2, A3, A12, B4} are IDENTICAL to v2.3** — all Luke-ruled or pre-existing/expected. **NO new engine-caused red.** Three new D14 laws green (D14a/b/c). Full report: `ship_gates_report_7c199a1f.md`; snapshot `data/gates_snapshots/gates_7c199a1f.json`.

| gate | CONTROL | v2.3 | v2.4 | note |
|---|---|---|---|---|
| A8 Berry≥2×Tsatas | PASS | PASS | **PASS** | 2421 / 1140 = 2.12× (Tsatas byte-unmoved) |
| A11 play>sit | PASS | PASS | **PASS** | Farrow 1644>Patterson 781; Cumming 1948>Annable 1533 |
| A12 sit-not-punished | FAIL | FAIL | **FAIL** | Travaglia 712<Moraes 887 (pre-existing); Smillie 1002>Retschko 730 |
| B1 growth law | PASS | PASS | **PASS** | cross-cohort AVG peak N=4 @130, path_ok (matrix s4_matrix_v24.json) |
| B5 floor feature | FEATURE | FEATURE | **FEATURE** | 54 saves +1335; lowered=0, non-ND moved=0 |
| B6 games ramp | PASS | PASS | **PASS** | ramp `[1287…3592]` byte-identical to v2.3; τ^1.5 + LAM_SIT diff-clean |
| D14a same-boat V0 | — | — | **PASS** | cross-draft dispersion 0.0000 |
| D14b V0 order | — | — | **PASS** | within-cell inversions 0 |
| D14c KPP floor depth-mono | — | — | **PASS** | max(KPP,nonKPP) non-increasing |

- **B6 GREEN** (all clauses): ramp(0..14g) = `[1287,1557,1852,2504,3103,3190,3238,3291,3305,3314,3367,3435,3523,3563,3592]`; dips = none; 0→6 rise T=+1951; steps>50%T = none; rise-by-3g = +1217 (≥488). τ^1.5 proration + LAM_SIT **byte-identical to v2.3 (diff-clean)**.
- **B1 GREEN, did NOT break** (never tuned to pass): cross-cohort AVG peak N=4 @130, path_ok=True; row d1 100·d2 120·d3 124·**d4 130**·d5 126·d6 120·d7 105; cohorts n=17. Same as v2.3 (matrix byte-identical).
- **WALK-FORWARD BOOK REPRODUCES — maxΔ = 0.000000** vs v2.3 (2649 stable-keyed players, anchor/cur/Vpath). Proven twice: (i) the v2.4 matrix regenerated with `_BOARD_PATH=False` equals `s4_matrix_v23.json` on every value; (ii) v2.4 with `_BOARD_PATH=False` is byte-identical to v2.3 on all 2656 board players (0 differing). **Luke's backtest exemption honoured — historical book unchanged.**
- **Leakage 0.00** (B2, `_gate1_wf.py`, matched @150 trees): backtest path byte-identical to v2.3 → median |IS−WF| = 0.0; GOOD>BUST separation intact all positions.
- **Panel BOTH sides:** CONTROL side — 10/10 at canonical restore (Daicos 7059 …). CANDIDATE side — the movers vs v2.3 are the sit-out/retention rows (Goad 844→823, Green 626→604, Smillie 993→1002); the rest byte-identical.
- **What did NOT move:** Tsatas **1140** byte-unmoved (A8 2.12×) · Berry **2421** unmoved · ruck cap default **1.73** in force · dial `d66291a` grep-ABSENT in the wired engine · **CONTROL byte-verified pre+post** (engine 8aed420a · store 644d1254 · band 34faa865).

---

## Ledger / obituary / override updates
- Rulings **R12** (V0 board curve, amended law) + **R13** (KPP floor, O1) — `docs/process/LUKE_RULINGS_LEDGER.md`.
- Obituary **E5** (D13 guard-transform → assertion, board path) — `BOARD_LAYERS_OBITUARY.md`.
- Owner override **O1** registered — `docs/process/OWNER_OVERRIDES.md`.
- SHIP_GATES: FEATURE-status defined; D14a/b/c laws registered.

## NEXT ACTION
Combined scoped audit **D13 + D14** (per directive) before any bake. #16 and #17 stay OPEN; canonical untouched. NOTHING BAKED.
