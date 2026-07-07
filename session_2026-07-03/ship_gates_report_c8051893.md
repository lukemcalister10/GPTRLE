# ship_gates_check report — STATE: CANDIDATE v2.1 games-ramp (CURRENT, this directive) — head c8051893 store 644d1254
_Three-column rule (Luke, binding D10): every board output reports CONTROL / PREVIOUS / CURRENT with explicit deltas._
```
=== STATE: CANDIDATE v2.1 games-ramp (CURRENT, this directive) ===
=== SHIP GATES BOARD — head c8051893 store 644d1254 — suite 764a0d91 — 2026-07-03 ===
=== THREE-COLUMN RULE (Luke, binding D10): CONTROL=8aed420a · PREVIOUS=4a134d05 · CURRENT=c8051893 ===
A1        PASS    | PASS    | PASS     Duursma>Uwland: 4160 vs 1976
A2        FAIL    | FAIL    | FAIL     Curtis>=0.90xWard: 1358 vs 1488 (Ward=1653, ratio=0.822) [AMENDED 02/07/2026; UNCHANGED at 0.90 by ruling D7 — Luke: "we can look at Curtis down the line"]; Weddle>Ward: 1572 vs 1653
A3   [DC] FAIL    | FAIL    | FAIL     Connor Rozee: 2026=2917 2025=3992 ratio=0.73 (need >=0.75) [evaluated PRE-LTI-layer — Luke 02/07; AMENDED 0.80->0.75 Luke D7 data-caused (out for 2026), knife-edge by design]
          triage: [DC] gate — attribute ENGINE- vs DATA-caused BEFORE this blocks (SHIP_GATES PROCESS)
A4        PASS    | PASS    | PASS     Harley Reid board rank=29 ev=3565 (need TOP 40)
A5        FAIL    | PASS    | PASS     Jack Ginnivan=1799 (floor 1600); Jake Bowey=2969 (floor 2100); Nick Blakey=3287 (floor 2600) [SCAR floors — RE-BASE if PVC re-levels]  <- MOVED
A6        PASS    | PASS    | PASS     yr1-3 RUC median=436 (n=13, pooled — thin slice) vs pick-matched MID kernel median=554 (n=66, bw=0.6 log-pick, RATIFIED 02/07)
A7        PASS    | PASS    | PASS     Ryan Maric: fut-dominant=MID(60%) gfut=MID (need MID/MID); Ed Langdon: fut-dominant=GDEF(70%) gfut=GEN_DEF (need GDEF/GEN_DEF)
A8   [DC] PASS    | PASS    | PASS     Berry=2421 Tsatas=1140 ratio=2.12x (need >=2.00x) [display de-ambiguated D4 02/07]
A9        FAIL    | PASS    | PASS     Ginnivan>Ward: 1799 vs 1653  <- MOVED
A10  [DC] PASS    | PASS    | PASS     Charlie Curnow: 2026=888 2025=1745 ratio=0.51 (need >=0.50) [AMENDED 0.70->0.50 Luke 02/07 data-caused, PROVISIONAL — review at season-complete]
A11  [DC] PASS    | PASS    | PASS     Farrow>Patterson: 1644 vs 884; Cumming>Annable: 1948 vs 1326
A12  [DC] FAIL    | FAIL    | FAIL     Travaglia>Moraes: 712 vs 887; Smillie>Retschko: 773 vs 730
          triage: [DC] gate — attribute ENGINE- vs DATA-caused BEFORE this blocks (SHIP_GATES PROCESS)
A13       PENDING | PENDING | PENDING  PVC stage not run; advisory vs stand-in PVC[1]=3000: George Wardlaw=3033 lineball=True; Levi Ashcroft=3270 lineball=True
A14       PENDING | PENDING | PENDING  PVC stage not run; advisory vs stand-in PVC[8]=1704: Trent Rivers=1713 lineball=True; Zach Reid=1613 lineball=True; Jase Burgoyne=2092 lineball=False
A15       STRUCK  | STRUCK  | STRUCK   Luke 02/07/2026 — convexity dimension seeded as V_NEXT #1
B1        PASS    | PASS    | PASS     cross-cohort AVERAGE peak N=4 AVG(peak)=151 (need peak in yrs 4-6, >100; pre-peak dips of the AVERAGE <5% tolerated, path_ok=True; per-cohort UNGATED, table printed every run — Luke redefinition 02/07 D5); avg row: 1:100 2:129 3:140 4:151 5:148 6:140 7:123; cohorts n=17; matrix=s4_matrix_v21_c8051893.json
B2        PASS    | PASS    | PASS     median |IS-WF| leakage=0.0 %-pts (tol 0.5, SET 02/07/2026 — N=5 spread 0.00); GOOD>BUST separation: GEN_DEF 46/1, GEN_FWD 43/1, KEY_DEF 55/1, KEY_FWD 62/1, MID 50/0
B3        PENDING | PENDING | PENDING  book-gate set not yet enumerated as scripted checks — definition proposal in report; book headline shape covered by B1
B4        FAIL    | FAIL    | FAIL     regenerated rl_app_data.json md5=6f30a7c6 vs shipped b8f9e998 (byte-agree gate; export exit=0)
B5        FAIL    | FEATURE | FEATURE  floor-as-pricing-feature (Luke-ruled 02/07; VARIANT A flat .05 tail): 58 saves, aggregate lift +2117; pure lower bound: lowered=0 (bar 0), non-ND moved=0 (bar 0); saves table printed below (the new alarm surface)  <- MOVED
B6        FAIL    | FAIL    | PASS     ramp(0..14g)=[1019, 1397, 1730, 2464, 3103, 3190, 3238, 3291, 3305, 3314, 3367, 3435, 3523, 3563, 3592]; dips(more games worth less)=none; 0->6 rise T=+2219; 0->6 steps>50%T=none; rise by 3g=+1445 (need >=555) [whole-ramp re-spec, DECLARED thresholds]  <- MOVED
C1        PENDING | PENDING | PENDING  naive-baseline book not yet built — definition proposal in report (needs its own directive)
C2        PENDING | PENDING | PENDING  V1-pick-model book not yet built — definition proposal in report (needs its own directive)
          columns: CONTROL | PREVIOUS | CURRENT (three-column rule; snapshots data/gates_snapshots/)
VERDICT: FAIL=4  FEATURE=1  PASS=12  PENDING=5  STRUCK=1  (125s)
```

## Supporting detail

B1 per-cohort curves (UNGATED — printed every gates-board run, Luke eyeball channel):
| cohort | peakN | d1 | d2 | d3 | d4 | d5 | d6 | d7 |
|---|---|---|---|---|---|---|---|---|
| 2004 | 5 | 100 | 139 | 168 | 172 | 184 | 164 | 144 |
| 2005 | 4 | 100 | 146 | 148 | 199 | 184 | 176 | 151 |
| 2006 | 4 | 100 | 133 | 146 | 162 | 160 | 157 | 136 |
| 2007 | 5 | 100 | 132 | 125 | 133 | 158 | 152 | 128 |
| 2008 | 4 | 100 | 134 | 179 | 195 | 173 | 155 | 135 |
| 2009 | 2 | 100 | 124 | 110 | 111 | 111 | 101 | 87 |
| 2010 | 4 | 100 | 136 | 148 | 165 | 159 | 140 | 116 |
| 2011 | 4 | 100 | 133 | 157 | 178 | 174 | 164 | 135 |
| 2012 | 4 | 100 | 118 | 129 | 131 | 125 | 120 | 100 |
| 2013 | 5 | 100 | 136 | 153 | 183 | 185 | 163 | 125 |
| 2014 | 4 | 100 | 130 | 148 | 159 | 144 | 141 | 138 |
| 2015 | 4 | 100 | 121 | 126 | 130 | 125 | 125 | 118 |
| 2016 | 4 | 100 | 130 | 146 | 168 | 157 | 159 | 135 |
| 2017 | 3 | 100 | 117 | 122 | 110 | 102 | 104 | 97 |
| 2018 | 4 | 100 | 129 | 127 | 136 | 132 | 122 | 112 |
| 2019 | 5 | 100 | 116 | 127 | 137 | 145 | 131 | 114 |
| 2020 | 3 | 100 | 116 | 116 | 105 | 107 | 107 | — |
| **AVG (the gated row)** | **4** | **100** | **129** | **140** | **151** | **148** | **140** | **123** |

B5 FLOOR-SAVES table (n=58, aggregate lift=+2117 — printed every gates-board run, the new alarm surface):
| player | club | yrs-in-system | raw ev | floor | saved-to | lift | register status |
|---|---|---|---|---|---|---|---|
| Billy Cootee | Sydney | 1 | 30 | 224.6 | 225 | +195 | clear |
| Dylan Patterson | Gold Coast | 1 | 760 | 884.2 | 884 | +124 | clear |
| Jamarra Ugle-Hagan | Western Bulldogs | 6 | 157 | 270.0 | 270 | +113 | clear |
| Paddy Dow | Carlton | 9 | 13 | 112.4 | 112 | +99 | clear |
| Jaeger O'Meara | Gold Coast | 15 | 62 | 150.0 | 150 | +88 | clear |
| Aidan Johnson | Melbourne | 2 | 30 | 107.8 | 108 | +78 | clear |
| Oliver Wiltshire | Geelong | 3 | 13 | 86.2 | 86 | +73 | clear |
| Conor Stone | GWS | 6 | 25 | 96.7 | 97 | +72 | clear |
| Chayce Jones | Adelaide | 8 | 9 | 80.2 | 80 | +71 | clear |
| Nicholas Coffield | St Kilda | 9 | 16 | 85.2 | 85 | +69 | clear |
| Jack Martin | Gold Coast | 14 | 44 | 112.4 | 112 | +68 | clear |
| Steele Sidebottom | Collingwood | 18 | 3 | 69.0 | 69 | +66 | clear |
| Jake Melksham | Essendon | 17 | 11 | 74.5 | 74 | +63 | clear |
| Luke Pedlar | Adelaide | 6 | 66 | 124.2 | 124 | +58 | clear |
| Angus Anderson | Collingwood | 1 | 91 | 139.1 | 139 | +48 | clear |
| Jacob Hopper | GWS | 11 | 42 | 89.7 | 90 | +48 | clear |
| Callum Ah Chee | Gold Coast | 11 | 38 | 85.2 | 85 | +47 | clear |
| Cody Angove | GWS | 2 | 174 | 215.6 | 216 | +42 | clear |
| Sam Davidson | Western Bulldogs | 2 | 92 | 133.0 | 133 | +41 | clear |
| Hunter Clark | St Kilda | 9 | 50 | 89.7 | 90 | +40 | clear |
| Liam Stocker | Carlton | 8 | 2 | 39.8 | 40 | +38 | clear |
| Brandon Starcevich | Brisbane | 9 | 6 | 43.0 | 43 | +37 | clear |
| Tai Hayes | Brisbane | 1 | 176 | 210.6 | 211 | +35 | clear |
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
| Mitch McGovern | Adelaide | 12 | 9 | 24.2 | 24 | +15 | clear |
| Daniel Butler | Richmond | 12 | 0 | 15.4 | 15 | +15 | clear |
| Harvey Gallagher | Western Bulldogs | 4 | 98 | 111.7 | 112 | +14 | clear |
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
| Judson Clarke | Richmond | 5 | 74 | 78.4 | 78 | +4 | LTI (2025) |
| Liam Ryan | West Coast | 9 | 27 | 30.6 | 31 | +4 | clear |
| Oskar Baker | Melbourne | 9 | 18 | 20.6 | 21 | +3 | clear |
| Finlay Macrae | Collingwood | 6 | 65 | 66.2 | 66 | +1 | clear |

## Board top-50 (A4 context) — CONTROL 8aed420a · PREVIOUS 4a134d05 · CURRENT c8051893
| # | player | pos | CONTROL | PREVIOUS | CURRENT | D vs ctl | D vs prev |
|---|---|---|---|---|---|---|---|
| 1 | Harry Sheezel | MID | 7287 | 7207 | 7207 | -80 | +0 |
| 2 | Nick Daicos | MID | 7059 | 7069 | 7069 | +10 | +0 |
| 3 | Luke Jackson | RUC | 7731 | 6986 | 6986 | -745 | +0 |
| 4 | Nasiah Wanganeen-Milera | MID | 5730 | 5961 | 5961 | +231 | +0 |
| 5 | Tristan Xerri | RUC | 5469 | 5755 | 5755 | +286 | +0 |
| 6 | Max Holmes | MID | 5154 | 5499 | 5499 | +345 | +0 |
| 7 | Errol Gulden | MID | 4947 | 5299 | 5299 | +352 | +0 |
| 8 | Zak Butters | MID | 5020 | 5225 | 5225 | +205 | +0 |
| 9 | Josh Treacy | KEY_FWD | — | — | 5166 | — | — |
| 10 | Finn Callaghan | MID | 4538 | 4952 | 4952 | +414 | +0 |
| 11 | Will Ashcroft | MID | 4885 | 4823 | 4823 | -62 | +0 |
| 12 | Bailey Smith | MID | 5122 | 4773 | 4773 | -349 | +0 |
| 13 | Lachlan Ash | GEN_DEF | 3934 | 4663 | 4663 | +729 | +0 |
| 14 | Archie Roberts | GEN_DEF | 4625 | 4597 | 4597 | -28 | +0 |
| 15 | Tom Green | MID | 3950 | 4472 | 4472 | +522 | +0 |
| 16 | Ryley Sanders | MID | 4268 | 4212 | 4212 | -56 | +0 |
| 17 | Caleb Serong | MID | 4276 | 4202 | 4202 | -74 | +0 |
| 18 | Jason Horne-Francis | MID | 4050 | 4199 | 4199 | +149 | +0 |
| 19 | Willem Duursma | MID | 4179 | 4183 | 4160 | -19 | -23 |
| 20 | Noah Anderson | MID | 4216 | 4131 | 4131 | -85 | +0 |
| 21 | Sam Darcy | KEY_FWD | 3902 | 3978 | 3978 | +76 | +0 |
| 22 | Jai Newcombe | MID | — | — | 3889 | — | — |
| 23 | Murphy Reid | GEN_FWD | 3819 | 3843 | 3843 | +24 | +0 |
| 24 | Colby McKercher | MID | 3862 | 3814 | 3814 | -48 | +0 |
| 25 | Matt Rowell | MID | 3628 | 3779 | 3779 | +151 | +0 |
| 26 | Darcy Wilmot | GEN_DEF | 3606 | 3774 | 3774 | +168 | +0 |
| 27 | Sam Lalor | MID | 3552 | 3703 | 3703 | +151 | +0 |
| 28 | Nick Watson | GEN_FWD | 3598 | 3579 | 3579 | -19 | +0 |
| 29 | Harley Reid | MID | 3523 | 3565 | 3565 | +42 | +0 |
| 30 | Riley Thilthorpe | KEY_FWD | 3649 | 3555 | 3555 | -94 | +0 |
| 31 | Mac Andrew | KEY_DEF | 3569 | 3530 | 3530 | -39 | +0 |
| 32 | Finn O'Sullivan | MID | 3467 | 3495 | 3495 | +28 | +0 |
| 33 | Brodie Grundy | RUC | 3318 | 3344 | 3344 | +26 | +0 |
| 34 | Isaac Heeney | MID | 3298 | 3327 | 3327 | +29 | +0 |
| 35 | Bodhi Uwland | GEN_DEF | — | — | 3288 | — | — |
| 36 | Nick Blakey | GEN_DEF | 3053 | 3287 | 3287 | +234 | +0 |
| 37 | Levi Ashcroft | MID | 3271 | 3270 | 3270 | -1 | +0 |
| 38 | Josh Worrell | GEN_DEF | 3341 | 3236 | 3236 | -105 | +0 |
| 39 | Jagga Smith | MID | 3270 | 3219 | 3188 | -82 | -31 |
| 40 | Chad Warner | MID | 3297 | 3148 | 3148 | -149 | +0 |
| 41 | Nicholas Martin | MID | — | — | 3122 | — | — |
| 42 | Marcus Bontempelli | MID | 3101 | 3109 | 3109 | +8 | +0 |
| 43 | Christian Petracca | MID | 3057 | 3057 | 3057 | +0 | +0 |
| 44 | George Wardlaw | MID | 3035 | 3033 | 3033 | -2 | +0 |
| 45 | Kysaiah Pickett | GEN_FWD | 3860 | 3031 | 3031 | -829 | +0 |
| 46 | Jordan Clark | GEN_DEF | 3123 | 3031 | 3031 | -92 | +0 |
| 47 | Jake Bowey | GEN_DEF | 2585 | 2969 | 2969 | +384 | +0 |
| 48 | Luke Davies-Uniacke | MID | 2967 | 2952 | 2952 | -15 | +0 |
| 49 | Connor Rozee | MID | 2679 | 2917 | 2917 | +238 | +0 |
| 50 | Timothy English | RUC | 2893 | 2907 | 2907 | +14 | +0 |

## C1/C2 DEFINITION PROPOSAL (for supervisor ruling)
Rebuild the walk-forward book (s4 matrix protocol, as-of values, only <=T data) twice more:
(a) NAIVE BASELINE: last-2-season era-adjusted avg -> value via simple age curve + position multipliers;
(b) ORIGINAL V1 PICK MODEL: value = PVC(effective pick) with the V1 age/tenure profile.
Headline metrics, engine must beat both on: (1) within-player GATE-1 protocol (WF good/bust separation,
leakage-matched); (2) rank correlation of as-of value vs realized fwd best-3 production (real_mat);
(3) cohort growth-law shape error vs the realized production curve. Each becomes C1x/C2x scripted lines.
