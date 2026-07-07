# DIAGNOSTIC A (rev3, READ-ONLY) — D4/D7/D8 ship-gates reconciliation · player decomposition · sit-out what-if · B6 spec+effects
_2026-07-03 · TARGET = BAKE CANDIDATE v2 (engine `4a134d05` / cp `5ac8b162`, branch `claude/d7-bake-candidate-v2`) · store `644d1254` · pinned env, one load per process, sequential evals · ENGINE UNTOUCHED (repo `engine/` md5 `8aed420a` before and after; runtime copy swapped for measurement and restored, verified)._

Measurement: `session_2026-07-03/scripts/diagA_v2_measure.py` → `diagA_v2_default.json` (v2 as-is), `diagA_v2_expoOff.json` (v2 + `RL_EXPO_F=1`, M2 kill-switch, for attribution). M3 attribution from the saved D7 runs `d7_v2_noM3.json` / `d7_v2_fe1.json`.

---

## ASK 1 — PROVENANCE & RECONCILIATION

### 1a. Sources (all three columns are SAVED REPORT FILES; no recompute was needed to locate them)

| stage | file | engine state measured | commit |
|---|---|---|---|
| D4 | `session_2026-07-02/ship_gates_report_8aed420a.md` (the **CONTROL** board) | canonical head `8aed420a` — no M1/v7/M2/M3/floor | updated at D4, `b6c4003` (branch `claude/d4-bake-candidate-m2-m1v7`); identical file on main today |
| D7 | `session_2026-07-02/ship_gates_report_4a134d05.md` | **BAKE CANDIDATE v2** `4a134d05` | `2e11c6e` (D7 ASK 3), on main via PR #10 |
| D8 | `session_2026-07-03/ship_gates_report_efc15c6c.md` | canonical head + graded-cap **prototype** `efc15c6c` (dial, WIRED NOWHERE) | `d66291a` (D8 ASK 2), branch `claude/staleness-cap-graded-form-4rjowk`, **PR #11 (open, unmerged)** |

Note: a D4 **candidate** board also exists (`ship_gates_report_fb39d88a.md`, commit `0806d90`) with Berry **2197** / Ginnivan **1667** / Travaglia **644** / Moraes **901** — Luke's D4 column is **not** that file; it is the D4-era control board.

### 1b. Reproduced beside Luke's (fresh v2 recompute this session confirms the D7 column exactly)

| player | Luke D4 / D7 / D8 | reproduced D4 (`8aed420a`) | reproduced D7 (`4a134d05`, re-verified live today) | reproduced D8 (`efc15c6c`) | agree? |
|---|---|---|---|---|---|
| Sam Berry | 3473 / 2421 / 3473 | 3473 (A8) | 2421 (A8 + recompute) | 3473 (A8) | YES |
| Jack Ginnivan | 1578 / 1799 / 1578 | 1578 (A5/A9) | 1799 (A5/A9 + recompute) | 1578 (A5/A9) | YES |
| Daniel Annable | 936 / 936 / 936 | 936 (A11) | 936 (A11 + recompute) | 936 (A11) | YES |
| Tobie Travaglia | 601 / 712 / 601 | 601 (A12) | 712 (A12 + recompute) | 601 (A12) | YES |
| Christian Moraes | 876 / 887 / 876 | 876 (A12) | 887 (A12 + recompute) | 876 (A12) | YES |

Luke's table is confirmed digit-for-digit. It is a **cross-state** table, not a cross-time table.

### 1c. What changed at D7, and what "changed back" at D8 — named

**D4→D7 (canonical → v2):** the D7 board measured the bake candidate, which adds four things to canonical: **M1 level-inference + v7-asc age-ascension markdown** (wired into the candidate lineage at `0806d90`, carried into v2 at `c16b970` with the cB band-compression term deleted), **M2-exposure** (`EXPO_F=0.545`, in `conditional_prior.py`), **M3 proportional-tenure blend** (`M3_FE=0.58`), and the **pricing floor**. Canonical `8aed420a` carries NONE of these (source-diff verified). Per-player owners (measured):

| player | Δ canonical→v2 | M1+v7-asc | M2 (measured, EXPO_F=1 toggle) | M3 (measured, noM3/fE=1 runs) | floor |
|---|---|---|---|---|---|
| Berry | −1052 | ≈ −1046 (of which cB-deletion gave back +224 vs the D4 candidate) | −6 | 0 | 0 |
| Ginnivan | +221 | ≈ +231 | −10 | 0 | 0 |
| Annable | 0 | 0 — sit-out anchor reads only draftval×retain; immune to every candidate term | 0 | 0 | 0 |
| Travaglia | +111 | ≈ 0 | +43 | +68 | 0 (floor 596 < 712, not binding) |
| Moraes | +11 | ≈ +6 | +31 | −26 | 0 |

(Berry is above the M2 evidence threshold by construction — 13 games in 2026 ≥ EXPO_DEN 11 → s=0; his move is the v7-asc age markdown at age ~24 with M1.)

**D7→D8: NOTHING changed back.** No commit reverted anything. The D8 board was run at a **different state** — canonical head + the graded-cap dial prototype (`efc15c6c`) — which contains none of the candidate terms; the dial moves only its 24/807 staleness-population players (none of these five), so the board reproduces canonical numbers, i.e. Luke's D4 column.

**Check-first suspects ruled out:** staleness-cap Form A (state `a9e1c14b`, D7 ASK 4) leaves all five at canonical values (saved report); per-group `REPL_DROP` is untouched in v2 (`price6` unchanged; the uniform −3 in `_inferM1` is a *new* v2 term, not a revert); the only recency/exposure change (M2) is attributed above.

### 1d. Classification — with evidence

**No revert occurred; none of (a)/(b)/(c) as defined.** The appearance of a rollback is a **REPORT-STATE MISMATCH**: three boards measuring three different engine states were read as one timeline.
- Not (a): no rejected fix was removed from any lineage (v2 diff vs canonical contains every D7-endorsed term; the only deletion is cB, which was Luke-ruled at D7 and is *inside* the D7 column, not between D7 and D8).
- Not (b): nothing lost — `origin/claude/d7-bake-candidate-v2` tip verified **this session** at engine `4a134d05` / cp `5ac8b162`.
- Not (c): the D8 report is not stale — it is a fresh, deliberate measurement of head+gradedfix, labelled in its own first line ("head efc15c6c"), produced by D8 ASK 2 whose commit says WIRED NOWHERE; PR #11 remains open/unmerged.

Hard stop therefore **not** triggered (it binds on (b)/(c) only). **Process gap flagged:** gates boards shown to Luke should carry a CANDIDATE vs CONTROL banner so cross-stage tables can't silently mix lineages.

### 1e. What v2 carries

**v2 (`4a134d05`) carries the D7 numbers**: Berry 2421 · Ginnivan 1799 · Annable 936 · Travaglia 712 · Moraes 887 (all re-verified live this session). The D4/D8 numbers are the canonical/control lineage.

---

## ASK 2 — DECOMPOSITION AT v2 (one table; components sum to final)

Name guard applied — every surname hit listed in `diagA_v2_default.json → name_resolution`; matched rows below (other hits: Joe/Jarrod/Oscar Berry, Ollie Lord, Isaac Cumming — none intended).

| player (matched) | pick | cohort | 2026 g / career g | base engine ev (production path) | sit-out haircut? | stalled-cap? | M3-blend Δ | floor applied? | final |
|---|---|---|---|---|---|---|---|---|---|
| Cooper Lord | 9 | 2024 | 3 / 27 | 1040 | N | **Y** (el 3, ns 1 → 0.25×dv on clicked clock; M3 blend softens) net **−646** | inside cap net | N (floor 108) | **394** |
| Sam Berry | 29 | 2020 | 13 / 89 | 2421 | N | N | 0 | N (floor 54) | **2421** |
| Jack Ginnivan | 9 | 2020 | 13 / 103 | 1799 | N | N | 0 | N (floor 28) | **1799** |
| Daniel Annable | 6 | 2025 | 1 / 1 | 1571 (bypassed) | **Y**: dv 1873 × 0.50 = 936 (−40.4% vs base) | — | — | N (floor 843) | **936** |
| Sam Cumming | 7 | 2025 | 7 / 7 | 1994 | N | N | −12 | N (floor 807) | **1982** |
| Tobie Travaglia | 8 | 2024 | 0 / 12 | 644 | N (ns=1: 2025 season qualifies) | N (el 2 < onset 3) | +68 | N (floor 596 — 116 below final) | **712** |
| Christian Moraes | 38 | 2024 | 7 / 21 | 913 | N | N | −26 | N (floor 190) | **887** |

Sums: Berry/Ginnivan final = base exactly; Annable = 1873×0.50; Cumming 1994−12; Travaglia 644+68; Moraes 913−26; Lord = M3 blend of capped click-eval (≈77 = 0.25×dv 308) and uncapped pinned eval → 394. Floor bound **nobody** in this set.

---

## ASK 3 — THE SIT-OUT HAIRCUT AS CODED (quoted from `_merged_recover.py`, identical in canonical and v2)

```python
SITOUT_RETAIN={'RUC':[0.85,0.85,0.74,0.62,0.51,0.40],'KPP':[0.70,0.70,0.60,0.50,0.40,0.30],'nonKPP':[0.50,0.50,0.42,0.35,0.28,0.20]}
def _sitout_cls(pos): return 'RUC' if pos=='RUC' else ('KPP' if pos in ('KEY_FWD','KEY_DEF') else 'nonKPP')
...
def nseas(p,Y=2026): return sum(1 for x in p['scoring'] if x['games']>=6 and x['year']<=Y)
...
    if ns==0:   # SIT-OUT (never played >=6g through Y, still listed): position-scaled retention anchor from Yr1
        N=min(max(el,1),6)
        return round(dv*SITOUT_RETAIN[_sitout_cls(pos)][N-1])
```

**In one sentence:** a still-listed player who has never had a season of ≥6 games is priced at a flat, position-classed fraction of his own draft value that steps down only with years-on-list — 50% for a year-1/2 non-key player — with **no** conditioning on games played this season (0 games and 5 games price identically) and **no** conditioning on season progress (R14/24 is never read).
**Fires on Annable:** YES (ns=0, el=1, nonKPP → 1873×0.50=936 — and why he is flat across every engine state). **Fires on Travaglia:** NO (ns=1 — his 2025 season qualifies; and no stalled/mediocre branch fires either: el=2 < onset 3 — his 712 is base+M3).

---

## ASK 4 — ILLUSTRATIVE WHAT-IF (scratch only; ENGINE UNTOUCHED; **NOT a proposed final**)

Forms: **(a)** games-smoothed — linear from the sit-out anchor at 0 games to the engine's own 6-game value (clone with 2026 games set to 6): `v = anchor + (g/6)·(v6g − anchor)`. **(b)** R14/24-prorated tenure — retention read at fractional elapsed tenure `el−1+14/24` on the same curve.

| player (haircut fires) | g26 | current | (a) games-smoothed | (b) R14/24-prorated |
|---|---|---|---|---|
| Daniel Annable | 1 | 936 | **1010** (+74) | 936 (±0 — the yr1→yr2 retention step is flat 0.50→0.50, so proration is a no-op in year 1) |
| (Oscar Berry — only other firer among resolved hits) | 0 | 216 | n/a (0 games) | 216 (±0) |

Annable's cliff is ahead of him: at his 6th game he jumps 936 → **1381** (+445) under current code.

---

## ASK 5 — BASE vs OVERLAY: Berry and Lord

**Sam Berry (v2 = 2421; Luke's 3473 is the canonical lineage):** 100% **base engine ev at both states** — floor N (not in the 54 saves), sit-out/stalled N. The height is a **BASE-VALUATION property**: comparable careers (MID, cohort 2019–21, best level ≈102, 78–107 career games) price high too — **Will Day 2823**, **Hayden Young 2869**, **Jason Horne-Francis 4199** (Errol Gulden 5299 sits a production level above). v2's 2421 is at/below the bottom of that comp band; the D4/D8 3473 sits inside it.

**Cooper Lord (v2 = 394):** not high — the outlier LOW. Base production path 1040 is crushed by the **stalled-cap** (el≥3, ns≤1 → 0.25×dv=77 on the clicked clock), M3's pinned blend recovers it to 394; floor (108) irrelevant. Comparables (pick 7–9 recent MIDs, best level ≈60): Windsor 1703, Cumming 1982, Carroll 990, Retschko 744 — Lord is far below all of them. His price is an **overlay artifact**, exactly the population the open PR #11 dial addresses (dial value 655 — still below comps). Consistent with Luke's D8 round-2 eyeball.

---

## ASK 6 — B6 GAMES-SEAM: SPEC + EFFECTS

### 6a. Verbatim from the FROZEN SHIP_GATES.md (commit `92315af`, file md5 `a55921f6` — verified this session)

> B6. No hard lines: value continuous across the games ramp (no step at the 6-game
>     seam) AND monotone in evidence — more games at the same scoring rate is never
>     worth less.

**Plain sentence:** it checks that a player's value climbs smoothly as he accumulates games — no jackpot at any game count, and never a case where playing more makes him worth less.

### 6b. Where the seam is and what code makes it

**At 6 games in a season.** `nseas()` counts only seasons with `games>=6`; `ev()`'s `if ns==0:` early-return dumps everyone below that into the sit-out anchor. It is a hard **retention-step boundary (cliff)** — not a blend boundary. Ramp at v2 (gate's synthetic pick-10 MID, avg 85):

| games (2026) | 0 | 3 | 4 | 5 | **6** | 7 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|
| value | 745 | 745 | 745 | 745 | **3296** | 3379 | 3551 | 3325 |

Step at the seam: **+2551 in one game**. Secondary monotonicity dips (adjacent band machinery, not the sit-out gate): 7→8 −3, 9→10 −226, 13→14 −5.

### 6c. Who it distorts (scratch estimates vs a locally-smooth curve = form (a) above)

**54 active players sit under the seam** (never a ≥6-game season, 1–5 games in 2026); aggregate under-crediting ≈ **+4,096** board points. Worst: **Louis Emmett +740** (518 now vs 1258 smooth), **Jack Ison +257**, **Jayden Nguyen +230**, **Jai Murray +215**, **Charlie Banfield +212**; **Daniel Annable +74** (and rising each game until the +445 jackpot at game 6). **22 players sit just over the seam** (sole qualifying season is the 2026 partial) and get full production pricing: Dyson Sharp 1166, Isaac Kako 1214, **Sam Cumming 1982**. The A11 pair **Cumming 1982 vs Annable 936 straddles the seam exactly** (7 games vs 1 game). **Travaglia is NOT seam-distorted** (ns=1 from his 2025 season; 0 games in 2026) — his A12 problem is base-valuation + recency, **adjacent** machinery. Overlap with ASK 3: **SAME machinery** — the sit-out branch *is* the seam.

### 6d. Why B6 reads RED — measured vs bar (v2 board line, `ship_gates_report_4a134d05.md`)

| clause (declared bar) | measured at v2 | verdict |
|---|---|---|
| no single 0→6 step > 50% of total rise T (≤1275) | step 5→6 = **+2551** (=100% of T) | RED |
| cumulative rise by 3 games ≥ 25% of T (≥638) | **+0** | RED |
| monotone in evidence (no dips) | dips −3 / −226 / −5 (7→8, 9→10, 13→14) | RED |

---

## ACCEPTANCE / HYGIENE
- Engine untouched: `git status` clean before commit; repo `engine/rl_after/_merged_recover.py` md5 `8aed420a` unchanged; runtime copy restored to `8aed420a`/`346cffbb` and re-verified. What-ifs computed on in-memory clones only.
- Dial (PR #11 graded cap) confirmed ABSENT from the v2 engine (`grep graded` = 0 hits in `4a134d05`/`5ac8b162`) and from every engine file on main (`engine/prototypes/staleness_graded_cap.py` exists only on the PR #11 branch).
- Sequential: three engine processes run one after another, one load each.

## BURN REPORT
Estimated 45–75 min; actual ≈ 40 min wall (3 engine loads ≈ 6 min compute). No blowout.
