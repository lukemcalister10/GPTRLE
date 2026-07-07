# ship_gates_check report — head 4a134d05 store 644d1254
```
=== SHIP GATES BOARD — head 4a134d05 store 644d1254 — suite 764a0d91 — 2026-07-02 ===
A1        PASS     Duursma>Uwland: 4183 vs 1829
A2        FAIL     Curtis>=0.90xWard: 1358 vs 1488 (Ward=1653, ratio=0.822) [AMENDED 02/07/2026; UNCHANGED at 0.90 by ruling D7 — Luke: "we can look at Curtis down the line"]; Weddle>Ward: 1572 vs 1653
A3   [DC] FAIL     Connor Rozee: 2026=2917 2025=3992 ratio=0.73 (need >=0.75) [evaluated PRE-LTI-layer — Luke 02/07; AMENDED 0.80->0.75 Luke D7 data-caused (out for 2026), knife-edge by design]
          triage: [DC] gate — attribute ENGINE- vs DATA-caused BEFORE this blocks (SHIP_GATES PROCESS)
A4        PASS     Harley Reid board rank=29 ev=3565 (need TOP 40)
A5        PASS     Jack Ginnivan=1799 (floor 1600); Jake Bowey=2969 (floor 2100); Nick Blakey=3287 (floor 2600) [SCAR floors — RE-BASE if PVC re-levels]
A6        PASS     yr1-3 RUC median=314 (n=13, pooled — thin slice) vs pick-matched MID kernel median=519 (n=66, bw=0.6 log-pick, RATIFIED 02/07)
A7        PASS     Ryan Maric: fut-dominant=MID(60%) gfut=MID (need MID/MID); Ed Langdon: fut-dominant=GDEF(70%) gfut=GEN_DEF (need GDEF/GEN_DEF)
A8   [DC] PASS     Berry=2421 Tsatas=1140 ratio=2.12x (need >=2.00x) [display de-ambiguated D4 02/07]
A9        PASS     Ginnivan>Ward: 1799 vs 1653
A10  [DC] PASS     Charlie Curnow: 2026=888 2025=1745 ratio=0.51 (need >=0.50) [AMENDED 0.70->0.50 Luke 02/07 data-caused, PROVISIONAL — review at season-complete]
A11  [DC] PASS     Farrow>Patterson: 1642 vs 982; Cumming>Annable: 1982 vs 936
A12  [DC] FAIL     Travaglia>Moraes: 712 vs 887; Smillie>Retschko: 896 vs 744
          triage: [DC] gate — attribute ENGINE- vs DATA-caused BEFORE this blocks (SHIP_GATES PROCESS)
A13       PENDING  PVC stage not run; advisory vs stand-in PVC[1]=3000: George Wardlaw=3033 lineball=True; Levi Ashcroft=3270 lineball=True
A14       PENDING  PVC stage not run; advisory vs stand-in PVC[8]=1704: Trent Rivers=1713 lineball=True; Zach Reid=1613 lineball=True; Jase Burgoyne=2092 lineball=False
A15       STRUCK   Luke 02/07/2026 — convexity dimension seeded as V_NEXT #1
B1        PASS     cross-cohort AVERAGE peak N=4 AVG(peak)=156 (need peak in yrs 4-6, >100; pre-peak dips of the AVERAGE <5% tolerated, path_ok=True; per-cohort UNGATED, table printed every run — Luke redefinition 02/07 D5); avg row: 1:100 2:132 3:143 4:156 5:153 6:145 7:128; cohorts n=17; matrix=s4_matrix_v2_4a134d05.json
B2        PASS     median |IS-WF| leakage=0.0 %-pts (tol 0.5, SET 02/07/2026 — N=5 spread 0.00); GOOD>BUST separation: GEN_DEF 49/1, GEN_FWD 40/1, KEY_DEF 55/1, KEY_FWD 62/0, MID 50/0
B3        PENDING  book-gate set not yet enumerated as scripted checks — definition proposal in report; book headline shape covered by B1
B4        FAIL     regenerated rl_app_data.json md5=08d91566 vs shipped b8f9e998 (byte-agree gate; export exit=0)
B5        FEATURE  floor-as-pricing-feature (Luke-ruled 02/07; VARIANT A flat .05 tail): 54 saves, aggregate lift +1684; pure lower bound: lowered=0 (bar 0), non-ND moved=0 (bar 0); saves table printed below (the new alarm surface)
B6        FAIL     ramp(0..14g)=[745, 745, 745, 745, 745, 745, 3296, 3379, 3376, 3551, 3325, 3459, 3526, 3583, 3578]; dips(more games worth less)=[(7, -3.0), (9, -226.0), (13, -5.0)]; 0->6 rise T=+2551; 0->6 steps>50%T=[(5, 2551)]; rise by 3g=+0 (need >=638) [whole-ramp re-spec, DECLARED thresholds]
C1        PENDING  naive-baseline book not yet built — definition proposal in report (needs its own directive)
C2        PENDING  V1-pick-model book not yet built — definition proposal in report (needs its own directive)
VERDICT: FAIL=5  FEATURE=1  PASS=11  PENDING=5  STRUCK=1  (141s)
```

## Supporting detail

B1 per-cohort curves (UNGATED — printed every gates-board run, Luke eyeball channel):
| cohort | peakN | d1 | d2 | d3 | d4 | d5 | d6 | d7 |
|---|---|---|---|---|---|---|---|---|
| 2004 | 5 | 100 | 140 | 166 | 171 | 185 | 163 | 143 |
| 2005 | 4 | 100 | 145 | 146 | 197 | 182 | 175 | 150 |
| 2006 | 4 | 100 | 143 | 156 | 173 | 171 | 168 | 145 |
| 2007 | 5 | 100 | 133 | 126 | 136 | 162 | 156 | 131 |
| 2008 | 4 | 100 | 133 | 176 | 194 | 173 | 155 | 135 |
| 2009 | 2 | 100 | 124 | 110 | 113 | 114 | 103 | 88 |
| 2010 | 4 | 100 | 143 | 156 | 175 | 169 | 149 | 124 |
| 2011 | 4 | 100 | 136 | 162 | 186 | 182 | 172 | 141 |
| 2012 | 4 | 100 | 123 | 133 | 135 | 129 | 124 | 103 |
| 2013 | 5 | 100 | 136 | 155 | 185 | 186 | 164 | 126 |
| 2014 | 4 | 100 | 133 | 150 | 161 | 146 | 144 | 141 |
| 2015 | 4 | 100 | 126 | 129 | 133 | 129 | 129 | 122 |
| 2016 | 4 | 100 | 137 | 153 | 179 | 167 | 170 | 145 |
| 2017 | 3 | 100 | 120 | 123 | 112 | 104 | 106 | 99 |
| 2018 | 4 | 100 | 126 | 131 | 140 | 136 | 127 | 116 |
| 2019 | 5 | 100 | 132 | 146 | 158 | 167 | 152 | 132 |
| 2020 | 3 | 100 | 113 | 115 | 105 | 107 | 107 | — |
| **AVG (the gated row)** | **4** | **100** | **132** | **143** | **156** | **153** | **145** | **128** |

B5 FLOOR-SAVES table (n=54, aggregate lift=+1684 — printed every gates-board run, the new alarm surface):
| player | club | yrs-in-system | raw ev | floor | saved-to | lift | register status |
|---|---|---|---|---|---|---|---|
| Jamarra Ugle-Hagan | Western Bulldogs | 6 | 157 | 270.0 | 270 | +113 | clear |
| Paddy Dow | Carlton | 9 | 13 | 112.4 | 112 | +99 | clear |
| Jaeger O'Meara | Gold Coast | 15 | 62 | 150.0 | 150 | +88 | clear |
| Oliver Wiltshire | Geelong | 3 | 13 | 86.2 | 86 | +73 | clear |
| Conor Stone | GWS | 6 | 25 | 96.7 | 97 | +72 | clear |
| Chayce Jones | Adelaide | 8 | 9 | 80.2 | 80 | +71 | clear |
| Nicholas Coffield | St Kilda | 9 | 16 | 85.2 | 85 | +69 | clear |
| Jack Martin | Gold Coast | 14 | 44 | 112.4 | 112 | +68 | clear |
| Steele Sidebottom | Collingwood | 18 | 3 | 69.0 | 69 | +66 | clear |
| Jake Melksham | Essendon | 17 | 11 | 74.5 | 74 | +63 | clear |
| Luke Pedlar | Adelaide | 6 | 66 | 124.2 | 124 | +58 | clear |
| Angus Anderson | Collingwood | 1 | 89 | 139.1 | 139 | +50 | clear |
| Jacob Hopper | GWS | 11 | 42 | 89.7 | 90 | +48 | clear |
| Callum Ah Chee | Gold Coast | 11 | 38 | 85.2 | 85 | +47 | clear |
| Sam Davidson | Western Bulldogs | 2 | 92 | 133.0 | 133 | +41 | clear |
| Hunter Clark | St Kilda | 9 | 50 | 89.7 | 90 | +40 | clear |
| Phoenix Gothard | GWS | 3 | 317 | 355.3 | 355 | +38 | clear |
| Liam Stocker | Carlton | 8 | 2 | 39.8 | 40 | +38 | clear |
| Brandon Starcevich | Brisbane | 9 | 6 | 43.0 | 43 | +37 | clear |
| Bailey Laurie | Melbourne | 6 | 21 | 55.6 | 56 | +35 | clear |
| Jade Gresham | St Kilda | 11 | 13 | 43.0 | 43 | +30 | clear |
| Luke McDonald | North Melbourne | 13 | 55 | 85.2 | 85 | +30 | clear |
| Charlie Spargo | Melbourne | 9 | 1 | 30.2 | 30 | +29 | clear |
| Liam Henry | Fremantle | 7 | 53 | 80.2 | 80 | +27 | clear |
| Laitham Vandermeer | Western Bulldogs | 8 | 2 | 27.7 | 28 | +26 | clear |
| Jacob Wehr | GWS | 6 | 3 | 27.7 | 28 | +25 | clear |
| Ben Long | St Kilda | 10 | 9 | 30.7 | 31 | +22 | clear |
| Sam Butler | Hawthorn | 5 | 60 | 80.3 | 80 | +20 | clear |
| Nicholas Holman | Carlton | 13 | 0 | 20.1 | 20 | +20 | clear |
| Xavier O'Halloran | GWS | 8 | 13 | 32.4 | 32 | +19 | clear |
| Callum Coleman-Jones | Richmond | 9 | 18 | 36.8 | 37 | +19 | clear |
| Harvey Gallagher | Western Bulldogs | 4 | 94 | 111.7 | 112 | +18 | clear |
| Mitch McGovern | Adelaide | 12 | 9 | 24.2 | 24 | +15 | clear |
| Daniel Butler | Richmond | 12 | 0 | 15.4 | 15 | +15 | clear |
| Corey Durdin | Carlton | 6 | 34 | 47.9 | 48 | +14 | clear |
| Alex Pearce | Fremantle | 13 | 14 | 27.7 | 28 | +14 | clear |
| Jed Bews | Geelong | 15 | 1 | 15.4 | 15 | +14 | clear |
| Oliver Henry | Collingwood | 6 | 65 | 77.3 | 77 | +12 | clear |
| Darcy Gardiner | Brisbane | 13 | 21 | 32.4 | 32 | +11 | clear |
| Matt Guelfi | Essendon | 9 | 5 | 15.4 | 15 | +10 | clear |
| Aidan Corr | GWS | 14 | 34 | 43.0 | 43 | +9 | clear |
| Joel Hamling | Geelong | 15 | 14 | 23.4 | 23 | +9 | clear |
| Rhys Stanley | St Kilda | 18 | 12 | 21.2 | 21 | +9 | clear |
| Tom Cole | West Coast | 11 | 20 | 28.1 | 28 | +8 | clear |
| Finn Maginness | Hawthorn | 7 | 23 | 30.2 | 30 | +7 | clear |
| Ben McKay | North Melbourne | 11 | 27 | 34.3 | 34 | +7 | clear |
| Ryan Gardner | Geelong | 11 | 9 | 15.4 | 15 | +6 | clear |
| Nathan Broad | Richmond | 11 | 9 | 15.4 | 15 | +6 | clear |
| Sam Sturt | Fremantle | 8 | 41 | 46.5 | 46 | +5 | clear |
| Jamie Cripps | St Kilda | 16 | 25 | 30.2 | 30 | +5 | clear |
| Liam Ryan | West Coast | 9 | 27 | 30.6 | 31 | +4 | clear |
| Oskar Baker | Melbourne | 9 | 18 | 20.6 | 21 | +3 | clear |
| Latrelle Pickett | Melbourne | 1 | 570 | 571.1 | 571 | +1 | clear |
| Finlay Macrae | Collingwood | 6 | 65 | 66.2 | 66 | +1 | clear |

## Board top-50 (A4 context)
  1. Harry Sheezel            MID         7207
  2. Nick Daicos              MID         7069
  3. Luke Jackson             RUC         6986
  4. Nasiah Wanganeen-Milera  MID         5961
  5. Tristan Xerri            RUC         5755
  6. Max Holmes               MID         5499
  7. Errol Gulden             MID         5299
  8. Zak Butters              MID         5225
  9. Josh Treacy              KEY_FWD     5166
 10. Finn Callaghan           MID         4952
 11. Will Ashcroft            MID         4823
 12. Bailey Smith             MID         4773
 13. Lachlan Ash              GEN_DEF     4663
 14. Archie Roberts           GEN_DEF     4597
 15. Tom Green                MID         4472
 16. Ryley Sanders            MID         4212
 17. Caleb Serong             MID         4202
 18. Jason Horne-Francis      MID         4199
 19. Willem Duursma           MID         4183
 20. Noah Anderson            MID         4131
 21. Sam Darcy                KEY_FWD     3978
 22. Jai Newcombe             MID         3889
 23. Murphy Reid              GEN_FWD     3843
 24. Colby McKercher          MID         3814
 25. Matt Rowell              MID         3779
 26. Darcy Wilmot             GEN_DEF     3774
 27. Sam Lalor                MID         3703
 28. Nick Watson              GEN_FWD     3579
 29. Harley Reid              MID         3565
 30. Riley Thilthorpe         KEY_FWD     3555
 31. Mac Andrew               KEY_DEF     3530
 32. Finn O'Sullivan          MID         3495
 33. Brodie Grundy            RUC         3344
 34. Isaac Heeney             MID         3327
 35. Bodhi Uwland             GEN_DEF     3288
 36. Nick Blakey              GEN_DEF     3287
 37. Levi Ashcroft            MID         3270
 38. Josh Worrell             GEN_DEF     3236
 39. Jagga Smith              MID         3219
 40. Chad Warner              MID         3148
 41. Nicholas Martin          MID         3122
 42. Marcus Bontempelli       MID         3109
 43. Christian Petracca       MID         3057
 44. George Wardlaw           MID         3033
 45. Kysaiah Pickett          GEN_FWD     3031
 46. Jordan Clark             GEN_DEF     3031
 47. Jake Bowey               GEN_DEF     2969
 48. Luke Davies-Uniacke      MID         2952
 49. Connor Rozee             MID         2917
 50. Timothy English          RUC         2907

## C1/C2 DEFINITION PROPOSAL (for supervisor ruling)
Rebuild the walk-forward book (s4 matrix protocol, as-of values, only <=T data) twice more:
(a) NAIVE BASELINE: last-2-season era-adjusted avg -> value via simple age curve + position multipliers;
(b) ORIGINAL V1 PICK MODEL: value = PVC(effective pick) with the V1 age/tenure profile.
Headline metrics, engine must beat both on: (1) within-player GATE-1 protocol (WF good/bust separation,
leakage-matched); (2) rank correlation of as-of value vs realized fwd best-3 production (real_mat);
(3) cohort growth-law shape error vs the realized production curve. Each becomes C1x/C2x scripted lines.
