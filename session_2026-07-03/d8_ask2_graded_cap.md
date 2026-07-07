# D8 ASK 2 — STALENESS-CAP GRADED FORM (derivation + verification; WIRED NOWHERE — M3 discipline)
_2026-07-03 · designed and measured at CANONICAL HEAD `8aed420a` / store `644d1254` / band `34faa865` ·
scratch identity head+gradedfix = `efc15c6c` (two-anchor patch, `engine/prototypes/staleness_graded_cap.py`) ·
NOT in BAKE CANDIDATE v2 (`4a134d05` untouched on its branch; the parallel cold audit is unaffected) ·
all engine evals sequential, run in a SELF-CONTAINED scratch deployment — the shared workspace engine was
never modified (md5 `8aed420a` verified before and after)._

## Why round 2 (Luke's verbatim, 2026-07-03 — the governing finding; also in SYMPTOM_REGISTER.md family 1)
> The two cap fix is odd, because someone like Cleary is far too low when he triggers it and probably too
> high when he doesn't. That Hardeman doesn't get rescued is a challenging one for me. And looking at
> Cooper Lord - he's another in the Cleary boat but worse - he shouldn't be so low now, but the idea of him
> being over 1000 if it didn't catch him is a bit crazy to me.

READ: the binary Form A (caught → 0.25×draftval · exempt → full ev) is wrong at the margins in BOTH
directions. This round derives the GRADED replacement. Form A's endorsement is WITHHELD (rulings ledger R3);
its gap=0 structural piece is RETAINED inside the graded form (Luke-endorsed via McAndrew, R4, and Gothard).

## THE GRADED FORM (one plain sentence)
Where the cap fires, the player's price now slides from the ghost floor toward his full engine price in
proportion to how often players with the same staleness and the same live-output quality went on to
re-realize their stale season's level — measured, not assumed: a current-season qualifying season is fully
trusted (cap exempt), no live games stays at the floor, and in between the release fraction is read off two
measured re-realization curves (last-season-stale vs longer-stale) over current output vs replacement.

```
e = min(e, cap + grade·(e − cap))            cap = dv·frac (the existing ghost floor — UNCHANGED)
grade = 1                      if gap = 0    (sole qualifying season IS season Y — cannot have vanished; D7 structural piece)
      = 0                      if g_Y = 0    (no live output this season — ghost anchor)
      = G_gapclass(q)          otherwise     (q = era-adjusted season-Y avg / REPL[pos]; classes: gap=1 · gap≥2 pooled)

q knots      0.40   0.45   0.50   0.55   0.60   0.65   0.70   0.75   0.80    (flat outside; piecewise linear)
G_gap=1      0.258  0.258  0.258  0.308  0.362  0.421  0.493  0.570  0.595
G_gap≥2      0.000  0.003  0.003  0.043  0.088  0.134  0.180  0.201  0.204
```

## DERIVATION BASIS (every number measured; zero invented constants)
- **Harvest** (`scripts/d8_ask2_harvest.py` → `d8_harvest_cells.json` md5 `097f4e85`): all 532 historical
  (player, Y) cells Y=2008–2022 where the stalled branch would fire (ns(Y)=1, el≥onset, listed at Y per the
  standing LISTED-WINDOW rule, CHANGELOG 2026-06-29; `_double_count` credit phantoms excluded). 285 gap=0 /
  136 gap=1 / 111 gap≥2; 460 unique players. Outcome = re-realization of the stale season's era-adjusted
  level over the next 3 seasons: v = min(fwd-peak/qual-level, 1) (the cap at 1 is structural — beyond-full
  realization cannot earn more than full release). Cells Y≤2022 only, so every outcome window is complete.
- **Evidence axis SELECTED BY THE DATA, not assumed:** the directive's example product (games × output/REPL)
  was tested and LOST to pure quality q — tau(q,v)=+0.234 (p=0.0001) vs tau(g·q)=+0.124; games volume has
  NO independent signal within 1–5 games (tau=+0.038, p=0.56; ≈0 at fixed-q halves); q beats g·q in 100%
  and √g·q in 96% of 2,000 player-clustered bootstrap resamples. Volume enters only structurally: the first
  live game arms the grade; the 6th game makes the season qualifying and the player graduates out. A rate
  axis is also season-progress-invariant — it largely dissolves the R14 partial-season seam.
- **Gap carries signal beyond q** (gap=1 realizes 0.579 vs gap≥2 0.316 at matched live evidence E∈[1.5,10))
  → two curves. Gap≥2 POOLED DELIBERATELY (gap 3/4/5+ singly thin: n=29/11/4). Stale-season quality was
  tested as a third axis and EXCLUDED (signal only in the high-E slice, none below; the band already prices
  the qual level directly).
- **Smoothing:** Gaussian kernel over q, bandwidth widened until eff-n≥35 (the D5 standing rule — stated,
  not tuned) + isotonic projection (monotone-in-evidence is structural: more live output cannot mean less
  trust).
- **Normalization = the two Luke-ruled boundary populations:** grade = clip((R_c(q) − Rg)/(Rtop − Rg), 0, 1)
  with Rg = 0.2120 (true-ghost baseline: the gap≥2 curve at q→0+ — the population Luke keeps at the floor)
  and Rtop = 0.8024 (the gap=0 curve's top plateau — the McAndrew/Gothard full-trust region, R4).
- **Rejected alternatives (computed, shown, not chosen):** (i) the q-matched normalization
  (grade vs R₀(q) at the same q) — principled but NON-MONOTONE at finite sample (grade fell 0.664→0.595 as
  q rose 0.80→1.00); (ii) per-class baselines (each curve zeroed at its own low end) — fails Luke's
  Hardeman read (gap=1's base premium over true ghosts is real signal: 0.364 vs 0.212).
- **Robustness:** outcome=survival and outcome=raw-ratio reproduce the same curve shape (Cleary-profile
  grade 0.57/0.75 vs 0.595 primary); Y≤2023 and Y≤2024 windows reproduce it (0.582/0.594); player-cluster
  bootstrap 90% CI — Cleary/Lord-profile [0.43, 0.75], Hardeman-profile [0.05, 0.43], Brain-profile
  [0.04, 0.31]: every anchor verdict below holds across the entire CI.
- **Declared biases:** the g_Y=0 historical bins are survivorship-biased UP (listing windows are inferred,
  min-window survivors dominate) — irrelevant to pricing because the ghost anchor pins grade(g_Y=0)=0; see
  the returner finding below.

## PRE-REGISTERED ACCEPTANCE — SIX ANCHORS (all measured at head+gradedfix `efc15c6c`, engine-applied)
| # | anchor | measured | verdict |
|---|---|---|---|
| 1 | Gothard stays ~1790 | **1790** — his exact uncapped price (gap=0, gr=1; no shaving) | **PASS** |
| 2 | true ghosts at/near floor | every zero-live-output row BYTE-IDENTICAL: Dowling 109 · Goater 129 · Clarke 98 · Archer 62 · Hall 136 · Collard 152 · McMahon 191 · K.Smith 90 | **PASS** |
| 3 | Cleary materially above cap AND materially below full | 154 → **523** (3.4× his cap, 68% of 775 — 252 below full) | **PASS** |
| 4 | Cooper Lord above cap, WELL below 1000 | 77 → **655** (62% of his 1050; grade 0.59 on 3g @ 0.96×REPL) | **PASS** |
| 5 | Hardeman PARTIALLY rescued | 154 → **257** (above floor, 47% of his 552; gap=1 base grade 0.26 — his rescue is RECENCY, his 2g @ 25.5 live output earns no more) | **PASS** |
| 6 | McAndrew at full ~1408 | **1408** = his full uncapped price (gap=0, gr=1) — WITH CAVEAT below | **PASS** |
| — | zero movement outside the 38 | full 807-sweep diff vs head: **24 movers, 24/24 in the fire population, 0 outside**; all lifts non-negative | **PASS** |
| — | all gates incl. new-B1 hold | board at `efc15c6c`: no gate that passed at head fails — fails = the head's own A2/A3/A5/A9/A12/B4/B6 set, values byte-equal to head on untouched rows; **new-B1 PASS avg peak N=4 @169** (head 160.5, Form A 169.2); B2 re-run at the graded engine: PASS, median |IS-WF| leakage 0.0 %-pts (tol 0.5), GOOD>BUST separation holds all 5 positions | **PASS** |

**McANDREW CAVEAT (found this session, ASK-3 adjacent):** the fire-population "Lachlan McAndrew (MSD
credit)" row is the deliberate `_double_count` CREDIT PHANTOM (backward pool credit only; excluded from the
805 board by `active()`). His REAL record was re-entered at year 2024 → tenure 2 < onset → the cap never
fires on it → he prices 1062 at head, fix-inert. So "McAndrew 99→1408" is real in the 807 sweep but reaches
no board; the anchor is satisfied mechanically and the DIRECTION (strong current output → full release) is
what R4 endorses. Same structure for Mark Keane (IRE credit) — not in the fire population (ns=2).

## INTERACTIONS — PROVEN, NOT ASSERTED
**(i) Floor feature (v2/v3 wiring):** application order = graded cap INSIDE ev(), then ev_final =
max(ev, floor_yrs×draftval) at the boundary (the v2 order). This order is LOAD-BEARING: reversed
(floor-then-cap), the cap would clip floored values back down (Hall 152→136, Collard 170→152 — the floor
defeated). At the v2 order the floor lifts exactly **4 post-grade rows**, all grade-0 or non-binding:
Wiltshire 44→86 · Hall 136→152 · Collard 152→170 · Stone 71→97. **No double-lift exists:** every row with
grade>0 already prices above its ND floor, so grade-lift and floor-lift are disjoint by measurement
(38/38 enumerated, `scripts/d8_population_graded.json` + the schedule).
**(ii) Games-ramp / cliff-blend seam:** the grade axis is a RATE (avg vs replacement), invariant to season
progress; games touch only the two structural gates. B6's synthetic ramp at head+gradedfix is BYTE-IDENTICAL
to head (dips 9:−220 · 13:−5, the known head shape; no new dip at any rung) — the graded rule adds no seam
artifact. The g26 gates DO share M2/M3's seam variable (their scope s=clip(1−g26/11,0,1)): at a future v3
the graded release hands back an e that M2/M3 have already lifted for g26<11 rows — composition is monotone
in g26 (both effects rise with games; no cancellation), but its MAGNITUDE at the 7g rung where v2 shows the
−3pt B6 micro-dip is UNMEASURED (v2 untouched this directive) → **h-M3-blend-seam-noise stays OPEN and now
explicitly covers the graded-cap×M3 composition; measure at v3 assembly.**
**(iii) Residual cliff, stated:** the 6th-game graduation cliff SHRINKS but does not vanish — Cleary at
game 6 goes 523 → ~775+ (ns=2, branch exempt); under Form A it was 154 → 775+. And the first live game
arms the gap=1 base grade (Hall 136 → ~328 the day he plays) — the 0-game→1-game step is the LTI seam
(below), kept out of the cap by design.

## NEW FINDING → HYPOTHESIS REGISTER: h-gap1-zero-games-returners (NEW, OPEN — LTI-shaped)
The harvested zero-live-games cells realize HIGH (gap=1 g_Y=0: v=0.683, n=25 unique; gap≥2 g_Y=0: 0.554 —
both ABOVE the played-1-2-games bins ~0.37): "did not play" ≠ "played badly" — this bin is the
missed-season-then-returned population (the Gibcus/Rozee family 2 shape), survivorship-biased up by the
inferred listing windows. The graded cap deliberately does NOT price it (Luke's design axis is live output;
grade(g_Y=0)=0 keeps Hall/Collard/McMahon/K.Smith at the floor). The signal is real, measured, and QUEUED
to the LTI workstream — the register entry cites these numbers as its first calibration evidence.

## BOARD AT HEAD+GRADEDFIX (full print: `ship_gates_report_efc15c6c.md`)
PASS A1/A4/A6/A7/A8/A10/A11 + B1 (169 pk4, path_ok, 2020 cohort printed ungated 100/112/130/114/110/110) ·
FAIL = the head's own A2 (0.652)/A3 (0.69 — the head basis, pre-M2/M3)/A5/A9/A12/B4/B6 set · B5
FEATURE-ABSENT at head (informational 45, alarm retired) · B2 PASS 0.0 leakage (re-run at the graded engine; harness tail errored cosmetically after the full table printed — parsed by the B2 gate logic verbatim) · A13/A14/B3/C1/C2
PENDING · A15 STRUCK. Nothing green at head went red; nothing red went green except by design (B1 lift).

## ARTIFACTS (filename · md5)
`scripts/d8_ask2_harvest.py` · harvest `scripts/d8_harvest_cells.json` `097f4e85` · analysis
`scripts/d8_ask2_analyze.py` + `scripts/d8_grade_curve.json` `4ab7e84d` · fit `scripts/d8_ask2_fit.py` +
`scripts/d8_grade_final.json` `2fb989f7` · prototype `engine/prototypes/staleness_graded_cap.py` · verify
`scripts/d8_ask2_verify.py` · sweep `scripts/d8_gradedfix_sweep.json` `af942ca2` · population detail
`scripts/d8_population_graded.json` `9a1ce39f` · 38-row table `scripts/d8_table38.md` · graded matrix
`data/s4_matrix_gradedfix_efc15c6c.json` · board report `ship_gates_report_efc15c6c.md`.

## THE 38-PLAYER TABLE (ALL fire-population rows; Luke eyeballs the whole interior — duplicated in the PR body)
Bold = moves vs current. Form-A = the rejected binary switch (gap=0 released, everything else capped).

| player | club | qual season | gap | 2026 live (g @ avg · q=avg/REPL) | grade | CURRENT capped | Form-A (rejected) | GRADED |
|---|---|---|---|---|---|---|---|---|
| Phoenix Gothard | GWS | 2026:13g@70.2 | 0 | 13g @ 70.2 · q=0.99 | 1.00 | 317 | 1790 | **1790** |
| Lachlan McAndrew (MSD credit) | Sydney | 2026:13g@87.1 | 0 | 13g @ 87.1 · q=1.11 | 1.00 | 99 | 1408 | **1408** |
| Jai Serong | Hawthorn | 2026:13g@76.7 | 0 | 13g @ 76.7 · q=0.98 | 1.00 | 72 | 1029 | **1029** |
| Oscar Steene | Collingwood | 2026:8g@51.6 | 0 | 8g @ 51.6 · q=0.66 | 1.00 | 123 | 818 | **818** |
| Max Heath | St Kilda | 2026:6g@52.8 | 0 | 6g @ 52.8 · q=0.67 | 1.00 | 99 | 666 | **666** |
| Will Edwards | Sydney | 2026:8g@51.7 | 0 | 8g @ 51.7 · q=0.76 | 1.00 | 123 | 296 | **296** |
| James Tunstill | Brisbane | 2026:7g@47.0 | 0 | 7g @ 47.0 · q=0.59 | 1.00 | 102 | 220 | **220** |
| Oliver Wiltshire | Geelong | 2026:6g@41.8 | 0 | 6g @ 41.8 · q=0.59 | 1.00 | 44 | 44 | 44 |
| Cooper Lord | Carlton | 2025:21g@59.9 | 1 | 3g @ 76.7 · q=0.96 | 0.59 | 77 | 77 | **655** |
| Clay Hall | West Coast | 2025:13g@66.8 | 1 | 0g — no live output | 0.00 | 136 | 136 | 136 |
| Caiden Cleary | Sydney | 2025:12g@45.0 | 1 | 5g @ 60.8 · q=0.86 | 0.59 | 154 | 154 | **523** |
| Jedd Busslinger | Western Bulldogs | 2025:7g@44.1 | 1 | 4g @ 74.5 · q=1.09 | 0.59 | 481 | 481 | **573** |
| Will Lorenz | Port Adelaide | 2025:6g@58.3 | 1 | 1g @ 52.0 · q=0.65 | 0.42 | 77 | 77 | **308** |
| Riley Hardeman | North Melbourne | 2025:17g@54.8 | 1 | 2g @ 25.5 · q=0.33 | 0.26 | 154 | 154 | **257** |
| Cooper Harvey | North Melbourne | 2025:7g@45.9 | 1 | 1g @ 73.0 · q=1.03 | 0.59 | 73 | 73 | **273** |
| Isaac Keeler | St Kilda | 2025:11g@40.3 | 1 | 2g @ 39.5 · q=0.58 | 0.34 | 187 | 187 | **256** |
| Ashton Moir | Carlton | 2025:9g@45.4 | 1 | 2g @ 46.0 · q=0.65 | 0.42 | 151 | 151 | **248** |
| Angus Hastie | St Kilda | 2025:9g@35.9 | 1 | 2g @ 51.0 · q=0.65 | 0.42 | 149 | 149 | **245** |
| Sandy Brock | Gold Coast | 2025:14g@62.5 | 1 | 4g @ 44.5 · q=0.65 | 0.42 | 111 | 111 | **197** |
| Tom Hanily | Sydney | 2025:8g@34.4 | 1 | 2g @ 42.5 · q=0.60 | 0.36 | 77 | 77 | **160** |
| Lance Collard | St Kilda | 2025:12g@30.9 | 1 | 0g — no live output | 0.00 | 152 | 152 | 152 |
| Will McLachlan | Brisbane | 2025:6g@23.3 | 1 | 1g @ 28.0 · q=0.40 | 0.26 | 77 | 77 | **125** |
| Liam McMahon | Collingwood | 2025:7g@42.1 | 1 | 0g — no live output | 0.00 | 191 | 191 | 191 |
| Kaleb Smith | Richmond | 2025:8g@40.0 | 1 | 0g — no live output | 0.00 | 90 | 90 | 90 |
| Bailey Macdonald | Hawthorn | 2025:6g@25.2 | 1 | 3g @ 53.0 · q=0.68 | 0.46 | 86 | 86 | **126** |
| Liam O'Connell | St Kilda | 2025:7g@35.7 | 1 | 5g @ 48.2 · q=0.62 | 0.38 | 77 | 77 | **90** |
| Luke Cleary | Western Bulldogs | 2025:16g@57.7 | 1 | 1g @ 10.0 · q=0.13 | 0.26 | 62 | 62 | **67** |
| Conor Stone | GWS | 2025:7g@48.3 | 1 | 3g @ 53.0 · q=0.68 | 0.46 | 71 | 71 | 71 |
| Billy Dowling | Adelaide | 2024:9g@66.8 | 2 | 0g — no live output | 0.00 | 109 | 109 | 109 |
| Shadeau Brain | Brisbane | 2024:9g@46.4 | 2 | 2g @ 54.5 · q=0.70 | 0.18 | 69 | 69 | **104** |
| Harvey Harrison | Collingwood | 2024:12g@46.6 | 2 | 2g @ 44.5 · q=0.63 | 0.11 | 74 | 74 | **86** |
| Andy Moniz-Wakefield | Melbourne | 2024:6g@53.7 | 2 | 2g @ 29.5 · q=0.38 | 0.00 | 62 | 62 | 62 |
| Harvey Gallagher | Western Bulldogs | 2024:20g@45.4 | 2 | 3g @ 38.0 · q=0.48 | 0.00 | 120 | 120 | 120 |
| Jackson Archer | North Melbourne | 2024:15g@46.0 | 2 | 0g — no live output | 0.00 | 62 | 62 | 62 |
| Darragh Joyce | St Kilda | 2024:6g@51.0 | 2 | 3g @ 54.0 · q=0.79 | 0.20 | 22 | 22 | 22 |
| Josh Goater | North Melbourne | 2023:10g@56.2 | 3 | 0g — no live output | 0.00 | 129 | 129 | 129 |
| Judson Clarke | Richmond | 2023:13g@43.3 | 3 | 0g — no live output | 0.00 | 98 | 98 | 98 |
| Josh Gibcus | Richmond | 2022:18g@53.7 | 4 | 1g @ 56.0 · q=0.82 | 0.20 | 323 | 323 | 323 |
