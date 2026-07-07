# D7 ASK 3 — FULL VERIFICATION AT BAKE CANDIDATE v2 (the Luke-ruled configuration)
_2026-07-02 · **BAKE CANDIDATE v2: engine `4a134d05` · cp `5ac8b162` · store `644d1254` · band `34faa865`** · branch `claude/d7-bake-candidate-v2` (assembly commit `c16b970`) · post-merge main `d0acfc08` · supersedes candidate `fb39d88a` (D4) · all engine evals sequential · v2 config = M1 + v7-asc (cB DELETED) + M2 (f=0.545) + M3 (fE=0.58, kill-switch RL_M3_FE=1) + pricing floor (variant A flat .05 tail)._

## Restore-verify at v2 — exactly the axes that must move moved
| axis | canonical expect | at v2 | verdict |
|---|---|---|---|
| head md5 | 8aed420a | **4a134d05** | moved BY DESIGN (the v2 assembly) |
| store md5 | 644d1254 | 644d1254 | PASS unchanged |
| band md5 | 34faa865 | 34faa865 | PASS unchanged |
| Maric ev(2026) | 1409 | 1407 | moved (M1+asc; cB-off + M3 at 9g nets him back to ~head) |
| Langdon ev(2026) | 593 | 575 | moved (== D4 candidate 575: his motion is asc/M1-side, cB-free) |
| harnesses present | 4/4 | 4/4 | PASS |
| panel tail | Smillie 896 / Green 741 | Smillie 896 / **Green 787** | Green +6.2% = the M3 design's predicted young-sat-out lift, to the point |

## Panel (10 rows) at v2 — canonical expect vs v2, with the v2@fE=1 column attributing M3
| player | canonical | v2 | v2 @ fE=1 | note |
|---|---|---|---|---|
| Nick Daicos | 7059 | 7069 | 7069 | +0.1% (asc rounding-level) |
| Marcus Bontempelli | 3101 | 3109 | 3109 | +0.3% |
| Harry Sheezel | 7287 | 7207 | 7207 | −1.1% (M1/asc side; on-pace, M3-inert) |
| Max Gawn | 2126 | 2137 | 2137 | +0.5% |
| Harley Reid | 3523 | 3565 | 3565 | +1.2% (cB deletion recovers his band) |
| Josh Ward | 1782 | 1653 | 1653 | −7.2% (M1 no-lift at gap 3.0<5 + asc; was 1329 at D4 candidate — cB deletion gives back +324) |
| Darcy Moore | 177 | 201 | 178 | +23 = M3 (g26<11, the clock pin); fE=1 returns him to ~head |
| Taylor Goad | 545 | 576 | 545 | +31 = M3 sat-out lift (intended direction) |
| Josh Smillie | 896 | 896 | 896 | pre-debut pole — inert across the whole config |
| Will Green | 741 | 787 | 741 | +6.2% = M3 (the design's named spot row, landed exactly) |

## Named rows (the directive's list) — measured at v2
| row | expectation (directive) | measured at v2 | verdict |
|---|---|---|---|
| **Rozee A3** | vs amended 0.75; supervisor range 0.74–0.78 TREAT AS UNKNOWN | **0.7307** (2917/3992) | **FAIL — red by 0.019.** M3 owns +0.072 of it (fE=1: 0.6591); cB deletion ≈ +0.001; the supervisor range was optimistic — the measured ratio sits BELOW the amended bar |
| Tsatas | expect < 1083 | **1140** | **MISS — above Luke's preferred 1083.** M3-caused: at fE=1 he is 979 (the D5 candidate number); the clock pin un-ages his pedigree (g26=0 → s=1, full blend). Fades to 979 as the season completes (fE→1). A8 still PASSES: Berry 2421 / Tsatas 1140 = 2.12x ≥ 2 |
| Curtis/Ward (A2) | expect ~0.822 red | **0.822** (1358/1653) | CONFIRMED exactly (= D6 fresh minus-cB measure); red vs 0.90 BY RULING — Luke: "we can look at Curtis down the line" |
| Curnow A10 | vs 0.50 | **0.509** (888/1745) | PASS — knife-edge. cB deletion lifted 2025 (1593→1745) more than 2026 (875→888); headroom shrank 0.549→0.509 |
| Ward M1-TOL | knife-edge statement | gap = **+3.0** vs TOL_M1=5 → no M1 lift | CONFIRMED (= D4; one strong fortnight flips it) |
| Gothard | STILL ~317 + floor → 355 (cap fix is ASK 4, NOT in v2) | prefloor **317**, final **355** | CONFIRMED — staleness cap binds at v2; floor lifts 0.28×1269 |

## M3 re-registered acceptance at this config (Luke's amended bar)
| criterion | bar | measured | verdict |
|---|---|---|---|
| A3 (pre-LTI, v2 config) | ≥ 0.75 | **0.7307** | **FAIL** (honest miss — fE=0.58 is the calendar, NOT tuned) |
| on-pace collateral (11–14g, n=288) | ZERO >2% | **0 movers** | PASS |
| byte-exact inert at fE=1 | required | **0/807 diffs** vs the physically-stripped build (`f4b35501`) | PASS |
| M3 scope | only g26<11 moves | 327 movers, **all g26<11** (Perez/Keane flags were offline-map artifacts — re-typed re-entry records; real g26 = 5 and 0) | PASS |
| B-gates | hold | B1 PASS 156.2 pk4 · B2 PASS 0.0 · B6 red-as-known (one new −3pt micro-dip at 7g = M3 blend seam noise, cliff-blend territory) | HOLD |

## Floor (ASK 1b re-verify at v2, printed on the board per the amended B5)
Pure lower bound on the wired run (n=807): **0 lowered · 0 non-ND moved** · **54 saves, aggregate +1684** (top: Ugle-Hagan +113 [raw 157 at v2 — asc pushes him lower than head's 213, floor holds 270], Dow +99, O'Meara +88, Wiltshire +73, Stone +72; Gothard +38). Full table: `ship_gates_report_4a134d05.md` (auto-printed every board run). Note: `round()` semantics from the signed prototype put 33/54 saved values ≤0.5 below the exact float floor line — rounding, not breach (same as D6's 51-vs-50 note).

## FULL GATES BOARD at v2 vs the D4 candidate board (11P/6F) — every delta attributed
| gate | D4 candidate (fb39d88a) | v2 (4a134d05) | delta → attribution |
|---|---|---|---|
| A1 | PASS 4183/1831 | PASS 4183/1829 | nil (rounding) |
| A2 | FAIL 0.875 | FAIL **0.822** | −0.053 = **cB deletion** (cB squeezed Ward −19.6% > Curtis −14.4%; both richer, ratio falls) — red BY RULING (Luke: Curtis down the line) |
| A3 | FAIL 0.66 vs 0.80 | FAIL **0.7307 vs 0.75** | +0.072 = **M3** · +0.001 = cB deletion · bar 0.80→0.75 = **Luke's A3 amendment** — still red by 0.019 |
| A4 | PASS rank 28 | PASS rank 29 | Reid 3481→3565 (**cB deletion**); one rank = neighbours moved more |
| A5 | PASS 1667/2643/3236 | PASS 1799/2969/3287 | all richer = **cB deletion** (the improver-slash gate breathes) |
| A6 | PASS 314 vs 474 | PASS 314 vs 519 | MID kernel richer = **cB deletion**; RUC side unmoved |
| A7 | PASS | PASS | nil |
| A8 | PASS 2.24x | PASS **2.12x** | Berry 2197→2421 (**cB deletion**) · Tsatas 979→1140 (**M3** — flagged above) |
| A9 | PASS 1667>1329 | PASS 1799>1653 | both richer (**cB deletion**); margin narrows (Ward recovers more) |
| A10 | PASS 0.55 | PASS **0.509** | −0.04 = **cB deletion** (2025 denominator lifts more than 2026) — knife-edge vs Luke's 0.50 |
| A11 | PASS | PASS 1642/982 · 1982/936 | nil material |
| A12 | FAIL (Travaglia leg) | FAIL (Travaglia leg) | Travaglia 644→712 (**M3** sat-out lift) vs Moraes 901→887 — gap −257→−175, direction right, still red |
| A13 | PENDING lineball 2/2 | PENDING lineball 2/2 | Wardlaw 2835→3033, Ashcroft 3166→3270 (cB deletion) — both still lineball |
| A14 | PENDING lineball 3/3 | PENDING lineball 2/3 | **Burgoyne 1858→2092 leaves ±20%** (cB deletion) — advisory only, PVC-staged |
| A15 | STRUCK | STRUCK | — |
| B1 | PASS 147.6 pk4 (16/17 backstop era) | PASS **156.2 pk4** | +8.6 = **cB deletion** (D5: minus-cB 156.6; M3 historically inert by construction; floor −0.4 index effect) · **2020 row back above 100 everywhere** (100/113/115/105/107/107) — Luke's eyeball channel |
| B2 | PASS 0.0 | PASS 0.0 | re-run fresh at v2 |
| B3 | PENDING | PENDING | — |
| B4 | FAIL 4d0584a3 vs b8f9e998 | FAIL 08d91566 vs b8f9e998 | expected — export re-cut is bake-gated (ONE new board on Luke's word) |
| B5 | FAIL 82 offenders | **FEATURE** 54 saves +1684, bound 0/0 | **Luke's B5 amendment** — alarm retired, floor wired, saves table = the new alarm surface |
| B6 | FAIL (flat-then-step; dips 9:−221, 13:−5) | FAIL (flat-then-step; dips **7:−3**, 9:−226, 13:−5) | structural seam UNCHANGED (cliff-blend directive); the 7g −3pt micro-dip is new = M3 blend seam noise (s differs per rung) |
| C1/C2 | PENDING | PENDING | — |
| **VERDICT** | 11P / 6F / 5PEND / 1STRUCK | **11P / 5F / 1FEATURE / 5PEND / 1STRUCK** | the B5 FAIL became the FEATURE line |

## new-B1 average + per-cohort (from the v2 matrix `s4_matrix_v2_4a134d05.json`)
Average row (the gated row): d1 100.0 · d2 131.9 · d3 143.2 · **d4 156.2 (peak)** · d5 153.4 · d6 144.9 · d7 127.7 — PASS (peak in 4-6, >100, path_ok; vs 147.6 at D4 candidate / 160.5 at head / 156.6 at minus-cB). Full 17-cohort pipe table: `ship_gates_report_4a134d05.md` (printed every board run). 2020 cohort at v2: 100/113/115/105/107/107 — above yr1 everywhere, peak d3 (the shocking-draft markdown is now the KEPT term's mediocrity-concentrated shape, not cB's indiscriminate squeeze).

## Walk-forward book
Rebuilt at v2: matrix `data/s4_matrix_v2_4a134d05.json` (7147 builder, 2649 players) · book `docs/AFL_RL_WALKFORWARD_book_v2_4a134d05.xlsx` (27 sheets, md5 `c5a7adc8`, dot-free stem).
