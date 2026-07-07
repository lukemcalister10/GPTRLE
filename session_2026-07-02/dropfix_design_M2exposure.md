# DROP-FIX DESIGN — prorated exposure clock (M2-exposure) — DERIVED, NOTHING WIRED
_D3 ASK 3 · 2026-07-02 · head `8aed420a` store `644d1254` (unchanged) · Luke reads before any wiring._

## IN ONE PARAGRAPH
The pinned mechanism said the current-season drop bites through the `_exposure` decay clock. The required
first step (the split bundle) shows that clock is only a MINORITY of the drop: most of it is the age/tenure
axis advancing at the calendar click. The lever below is derived, scoped, and passes every safety bar with
ZERO on-pace collateral — but it moves A3 only from 0.69 to 0.71 and cannot touch A10 at all, because
Curnow has played 13 games of 2026 and his halving is his actual 2026 form. The pre-registered acceptance
(A3 ≥ 0.80, A10 ≥ 0.70) is therefore NOT reachable through the decay/exposure channel alone; the numbers
below say precisely where the rest of the gap lives.

## 1. SPLIT BUNDLE (ASK 3a — required first; 2×2 factorial on the no-2026-row player)
E-axis = the year the `_exposure` clock reads; A-axis = the evaluation year (age, tenure, pole fade, pricing).
Cells: [E25,A25]=as-of-2025 · [E26,A26]=as-of-2026 · [E25,A26]=age/tenure-alone · [E26,A25]=decay/exposure-alone.

| player / bucket | n | age/tenure-alone | decay/exposure-alone | interaction | total (channel a) |
|---|---|---|---|---|---|
| Connor Rozee | — | **−17.9%** | −3.7% | +0.2% | −21.3% |
| Josh Ward | — | −22.2% | −6.2% | +0.4% | −28.0% |
| Paul Curtis | — | −23.6% | **+0.5%** | 0.0% | −23.0% |
| Joshua Weddle | — | −12.1% | −3.8% | +0.2% | −15.7% |
| Jack Ginnivan | — | −21.9% | −1.6% | +1.2% | −22.3% |
| young (2–4 yrs) | 14 | **−40.1%** | **−12.9%** | +4.9% | −48.0% |
| mid (5–7 yrs) | 12 | −28.1% | −1.6% | −1.7% | −31.4% |
| old (8+ yrs) | 36 | −26.1% | −0.6% | +0.3% | −26.4% |

**Calibration consequence:** the fix targets ONLY the decay/exposure column. Its ceiling is ~+13% for the
young bucket and ~+4% for Rozee — far short of A3's 11-point ratio gap. This was measured BEFORE the lever
was built, per the directive, and the backtests below land exactly where the split predicted.

## 2. THE LEVER (ASK 3b)
For evaluation year Y with elapsed-season fraction f:
```
_exposure(p,Y) = Σ over seasons yr:  games · w(yr)
  w(yr) = 1.0                                          for yr == Y  (the in-progress season's own games)
        = 0.72 ^ ( max(0, Y−yr−1) + 1 − s·(1−f) )      for yr < Y
  s(p,Y) = clip( 1 − g_Y / 11 , 0, 1 )                 (evidence-replacement scope; g_Y = games banked in Y)
  f = 0.545  (derived below; f ≡ 1 for every completed season)
```
- **Byte-exact reduction to status quo** (the old inert-at-f=1 bar): at f=1 the exponent is `Y−yr`
  identically; VERIFIED byte-exact at f=1 and on all 2025 evaluations.
- **Zero touch of `_lvl_wt`**: only `cp._exposure` changes; `_lvl_wt` keeps its own `_swt` reads.
- **Scope derivation (the model-sensitive region, learned the hard way):** the UNSCOPED lever reproduced
  the D1 on-pace failure — 86/288 on-pace players moved >2% (max 21.5%, James Jordon −21.5% again) — with
  `_lvl_wt` untouched, which CORRECTS D1's attribution: the collateral was the band's non-monotone response
  to the exposure FEATURE, not `_lvl_wt` perturbation. Scope: prorate only the UN-REPLACED fraction of the
  season — a player who has banked ≥11 games (the on-pace floor) has replaced his decayed prior evidence at
  pace and is untouched by construction (s=0); a 2-game player gets s=0.82 of the proration. Smooth in g_Y,
  no hard boundary. The pace-median denominator (12) left one knife-edge mover (McGrath, 11g, +6.1%);
  the on-pace-floor denominator (11) was verified at ZERO movers.
- **f derivation (finest store-derivable resolution + robustness band):** durable players (g25 ≥ 18,
  n=300): median g26 = 12.0 → f = 12/22 = **0.545**; variants: p90/22 = 0.636, max/22 = 0.682,
  med26/med25 = 0.522. A3 is flat across the band (0.701–0.717 over f ∈ [0.4, 0.9]) — the lever's
  shortfall is not an f-tuning problem. f must be recomputed per evaluation date (f→1 as the season
  completes; the lever fades to zero smoothly and re-arms for 2027 at the next year-click).

## 3. BOUNDARY DECLARATION (ASK 3c)
The 9→10g evidence-onset seam (D2 Task D: `_eo` activates at 10 games and caps `Leff`, −220 on the canonical
synth) is **EXCLUDED from this fix and assigned to the cliff-blend directive as seam #2.** Compatibility:
`_eo` keys on RAW game counts, which this lever never touches, so the two are orthogonal by construction
(verified: B6 ramp byte-identical under the fix). The queued cliff-only-blend operates on the `ns==0`
sit-out branch (draftval·retain), which prices before the band and reads no `_exposure`; sat-out players
have no scoring rows so the proration is inert on them either way. Both changes can land in either order
without interacting; the onset-seam smoothing, when designed, should key on the same raw-games axis it
already lives on.

## 4. PRE-REGISTERED ACCEPTANCE — RESULTS (ASK 3d)
| criterion | pre-registered bar | result | verdict |
|---|---|---|---|
| on-pace collateral (11–14g, n=288) | ZERO >2% moves (the `_swt` failure bar) | **0 movers, max 0.00%** | **PASS** |
| historical inertness | byte-exact at f=1 / all complete seasons | byte-exact (verified 2025 + f=1) | **PASS** |
| B-gates hold | B1/B2/B5/B6 | B1 spliced-2026 PASS (peak N4, R160, 17/17) · B2 inert by construction · B5 9→8 · B6 byte-identical | **PASS** |
| A3 (Rozee 2026 ≥ 0.80×2025) | ≥ 0.80 | 0.692 → **0.706** (+2.1% on Rozee) | **FAIL** |
| A10 (Curnow ≥ 0.70) | ≥ 0.70 | 0.511 → **0.511** (untouched) | **FAIL** |
| M1+v7 interaction | must repair the pre-logged A3 compounding | overlay A3 0.642 → 0.659 (does NOT repair) | **FAIL** |

**Where the rest of the gap lives (stated, not designed):**
1. **A3 residual (Rozee):** −17.9% sits on the age/tenure axis — age, tenure, pole fade and pricing year all
   advance a FULL year at the calendar click while the season is 55% elapsed. That is the same asymmetry
   this lever fixes for exposure, one axis over. A sibling lever (prorated age/tenure clock) is the natural
   candidate — it is OUT OF SCOPE here and is a Luke decision, because it changes what "a year older" means
   engine-wide.
2. **A10 (Curnow):** he has banked 13 games of 2026 — the drop is the engine responding to his actual 2026
   form at age 29, not the calendar artifact. Under the SHIP_GATES failure triage this reads DATA-CAUSED
   (escalate to Luke for uphold-or-amend), not engine-caused.
3. The four A2 players (Ward/Curtis/Weddle/Ginnivan, all 12–13 games) are untouched by the fix —
   consistent with ASK 2's finding that the A2 residual is not drop-contaminated.

## 5. WIRING SPEC (if Luke signs, exactly this and nothing more)
One function change in `conditional_prior.py` (`_exposure`), reading f from a single derived constant
(recomputed per evaluation date) and s from the player's own current-season games; no other call site,
no `_lvl_wt`, no `_eo`, no store change. Prototype: `session_2026-07-02/scripts/d3_ask3_final.py`
(zero-collateral verified); full derivation chain in `d3_ask3_fixproto.py` (unscoped, falsified) and
`d3_ask3_scoped.py` (pace-median scope, one knife-edge mover).
