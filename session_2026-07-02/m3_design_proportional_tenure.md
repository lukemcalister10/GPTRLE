# M3 — PROPORTIONAL-TENURE/AGE DERIVATION (design + backtest; NOTHING WIRED)
_D4 ASK 5 · 2026-07-02 · evaluated on the BAKE CANDIDATE base (M1+v7 + M2, engine `fb39d88a` / cp `5ac8b162`) · store `644d1254` unchanged._

## IN ONE PARAGRAPH
The D3 split bundle proved the current-season drop is DOMINATED by the age/tenure axis: at the calendar click the engine advances age, tenure, pole-fade and the pricing year a FULL year while the season is ~58% elapsed (young cohort −40.1% age/tenure vs −12.9% decay/exposure; Rozee −17.9% vs −3.7%). M2 (wired at the candidate) prorates the decay clock; M3 is the sibling lever on the age/tenure clock: mid-season, advancement against the expectation curves runs at the elapsed-season fraction, clicking fully at season-complete. The design below derives the lever as a VALUE-SPACE interpolation between the full-click evaluation and a clock-pinned evaluation — the engine's own year-over-year value surface is the expectation curve — scoped exactly like M2 so on-pace players are untouched by construction and completed seasons are byte-exact.

## 1. THE LEVER
```
v_M3(p, Y) = w · ev(p, Y)  +  (1 − w) · ev_pin(p, Y)
  w(p, Y)  = 1 − s(p, Y) · (1 − fE)
  s(p, Y)  = clip(1 − g_Y / 11, 0, 1)          (M2's evidence-replacement scope, same denominator)
  fE       = elapsed-season fraction at the evaluation date (SEASON_PROG = 0.58 at this cut;
             the M2 pace constant 0.545 is the games-pace sibling — both swept in §4)
  ev_pin   = ev at Y with ONLY the age/tenure clock surfaces pinned to Y−1:
             cp._age_asof → −1yr · MA.age → −1yr · PR.tenure → −1yr (floor 1) · _eo's years-since-draft N → −1
             (evidence windows, era adjust, nseas/nqual, the M2'd exposure clock ALL stay at Y — the pin
              moves the CLOCKS only; using plain ev(p, Y−1) as the endpoint would re-prorate the decay
              channel M2 already prorates — the double-count this construction exists to avoid)
```
- **Byte-exact inert at fE=1** (w≡1) and on all completed seasons (the lever keys on Y == the in-progress season, as M2 does). On-pace players (g_Y ≥ 11): s=0 → w=1 → untouched BY CONSTRUCTION.
- **Interpolation = curve advancement:** tenure/pole-fade/age enter the engine through np.interp ramps and integer-keyed par tables; interpolating the two integer-clock evaluations advances the player along the engine's own expectation curve at fraction fE without fractionalising every table key (the wiring-time optimisation can push fractional clocks inward where tables allow).
- **Hook inventory** (the pin patches; identical axis split to D3's proven 2×2 machinery, inverted): `cp._age_asof`, `MA.age`, `PR.tenure` (covers raw_ev's T/et, ev()'s el, staleness onsets), `_eo`'s N (body re-issued with N−1, data window untouched), `_feat_infer`'s explicit ten term. Residual AGE_REF-keyed surfaces enumerated for wiring time: `MA.seasons/los` (brodie/pedDecay display only), `_dev_advance` offset (inert while AGE_REF==BASE_REF).
- **B1 interaction (stated, pre-registered):** the walk-forward book evaluates historical as-of years — all COMPLETED seasons — so M3 is inert on every matrix cell except the in-progress 2026 column; B1 (cohorts 2004-2020) is byte-identical by construction. Verified in §4.
- **B6 interaction (measured, not assumed):** the B6 ramp synth is a 2025-draftee with g26 ∈ 0..14 — its g<11 rungs are IN scope (s>0), so the ramp shape moves under M3; reported in §4. The 0-game anchor rides the sit-out branch (dv·retain, prices before the band) — its el comes from PR.tenure, so the pin touches it coherently.

## 2. SCOPING DERIVATION (finest resolution + smoothing)
Scope carrier candidates, evaluated in §4 at finest resolution (per-game g_Y gradient, kernel-smoothed):
- **s = clip(1 − g_Y/11, 0, 1)** (M2's scope): zero on-pace collateral by construction; smooth phase-out per game banked; one derivation, two levers — the cohesive choice.
- **Universal (s ≡ 1):** rejected — rejuvenates on-pace players (their age also clicked) by (1−fE)·1yr; violates the pre-registered zero-collateral bar.
- **Per-axis split scopes** (age scoped, tenure universal, etc.): measured in the §4 ablation; adopted only if the joint lever fails a bar the split passes.

## 3. PRE-REGISTERED ACCEPTANCE (from the directive, verbatim bars)
| criterion | bar |
|---|---|
| A3 (pre-LTI basis, candidate base) | ≥ 0.80 in combination with M2 |
| on-pace collateral (11-14g, n=288) | ZERO moves >2% |
| B-gates | hold (B1 interaction stated; B5/B6 measured) |
| read-pass panel spot rows | reported |

## 4. BACKTEST NUMBERS
_(filled by `session_2026-07-02/scripts/d4_ask5_m3_backtest.py` — run sequentially after the ASK-4 verification chain)_

_Run: `d4_ask5_m3_backtest.py` → `d4_ask5_m3_out.json` (md5 `7419c3d0`), candidate base `fb39d88a`._

### 4a. Per-axis ablation, named players (base → age-pin → tenure-pin → joint pin → M3 blend @fE=0.58)
| player | g26 | s | base | age-pin | ten-pin | joint pin | M3 | Δ |
|---|---|---|---|---|---|---|---|---|
| Connor Rozee | 2 | 0.82 | 2525 | 3148 (+24.7%) | 2652 (+5.0%) | 3312 (+31.2%) | **2795** | **+10.7%** |
| Josh Ward | 13 | 0.00 | 1329 | 2026 | 1552 | 2258 | 1329 | +0.0% (by construction) |
| Paul Curtis | 13 | 0.00 | 1163 | 1351 | 1274 | 1509 | 1163 | +0.0% |
| Joshua Weddle | 12 | 0.00 | 1409 | 1685 | 1593 | 1895 | 1409 | +0.0% |
| Jack Ginnivan | 13 | 0.00 | 1667 | 2179 | 1679 | 2202 | 1667 | +0.0% |
| Charlie Curnow | 13 | 0.00 | 875 | 1196 | 875 | 1204 | 875 | +0.0% |

The AGE axis dominates the pin (Rozee +24.7% age vs +5.0% tenure), matching the D3 split's attribution. On-pace names show what the click is "worth" (Ward joint pin +70%) and why the scope must exclude them.

### 4b. Acceptance vs the pre-registered bars
| criterion | bar | result | verdict |
|---|---|---|---|
| A3 (pre-LTI, candidate base, with M2) | ≥ 0.80 | 0.658 → **0.728** @fE=0.58 (0.742 @0.50 · 0.734 @0.545 · 0.717 @0.65 · **full-pin ceiling 0.863 @fE→0**) | **FAIL** |
| on-pace collateral (11-14g, n=288) | ZERO >2% | **0 movers** (s=0 by construction, verified) | **PASS** |
| B1 interaction | stated | historical matrix cells evaluate COMPLETED seasons → M3 inert on them by construction; only the in-progress 2026 column moves | **STATED** |
| B5 (signed schedule) | hold | 82 → **63** (lifts 19 development-window offenders above floor) | **IMPROVES** |
| B6 ramp | hold | 0-5g anchor unchanged (745); 6-10g rungs +0.3-0.9%; ≥11g identical; no new dips (the 9→10g seam stays, cliff-blend territory) | **HOLDS** |
| A10 | — | 0.549 untouched (Curnow 13g on-pace, s=0) | as designed |
| read-pass spot rows | reported | Maric +2.8% (9g, s=0.18) · Langdon/Reid/Berry +0.0% (on-pace) · Smillie +0.0% (pre-debut pole) · Will Green +6.2% (young sat-out — the intended direction) | **REPORTED** |

### 4c. VERDICT (honest, mirrors the M2 finding)
M3 passes every safety bar and moves the right players in the right direction, but **the pre-registered A3 ≥ 0.80 is NOT reachable at any honest elapsed fraction on the candidate base** — the sweep is monotone in fE and even fE=0.50 gives 0.742; only the absurd full-pin (fE→0, i.e. pretending the season hasn't started) reaches 0.863. fE was NOT tuned to chase the bar (it is the calendar fraction; tuning it would be curve-fitting the gate).

### 4d. WHERE THE RESIDUAL LIVES — measured, not asserted (`d4_ask5_m3_preoverlay_out.json`, md5 `9c6b409e`)
Same M2 patch + same M3 pin on the PRE-OVERLAY canonical engine (`8aed420a`):
| base | A3 plain | +M2 | +M2+M3 @fE=0.58 | @0.545 | @0.50 |
|---|---|---|---|---|---|
| canonical head (no M1+v7) | 0.692 | 0.706 | **0.780** | 0.786 | 0.794 |
| bake candidate (M1+v7 wired) | — | 0.658 | **0.728** | 0.734 | 0.742 |

**The clock pair M2+M3 lands a whisker under the bar (~0.78-0.79) on the pre-overlay engine; the M1+v7 overlay costs A3 ~0.05** (its v7 compression pushes Rozee −8% — the D2 read-pass flag, now priced). This is a LUKE TENSION to rule on, not a calibration gap: the overlay that repairs A2/A5/A9 works against A3. The remainder of the drop is Rozee's thin-2026 level channel, which is not a clock and which M2/M3 correctly refuse to touch.

### 4e. B1 attribution addendum (candidate book, same-builder control)
Canonical engine + SAME 7147 builder: pooled R=160, **17/17 cohorts** (cohort 2020 yrs4-6 R=109/110/110). Candidate: R=148, **16/17** — cohort 2020 falls to 97/98/95. Builder confound eliminated → **ENGINE-CAUSED by the M1+v7 wiring** (M2 is byte-exact on the completed seasons those cells evaluate). Under the frozen B1 backstop this is a live bake-blocker for the cold audit + Luke's read of the candidate.

## 5. WIRING SPEC (if Luke signs, exactly this and nothing more)
One scoped wrapper at the `ev()` boundary in `_merged_recover.py` (candidate lineage): compute `ev_pin` via the pinned clock surfaces (the §1 hook inventory, made first-class parameters instead of monkeypatches), blend by w. fE recomputed per evaluation date from the fixture calendar (SEASON_PROG); s shares M2's derived denominator. No store change, no `_lvl_wt`, no `_eo` data-window change. Kill-switch: fE=1.
