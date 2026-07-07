# BOARD LAYERS PACK — D3 — for Luke's ONE-price ruling
_2026-07-02 · head `8aed420a` store `644d1254` · scratch evaluations only, nothing changed._

## 1a. Which price do the gates check?
`ship_gates_check.py` prices **the engine** (`_merged_recover.ev()`) — it loads the head engine and asks it
directly for every gate number. **The board you trade from is priced by a different function**: the export
(`rl_export.py`) runs the older `rl_model.py` chain and then overwrites every value with the cont.27
"production router" (`wire_redesign` → `TR.production_value`); the JS in the app displays that number
verbatim (the old in-browser pricing chain is dead fallback code). The only gate that ever looks at the
board is B4, and only to check the file bytes.

## 1b. Every board-path layer, toggled off one at a time
("% of board moved" = sum of absolute value changes / total board value when the layer is switched off.)

| layer | plain description | LIVE/DEAD | players moved | % of board | biggest movers (value with layer OFF) | recorded rationale |
|---|---|---|---|---|---|---|
| the WIRE overwrite | the entire cont.27 router that replaced the legacy board pricing | **LIVE — it IS the board** | 800/805 | 31.6% | Uwland 834→3274 (+293%), Newcombe 3668→1906 (−48%), Max King 420→1979 | cont.27 board switch, 2026-06-26 |
| REPL −3 | prices everyone against a slightly weaker "free replacement player" | LIVE | 802/805 | 19.6% | Logan Morris −22%, Ginbey −20%, O'Sullivan −20% | cont.25 dial; Luke reverted to uniform −3 on 2026-06-28 |
| tail restoration | restores the star-outcome ceiling for high-pick pre-debut MID/KEY_FWD/GEN_DEF | LIVE | 29 | 1.4% | Smillie −52%, DeMattia −66%, Annable −37% | cont.27–28, empirical p90 under-dispersion |
| RUC draft pool | prices pre-debut rucks off the scorer pool shape at ruck level | LIVE | 19 | 1.1% | Carr +318%, Uhr-Henry +281% if off (pool holds them DOWN) | cont.27, fixes the pk20-30 ruck inversion |
| RUCK TAX 0.25 | taxes the speculative (non-production) part of established rucks | **LIVE on the board** | 16 | 0.3% | Madden +16%, McAndrew +12%, L. Jackson +4% if off | cont.24-25, Luke-approved, rucks-only |
| pedigree soft floor | stops young high-pedigree strugglers falling below a fading draft floor | LIVE | 35 | 0.1% | Tunstill −64%, Goater −60% if off | cont.25, Luke's spec form |
| Brodie ×0.5 | halves one specific role-risk profile | LIVE | exactly 1 (Will Brodie) | 0.1% | Brodie 508→1015 if off | ported 2026-06-21 |
| lens tilt | now/balanced/future slider | LIVE code, **inert** at the shipped 'bal' lens (=1.0 for all) | 0 | 0% | — | cont.21 |
| surv, P, cvx, vP1/vM1, pedDecay, losd, brodieBase, CAPT/TILT constants, JS PVC/SCALE rebuild | the legacy in-browser pricing chain and its exported knobs | **DEAD** (JS uses the baked `v`; these fire only in a fallback that never runs) | 0 | 0% | — | RELEASE note at `_engine_block_v23.js:97` |

**RUCK_TAX reconciled:** the ledger's "DEAD relic" entry is true **for the engine path only** (`ev()` never
calls the function that applies it). The board path DOES apply it to 16 established rucks (0.3% of board
value). Both statements were path-relative; the ledger conflated the two paths.

## 1c. INTERIM RULER — same gates, both prices
| gate | ENGINE path (what gates report) | BOARD path (what you trade on) | agree? |
|---|---|---|---|
| A1 Duursma>Uwland | PASS 4179 vs 1781 | PASS 4030 vs 834 | yes |
| A2 Curtis ≥ 0.90×Ward (amended) | FAIL ratio 0.652 (1162/1782) | FAIL ratio 0.667 (923/1384) | yes (both red) |
| A3 Rozee ≥0.80 | FAIL 0.69 | FAIL 0.68 | yes |
| A4 Reid top-40 | **PASS rank 32** | **FAIL rank 47** | **NO** |
| A5 floors (Ginnivan/Bowey/Blakey) | FAIL (Ginnivan 1578 < 1600) | FAIL (Ginnivan 1461) | yes |
| A6 ruck cohort | PASS | PASS | yes |
| A8 Berry > 2×Tsatas | PASS 3473 vs 2166 | PASS 2199 vs 1136 | yes |
| A9 Ginnivan > Ward | **FAIL 1578 vs 1782** | **PASS 1461 vs 1384** | **NO** |
| A10 Curnow ≥0.70 | FAIL 0.51 | FAIL 0.68 (near-miss) | yes (magnitude differs a lot) |
| A11 playing beats sitting | **PASS both pairs** | **FAIL (Cumming 1567 < Annable 1719)** | **NO** |
| A12 sitting not over-punished | FAIL (Travaglia leg) | FAIL (both legs) | yes |
| B5 crater guard | FAIL 9 offenders | FAIL 18 offenders (different names) | no (different lists) |
| B6 games-ramp | FAIL (flat-then-step +2518 at 6g; 9→10g dip) | FAIL (dip at 0→1g; big step 2→3g) | no (different shapes) |

**Aggregate gap (805 matched players):** board total sits **−7.6%** under the engine; the median player
differs by **24.9%**; **57% of players differ by more than 20%**; rank agreement (Spearman) 0.90.
Three gates flip PASS↔FAIL depending on which price you believe. Your presumption on record — ONE price,
at-rest board == engine, layers promoted-or-deleted — now has its evidence table.

## 1d. 2866 provenance
CONFIRMED — 2866 is Rozee-under-proration in the decay-proration prototype report
(`BUILD_report_2026-07-01_decay-proration-prototype.md` line 17: 2679→2866, +7%); live baseline 2679
separately confirmed by D2 Task F.

## 1e. What board are you actually trading from?
The shipped bundle in the workspace (`rl_build/rl_app_data.json`, md5 `b8f9e998`) is the board the app was
built from, and it is **two generations behind today's tree on the export axis**: its pick curve tops out
at PVC[1]=3883, which means it was cut BEFORE the 2026-06-21 "pick 1 = 3000" anchor that every current
regeneration enforces; it carries 785 players to today's 805 and a cohort payload two-thirds the current
size. No git-recoverable store or engine reproduces it (ASK 4 below) — your live board is an orphaned
artifact of an earlier export-code + store state.

## ASK 4 — B4 archaeology (canonical engine × 3 seed stores; no cause label — nothing reproduced the ship)
| cut | artifact md5 | SCALE | intakePickSum | PVC[1] | PVC[8] | active | cohort rows |
|---|---|---|---|---|---|---|---|
| canonical `e0ac9c37` × reconciled `644d1254` | `1898ead7` | 4.48537 | 58403 | 3000 | 1704 | 805 | 1978 |
| canonical × pre_stage0 `644d1254` | `1898ead7` (identical) | 4.48537 | 58403 | 3000 | 1704 | 805 | 1978 |
| canonical × stage0 `91a3de6b` | `c16e1024` | 4.48588 | 58410 | 3000 | 1705 | 805 | 1978 |
| **SHIPPED** | **`b8f9e998`** | **6.53492** | **97973** | **3883** | **2596** | **785** | **1303** |

The store axis moves SCALE in the 5th decimal; the `_merged_recover` engine axis is provably not on the
export dependency graph (nothing on the export path imports it — verified). Every fingerprint that differs
is export-CODE-generation-sized, and the PVC[1]=3883 signature dates the shipped cut to before the
2026-06-21 pick-1 anchor. Cause stays UNLABELED (no cut reproduced the artifact); the git history simply
does not contain the code+store state that built your live board.

## G3-CLEAN — the year-1 "crater" was contamination (proposal only; you name the numbers)
Re-derived value/draftval percentile track, LISTED players, single-year resolution:

| years in system | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8+ |
|---|---|---|---|---|---|---|---|---|
| p5, ALL entrants (D2 baseline) | .16 | .27 | .25 | .23 | .19 | .07 | .08 | .01–.09 |
| p5, NATIONAL DRAFT only | **.50** | .50 | .25 | .23 | .19 | .07 | .07 | .01–.09 |
| p5, excl. MSD/SSP | .50 | .50 | .25 | .23 | .20 | .07 | .08 | .01–.09 |
| p5, MSD/SSP only | .14 | .17 | .29 | .22 | .14 | — | — | — |

**The yr1 .16-below-yr2-.27 anomaly disappears on the clean population** — it was entirely the MSD/SSP
cohort (whose draft-value denominator is the deep-tail 308). Guard-shape skeleton per your stated instinct,
with the empirical track alongside so you can name the numbers:

| years | 1 | 2 | 3 | 4 | 5 | 6 | 7+ |
|---|---|---|---|---|---|---|---|
| empirical clean p5 (smoothed) | .50 | .42 | .31 | .23 | .15 | .10 | ≤.07 |
| skeleton (HIGH yr1 → 0.25× by yr4 → veteran tail) | [.45–.50] | [.35–.40] | [.28–.30] | 0.25 | 0.15 | 0.10 | 0.05 |

Nothing wired; the flat 0.25× stays provisional on the board. The MSD/SSP exclusion is your ruling.

## Q4 — the nine B5 offenders: all MSD/SSP/RD entrants (entry path drives BOTH their board value and the B5 denominator)
| player | entry | entry pick | pick-equivalent used | draftval | drafted |
|---|---|---|---|---|---|
| Jack Watkins | Rookie Draft | 3 | 61 | 308 | 2025 |
| Flynn Perez | SSP | 35 | 94 | 308 | 2025 |
| Zac Banch | Mid-Season Draft | 2 | 59 | 308 | 2025 |
| Flynn Young | Mid-Season Draft | 4 | 59 | 308 | 2025 |
| Saad El-Hawli | Mid-Season Draft | 13 | 59 | 308 | 2024 |
| Lachlan Blakiston | Mid-Season Draft | 13 | 59 | 308 | 2025 |
| Jack Hutchinson | Mid-Season Draft | 3 | 59 | 308 | 2024 |
| Mani Liddy | Mid-Season Draft | 16 | 59 | 308 | 2025 |
| Roan Steele | Mid-Season Draft | 8 | 59 | 308 | 2025 |

The mechanism pick-equivalent (MSD→59, SSP→94, RD pick 3→61) feeds the live valuation (pedigree/pole/band
inputs) AND sets draftval = PVC[equivalent] = 308 — one shared object, not two.
