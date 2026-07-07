# ship_gates_check report — head 8aed420a store 644d1254
```
=== SHIP GATES BOARD — head 8aed420a store 644d1254 — suite 764a0d91 — 2026-07-02 ===
A1        PASS     Duursma>Uwland: 4179 vs 1781
A2        FAIL     Curtis>=0.90xWard: 1162 vs 1604 (Ward=1782, ratio=0.652) [AMENDED 02/07/2026]; Weddle>Ward: 1628 vs 1782
A3   [DC] FAIL     Connor Rozee: 2026=2679 2025=3874 ratio=0.69 (need >=0.80) [evaluated PRE-LTI-layer — Luke 02/07]
          triage: [DC] gate — attribute ENGINE- vs DATA-caused BEFORE this blocks (SHIP_GATES PROCESS)
A4        PASS     Harley Reid board rank=32 ev=3523 (need TOP 40)
A5        FAIL     Jack Ginnivan=1578 (floor 1600); Jake Bowey=2585 (floor 2100); Nick Blakey=3053 (floor 2600) [SCAR floors — RE-BASE if PVC re-levels]
A6        PASS     yr1-3 RUC median=314 (n=13, pooled — thin slice) vs pick-matched MID kernel median=502 (n=66, bw=0.6 log-pick, RATIFIED 02/07)
A7        PASS     Ryan Maric: fut-dominant=MID(60%) gfut=MID (need MID/MID); Ed Langdon: fut-dominant=GDEF(70%) gfut=GEN_DEF (need GDEF/GEN_DEF)
A8   [DC] PASS     Berry=3473 Tsatas=1083 ratio=3.21x (need >=2.00x) [display de-ambiguated D4 02/07]
A9        FAIL     Ginnivan>Ward: 1578 vs 1782
A10  [DC] PASS     Charlie Curnow: 2026=944 2025=1849 ratio=0.51 (need >=0.50) [AMENDED 0.70->0.50 Luke 02/07 data-caused, PROVISIONAL — review at season-complete]
A11  [DC] PASS     Farrow>Patterson: 1641 vs 982; Cumming>Annable: 2002 vs 936
A12  [DC] FAIL     Travaglia>Moraes: 601 vs 876; Smillie>Retschko: 896 vs 730
          triage: [DC] gate — attribute ENGINE- vs DATA-caused BEFORE this blocks (SHIP_GATES PROCESS)
A13       PENDING  PVC stage not run; advisory vs stand-in PVC[1]=3000: George Wardlaw=3035 lineball=True; Levi Ashcroft=3271 lineball=True
A14       PENDING  PVC stage not run; advisory vs stand-in PVC[8]=1704: Trent Rivers=1725 lineball=True; Zach Reid=1680 lineball=True; Jase Burgoyne=2191 lineball=False
A15       STRUCK   Luke 02/07/2026 — convexity dimension seeded as V_NEXT #1
B1        PASS     cross-cohort AVERAGE peak N=4 AVG(peak)=161 (need peak in yrs 4-6, >100; pre-peak dips of the AVERAGE <5% tolerated, path_ok=True; per-cohort UNGATED, table printed every run — Luke redefinition 02/07 D5); avg row: 1:100 2:132 3:146 4:161 5:158 6:148 7:131; cohorts n=17; matrix=s4_matrix_nogames.json
B2        PASS     median |IS-WF| leakage=0.0 %-pts (tol 0.5, SET 02/07/2026 — N=5 spread 0.00); GOOD>BUST separation: GEN_DEF 52/1, GEN_FWD 44/1, KEY_DEF 60/1, KEY_FWD 64/1, MID 52/0
B3        PENDING  book-gate set not yet enumerated as scripted checks — definition proposal in report; book headline shape covered by B1
B4        FAIL     regenerated rl_app_data.json md5=1898ead7 vs shipped b8f9e998 (byte-agree gate; export exit=0)
B5        FAIL     51 ND-entrant LISTED players below the signed year-schedule floor (yrs1-7+ .45/.35/.28/.21/.13/.09/.05 x draftval; Luke 02/07 D4); worst: Nicholas Holman(yr13)=0<20(0.05x); Steele Sidebottom(yr18)=3<69(0.05x); Daniel Butler(yr12)=1<15(0.05x); Jed Bews(yr15)=1<15(0.05x)
B6        FAIL     ramp(0..14g)=[745, 745, 745, 745, 745, 745, 3263, 3352, 3357, 3538, 3318, 3464, 3531, 3583, 3578]; dips(more games worth less)=[(9, -220.0), (13, -5.0)]; 0->6 rise T=+2518; 0->6 steps>50%T=[(5, 2518)]; rise by 3g=+0 (need >=630) [whole-ramp re-spec, DECLARED thresholds]
C1        PENDING  naive-baseline book not yet built — definition proposal in report (needs its own directive)
C2        PENDING  V1-pick-model book not yet built — definition proposal in report (needs its own directive)
VERDICT: FAIL=8  PASS=9  PENDING=5  STRUCK=1  (109s)
```

## Supporting detail

B1 per-cohort curves (UNGATED — printed every gates-board run, Luke eyeball channel):
| cohort | peakN | d1 | d2 | d3 | d4 | d5 | d6 | d7 |
|---|---|---|---|---|---|---|---|---|
| 2004 | 5 | 100 | 139 | 168 | 175 | 190 | 168 | 146 |
| 2005 | 4 | 100 | 145 | 148 | 203 | 185 | 179 | 157 |
| 2006 | 5 | 100 | 142 | 159 | 178 | 180 | 172 | 148 |
| 2007 | 5 | 100 | 133 | 128 | 140 | 166 | 155 | 135 |
| 2008 | 4 | 100 | 134 | 181 | 197 | 177 | 158 | 139 |
| 2009 | 2 | 100 | 122 | 111 | 114 | 117 | 104 | 91 |
| 2010 | 4 | 100 | 143 | 160 | 178 | 169 | 153 | 130 |
| 2011 | 4 | 100 | 136 | 167 | 192 | 187 | 174 | 142 |
| 2012 | 4 | 100 | 123 | 136 | 140 | 135 | 128 | 106 |
| 2013 | 5 | 100 | 137 | 159 | 192 | 193 | 167 | 129 |
| 2014 | 4 | 100 | 134 | 156 | 169 | 156 | 150 | 145 |
| 2015 | 4 | 100 | 126 | 131 | 136 | 135 | 134 | 123 |
| 2016 | 4 | 100 | 138 | 157 | 183 | 174 | 175 | 152 |
| 2017 | 3 | 100 | 119 | 125 | 115 | 109 | 105 | 98 |
| 2018 | 4 | 100 | 126 | 134 | 144 | 139 | 128 | 118 |
| 2019 | 5 | 100 | 132 | 148 | 162 | 170 | 151 | 135 |
| 2020 | 3 | 100 | 112 | 118 | 109 | 110 | 110 | — |
| **AVG (the gated row)** | **4** | **100** | **132** | **146** | **161** | **158** | **148** | **131** |

## Board top-50 (A4 context)
  1. Luke Jackson             RUC         7731
  2. Harry Sheezel            MID         7287
  3. Nick Daicos              MID         7059
  4. Nasiah Wanganeen-Milera  MID         5730
  5. Tristan Xerri            RUC         5469
  6. Max Holmes               MID         5154
  7. Bailey Smith             MID         5122
  8. Zak Butters              MID         5020
  9. Errol Gulden             MID         4947
 10. Josh Treacy              KEY_FWD     4928
 11. Will Ashcroft            MID         4885
 12. Archie Roberts           GEN_DEF     4625
 13. Finn Callaghan           MID         4538
 14. Caleb Serong             MID         4276
 15. Ryley Sanders            MID         4268
 16. Noah Anderson            MID         4216
 17. Willem Duursma           MID         4179
 18. Jason Horne-Francis      MID         4050
 19. Jai Newcombe             MID         3991
 20. Tom Green                MID         3950
 21. Lachlan Ash              GEN_DEF     3934
 22. Sam Darcy                KEY_FWD     3902
 23. Colby McKercher          MID         3862
 24. Kysaiah Pickett          GEN_FWD     3860
 25. Murphy Reid              GEN_FWD     3819
 26. Riley Thilthorpe         KEY_FWD     3649
 27. Matt Rowell              MID         3628
 28. Darcy Wilmot             GEN_DEF     3606
 29. Nick Watson              GEN_FWD     3598
 30. Mac Andrew               KEY_DEF     3569
 31. Sam Lalor                MID         3552
 32. Harley Reid              MID         3523
 33. Sam Berry                MID         3473
 34. Finn O'Sullivan          MID         3467
 35. Bodhi Uwland             GEN_DEF     3376
 36. Josh Worrell             GEN_DEF     3341
 37. Brodie Grundy            RUC         3318
 38. Isaac Heeney             MID         3298
 39. Chad Warner              MID         3297
 40. Levi Ashcroft            MID         3271
 41. Jagga Smith              MID         3270
 42. Jordan Clark             GEN_DEF     3123
 43. Marcus Bontempelli       MID         3101
 44. Christian Petracca       MID         3057
 45. Nick Blakey              GEN_DEF     3053
 46. George Wardlaw           MID         3035
 47. Luke Davies-Uniacke      MID         2967
 48. Reuben Ginbey            KEY_DEF     2896
 49. Timothy English          RUC         2893
 50. Logan Morris             KEY_FWD     2879

## C1/C2 DEFINITION PROPOSAL (for supervisor ruling)
Rebuild the walk-forward book (s4 matrix protocol, as-of values, only <=T data) twice more:
(a) NAIVE BASELINE: last-2-season era-adjusted avg -> value via simple age curve + position multipliers;
(b) ORIGINAL V1 PICK MODEL: value = PVC(effective pick) with the V1 age/tenure profile.
Headline metrics, engine must beat both on: (1) within-player GATE-1 protocol (WF good/bust separation,
leakage-matched); (2) rank correlation of as-of value vs realized fwd best-3 production (real_mat);
(3) cohort growth-law shape error vs the realized production curve. Each becomes C1x/C2x scripted lines.
