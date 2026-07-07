# D7 ASK 4 — STALENESS-CAP RECENCY FIX (design + derivation; WIRED NOWHERE — M3 discipline, joins a candidate only on Luke's endorsement)
_2026-07-02 · designed and measured at CANONICAL HEAD `8aed420a` / store `644d1254` · scratch prototype `a9e1c14b` (one-condition patch, below) · NOT in BAKE CANDIDATE v2 (`4a134d05` still carries the unfixed cap: Gothard prices 317→355 there via the floor)._

## THE DEFECT (from D6, restated in one sentence)
`ev()`'s stalled-non-producer branch — `if el>=onset and ns<=1: e = min(e, dv·frac)` — counts qualifying seasons (≥6 games) without asking WHEN the one season happened or HOW GOOD it is, so it cannot tell "appeared once years ago and vanished" (its correct target) from "the breakout is happening right now" (Gothard: 13g @ 70.2 vs REPL 70.9, engine price 1790, capped to 317).

## 4a — THE CAP POPULATION AT HEAD (every player where the branch FIRES): n = 38, binds for 33
The branch fires only for ns==1 (ns==0 routes to the sit-out anchor first). UNCAPPED = raw_ev × iso (the price the cap overwrites). `gap` = 2026 − the sole qualifying season's year. Sorted by gap, then uncapped value.

| player | club | yrs | draft yr/pick | type | seasons on file (yr:g@avg) | qual season | gap | 2026 g/avg | uncapped | CAPPED (head) | binds | new rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Phoenix Gothard | GWS | 3 | 2023/12 | ND | 2026:13g@70.2 | 2026 (13g@70.2) | 0 | 13g@70.2 | 1790 | 317 | Y | **RELEASED** |
| Lachlan McAndrew (MSD credit) | Sydney | 5 | 2021/12 | MSD | 2026:13g@87.1 | 2026 (13g@87.1) | 0 | 13g@87.1 | 1408 | 99 | Y | **RELEASED** |
| Jai Serong | Hawthorn | 5 | 2021/53 | ND | 2022:3g@21.0 · 2023:2g@44.5 · 2024:5g@45.0 · 2026:13g@76.7 | 2026 (13g@76.7) | 0 | 13g@76.7 | 1029 | 72 | Y | **RELEASED** |
| Oscar Steene | Collingwood | 4 | 2022/— | SSP | 2026:8g@51.6 | 2026 (8g@51.6) | 0 | 8g@51.6 | 818 | 123 | Y | **RELEASED** |
| Max Heath | St Kilda | 5 | 2021/7 | MSD | 2025:4g@45.5 · 2026:6g@52.8 | 2026 (6g@52.8) | 0 | 6g@52.8 | 666 | 99 | Y | **RELEASED** |
| Will Edwards | Sydney | 4 | 2022/— | PDA | 2026:8g@51.7 | 2026 (8g@51.7) | 0 | 8g@51.7 | 296 | 123 | Y | **RELEASED** |
| James Tunstill | Brisbane | 5 | 2021/41 | ND | 2022:3g@42.7 · 2023:2g@22.0 · 2024:4g@23.8 · 2025:3g@37.3 · 2026:7g@47.0 | 2026 (7g@47.0) | 0 | 7g@47.0 | 220 | 102 | Y | **RELEASED** |
| Oliver Wiltshire | Geelong | 3 | 2023/61 | ND | 2025:2g@34.5 · 2026:6g@41.8 | 2026 (6g@41.8) | 0 | 6g@41.8 | 44 | 44 | n | released (non-binding — value unchanged) |
| Cooper Lord | Carlton | 2 | 2024/9 | MSD | 2024:3g@78.5 · 2025:21g@59.9 · 2026:3g@76.7 | 2025 (21g@59.9) | 1 | 3g@76.7 | 1050 | 77 | Y | caught |
| Clay Hall | West Coast | 3 | 2023/38 | ND | 2024:3g@34.3 · 2025:13g@66.8 | 2025 (13g@66.8) | 1 | 0g | 882 | 136 | Y | caught |
| Caiden Cleary | Sydney | 3 | 2023/24 | ND | 2024:5g@28.8 · 2025:12g@45.0 · 2026:5g@60.8 | 2025 (12g@45.0) | 1 | 5g@60.8 | 775 | 154 | Y | caught |
| Jedd Busslinger | Western Bulldogs | 4 | 2022/13 | ND | 2025:7g@44.1 · 2026:4g@74.5 | 2025 (7g@44.1) | 1 | 4g@74.5 | 636 | 481 | Y | caught |
| Will Lorenz | Port Adelaide | 3 | 2023/57 | ND | 2024:2g@22.0 · 2025:6g@58.3 · 2026:1g@52.0 | 2025 (6g@58.3) | 1 | 1g@52.0 | 626 | 77 | Y | caught |
| Riley Hardeman | North Melbourne | 3 | 2023/23 | ND | 2024:3g@44.3 · 2025:17g@54.8 · 2026:2g@25.5 | 2025 (17g@54.8) | 1 | 2g@25.5 | 552 | 154 | Y | caught |
| Cooper Harvey | North Melbourne | 4 | 2022/56 | ND | 2023:3g@35.0 · 2025:7g@45.9 · 2026:1g@73.0 | 2025 (7g@45.9) | 1 | 1g@73.0 | 410 | 73 | Y | caught |
| Isaac Keeler | St Kilda | 4 | 2022/44 | ND | 2025:11g@40.3 · 2026:2g@39.5 | 2025 (11g@40.3) | 1 | 2g@39.5 | 386 | 187 | Y | caught |
| Ashton Moir | Carlton | 3 | 2023/29 | ND | 2024:2g@28.5 · 2025:9g@45.4 · 2026:2g@46.0 | 2025 (9g@45.4) | 1 | 2g@46.0 | 381 | 151 | Y | caught |
| Angus Hastie | St Kilda | 3 | 2023/33 | ND | 2024:5g@20.4 · 2025:9g@35.9 · 2026:2g@51.0 | 2025 (9g@35.9) | 1 | 2g@51.0 | 376 | 149 | Y | caught |
| Sandy Brock | Gold Coast | 5 | 2021/— | PDA | 2025:14g@62.5 · 2026:4g@44.5 | 2025 (14g@62.5) | 1 | 4g@44.5 | 314 | 111 | Y | caught |
| Tom Hanily | Sydney | 2 | 2024/14 | MSD | 2025:8g@34.4 · 2026:2g@42.5 | 2025 (8g@34.4) | 1 | 2g@42.5 | 307 | 77 | Y | caught |
| Lance Collard | St Kilda | 3 | 2023/28 | ND | 2024:3g@6.3 · 2025:12g@30.9 | 2025 (12g@30.9) | 1 | 0g | 279 | 152 | Y | caught |
| Will McLachlan | Brisbane | 2 | 2024/6 | MSD | 2025:6g@23.3 · 2026:1g@28.0 | 2025 (6g@23.3) | 1 | 1g@28.0 | 263 | 77 | Y | caught |
| Liam McMahon | Collingwood | 6 | 2020/33 | ND | 2025:7g@42.1 | 2025 (7g@42.1) | 1 | 0g | 232 | 191 | Y | caught |
| Kaleb Smith | Richmond | 4 | 2022/49 | ND | 2024:4g@25.0 · 2025:8g@40.0 | 2025 (8g@40.0) | 1 | 0g | 176 | 90 | Y | caught |
| Bailey Macdonald | Hawthorn | 4 | 2022/51 | ND | 2023:2g@44.5 · 2025:6g@25.2 · 2026:3g@53.0 | 2025 (6g@25.2) | 1 | 3g@53.0 | 173 | 86 | Y | caught |
| Liam O'Connell | St Kilda | 3 | 2023/— | IRE | 2025:7g@35.7 · 2026:5g@48.2 | 2025 (7g@35.7) | 1 | 5g@48.2 | 112 | 77 | Y | caught |
| Luke Cleary | Western Bulldogs | 5 | 2021/61 | ND | 2022:4g@34.0 · 2023:1g@49.0 · 2024:2g@45.5 · 2025:16g@57.7 · 2026:1g@10.0 | 2025 (16g@57.7) | 1 | 1g@10.0 | 81 | 62 | Y | caught |
| Conor Stone | GWS | 6 | 2020/15 | ND | 2021:5g@35.2 · 2022:1g@27.0 · 2023:3g@16.0 · 2024:4g@19.8 · 2025:7g@48.3 · 2026:3g@53.0 | 2025 (7g@48.3) | 1 | 3g@53.0 | 71 | 71 | n | caught |
| Billy Dowling | Adelaide | 4 | 2022/43 | ND | 2024:9g@66.8 · 2025:1g@55.0 | 2024 (9g@66.8) | 2 | 0g | 578 | 109 | Y | caught |
| Shadeau Brain | Brisbane | 4 | 2022/— | PDA | 2024:9g@46.4 · 2026:2g@54.5 | 2024 (9g@46.4) | 2 | 2g@54.5 | 264 | 69 | Y | caught |
| Harvey Harrison | Collingwood | 5 | 2021/52 | ND | 2023:4g@40.2 · 2024:12g@46.6 · 2026:2g@44.5 | 2024 (12g@46.6) | 2 | 2g@44.5 | 176 | 74 | Y | caught |
| Andy Moniz-Wakefield | Melbourne | 5 | 2021/— | PDN | 2024:6g@53.7 · 2026:2g@29.5 | 2024 (6g@53.7) | 2 | 2g@29.5 | 150 | 62 | Y | caught |
| Harvey Gallagher | Western Bulldogs | 4 | 2022/39 | ND | 2024:20g@45.4 · 2025:5g@35.8 · 2026:3g@38.0 | 2024 (20g@45.4) | 2 | 3g@38.0 | 145 | 120 | Y | caught |
| Jackson Archer | North Melbourne | 5 | 2021/59 | ND | 2022:3g@48.7 · 2023:5g@32.0 · 2024:15g@46.0 · 2025:3g@34.7 | 2024 (15g@46.0) | 2 | 0g | 125 | 62 | Y | caught |
| Darragh Joyce | St Kilda | 10 | 2016/— | IRE | 2018:2g@15.0 · 2019:3g@55.0 · 2021:5g@42.2 · 2022:3g@31.0 · 2023:5g@45.2 · 2024:6g@51.0 · 2026:3g@54.0 | 2024 (6g@51.0) | 2 | 3g@54.0 | 22 | 22 | n | caught |
| Josh Goater | North Melbourne | 5 | 2021/22 | ND | 2022:1g@70.0 · 2023:10g@56.2 · 2024:1g@42.0 | 2023 (10g@56.2) | 3 | 0g | 150 | 129 | Y | caught |
| Judson Clarke | Richmond | 5 | 2021/30 | ND | 2022:3g@44.7 · 2023:13g@43.3 · 2024:1g@8.0 | 2023 (13g@43.3) | 3 | 0g | 98 | 98 | n | caught |
| Josh Gibcus | Richmond | 5 | 2021/9 | ND | 2022:18g@53.7 · 2024:2g@47.5 · 2025:1g@43.0 · 2026:1g@56.0 | 2022 (18g@53.7) | 4 | 1g@56.0 | 323 | 323 | n | caught |
## 4b — THE DERIVED EXEMPTION (recency-aware condition)
**Derived rule (Form A): the cap must NOT fire when the sole qualifying season IS the season being evaluated.**
```
live = (ns == 1) and any(x.games >= 6 and x.year == Y for x in p.scoring)
if el >= onset and ns <= 1 and not live:        # (was: if el >= onset and ns <= 1)
    e = min(e, dv * frac)
```
**Why this exact form, from the data:**
1. **It is structural, with ZERO invented constants.** A ghost is a player who appeared once and then vanished — vanishing requires elapsed football AFTER the qualifying season. A player whose only qualifying season is the one in progress (gap=0) cannot have vanished from it; the cap's founding premise is unfalsifiable for him. Every gap=0 row above is a player the band is pricing on LIVE evidence.
2. **Quality needs no threshold at gap=0 — the band already prices it.** The gap=0 block's uncapped prices track quality monotonically: Gothard (0.99×REPL) → 1790, McAndrew (1.11×REPL) → 1408, Serong (0.98×REPL) → 1029, down to Wiltshire (0.59×REPL) → 44, where the cap did not even bind. Releasing gap=0 hands pricing back to the machinery that already handles quality; no replacement-fraction bar is needed (the bar the directive contemplated was checked and found redundant on this population).
3. **The gap=1 axis does NOT support a threshold at finest resolution.** Sorting the 20 gap=1 players by current-season output as a fraction of REPL[pos] gives breaks of 0.198 (0.326→0.128), 0.188 (0.583→0.395) and 0.181 (0.858→0.677) — three near-equal gaps at three different altitudes on 1–5-game samples. No dominant mode separation exists; any quality bar there would be an invented constant on noise. Per the standing statistics instruction (finest supportable resolution — and no finer), gap=1 stays OUT of the derived rule.
4. **Chain preserved:** an exempted player falls through to the mediocre-for-years branch (`elif el>=onset+2 and pr<0.55`), which stays armed — the safety net for a long-tenured exemptee who has never approached par survives (measured: it fired on none of the 7 released — all price at their uncapped values).
5. **Generalizes across as-of years:** at any evaluation year Y the condition reads that year's own season, so historical walk-forward cells get the identical rule (measured in 4d: B1 average RISES to 169.2 and still passes — the released historical cells are young breakouts mid-first-season, which is exactly the shape B1 rewards).

**Priced extension (Form B — NOT recommended, data-thin; listed so Luke can rule with numbers):** also exempt gap=1 when the current season shows live output (g26 ≥ 4 = the 6-game qualifying bar × SEASON_PROG 0.58 rounded up, AND avg26 ≥ 0.75×REPL = the midpoint of the 0.858→0.677 break). Releases in addition: **Jedd Busslinger 481→636** and **Caiden Cleary 154→775**; leaves Cooper Lord (3g, misses the games bar by one) and Cooper Harvey (1 game) caught. Support: WEAK (the break is not dominant; 4-5 game samples). Note Luke's D6 read seeded Cleary as *tolerable-but-noted* AT THE CAPPED VALUE — Form A keeps that read intact; Form B overrides it.

## 4c — THE SAME TABLE UNDER THE NEW RULE (Form A)
**RELEASED (7 binding + 1 non-binding):**
| player | club | capped (head) | released to | why it is safe |
|---|---|---|---|---|
| Phoenix Gothard | GWS | 317 | **1790** | 13g @ 70.2 NOW, 0.99×REPL — Luke's ~1790 read; NO artificial shaving applied |
| Lachlan McAndrew (MSD credit) | Sydney | 99 | **1408** | 13g @ 87.1 NOW — 1.11×REPL, the population's best current output |
| Jai Serong | Hawthorn | 72 | **1029** | 13g @ 76.7 NOW, 0.98×REPL |
| Oscar Steene | Collingwood | 123 | **818** | 8g @ 51.6 NOW (RUC — high REPL bar; band prices the discount) |
| Max Heath | St Kilda | 99 | **666** | 6g @ 52.8 NOW |
| Will Edwards | Sydney | 123 | **296** | 8g @ 51.7 NOW |
| James Tunstill | Brisbane | 102 | **220** | 7g @ 47.0 NOW (band prices the mediocrity: released value is modest) |
| Oliver Wiltshire | Geelong | 44 | 44 (unchanged) | fires but never bound — his uncapped price is already below the cap |

**REMAIN CAUGHT (the true ghosts + the gap=1 band — Luke's requested second list):** all 30 remaining rows of the 4a table, unchanged to the byte. Headline ghosts: Billy Dowling (qual 2024, 0g since → 109), Josh Goater (qual 2023 → 129), Judson Clarke (qual 2023, LTI → 98), Josh Gibcus (qual 2022, LTI → 323, never bound), Harvey Harrison / Jackson Archer / Shadeau Brain / Andy Moniz-Wakefield / Harvey Gallagher / Darragh Joyce (qual 2024). Gap=1 kept: Cooper Lord (77), Clay Hall (136), Caiden Cleary (154), Riley Hardeman (154 — Luke: tolerable-but-noted, intact), Jedd Busslinger (481), Ashton Moir (151), Angus Hastie (149), Lance Collard (152), Will Lorenz (77), Cooper Harvey (73), + 10 more.

## 4d — PRE-REGISTERED ACCEPTANCE (all measured at head+fix scratch `a9e1c14b`)
| criterion | bar | measured | verdict |
|---|---|---|---|
| Gothard | ~1790 neighbourhood (Luke: "probably fine, a touch rich, happy to leave it" — tolerance logged; NO shaving) | **1790** (= his uncapped engine price, to the point) | **PASS** |
| true ghosts stay capped | required | all gap≥1 rows byte-identical (see collateral) | **PASS** |
| zero collateral outside the cap population | required | full-population diff head vs head+fix: **7 movers of 807**, every one a gap=0 binding row | **PASS** |
| all gates incl. new-B1 hold at head+fix | required | board at head+fix: **no gate that passed at head fails** (9 PASS; fails = the head's own A2/A3/A5/A9/A12/B4/B6 set); **new-B1 PASS, avg peak N=4 @ 169.2** (vs 160.5 at head — released historical gap=0 cells LIFT the growth curve); B2 re-run 0.0 leakage | **PASS** |
| Tsatas guard (A8) | ≥2x | untouched: 3.21x at head+fix (Tsatas has 2 qualifying seasons — not in the population) | PASS |

**Known limits, flagged (not silent):** (i) forward-year views (ev at Y > the store cut, e.g. vP1 2027) re-cap a gap=0 player the moment the year clicks and his season completes as his only one — same class as the delisted()-hardcodes-2026 flag; an M3-style proration or ns-credit at the year boundary is future work, Luke's call. (ii) The exemption keys on the ≥6-games qualifying bar itself; a 5-game current breakout (e.g. Caiden Cleary at 5g @ 60.8) is not exempted until game 6 lands — the bar is the store's own qualifying convention, kept deliberately.

**Artifacts:** population `scripts/d7_ask4_population.json` (95bf9f4e) · sweeps `scripts/d7_head_sweep.json` (db71e884) / `scripts/d7_headfix_sweep.json` (92991f4a) · head+fix board `ship_gates_report_a9e1c14b.md` · prototype `engine/prototypes/staleness_recency_fix.py`.
