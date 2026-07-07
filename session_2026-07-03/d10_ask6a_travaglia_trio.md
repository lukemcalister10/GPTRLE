# D10 ASK 6a — TRAVAGLIA COMPARISON DECOMPOSITION (diagnosis only — NOTHING wired; Luke rules on the finding)

**STATES: CONTROL `8aed420a` · PREVIOUS v2 `4a134d05` · CURRENT v2.1 `c8051893`. All three resolved by ID (name|cohort|pick). Book-Yr1 = pinned matrix anchor column; board-Current = matrix `cur` (CONTROL/v2) and the live candidate eval (CURRENT).**

## Finals, three-column (book-Yr1 → board-Current)

| player (ID) | pedigree | Yr1 output | CONTROL Yr1→cur | v2 Yr1→cur | v2.1 Yr1→cur |
|---|---|---|---|---|---|
| Tobie Travaglia\|2024\|8 (GEN_DEF, age 20) | pick 8 | 2025: 12g @ 39.7 | 601 → 601 | 601 → 712 | 601 → **712** |
| Angus Clarke\|2024\|39 (GEN_DEF, age 20) | pick 39 | 2025: 14g @ 59.0 | 575 → 575 | 575 → 675 | 575 → **675** |
| Jacob Farrow\|2025\|10 (GEN_DEF, age 19) | pick 10 | 2026 (live): 12g @ 71.0 | (Yr1 in progress) → 1641 | → 1642 | → **1644** |

D10 moves none of them materially (all ns=1; Farrow +2 via prorated ramps with an inert pole term) — this channel is NOT the games-ramp seam.

## Component decomposition at CURRENT v2.1 (fresh probe, d10_p7_trio.py; v2 cross-check: DIAG-A decomposed Travaglia 644 base + 68 M3 = 712 — matches)

| component | Travaglia | Clarke | Farrow |
|---|---|---|---|
| demonstrated level (lvl_wt, era-wtd) | 39.7 (2025, decayed) | 59.0 (2025, decayed) | **71.0 (live 2026)** |
| reliability-shrunk level into the band | 55.8 | 59.1 | 62.2 |
| recency-wtd exposure | 10.0 (12 g × 0.72 decay) | 11.7 | **12.0 (no decay)** |
| band price pr | **404** | 618 | **1738** |
| pedigree pole po (weight w) | 1125 (w=0.347: tfade 0.76 · expgate 0.46) | 765 (w=0.404) | 1104 (w=0.940 but **inert: po < pr**) |
| recover(perf/par) | 0.812 (39.7 vs par 61.2) | 1.000 | 1.000 |
| raw → ×iso → e_full | 607 → **644** | 677 → **660** | 1738 → **1644** |
| M3 clock blend | +68 → 712 | +15 → 675 | 0 (on-pace) |
| floor | not binding | not binding | not binding |

## THE CHANNEL, NAMED

**Performance-weighting of demonstrated output, compounded by recency/exposure decay — not pedigree, not a cohort-year effect.** The band prices what a player actually scored: Farrow's 71-per-game LIVE season prices at pr=1738 while Travaglia's 39.7-per-game season from a year ago — era-weighted, recency-decayed 0.72×, and 35% below his positional par — prices at pr=404. Pedigree (pick) survives only in the pole term, and by year 2 the pole is throttled three ways (tenure-fade 0.76, exposure gate 0.46, recover 0.81): Travaglia's pick-8 pole is worth ~+240 net vs Clarke's pick-39 ~+60 — a ~+180 pedigree edge, swamped by Clarke's +19-points-per-game output edge (~+210 of band) and Farrow's +31 (~+1,300 of band). Cohort-year effects are ruled out by the same-cohort control: Clarke (2024, pick 39) prices ABOVE Travaglia (2024, pick 8) on output alone at every candidate state.

In plain terms: the engine has watched Travaglia play 12 games below replacement level and is pricing that evidence; Farrow is near 2× because he is CURRENTLY producing at 71 while Travaglia's weak season is both weak and aging. If Luke wants pedigree to hold up longer against one thin weak season (A12's Travaglia>Moraes is the standing red on this family), the lever is the pole throttle (tfade/expgate) or the recover() clip — a ruling, not a D10 wire.
