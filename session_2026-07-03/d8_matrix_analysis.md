# DIAG-B rev3 — matrix-side analysis (v2 matrix s4_matrix_v2_4a134d05.json)

## ASK 4 — cross-cohort Measure-1 mean (Yr-k as % of own end-of-Yr1), slopes, peak

### FULL HISTORY (2004-2024)
| Yr | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mean % of own Yr1 | 100% | 130% | 142% | 154% | 153% | 145% | 128% | 106% | 83% | 66% | 49% | 39% | 26% | 17% | 10% | 6% | 3% | 1% |
- mean yr1->2 slope: **+30.4 pp** (n=21 cohorts) · mean yr4->5 slope: **-3.5 pp** (n=18)
- OVERALL-row peak: **Yr 4 at 154%** -> peaks in yrs 4-6: **YES**

### 2015-2024 WINDOW
| Yr | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| mean % of own Yr1 | 100% | 125% | 133% | 138% | 138% | 132% | 123% |
- mean yr1->2 slope: **+25.0 pp** (n=10 cohorts) · mean yr4->5 slope: **-4.7 pp** (n=7)
- OVERALL-row peak: **Yr 4 at 138%** -> peaks in yrs 4-6: **YES**

### slopes/peak summary
| view | yr1->2 slope (pp) | yr4->5 slope (pp) | peak yr | peak value | peaks in yrs 4-6? |
|---|---|---|---|---|---|
| FULL HISTORY (2004-2024) | +30.4 | -3.5 | Yr 4 | 154% | YES |
| 2015-2024 WINDOW | +25.0 | -4.7 | Yr 4 | 138% | YES |

## ASK 3 — 2020 cohort: current total vs draft-day pick sum (engine PVC, as stored per-player in the matrix)

- 2020 ND+RD n=73 · current SUM (retired=0) = **43831** · draft-day pick-value SUM = **54355**
- **ratio current/pick-sum = 80.6%** -> verdict: **NOT above 100%**
- for contrast, Measure-1 Current (vs its OWN end-of-Yr1 total 40874) = **107%** — this is the number that reads >100% in TABLE 1
- 2020 per-cohort Measure-1 curve (% of own Yr1):
| Yr | 1 | 2 | 3 | 4 | 5 | 6 | Current |
|---|---|---|---|---|---|---|---|
| 2020 | 100% | 113% | 115% | 105% | 107% | 107% | 107% |

## ASK 5a — 2025 cohort Yr1 vs prior cohorts END-of-Yr1

| measure | value |
|---|---|
| 2025 Yr1 SUM (n=64 ND+RD, at store R14/24) | **37875** |
| prior end-of-Yr1 mean (2004-2024, n=21) | 51049 |
| prior end-of-Yr1 recent-5 mean (2020-2024) | 46283 |
| prior end-of-Yr1 range | 40874 - 61082 |
| shortfall vs 2004-2024 mean | **-25.8%** |
| shortfall vs recent-5 mean | **-18.2%** |
| shortfall vs 2023 (51548) / 2024 (51408) | -26.5% / -26.3% |

**Pick-mix control** (anchor SUM / draft-day pick-value SUM — removes cohort size/pick-sum differences):

| cohort | anchor/pick-sum |
|---|---|
| 2018 | 75.8% |
| 2019 | 76.3% |
| 2020 | 75.2% |
| 2021 | 81.8% |
| 2022 | 80.3% |
| 2023 | 94.8% |
| 2024 | 91.0% |
| **2025** | **73.4%** |

- normalized shortfall: vs 2004-2024 mean ratio 82.3% -> **-10.8%**; vs recent-5 mean ratio 84.6% -> **-13.2%**
- i.e. of the raw shortfall vs the recent-5 mean, cohort size/pick-mix (64 players, pick sum 51583 vs recent-5 mean 54663) explains the difference between the raw and normalized numbers.
- book Yr1 slot == matrix current (ASOF 2026) for the 2025 cohort: IDENTICAL all 64 (live-board equality vs a fresh engine eval is checked in the decomposition script)
