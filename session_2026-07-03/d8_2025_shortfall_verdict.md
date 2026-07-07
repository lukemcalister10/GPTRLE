# DIAG-B rev3 — ASK 5: the 2025 cohort Yr1 shortfall — quantified, decomposed, attributed

_2026-07-03 · TARGET = BAKE CANDIDATE v2 (engine `4a134d05` · cp `5ac8b162` · store `644d1254` R14/24) · all numbers v2's, unmodified · counterfactuals were runtime patches in a throwaway process — no engine file changed · matrix `data/s4_matrix_v2_4a134d05.json` · decomposition run: `d8_decomp_log.txt`, script `scripts/d8_decomp_2025.py`._

## 5a — QUANTIFY (the 37875 and the ~27–30% both checked)

| measure | value |
|---|---|
| 2025 Yr1 SUM (64 ND+RD, at R14/24) | **37875 — CONFIRMED exactly** |
| prior end-of-Yr1 mean (2004–2024) | 51049 → shortfall **−25.8%** |
| prior end-of-Yr1 recent-5 mean (2020–2024) | 46283 → shortfall **−18.2%** |
| vs 2023 (51548) / 2024 (51408) | −26.5% / −26.3% |
| prior range | 40874 (2020) – 61082 (2008) → 2025 is **below every prior cohort** (−7.3% vs the lowest) |

The ~27–30% figure is right **only against 2023/2024 and the full-history mean**; against the recent-5 mean it is −18.2%. Two benchmark distortions inflate it: (i) **2025 is the smallest cohort on record** (64 players, pick-value sum 51583 vs recent-5 mean 54663); (ii) **2023 and 2024 are the two richest Yr1 cohorts in the entire book** on the pick-mix-controlled ruler (94.8% and 91.0% of own pick sum vs the 2004–2024 mean of 82.3%).

**Pick-mix control** (Yr1 SUM ÷ own draft-day pick-value SUM — removes size/mix):

| cohort | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | **2025** |
|---|---|---|---|---|---|---|---|---|
| Yr1 / pick sum | 75.8% | 76.3% | 75.2% | 81.8% | 80.3% | 94.8% | 91.0% | **73.4%** |

Normalized shortfall: **−13.2%** vs the recent-5 mean ratio (84.6%), **−10.8%** vs the 2004–2024 mean ratio.

**Book ≈ board CONFIRMED:** a fresh v2 engine evaluation of all 64 players reproduces the book's Yr1 column **exactly (max per-player difference = 0; sum 37875)** — this is a live trading surface, not a display artifact. (Matrix draftvals also match live `MA.PVC` 0/73 mismatches on the 2020 check.)

## 5b — DECOMPOSE (10 players spanning games-played; all values v2)

`band_pr` = distribution-band price · `raw×iso` = band + pedigree-pole recovery × isotonic guard (the value the raw path would assign) · `sit-out` = the `ns==0` branch that **replaces** the raw path with retain×draftval · `CF6` = full-season-equivalent games counterfactual (g26 × 24/14, M3 off) · `2024 comp` = nearest-pick 2024 draftee END-of-Yr1 book value.

| player | pos | pk | g26 | avg26 | draftval | band_pr | expgate | raw×iso | sit-out branch | M3 s | floor(.45dv) | **final** | CF6 | 2024 comp (anchor) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Willem Duursma | MID | 1 | 13 | 86.4 | 3000 | 4183 | 0.59 | 4183 | no | 0.00 | 1350 | **4183** | 3968 | Lalor pk1 (3280) |
| Samuel Grlj | MID | 8 | 12 | 59.8 | 1704 | 2289 | 0.55 | 2256 | no | 0.00 | 767 | **2256** | 2337 | Travaglia pk8 (873) |
| Josh Lindsay | GEN_DEF | 19 | 12 | 74.3 | 795 | 1464 | 0.55 | 1454 | no | 0.00 | 358 | **1454** | 1519 | Oliver pk19 (398) |
| Zeke Uwland | GEN_DEF | 2 | 10 | 44.7 | 2501 | 1644 | 0.45 | 1831 | no | 0.09 | 1125 | **1829** | 2062 | O'Sullivan pk2 (3167) |
| Lachy Dovaston | GEN_FWD | 16 | 6 | 38.5 | 1001 | 909 | 0.27 | 969 | no | 0.45 | 450 | **953** | 1062 | Allan pk16 (624) |
| Daniel Annable | MID | 6 | 1 | 40.0 | 1873 | 1533 | 0.05 | 1571 | **YES 0.50×dv → 936** | 0.91 | 843 | **936** | 936 | Langford pk6 (2785) |
| Max Kondogiannis | GEN_DEF | 36 | 5 | 41.6 | 561 | 389 | 0.23 | 457 | **YES 0.50×dv → 280** | 0.55 | 252 | **280** | 505 | Ough pk36 (280) |
| Noah Roberts-Thomson | GEN_FWD | 54 | 3 | 38.7 | 349 | 574 | 0.14 | 543 | **YES 0.50×dv → 174** | 0.73 | 157 | **174** | 174 | Camporeale pk54 (174) |
| Dylan Patterson | GEN_DEF | 5 | 0 | 0.0 | 1965 | 1201 | 0.00 | 1201 | **YES 0.50×dv → 982** | 1.00 | 884 | **982** | 982 | Ashcroft pk5 (3514) |
| Koby Evans | GEN_FWD | 38 | 0 | 0.0 | 543 | 585 | 0.00 | 591 | **YES 0.50×dv → 272** | 1.00 | 244 | **272** | 272 | Moraes pk38 (764) |

What the table shows, channel by channel:
- **The sit-out/no-games channel is the whole story for 49 of the 64 players** (games census below): once `nseas==0`, the retain×draftval anchor REPLACES everything — Annable's 1 game at 40.0 avg is discarded and he prices at 936 where the raw path holds 1571 (−635 = the sit-out haircut alone), Patterson 982 vs raw 1201 (−219). M3 cannot help them (the pinned eval lands in the same branch → identity), and the effective penalty vs a comparable **played** prior-cohort Yr1 (Langford 2785, Ashcroft 3514) is −66% / −72% — but note that gap is played-vs-unplayed, not mid-season-vs-end-season: a 2024 draftee who was still unplayed at END of Yr1 got the identical anchor (Ough 280 = Kondogiannis's 280; Camporeale 174 = Roberts-Thomson's 174).
- **The played (≥6g) 2025 draftees are NOT underpriced** — Duursma 4183, Grlj 2256, Lindsay 1454 all sit ABOVE their nearest-pick 2024 comparables' end-of-Yr1 anchors. The unprorated `expgate` (max 14/22=0.64 mid-season) costs them little because for strong debutants the band already exceeds the pole (pole term ≈ 0).
- **Floor (0.45×dv)** binds nowhere in the sample — the sit-out retains (0.50/0.70/0.85) sit above it by construction.

Games census (14 rounds possible) with the prior-cohort contrast:

| bucket | n | draftval sum | v2 value sum |
|---|---|---|---|
| 0 games | 35 | 19387 | 10278 |
| 1–5 games (sit-out-classed DESPITE playing) | 14 | 10437 | 5527 |
| 6–10 games | 8 | 9169 | 8708 |
| 11+ games | 7 | 12590 | 13362 |

Sit-out-classed share: **2025 at R14 = 49/64 (77%)** vs 2023 at END-of-Yr1 = 50/73 (68%) and 2024 = 50/80 (63%) — the mid-season excess sit-out population is real but modest (~6–9 players who will clear 6 games by R24).

## 5c — THE PRORATION QUESTION
Full code quotes with line numbers: `d8_penalty_code_paths.md`. Plainly: **the sit-out bar (≥6 games), the qualifying-season bar (≥10), the level ramp (14) and the pole ramp (22) are all absolute full-season-scale constants — nothing prorates them to the 14-of-24 season position.** The only proration anywhere is M2 (prior-season decay clock — a structural no-op for Yr1 players, who have no prior seasons) and M3 (age/tenure clocks — a structural no-op inside the sit-out branch). Games-played smoothing exists inside the level machinery (`_lvl_wt`/`_exposure` are cliff-free), but the `ev()`-level sit-out gate is a hard unprorated threshold that discards scoring evidence entirely.

## 5d — ATTRIBUTION VERDICT: **PARTIAL — Luke's channel is real but owns slightly under half of the gap, not most of it**

Cohort-wide counterfactuals (all 64 players, sequential evals, one process):

| counterfactual | sum | Δ vs base |
|---|---|---|
| BASE v2 (as shipped) | 37875 | — |
| CF1 sit-out bar prorated (6 → 3.5 games) | 39671 | **+1796** |
| CF2 POLE_RAMP prorated (22 → 12.8) | 38226 | +351 |
| CF3 LEVEL_RAMP prorated (14 → 8.2) | 37875 | +0 |
| CF4 nqual bar prorated (10 → 5.8) | 38025 | +150 |
| CF5 = CF1–CF4 combined | 40188 | +2313 |
| **CF6 full-season-equivalent games (g×24/14, M3 off) — "priced as a completed Yr1 at current rate"** | **41746** | **+3871 (+10.2%)** |

Attribution of the raw shortfall, two benchmarks:

| channel | vs recent-5 mean (gap 8408) | vs 2023/24 mean (gap 13603) |
|---|---|---|
| cohort size / pick mix (smallest pick sum on record) | 2644 → **31%** | 3557 → **26%** |
| unprorated games-basis machinery (CF6; ~78% of it = the ≥6-games sit-out bar, CF1) | 3871 → **46%** | 3871 → **28%** |
| residual: 35 not-yet-debuted players held at retain×dv until they play (H2 debuts can't be extrapolated), the sit-out anchor's known ~16% over-discount (pre-registered book caveat), within-season rate improvement, and (vs 23/24 only) those two cohorts being the richest on record | 1893 → **23%** | 6175 → **45%** |

Even priced as a fully-completed season at current per-game rates, the 2025 cohort reaches 41746 = 80.9% of its pick sum — inside the historical band (2018–2022: 75–82%) and short only of the exceptional 2023/24. **So: hypothesis PARTIALLY CONFIRMED — the unprorated full-season penalty channel is real, material (+10.2% of cohort value suppressed), and almost entirely the sit-out ≥6-games bar rather than the ramps — but it does not explain most of the gap against 2023/24; benchmark richness, cohort size, and not-yet-debuted players own the larger share.**

## 5e — RELATIONSHIP TO DIAG-A / B6
**Same machinery, one rework owns all of it.** The Annable/Travaglia sit-out haircut (DIAG-A rev2 ASK 3; A12 gate FAIL Travaglia 712 < Moraes 887 at v2) is the identical `nseas==0 → SITOUT_RETAIN×draftval` branch decomposed above (Annable 936 = 0.50×1873 in this very table), and the B6 games-seam (flat-then-step dips at 7/9/13 games) is the same family of hard games thresholds (6-games qual bar, 10-games nqual, ramp knees) stepping across the games axis. A single games-ramp rework — smooth, season-progress-prorated games machinery at the `ev()` gates — owns the 2025 mid-season channel, the A12 sit-out punishment, and the B6 seam without double-fixing. (2025 shows "ref-only" in the book purely by display convention — `REFONLY={2003,2025}` in the render: its Yr1 is an in-progress season so it is excluded from the pick-order curve fit, not a data gap.)
