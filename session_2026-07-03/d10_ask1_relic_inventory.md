# D10 ASK 1 — RELIC INVENTORY: every penalty path on the old-PVC basis + the live start-value anchor

_As-of 2026-07-03 · base = CANDIDATE v2.1 branch (`claude/games-ramp-engine-change-qt7824`), engine at merge = v2 `4a134d05` / cp `5ac8b162` · canonical CONTROL `8aed420a` untouched. "old PVC" = `MA.PVC` (3000-down pick-value curve, `RL_PICK1=3000`); `draftval(p) = MA.PVC[min(effpk,KMAX)]` (mr:211)._

## 1. The purge set — penalty/haircut/staleness/games paths whose VALUE BASIS is old-PVC draftval

| # | path | constant(s) | what it computes | liveness | D10 action |
|---|---|---|---|---|---|
| 1 | `engine/rl_after/_merged_recover.py:225-236` | `SITOUT_RETAIN` RUC .85/.85/.74/.62/.51/.40 · KPP .70/.70/.60/.50/.40/.30 · nonKPP .50/.50/.42/.35/.28/.20 | SIT-OUT anchor: `ns==0` (never ≥6g through Y, still listed) → **`dv × retain[cls][years-on-list]` replaces the whole valuation** — scores, games-this-season, season progress all discarded; position adjustment erased (flat class fraction of raw PVC) | LIVE — fires on 49/64 of the 2025 cohort at R14; the B6 seam | **DELETED** — replaced by the derived V0-anchored treatment (ASK 2); obituary in BOARD_LAYERS_OBITUARY.md |
| 2 | `mr:237-240` | 0.25 · decay `max(0.4, 1-0.10(el-onset))` · keyruc 1.6 | STALLED cap: `el>=onset & ns<=1` → `e=min(e, dv×frac)` | LIVE (the 38-population family; D8 graded dial supersedes it at v3, unwired) | **RE-ANCHORED** dv → V0 |
| 3 | `mr:241-243` | 0.45 · decay `max(0.3, 1-0.08(el-onset))` · keyruc 1.5 | MEDIOCRE cap: `el>=onset+2 & pr<0.55` → `e=min(e, dv×frac)`; `pr = bestlvl/par` (bestlvl carries the unprorated ≥6g bar) | LIVE | **RE-ANCHORED** dv → V0; bestlvl bar prorated |
| 4 | `mr:230` | 0.02 | DELIST gate: `delisted(p)` → `0.02 × dv` (scrap value) | LIVE | **RE-ANCHORED** 0.02 → 0.02 × V0 |
| 5 | `mr:280-291` | FLOOR_YRS .45/.35/.28/.21/.13/.09 + .05 tail | PRICING FLOOR `max(ev, floor_yrs × dv)` | LIVE — **NOT a penalty**: Luke-signed B5 pricing feature (variant A, D7) | **KEPT on dv basis** (Luke's signed schedule is dv-denominated; re-anchoring it is a Luke ruling, flagged to supervisor) |
| 6 | `engine/prototypes/staleness_graded_cap.py` | cap = dv·frac baseline | D8 graded dial (Luke-endorsed values, version entry deferred) | **WIRED NOWHERE** (grep re-verified this session: no graded/dial reference in live engine) | untouched; NOTE: at v3 wiring it inherits whatever basis the stalled cap then has (V0) — supervisor flag |
| 7 | `engine/rl_after/rl_model.py:645-676` | `unpl_eq = PVC[pick]·decu·debut_factor`; pedestal `PVC[pick]·relative·decay` | OLD board `value()` path (pre ONE-price) | SUPERSEDED SURFACE — no live caller in the ev() lineage (relic audit 2026-06-30 confirmed; ONE-price ruling deleted the board path) | untouched (delete-candidate batch, Luke sign-off pending) |
| 8 | `rl_model.py` `realized_cv`/`_natcv`/`pe()` | PVC-inverted curves | export panel / display rulers | display-only, not penalty paths | untouched |

Games bars feeding the family (prorated under ASK 2c): `nseas` ≥6g (mr:215) · `_nqual` ≥10g (mr:37) · `LEVEL_RAMP=14` (cp:77) · `POLE_RAMP=22` (mr:26) · `bestlvl` ≥6g filter (mr:212-214). `G_ADQ=12` (M1 recent-adequacy window, proven players only) is deliberately NOT prorated — outside the directive's 6/10/14/22 enumeration; noted.

## 2. The LIVE start-value assignment — the sole legitimate anchor going forward

**V0(p) = raw_ev(p, draft-year) × iso_corr(pos, effpk)** — the conditional-prior band priced at zero evidence (features: position one-hot, log effective pick, exposure 0, tenure 0, draft age), times the per-position isotonic pick guard. The pedigree-pole term self-gates to zero at zero exposure (`expgate = min(1, exposure/POLE_RAMP) = 0`), so V0 is pure band price × iso. It is pick+position-adjusted and Y-invariant per player (cached).

Verified this session (scratch v2 deploy, engine 4a134d05 — the Dean-below/Robey-above property):

| player (ID key) | pos | PVC[pick] | V0 | V0/PVC |
|---|---|---|---|---|
| Harry Dean\|2025\|3 | KEY_DEF | 2248 | 1237 | **0.55 (below)** |
| Sullivan Robey\|2025\|9 | MID | 1603 | 1882 | **1.17 (above)** |
| Daniel Annable\|2025\|6 | MID | 1873 | 1859 | 0.99 |
| Sam Cumming\|2025\|7 | MID | 1793 | 1864 | 1.04 |
| Dylan Patterson\|2025\|5 | GEN_DEF | 1965 | 1136 | 0.58 |
| Jacob Farrow\|2025\|10 | GEN_DEF | 1490 | 860 | 0.58 |
| Xavier Taylor\|2025\|11 | GEN_DEF | 1380 | 860 | 0.62 |
| Louis Emmett\|2025\|27 | RUC | 609 | 1536 | **2.52 — RUC start values run hot vs PVC; flagged to the eyeball channel** |

MIDs price above their pick value, GEN_DEFs below, KEYs pick-dependent — the position adjustment is exactly the one Luke described. EYEBALL FLAG: the zero-evidence band prices RUCs ~2.5× their PVC pick value (scarcity prior); nothing in this directive changes V0 itself — it is the engine's own live assignment.

## 3. Grep proof target (acceptance)

After the ASK 2 wiring: `grep -n "draftval\|PVC" engine/rl_after/_merged_recover.py` must show draftval/PVC referenced ONLY in: `draftval()`'s own definition, the delist/stalled/mediocre lines via `_v0` (no dv), and the Luke-signed FLOOR block (declared exception, feature not penalty). Result recorded in the ASK 4 verification file.
