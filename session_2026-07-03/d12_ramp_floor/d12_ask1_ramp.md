# D12 ASK 1 — CONCAVE PENALTY RAMP (Luke-signed OPTION A)  — CANDIDATE v2.2

**STATE: CONTROL = canonical `8aed420a` · PREVIOUS = v2.1 `c8051893` · CURRENT = v2.2 (engine `05d38c65` after ASK 1 only).**

## Ruling executed (verbatim)
Luke 2026-07-03: _"I'm not sure that the proration should be strictly linear... especially when it comes as a penalty, it should be slightly more generous as the sample is smaller... it will be 100% after 24 games, as it should... something like 33-40% at half way."_ → **OPTION A signed: penalty fraction = (season progress)^1.5.**

## The change (one line, penalty path only)
`sitout_ev()` in `_merged_recover.py`: the within-season proration of the sit-out retention `R` was **linear** in season progress; it is now **concave**:

```
-  tau = max(0, Y-debutyr) + (fe          if Y>=debutyr else 0)   # D10 linear
+  tau = max(0, Y-debutyr) + (fe**1.5     if Y>=debutyr else 0)   # D12 concave (Luke OPTION A)
   R   = interp(tau, [0..6], [1.0]+R_SIT[class])
```
`R` is the retained fraction of the **no-games** anchor `R·V0` (the penalty). Completed seasons stay full (integer knots); only the in-progress season accrues concavely. Retained value at year 1: `R_applied = 1 − (1 − R_full)·τ'`, `τ' = (R/24)^1.5`. **Diff vs v2.1 = this one line + its comment.** The reward-side M1 `G_ADQ` gate and the `lam` evidence blend (`min(gy/fe,6)` on the next line) are **byte-untouched** (verified by diff).

## Penalty fraction τ' printed at R6/R12/R18/R24

| Round | season prog R/24 | BEFORE (linear) | AFTER (R/24)^1.5 | Δ |
|---|---|---|---|---|
| R6  | 0.2500 | 0.2500 | **0.1250** | −0.1250 |
| R12 | 0.5000 | 0.5000 | **0.3536** | −0.1464 |
| R18 | 0.7500 | 0.7500 | **0.6495** | −0.1005 |
| R24 | 1.0000 | 1.0000 | **1.0000** | 0.0000 |

Halfway = **0.354** (inside Luke's "33–40%"); full at R24 = **1.000** ("100% after 24 games"). Operative cut fE=0.58 (engine's R14/24 approx): linear 0.580 → concave **0.442** (directive's 0.445 uses 14/24=0.5833; engine cut is 0.58).

## Constraint re-assert (Luke, standing): a single 2026 game never weighs less than a single 2025 game — HOLDS
The ramp change prorates the **penalty** only: `τ'` scales the `R` retention multiplier applied to the no-games anchor `V0`. Games enter value **only** through the untouched `lam` blend (line: `lam=interp(min(gy/fe,6),…)`) and the untouched production price `e_full`; a 2026 game and a 2025 game are weighted by the recency/exposure machinery in `conditional_prior` (RL_RECENCY_DECAY=0.72), which the ramp change does not touch. Recency already weights 2026 **above** 2025 (0.72^(Y−yr)); prorating the penalty cannot invert that. **No game-weight is touched.**

## Monotonicity RE-PROOF across the old 6-game seam (whole 0..14g ramp, B6 methodology)

| synth | ramp(0..14g) | dips | 0→6 rise T | rise-by-3g | step>50%T | verdict |
|---|---|---|---|---|---|---|
| MID pk10 | 1139,1469,1785,2482,3103,3190,3238,3291,3305,3314,3367,3435,3523,3563,3592 | NONE | +2099 | +1343 (≥525) | NONE | **PASS** |
| KEY_FWD pk10 | 671,822,1436,2770,4184,4286,4349,4402,4435,4460,4514,4571,4618,4628,4650 | NONE | +3678 | +2099 (≥920) | NONE | **PASS** |

The concave change lifts only the sit-out segment (g0–3, where ns==0): MID g0 1019→1139, g1 1397→1469, g2 1730→1785, g3 2464→2482; g≥4 (production path, ns==1) is **byte-identical to v2.1**. Continuity into the production segment is preserved because `lam→1` at the prorated graduation bar kills the `R·V0` term regardless of `R`. **No dip; B6 seam green at v2.2.**

## Sit-out anchor moves v2.1 → v2.2 (played-some players unaffected — ns≥1 skips this path)

| player | pos | g26 | V0 | draftval | prefloor v2.1 → v2.2 | EV v2.1 → v2.2 |
|---|---|---|---|---|---|---|
| Dylan Patterson | GEN_DEF | 0 | 1136 | 1965 | 760 → **849** | 884 → 884 (floor 0.45×dv=884 still binds until ASK 2) |
| Daniel Annable | MID | 1 | 1859 | 1873 | 1326 → **1414** | 1326 → **1414** (floor non-binding) |
| Xavier Taylor | GEN_DEF | 2 | 860 | 1380 | 662 → **693** | 662 → **693** |

Cumming/Emmett/Ison/Lord/Berry/Tsatas all have nseas_pro≥1 → they never enter `sitout_ev` → **unmoved by ASK 1** (Cumming 1948, Emmett 1338, Ison 538, Lord 414, Berry 2421, Tsatas 1140).

## Revisit hook (ledger)
PVC-era derivation may later replace the **shape** (t^1.5) from partial-season snapshots — recorded as an open revisit, not a block.
