# BUILD — DIRECTIVE v3: low-games / no-games pricing — prototype + diagnosis (NOTHING BAKED)
Engine head `8aed420a` unchanged. Three prototype books built (M1+v7 inherited in all). Deliverables listed at end.

## PART A — prototype into the walk-forward book (year-1 / curve movers)
Applied to a **copy** of the matrix builder, swapped into `ev` before the ASOF loop; **PLACEHOLDER, direction-only:**
1. Retain table **+0.1** at every entry (RUC .95/.95/.84/.72/.61/.50, KPP .80/.80/.70/.60/.50/.40, nonKPP .60/.60/.52/.45/.38/.30).
2. Cliff replaced by a smooth **w-blend** `value=(1−w)·anchor+w·production`; anchor=`draftval×retain_eff` (retain<1 ⇒ capped at 1.0). w-ramp is a **principled convex placeholder** (`w=clip(G_career/44,0,1)^1.3`, small at few games — real ramp not yet derived, see C.8).

### Finding — year-1 does NOT lift; it DROPS. Decomposition is decisive.
Absolute opportunity-matched cohort value by career-year (SCAR k), 2004–24 ND+RD, busts=0:
```
Yr:                    1     2     3     4     5     6     7
(0) M1v7 baseline:   1067  1365  1378  1403  1306  1176   985     Yr1/mean(Yr2-7)=0.84
(1) +retain0.1 only: 1126  1397  1392  1409  1309  1177   985     0.88   Yr1 +60k (+5.6%)
(2) +retain +wblend:  865  1115  1264  1364  1289  1172   980     0.72   Yr1 −262k vs (1)
```
- **(1) the +0.1 retain raise WORKS**: Yr1 +5.6%, ratio 0.84→0.88 — moves toward the plateau, the direction the premise wants. The "harsh sit-out haircut" half of the premise **holds**.
- **(2) the w-blend BACKFIRES on net Yr1**: −23% vs (1), ratio → 0.72 (gap WIDENS), indexed peak 146%→175%. Mechanism: **only 29% of Yr1 players sat out; 71% played.** The unified blend pulls those played-6-to-22-game rookies from their production value DOWN toward the draft-anchor (a thin-sample discount, w<0.5 for ≤1 season at G_FULL=44).

**Interpretation (for Luke's reads to settle):** Yr1 is NOT uniformly too low. The **cliff/sit-out slice is** under-valued (retain-raise fixes it), but the engine currently **over-trusts 6–22g rookies at full production**, and the blend discounts them. Whether that discount is *correct* or *wrong* is a player-read call:
- If played 6–22g rookies are currently **over-valued** → blend-all is right, and Yr1 *should* drop.
- If they're **fine** → blend only the `ns==0` cliff population, leaving ns≥1 at production. A **cliff-only-blend** would LIFT Yr1 (retain-raise + few-games lift, no played-rookie discount). **I can build this variant on your word.**

**Bright line kept:** M1+v7 = validated + bake-ready (proven slice). Both Part-A changes are PLACEHOLDER, direction-only.

## PART C.5 — Lombard mechanism (confirmed)
`leo-lombard`, GEN_FWD/nonKPP, pick 9, draftval 1603. Real scoring 2025=4g/19.2, 2026=13g/58.6. **His current (2026) value is fine** (ns=1, priced on production, ev=1531). The cliff is his **YEAR-1**: at ASOF 2025 scoring truncates to [4g/19.2], `ns=nseas=0` because **nseas counts seasons with games≥6** (4<6) → the `if ns==0` branch returns the sit-out anchor **802** (=1603×0.50), discarding his 4-game production (995). **Exact cutoff that makes 4≡0 = the 6-game nseas threshold.** Post-fix: retain-raise 802→**962** (heavy lift); w-blend adds ~+1 (w=0.044 at 4g, production 995≈anchor) → **963**. The blend's value at 4g is conceptual (no longer identical to a 0-game sit-out), small by design (guardrail 2).

## PART C.6 — hard-cutoff inventory + discontinuity
| # | cutoff | threshold | discontinuity |
|---|--------|-----------|---------------|
| 1 | **sit-out cliff** (`ns==0`) | nseas **games≥6** | anchor↔production at 6g; aggregate size = the **−23% played-rookie over-trust** measured above; per-player = production_at_6g − dv·retain[N] (Lombard yr1: 995 vs 802) |
| 2 | proven shed / level-hold | `_nqual≥PROVEN_N=4` (qual = **games≥10** seasons) | below→exposure-ramped+gated lift; at→full tenure/no shrink |
| 3 | M1 fire | **G_ADQ=12** games, gap **TOL_M1=5**, window **WIN=2** | level-lift unlocks in a step at the gate |
| 4 | staleness crush | `el≥onset(2/4/3) & ns≤1` | e→dv·0.25·(…) step at el=onset |
| 5 | mediocre crush | `el≥onset+2 & pr<0.55` | e→dv·0.45·(…) step at par-ratio 0.55 |
| 6 | v7 exposure cB | clip at effs∈{1,4} | band-compression clipped at the ends |
| 7 | hold-band | FLAT_TOL_G KEY10.3/GEN12.0/MR14.0; DOWN_TOL 3.0 | symmetric hold → damps improvers (known §4.2 lever) |
| 8 | **delist gate** | `delisted` | dv·0.02 — the **largest** jump (full value → ~0); intentional (no keeper value) |
| 9 | tenure cap | N=min(el,6) | retain table flattens past yr6 |

Biggest: the delist gate (intentional) and the 6-game cliff (the one being addressed).

## PART C.7 — retain reconcile / provenance / re-derivation
**(i) Wired (`8aed420a`, code line 147, matches handover §3):** RUC .85/.85/.74/.62/.51/.40, KPP .70/.70/.60/.50/.40/.30, nonKPP .50/.50/.42/.35/.28/.20.

**(ii) PROVENANCE — NOT a silent bug; a documented DESIGNED placeholder.** The code header calls these "the deferred-to-PVC shape placeholders (final calibration at the pick-curve step)." Handover §3 (triple-confirmed): *"SITOUT yr3-6 TAIL — DESIGNED/placeholder. Measured only to N5; yr3-6 terminals were 'placeholder… rounded' (source's own words). The designed tail sits ABOVE the measurement for RUC/KPP (RUC yr3-4 +0.24/+0.22, KPP yr4-5 +0.36/+0.22; non-KPP aligned)."* So the wired numbers are a **plateau-then-linear designed shape**, knowingly above the RUC/KPP measurement in the mid-tail, with a **standing action to re-derive on the (lower) measurement, pooling deliberately** at the PVC step. Your memory checks out: you derived a measurement; the wired curve is a designed shape sitting above it; the audit is the note that flagged the gap. Related: the "1.19× uniform sit-out lift" is **parked** in §3 precisely because raising sit-out Yr1 only moves the denominator (matches the Part-A absolute-vs-indexed split above).

**(iii) measured vs designed:** yr1==yr2 identical across all three classes + KPP's clean −0.10/yr = a **designed** flat-then-linear signature, not measurement. The header + handover confirm designed/placeholder for the tail.

**(iv) RE-DERIVATION (realized, with SAMPLE SIZE).** Players with <6 games in ALL of career-yrs 1..N, still listed at yr N; realized = production value (raw_ev, **no anchor**)/draftval if they ever played ≥6g else 0 (washout). This is a raw_ev-scaled PROXY (the wired curve used a daEV/PVC ruler), so read **shape + samples + relative levels**, not drop-in absolutes.
```
cls      N   n(sit-thru-N)  washout%   median   mean    wired
RUC      1        103          27%       0.07    1.10    0.85
RUC      2         72          29%       0.08    1.29    0.85
RUC      3         47          30%       0.10    1.44    0.74
RUC      4         22          45%       0.07    0.85    0.62
RUC      5         13          46%       0.06    0.36    0.51
RUC      6          6          83%       0.00    0.03    0.40
KPP      1        269          28%       0.05    0.38    0.70
KPP      2        168          36%       0.02    0.33    0.70
KPP      3         85          48%       0.01    0.28    0.60
KPP      4         36          56%       0.00    0.17    0.50
KPP      5         18          61%       0.00    0.05    0.40
KPP      6          9          44%       0.01    0.10    0.30
nonKPP   1        767          25%       0.01    0.37    0.50
nonKPP   2        387          34%       0.01    0.26    0.50
nonKPP   3        169          43%       0.00    0.24    0.42
nonKPP   4         60          55%       0.00    0.20    0.35
nonKPP   5         22          45%       0.00    0.22    0.28
nonKPP   6          9          56%       0.00    0.01    0.20
```
Reads:
- **Tail is thin** (N≥4: RUC ≤22, KPP ≤36, nonKPP ≤60; N5–6 single digits for RUC/KPP). Confirms the "measured-only-to-N5, tail = placeholder" note and the recurring "AFL rucks are thin — pool and say so." → the yr3-6 tail is **not well-supported**; re-derive with deliberate pooling.
- **Washout rises with N** (26%→~55–83%): the more years sat out, the more likely to wash out → retention should **decline with N** (shape is directionally right) and probably **steeper** than the gentle wired curve (washout hits 50%+ by N4).
- **RUC is bimodal + thin**: median ~0.1 but mean >1.0 at N1–3 — a handful of elite sit-then-play rucks (Xerri-type) drag the mean up in a ~100-player sample. The **mean is unreliable**; wired RUC 0.85 can't be cleanly justified on this sample → pool/smooth, ceiling DERIVED not picked.

**(v) NON-KPP verdict — 0.50 yr1 is NOT too harsh (data-supported, arguably slightly generous).** nonKPP has the healthiest sample (767 @ N1) and the realized production retention sits **below** 0.50 (mean 0.37, median ~0, 25% washout). So the directive's "nonKPP too harsh?" hypothesis is **not supported** — if anything 0.50 is a touch generous vs realized production. Matches the handover's "non-KPP aligned."

**Net C.7:** the wired curve is a designed placeholder that runs **above** realized production retention for RUC/KPP (KPP clearly; RUC unquantifiable on a thin bimodal sample); nonKPP is aligned/slightly generous. The proper replacement is a **pooled, sample-weighted re-derivation on the PVC ruler at the pick-curve step** (already the standing action) — the +0.1 placeholder is the wrong direction for KPP (it widens the over-statement).

## PART C.8 — data availability for the two curves needing it
- **w-ramp (k-games-in-yr1 → eventual-level reliability): DERIVABLE** from the DB (season games + eventual production are present; bin rookies by yr1 games, measure how well yr1 output predicts eventual level). Not yet done — prototype used the principled convex placeholder. A proper derivation is a bounded next task.
- **within-season penalty-proration shape (round-level debut timing): NOT derivable** — the DB is **season-aggregate** (games + avg per season, no round-by-round). So the live-board `f=round/rounds` proration must be **principled** (Part B), not fit from history.

## PART B — live-board / current-season proration (does NOT move the historical book)
`f = round_current/rounds_total` (round 14 now). Not wired; shapes for your eye.
- **Penalty proration — CONVEX-GENTLE** `retain_eff = 1 − f^k·(1−retain[pos][N])`. Penalty fraction applied at mid-season `f=0.5`: k=1.5→**35%**, k=2→**25%**, k=3→**12.5%** of the full penalty — all well under 50% (protect the player). k=2 is the natural default (¼ of the penalty at half-season).
- **M1 games-gate — CONVEX-HARDER** (a benefit unlock earned harder early): required games = `G_ADQ · f^0.58`. At round 12 of 24 (f=0.5) → 12·0.67 ≈ **8** (~67% of the requirement, > 50%), ramping to 12 by season end. Matches your calibration (need ~8 by round 12). Mirror of the softened penalty.

## DELIVERABLES
- `AFL_RL_WALKFORWARD_book_M1v7_blend-proto.xlsx` — +retain0.1 + w-blend (Yr1 −19%).
- `AFL_RL_WALKFORWARD_book_M1v7_retain0.1only-proto.xlsx` — +retain0.1 only (Yr1 +5.6%, the version that lifts).
- `AFL_RL_WALKFORWARD_book_M1v7-proto.xlsx` — M1+v7 baseline (opportunity-matched summary).
- This report + a per-turn notepad.

## OPEN DECISIONS (your call — nothing baked)
1. **Cliff-only-blend variant?** (blend `ns==0` only, leave ns≥1 at production) — would LIFT Yr1. Build it?
2. Confirm the read: are 6–22g played rookies currently over-valued (blend-all) or fine (cliff-only)?
3. Retain re-derivation: proceed to the **pooled PVC-ruler re-derivation** (replaces the +0.1 placeholder; note +0.1 is wrong-direction for KPP). w-ramp derivation can run alongside.
