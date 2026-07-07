# AUDIT — COLD EXTERNAL AUDIT of CANDIDATE v2.1 (games-ramp rework) — engine `c8051893` / cp `7c3652da`

**DIRECTIVE 11 · SEAT OPUS · EFFORT XHIGH · READ-ONLY on engine values.** No shared context with the build
that produced this candidate — every number below is re-derived/reproduced from the repo + raw store, not
lifted from the build's artifacts.

**STATE STAMP (three-column, binding reporting rule R6):**
`CONTROL = canonical 8aed420a / store 644d1254 / band 34faa865` ·
`PREVIOUS = CANDIDATE v2 4a134d05` ·
`SUBJECT = CANDIDATE v2.1 c8051893 / cp(conditional_prior)=7c3652da` on branch
`claude/games-ramp-engine-change-qt7824` (PR #14, audited at head `447f61b`; **NOT merged**).

**Reproduction harness:** candidate engine deployed to `/home/claude/rl_workspace/rl_after` (md5 `c8051893`
verified), store `644d1254` (byte-identical to control — the change is engine-only; the `cp 7c3652da` label is
`conditional_prior.py`, not the store). One engine load per process, sequential, pinned ENV
(`PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22`,
py3.12.3/numpy2.4.4/scipy1.17.1/sklearn1.8.0). Workspace restored to `8aed420a` at close (panel 10/10 at
canonical — CONTROL untouched, byte-checked).

---

## VERDICT: **CLEAR** (engine sound; games-ramp behaves to spec)

Pre-registered rule: CLEAR iff A1–A3, A5–A8 pass **and** A4 = "prorated: yes". All satisfied. Four **reporting-
hygiene reds** are flagged below with named fixes — none is an engine fault, a spec breach, or a CLEAR-gate.
No OPEN-QUESTIONs on the engine; the ⚠RUC-V0 flag (Emmett) is carried unresolved per instruction (Luke-routed
`h-ruc-startvalue-hot`).

| item | verdict | one line |
|---|---|---|
| **A1** relic grep | **PASS** | V0 is the sole penalty anchor; `draftval` survives only in its def, the B5 floor, display prints |
| **A2** derivation | **PASS** | independent re-derivation reproduces R_SIT (maxΔ **0.001**) & λ (maxΔ **0.003**), inside pre-stated tol |
| **A3** behaviour | **PASS** | pre-season hold exact; monotone in games+output; bars 6/10/14/22 prorated; position preserved |
| **A4** Patterson | **PASS — prorated: YES** | τ=0.58 (not 1.0) → R=0.669; final 884 is B5-floor-bound |
| **A5** scope | **PASS** | board-wide 10-bar proration rejected & **unwired**; f1 is first-evidence scoped |
| **A6** gates | **PASS** | 12P/4F/1FEAT/5PEND/1STRUCK; reds all Luke-ruled/pre-existing; B6 green; B2 leak 0.0 |
| **A7** anchors | **PASS** (2 reporting reds) | 13/13 anchors byte-exact; cohort control exact; PR cohort table stale vs matrix |
| **A8** paperwork | **PASS** | obituary, Measure-2, R5/R6 verbatim, Travaglia decomp, dial absent, CHANGELOG keep-both, CONTROL untouched |

**Reporting reds (build artifacts, not engine):** (R-a) PR anchor-table 2025-cohort v2/v21 = 37,103/43,703 is a
stale scratch census; the shipped matrices (and the build's own ASK4) give **37,875/43,967** — fix: report the
pinned-matrix numbers. (R-b) build's position-preservation line "V0 identical 1524 pre-season" is wrong (V0
differs by position) — the conclusion is right, the supporting number is not. (R-c) scripted B1 uses
`s4_matrix_nogames.json` → peak N4@**161**, not the v2.1 matrix (build's ASK4 "151"); both peak yr4, gate green.
(R-d) panel is **not** 10/10 at the candidate (3 of 10 move under the ramp) — build only evidenced the
restored-to-canonical side.

---

## A1 — RELIC GREP (independent)

Grep of the candidate `_merged_recover.py` for `draftval|PVC`: hits at the `draftval()` definition (238), the
purge **comments** (245/246/318), the **B5 floor** (`floor_frac(yis)*draftval(p)`, 375 — Luke-signed pricing
feature, declared exception), and **display prints** (386/421/422). Cross-module `PVC` hits are the superseded
`rl_model.value()/unpl_eq/pedestal` board path (relic #7 — **no caller in the `ev()` lineage**, confirmed) and
the export/Measure-2 rulers (relic #8, display). Reconciles with the build's 8-entry relic list. The four penalty
paths are all V0-based in code: delist `0.02*v0_start`, sit-out `sitout_ev(...v0_start...)`, stalled/mediocre
`min(e, v0*frac)`. `raw_ev` / `v0_start` are band/par-based, **not** PVC.

Live V0 spot-check **at v2.1** (reproduced, not v2): **Harry Dean V0=1237 < PVC 2248** (below) · **Sullivan
Robey V0=1882 > PVC 1603** (above) · Emmett V0=1536 = 2.5×PVC[27] (RUC hot). Position adjustment is exactly the
Dean-below/Robey-above assignment Luke described.

## A2 — DERIVATION REPRODUCTION (the XHIGH core)

Re-implemented the harvest + kernel + isotonic **from scratch** (own code, own engine load) against the raw
store scoring histories. Estimator (per spec): sit-out cell = no ≥6-game season through Y; r = O/V0, O = price6 of
best forward qualifying era-adj level in (Y, Y+4], busts=0; R_SIT = M_SIT/NORM ("0.76-form"); λ from depth-1
g0–5 + graduated 6–9. Harvest: **2464** sit-out cells / **163** graduated (build 2465/163); RUC pool scale 1.065
(build 1.065). **Pre-stated tolerance (declared before compute): retention ±0.05, λ ±0.10 per knot; structural
endpoints exact.**

| curve | re-derived (mine) | wired | maxΔ |
|---|---|---|---|
| R_SIT nonKPP | 0.428 0.404 0.410 0.432 0.438 0.424 | 0.429 0.404 0.410 0.432 0.437 0.424 | **0.001** |
| R_SIT KPP | 0.468 0.380 0.325 0.278 0.253 0.266 | 0.468 0.380 0.325 0.278 0.253 0.266 | **0.000** |
| R_SIT RUC | 0.675 0.548 0.503 0.472 0.435 0.434 | 0.674 0.547 0.503 0.472 0.435 0.435 | **0.001** |
| LAM_SIT (g0..6) | 0 0.16 0.493 0.548 0.548 0.819 1.0 | 0 0.16 0.493 0.547 0.547 0.816 1.0 | **0.003** |

Shape confirmed: nonKPP ~flat 0.40–0.44; KPP declines 0.47→0.27; RUC 0.67→0.43. Evidence-axis Kendall τ within
played depth-1 cells: g=**0.064**, q=0.096, g·q=0.103 (build +0.059/+0.099/+0.102) — a λ-side quality term is
weak/non-monotone; the build correctly did **not** wire it (quality credits through e_full). **All curves inside
pre-stated tolerance → derivation reproduces.**

**"0.76-form" — grounded (NOT an OPEN-QUESTION).** From `docs/rationale/NOTEPAD_2026-06-30_nogames_basis.md`: the
retention estimator is `daEV(WQ6) realized-value ratio for sat-out players ÷ same-depth normal-development
baseline (all still-listed), busts=0, still-listed conditioning`. The literal "0.76" is the *original locked
RUC-N1 value* of that estimator (`SESSION_SUMMARY_2026-06-30_step4_book.md`: "RUC sat≥1 0.76× / sat≥2 0.97×") —
a named convention, not a live constant. The D10 re-derivation applies the same convention to a fuller harvest,
giving RUC-d1 = 0.674 (the name persists; the number evolved). It is NOT the `tfade` 0.76 pole-fade (unrelated).

## A3 — BEHAVIOUR PROOFS at v2.1

- **(a) pre-season penalty exactly zero:** not-yet-started synth (debutyr 2027), `ev(2026) = 1892.00 == V0 =
  1891.61` (τ=0 → R=1.0 structural). PASS.
- **(b) monotone in games AND output, straddling the old 6-game seam:** first-evidence MID pk10 @avg85, games
  0..14 → ramp `[1019,1397,1730,2464,3103,3190,3238,3291,3305,3314,3367,3435,3523,3563,3592]` — **no dips**, no
  game-6 cliff/jackpot (the old +2551 seam is gone). Low-rate (avg40) ramp monotone. Output ramp at fixed g=2,
  avg 20→110 → `[1084…2344]` strictly rising. Never worth less for one more game or one more point. PASS.
- **(c) bars 6/10/14/22 + decay prorated to R14/24 (fE=0.58), code quoted:**
  - `nseas_pro`: `x['games']>=6.0*(_fEy(Y) if x['year']==Y else 1.0)` (6→3.48 in-progress).
  - `_coreM1` f1: `f1=min(1.0, gy/(10.0*SEASON_FE))` (10-bar → first-qual-season fractional credit).
  - `expgate`: `... /max(1e-9, POLE_RAMP*min(1.0,_playable(p,Y)/cp.SEASON))` (22-bar → 12.8 yr-1 mid-season).
  - `conditional_prior`: `LEVEL_RAMP=14`, `_SFE=RL_M3_FE=0.58` (14-bar → 8.2).
  - decay: `tau=max(0.0,Y-cp.debutyr(p))+(fe if Y>=cp.debutyr(p) else 0.0)` — **within-season linear accrual**.
  - `G_ADQ=12` deliberately NOT prorated (outside the 6/10/14/22 enumeration) — declared. PASS.
- **(d) position preserved through the treatment:** same-pick(12) zero-evidence sit-out synths at v2.1 →
  MID `975` / KEY_DEF `610` / GEN_DEF `577` / RUC `880`, driven by distinct V0 (1458/883/863/1085). Position
  basis survives end-to-end; nothing collapses to a flat PVC fraction. PASS. *(Reporting red R-b: the build's
  ASK3 claim "V0 identical 1524 pre-season" is false — V0 differs by position; the conclusion is nonetheless
  correct.)*

## A4 — PATTERSON DECOMPOSITION (MUST-ANSWER)

Dylan Patterson|2025|pk5 (GEN_DEF, 0 games 2026), reproduced live at v2.1:

```
debutyr=2026 · fE=0.5800 · tau = max(0,2026-2026)+0.58 = 0.5800 · class=nonKPP
V0 = 1135.7 · R(tau=0.58) = 0.6688 · lambda(g26=0) = 0.0 · e_full = 1201.4
sit-out anchor = (1-λ)·R·V0 + λ·e_full = 0.6688·1135.7 = 759.6  ->  ev_prefloor = 760
B5 floor: yis=1 · floor_frac=0.45 · draftval=1965 · floor = 0.45·1965 = 884.2  (BINDS)
FINAL ev = 884
```

**VERDICT: decay is prorated to season progress — YES.** τ=0.58 (not 1.0), so R=0.669 vs the full-season nonKPP
0.429; the decay has accrued only 58% of season 1 (`tau=max(0,Y-debutyr)+fE`). Patterson is **not** branded a
full no-play year — that is exactly D10 ASK 2c / Luke's verbatim ("we should not be punishing players like
Patterson … when the full season has not concluded"). **Nuance (honest):** his FINAL 884 is set by the B5 floor
(`0.45×dv`), not the prorated anchor (760) — the floor is dv-based and would bind at 884 even without proration.
The proration is genuinely coded and moves the pre-floor anchor (760 vs unprorated 487); it just isn't the
binding term for *this* player. The build's 884 is correct under the coded proration. No spec breach.

## A5 — SCOPE CHECK on the rejected proration

`_nqual` (line 47) is the **unprorated** career/qual counter; the 10-bar proration is delivered ONLY via the
first-qualifying-season `f1` credit in `_coreM1`, gated to first-evidence players
(`if Y!=INPROG_Y or any(x['games']>0 and x['year']<Y ...): return Lo`). The board-wide prorated 10-bar (Tsatas
1140→2080 breaking A8; O'Driscoll −525; Cadman −253) and the unscoped f1 (+940 Tsatas) were measured and
**REJECTED**; nothing of them is wired (grep-confirmed; Tsatas byte-unmoved at 1140, A8 = 2.12×). Inside the
sit-out treatment all bars (6/10/14/22 + bestlvl 6-bar) prorate per 2c. PASS.

## A6 — GATES at v2.1 (three-column, reproduced)

`ship_gates_check.py` run at the candidate (workspace engine `c8051893`) + walk-forward `_gate1_wf.py` for B2.

```
VERDICT: PASS=12  FAIL=4  FEATURE=1  PENDING=5  STRUCK=1
```

| gate | CONTROL | PREV v2 | CURRENT v2.1 | note |
|---|---|---|---|---|
| A1/A4/A6/A7 | PASS | PASS | PASS | Duursma 4160>Uwland 1976; Reid rank 29; Maric MID/MID; Langdon GDEF |
| A2 | FAIL | FAIL | FAIL | Curtis 0.822 — **Luke-ruled red** (unchanged) |
| A3 [DC] | FAIL | FAIL | FAIL | Rozee 0.73 (bar 0.75) — **Luke accept-red, data-caused** |
| A5 | FAIL | PASS | PASS | Ginnivan 1799 / Bowey 2969 / Blakey 3287 |
| A8 [DC] | PASS | PASS | PASS | **Berry 2421 / Tsatas 1140 = 2.12×** |
| A9 | FAIL | PASS | PASS | Ginnivan 1799 > Ward 1653 |
| A10 [DC] | PASS | PASS | PASS | Curnow 0.51 (bar 0.50) knife-edge |
| A11 [DC] | PASS | PASS | PASS | Farrow 1644>Patterson 884; Cumming 1948>Annable 1326 |
| A12 [DC] | FAIL | FAIL | FAIL | Travaglia 712 vs Moraes 887 — **pre-existing** (6a diagnoses); Smillie 773>Retschko 730 passes |
| B1 | PASS | PASS | PASS | cross-cohort avg peak **N4@161** (nogames matrix); per-cohort table printed; 2025 ref-only |
| B2 | PASS | PASS | **PASS** | walk-forward leakage IS−WF ≤3, **median 0.0**; GOOD/BUST separation intact every pos |
| B4 | FAIL | FAIL | FAIL | export parity vs orphaned shipped bundle — **expected red at any candidate** |
| B5 | FAIL | FEATURE | FEATURE | floor feature: **58 saves +2117**; lower-bound 0 lowered / 0 non-ND moved |
| B6 | FAIL | FAIL | **PASS** | ramp green: dips none · max first-6 step 734 ≤ cap 1109 · rise-by-3g 1445 ≥ 555 |

The **4 reds are all Luke-ruled or pre-existing/expected** (A2 Curtis, A3 Rozee [DC], A12 Travaglia [DC], B4
export) — **no new engine-caused red** from the games-ramp; one more green than v2 (B6). Floor-saves table printed
(58 rows; Patterson 760→884 +124 present). Panel evidenced BOTH sides: **candidate-side** live run byte-matches
the pinned v21 matrix (Daicos 7069, Goad 846, Smillie 773, Green 545); **control-side** restored 10/10 at
canonical. *(Reporting red R-d: at the candidate the panel is not 10/10 — 3 young players move under the ramp;
the build only evidenced the restored side.)*

## A7 — ANCHORS (three-column, all reproduced live at v2.1)

| player (name\|cohort\|pick) | g26 | prod | CONTROL | PREV v2 | CURRENT v2.1 | note |
|---|---|---|---|---|---|---|
| Annable\|2025\|6 (MID) | 1 | 40.0 | 936 | 936 | **1326** | V0 1859 · R(0.58)=0.667 · λ(1g)=0.40 → 1g@40 is now information |
| Patterson\|2025\|5 (GEN_DEF) | 0 | — | 982 | 982 | **884** | anchor 760 → **B5 floor** 0.45·1965 binds; decay prorated (τ=0.58) |
| X.Taylor\|2025\|11 (GEN_DEF) | 2 | 42.0 | 690 | 690 | **662** | V0 860 (0.62×PVC); derived treatment prices below old 0.50×dv placeholder |
| Cumming\|2025\|7 (MID) | 7 | 61.3 | 2002 | 1982 | **1948** | qualified; small net from prorated ramps + first-season level credit |
| Emmett\|2025\|27 (RUC) | 5 | 32.8 | 518 | 518 | **1338** | released at pace. **⚠RUC-V0 flag carried** (V0=1536=2.5×PVC[27]; `h-ruc-startvalue-hot`, Luke-routed) |
| Ison\|2025\|47 (GEN_FWD) | 4 | 53.2 | 212 | 212 | **538** | released at pace (DIAG-A +257 under-credit, direction confirmed) |
| Lord\|2024\|9-MSD (MID) | 3 | 76.7 | 77 | 394 | **414** | v2 394 = **M3 recovery of stalled-cap crush** (floor 108 non-binding — confirmed); dv→V0 re-anchor lifts to 414 |
| Travaglia\|2024\|8 (GEN_DEF) | 0 | — | 601 | 712 | **712** | untouched by D10 (ns=1) |
| **Taylor (Xavier) printed above; Oskar Taylor\|2025\|15** | 0 | — | 537 | 537 | **572** | name-guard: the OTHER 2025 Taylor, keyed by pick/cohort |

**54 under-seam players (MUST print) — aggregate, from the pinned matrices:** the material games-ramp footprint
(v2→v21, |Δ|>50) is **83 players +6.3k**, dominated by the young never-qualified family (Emmett +820, Cleary
+466, Annable +390, Murray +374, Nairn +346, Ison +326, Goad +270, Green −242, Kondogiannis +212 …). Whole
board-wide footprint = 1,438 incurve movers, but **864 are ≤3 pts (median |Δ|=2)** — prorated in-progress-ramp
jitter, +889 net; established stars unchanged (board top Δ=0 vs v2). *(This is broader than the build's reported
"146 movers"; immaterial but the build's "everyone else unchanged by construction" is approximate, not exact.)*

**2025 cohort total (three-column):**

| source | CONTROL | PREV v2 | CURRENT v2.1 | Δ v2→v21 |
|---|---|---|---|---|
| pinned matrices (incurve n=64, authoritative — book/board use these) | **37,901** | 37,875 | **43,967** | +6,092 |
| build PR anchor table (scratch census, "n=58") | 37,901 | 37,103 | 43,703 | +6,600 |

CONTROL 37,901 reproduces byte-exact. The **+6k rise and its stated reasons are sound** (λ evidence-credit blend
= biggest channel; V0 re-anchor; prorated POLE/LEVEL ramps — all verified in code; DIAG-B CF6 +3,871 direction
confirmed, larger for the stated reasons). **Reporting red R-a:** the PR anchor table's v2/v21 (37,103/43,703) is
a stale scratch census inconsistent with the shipped matrices and the build's own ASK4 (43,967) — fix: quote the
pinned-matrix numbers.

## A8 — PAPERWORK

- **Obituary (flat-50%) — PRESENT (E2, BOARD_LAYERS_OBITUARY.md):** name (`SITOUT_RETAIN×draftval`), did (flat
  class-fraction of old-PVC, games/scoring/season/position all discarded), magnitude (49/64 of 2025 cohort;
  54 under-seam ≈+4,096; +2551 game-6 jackpot), rationale (Luke's D10 ruling verbatim), commit (deleted on
  branch, engine e15bafa9), resurrection ref ("returns only with a derivation that beats the kernel curves
  out-of-sample"). ✓
- **Measure-2 pick-sum ruler — PRESENT** as a permanent display-only book sheet (`s4_render_7147.py`:
  `m2=wb.create_sheet('Measure-2 vs pick sum')`). ✓
- **Three reporting rules (R6) verbatim — PRESENT** in `BAKE_CHECKLIST.md §REPORTING`, `KICKOFF_PROMPT.md`,
  `START_HERE.md`, `LUKE_RULINGS_LEDGER R6`; R5 (games-ramp design statement, Luke verbatim) present. ✓
- **Travaglia/Clarke/Farrow decomposition — PRESENT** (d10_ask6a + PR); channel named =
  **performance-weighting of demonstrated output × recency/exposure decay** (Farrow pr=1738 live vs Travaglia
  pr=404 aged/decayed). **Clarke same-cohort control logic is SOUND:** Clarke (2024, pick 39) prices above
  Travaglia (2024, pick 8) *on output alone* — same cohort year isolates and rules out a cohort-year effect;
  deeper pick + higher output pricing above shallower pick shows output dominates pedigree (~+180 net). Diagnosis
  only, nothing wired. *(No opinion on the remedy per instruction.)*
- **D8 graded dial — grep-ABSENT** from the live engine (no `import staleness_graded_cap` / graded-cap call in
  `_merged_recover.py` or the imported modules; only generic env-param "dial" comments). ✓
- **CHANGELOG keep-both merge (step 0) — CLEAN:** `main → candidate` CHANGELOG diff = **0 lines deleted, 50
  added** (the D10 entry only); both the D8 graded-cap and DIAG-B rev3 entries survive. ✓
- **CONTROL untouched (byte-check):** audit tree `_merged_recover.py`=8aed420a, `cm_400.pkl`=34faa865,
  `rl_model_data.json`=644d1254; tree clean; workspace restored to 8aed420a with panel 10/10 at canonical. ✓

---

## OPEN-QUESTIONs

**None on the engine.** The games-ramp treatment is correct, derived, and behaves to spec. The ⚠RUC-V0 flag
(Emmett 1338 flows from V0=2.5×PVC[27]) is **carried unresolved by design** — it is `h-ruc-startvalue-hot`, a
PVC-stage/Luke-routed item, not a D10 defect. The four reporting reds (R-a…R-d) each have a named fix and none
gates CLEAR.

## BURN

Engine loads (sequential, one per process): candidate anchor/V0/Patterson/B6/position probe · independent
re-derivation harvest · gates board (158s) · walk-forward gate1 (~2min) · control-restore panel = **5**. Plus
pure-JSON matrix passes (no engine). Heavy turns: ~4 (build artifacts + report ingest). CONTROL byte-verified
pre + post. ~2.5h vs the ~2.5h estimate — no >2× blowout.

**IN PLAIN TERMS:** The new games-ramp is honest — a kid holds his drafted value through the pre-season, loses
it only slowly while he sits (at the rate history says sitting costs kept kids), and every game he plays pulls
his price toward what he's actually scoring, with no jackpot at game six and no full-year no-show penalty on a
half-finished season; I rebuilt the retention and blend curves from the raw histories myself and they land on
the wired numbers to three decimals, Patterson's decay IS prorated (his 884 is the signed floor catching him),
and the canonical engine is untouched — the only things to clean up are four places where the write-up's numbers
drifted from the engine's own shipped tables, none of which change a player's value.
