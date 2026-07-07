# D6 ASK 1 — PHOENIX GOTHARD DECOMPOSITION (the headline defect from Luke's offender-table eyeball)
_2026-07-02 · head `8aed420a` · store `644d1254` · candidate `fb39d88a`/cp `5ac8b162` measured READ-ONLY · cB-off variant `82b6c0c3` (factor-form patch `0.47→0.0`, functionally = D5's `ca9df823`) · all engine evals sequential · canonical restored + md5-verified after the variant block._

## 1a — STORE RECORD vs Luke's ground truth: **STORE AGREES** (mechanism hunt proceeded)
| field | store | Luke's ground truth | match |
|---|---|---|---|
| 2026 games | 13 | 13 | ✓ |
| 2026 season average | 70.2 | 70.2 | ✓ |
| drafted position | GFWD (gen-fwd) | gen-fwd | ✓ |
| current position | GFWD (no switch; `_pos_now`=None, `_fut`=[[GFWD, 100%]]) | — | ✓ |
| draft year / pick | 2023 / pick 12 (National) | pick 12 | ✓ |
| years-in-system | 3 | year 3 | ✓ |
| club / age | GWS / 21.0 (dob 2005-09-07) | — | — |

The one structural fact the summary numbers hide: **his ONLY scoring season is 2026** — no 2024/2025 rows at all. 13 games @ 70.2 is his entire career output, and it is happening right now.

## 1b — CHANNEL-BY-CHANNEL DECOMPOSITION OF 317 AT HEAD
The engine pipeline for Gothard, each channel's contribution printed:

| stage / channel | value | contribution |
|---|---|---|
| conditional-prior band [q10..q97] | [59.6, 68.0, 72.5, 82.1, 91.9, 101.2] | the band believes in him |
| replacement netting (REPL[GEN_FWD]=70.9 vs his 70.2) | −0.7 SC vs replacement | **innocent** — nets him fairly; Luke's "nearly above replacement" is the engine's own read |
| band price pr (replacement-netted) | 1815.2 | the base |
| pole recovery (po=1879, wage .833 × tfade(et=3) .400 × expgate .591 → w=.197; recover=1.000 at perf/par=1.05) | +12.6 | tenure fade + exposure gate already mute this channel — small and fair |
| raw_ev | 1827.8 | |
| isotonic position guard iso_corr(GEN_FWD,12)=0.9795 | −37.5 | **innocent** — 2% trim |
| **e_pre (uncapped engine price)** | **1790.3** | what the engine actually thinks he's worth |
| **STALENESS CAP** `min(e, 0.25·draftval)` — armed by el=3 ≥ onset=3 AND ns=1 | **317.2** | **−1473.0 — owns the ENTIRE gap** |
| ev (rounded) | **317** | = 0.25 × 1269 exactly; confirm head 317 ✓ |

Counterfactual escapes (measured, one process, monkeypatch toggles):
| counterfactual | ev |
|---|---|
| tenure-click −1yr (el 3→2: cap onset not reached) | 1480 |
| a second qualifying season (6g @ 70.2 in 2025 → ns=2, cap branch off) | 1938 |
| staleness-cap OFF, all else head | 1790 |
| iso guard off, cap on | 317 (cap binds regardless) |
| expgate=1 (proven treatment), cap on | 317 (cap binds regardless) |

**MECHANISM VERDICT (one paragraph):** The gap between 317 and a sane price is owned entirely by ev()'s **staleness cap** — the stalled-non-producer branch `if el>=onset and ns<=1: e=min(e, dv*0.25)`. Every pricing channel of the engine (band, replacement netting, pole recovery, position guard) values Gothard at ~1790; the cap then overwrites that with 0.25×draftval because he has tenure ≥3 and exactly one ≥6-game season. The defect is that the cap counts qualifying seasons without asking **when** the one season is or **how good** it is: it was built for "played once long ago, nothing since" (its correct targets share the branch: Hardeman 2g@25.5, Collard 0g26) and cannot distinguish that profile from "the breakout is happening right now" (13g @ 70.2 vs REPL 70.9, perf/par=1.05). Every yr-3 offender in the B5 table at ratio ≈0.250 is this same cap — the yr-3 offender block is the staleness cap sitting 0.03 below the signed 0.28 floor, and Gothard is its one victim who is actually producing. Tenure/age click, exposure/recency, replacement netting and GEN_FWD handling all price him correctly; the tenure click's only guilt is arming the cap's onset (el 3→2 escapes to 1480).

## 1c — GOTHARD AT THE FOUR STATES (one row)
| state | ev | uncapped e_pre | note |
|---|---|---|---|
| head `8aed420a` | **317** | 1790 | cap binds |
| candidate `fb39d88a` | **317** | 1766 | cap binds; M1/v7 move only the uncapped price (−24) |
| candidate − cB (`82b6c0c3`) | **317** | 1766 | identical to candidate: his effs=13/17<1 → cB=0 for his profile anyway |
| head + M3-prototype (D5/D4 design, fE=0.58) | **317** | — | g26=13 → s=0 → M3 is identity BY CONSTRUCTION (scopes to g26<11) |

No wired or proposed lever touches him: M2/M3 scope to in-progress under-exposure (he is on-pace), M1 needs 4 proven seasons, v7 only compresses. **The floor-as-pricing-feature (ASK 2) lifts him 317 → 355 (0.28×1269) — a patch, not the fix; the fix is a recency/quality term in the staleness cap (candidate-branch item, needs Luke's word).**

## The 0.25-cap fingerprint across ALL yr-3 ND offenders (from the head sweep)
| player | ev | draftval | ratio | ns | g26 | avg26 |
|---|---|---|---|---|---|---|
| Phoenix Gothard | 317 | 1269 | 0.250 | 1 | 13 | 70.2 |
| Riley Hardeman | 154 | 618 | 0.249 | 1 | 2 | 25.5 |
| Caiden Cleary | 154 | 616 | 0.250 | 1 | 5 | 60.8 |
| Lance Collard | 152 | 607 | 0.250 | 1 | 0 | — |
| Ashton Moir | 151 | 605 | 0.250 | 1 | 2 | 46.0 |
| Angus Hastie | 149 | 596 | 0.250 | 1 | 2 | 51.0 |
| Clay Hall | 136 | 543 | 0.250 | 1 | 0 | — |
| Will Lorenz | 77 | 309 | 0.249 | 1 | 1 | 52.0 |
| Oliver Wiltshire | 44 | 308 | 0.143 | 1 | 6 | 41.8 |

(Wiltshire is the exception that proves the rule: his uncapped price is already below the cap.) Gothard is the ONLY one producing at replacement level; Cleary (5g @ 60.8) is the nearest second — consistent with Luke's tolerable-but-noted read.
